#!/usr/bin/env python3
"""Download and parse Hi-net/JMA arrival-time measure files for Sanriku.

This script is intentionally self-contained and uses only fixed byte slices for
JMA measure records (96 bytes excluding line endings). It performs a first-chunk
smoke test before processing the complete requested interval.
"""
from __future__ import annotations

import csv
import hashlib
import json
import os
import re
import sys
import time
import traceback
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

import pandas as pd

# ----------------------------- fixed configuration -----------------------------
PROJECT_DIR = Path("<CASE_ROOT>")
OUTPUT_DIR = PROJECT_DIR / "run/00_travel_time_download/exp_run/outputs/01_hinet_jma_arrivals_workflow"
SCRIPT_PATH = PROJECT_DIR / "run/00_travel_time_download/exp_run/scripts/01_hinet_jma_arrivals_workflow.py"
ENV_PATH = PROJECT_DIR / "data/hinet_account/.env"
EXISTING_RAW_DIR = PROJECT_DIR.parent / "data_downloading/travel_time/data/raw"
REFERENCE_PHASE = PROJECT_DIR / "data/regional/phase.dat"
REFERENCE_STATION = PROJECT_DIR / "data/regional/station.sta"
STATION_TEXT = PROJECT_DIR / "data/stations/station.txt"

START_DATE = date(2025, 6, 1)
END_DATE_EXCLUSIVE = date(2026, 5, 2)
CHUNK_DAYS = 5
MAX_SPAN_DAYS = 7
SMOKE_START = START_DATE
SANRIKU = {"lat_min": 38.50, "lat_max": 42.50, "lon_min": 141.00, "lon_max": 144.50}
JST = timezone(timedelta(hours=9))
UTC = timezone.utc
RETRIES_PER_ACCOUNT = 3
INITIAL_BACKOFF_SECONDS = 10

EVENT_COLUMNS = ["event_id", "origin_time", "latitude", "longitude", "depth_km", "magnitude", "region", "npicks", "source_file"]
PICK_COLUMNS = ["event_id", "station_code", "station_number", "p_pick_time", "s_pick_time", "p_quality", "s_quality", "weight", "source_file"]
MANIFEST_COLUMNS = ["start_date", "span_days", "raw_file", "exists", "size_bytes", "status", "message"]

# ----------------------------- utility functions ------------------------------
def log(message: str) -> None:
    print(f"[{datetime.now(timezone.utc).isoformat()}] {message}", flush=True)


def ensure_output_dir() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def cleanup_stale_derived_outputs() -> None:
    """Remove quick-to-regenerate products while preserving raw measure files.

    Existing non-empty measure_*.txt files are intentionally retained because
    the task requires reusing them by default rather than overwriting raw data.
    All normalized tables, QC files, manifests, and compatibility exports are
    regenerated from the current raw/download workflow on every run.
    """
    for path in OUTPUT_DIR.iterdir():
        if not path.is_file():
            continue
        if path.name.startswith("measure_") and path.suffix == ".txt":
            # The complete source raw files live outside this task output.
            # Remove stale task-local downloads so they cannot be mistaken for
            # the authoritative input in source-reuse mode.
            if EXISTING_RAW_DIR.exists():
                path.unlink()
            continue
        if path.name.startswith("measure_") and path.name.endswith(".txt.part"):
            path.unlink()
            continue
        path.unlink()


def write_json(path: Path, obj: Any) -> None:
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False, sort_keys=True), encoding="utf-8")


def safe_message(message: Any, secrets: Sequence[str] = ()) -> str:
    text = str(message)
    for secret in secrets:
        if secret:
            text = text.replace(secret, "<REDACTED>")
    # Redact common password assignments in library messages.
    text = re.sub(r"(?i)(password\s*[=:]\s*)\S+", r"\1<REDACTED>", text)
    text = re.sub(r"(?i)(passwd\s*[=:]\s*)\S+", r"\1<REDACTED>", text)
    return text[:1000]


def iso_utc(dt: datetime) -> str:
    return dt.astimezone(UTC).isoformat(timespec="microseconds").replace("+00:00", "Z")


def parse_int(text: str) -> Optional[int]:
    s = text.strip()
    if not s:
        return None
    try:
        return int(s)
    except ValueError:
        return None


def parse_implied_float(text: str, decimals: int) -> Optional[float]:
    s = text.strip()
    if not s:
        return None
    try:
        if "." in s:
            return float(s)
        return int(s) / (10 ** decimals)
    except ValueError:
        return None


def add_fractional_seconds(base: datetime, seconds: float) -> datetime:
    whole = int(seconds)
    micro = int(round((seconds - whole) * 1_000_000))
    if micro >= 1_000_000:
        whole += 1
        micro -= 1_000_000
    return base.replace(second=0, microsecond=0) + timedelta(seconds=whole, microseconds=micro)


def make_datetime_jst(year: int, month: int, day: int, hour: int, minute: int, second: float) -> datetime:
    base = datetime(year, month, day, hour, minute, 0, tzinfo=JST)
    return add_fractional_seconds(base, second)


def read_dotenv(path: Path) -> Dict[str, str]:
    values: Dict[str, str] = {}
    if not path.exists():
        return values
    for raw in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, val = line.split("=", 1)
        key = key.strip()
        val = val.strip().strip('"').strip("'")
        if key:
            values[key] = val
    return values


@dataclass(frozen=True)
class Account:
    username: str
    password: str
    label: str


def load_accounts() -> List[Account]:
    envfile = read_dotenv(ENV_PATH)
    merged = dict(envfile)
    merged.update({k: v for k, v in os.environ.items() if v is not None})

    pairs: List[Tuple[str, str]] = []
    candidate_pairs = [
        ("HINET_USERNAME", "HINET_PASSWORD"),
        ("HINET_USER", "HINET_PASS"),
        ("HINET_ID", "HINET_PASSWORD"),
        ("NIED_USERNAME", "NIED_PASSWORD"),
        ("USERNAME", "PASSWORD"),
    ]
    for ukey, pkey in candidate_pairs:
        if merged.get(ukey) and merged.get(pkey):
            pairs.append((merged[ukey], merged[pkey]))

    # Indexed account pairs: HINET_USERNAME_1/HINET_PASSWORD_1, etc.
    for key, val in merged.items():
        m = re.match(r"^(?:HINET_)?(?:USERNAME|USER|ID)_(\d+)$", key)
        if not m:
            continue
        idx = m.group(1)
        for pkey in (f"HINET_PASSWORD_{idx}", f"HINET_PASS_{idx}", f"PASSWORD_{idx}", f"PASS_{idx}"):
            if merged.get(pkey):
                pairs.append((val, merged[pkey]))
                break

    # List-style account values, separated by comma/semicolon/colon-free pipes.
    users = merged.get("HINET_USERNAMES") or merged.get("HINET_USERS")
    pwds = merged.get("HINET_PASSWORDS") or merged.get("HINET_PASSES")
    if users and pwds:
        split_users = [x.strip() for x in re.split(r"[,;|]", users) if x.strip()]
        split_pwds = [x.strip() for x in re.split(r"[,;|]", pwds) if x.strip()]
        for u, p in zip(split_users, split_pwds):
            pairs.append((u, p))

    seen = set()
    accounts: List[Account] = []
    for u, p in pairs:
        if not u or not p:
            continue
        key = (u, p)
        if key in seen:
            continue
        seen.add(key)
        accounts.append(Account(u, p, f"account_{len(accounts)+1}"))
    if not accounts:
        raise RuntimeError(f"No Hi-net credentials found in environment or {ENV_PATH}")
    log(f"Loaded {len(accounts)} Hi-net account(s); credential values are redacted.")
    return accounts


@dataclass(frozen=True)
class Chunk:
    index: int
    start: date
    end: date
    span_days: int
    raw_file: Path


def build_chunks() -> List[Chunk]:
    chunks: List[Chunk] = []
    current = START_DATE
    idx = 1
    while current < END_DATE_EXCLUSIVE:
        end = min(current + timedelta(days=CHUNK_DAYS), END_DATE_EXCLUSIVE)
        span = (end - current).days
        if span <= 0 or span > MAX_SPAN_DAYS:
            raise RuntimeError(f"Invalid chunk span {span} for {current}")
        raw = OUTPUT_DIR / f"measure_{current:%Y%m%d}_{span}.txt"
        chunks.append(Chunk(idx, current, end, span, raw))
        idx += 1
        current = end
    if chunks[0].start != date(2025, 6, 1) or chunks[-1].start != date(2026, 4, 27) or len(chunks) != 67:
        raise RuntimeError("Chunk schedule does not match the requested 67 five-day half-open windows")
    return chunks


def scheduled_output_manifest(chunks: Sequence[Chunk], status: str, message: str) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for chunk in chunks:
        rows.append({
            "start_date": chunk.start.isoformat(),
            "span_days": chunk.span_days,
            "raw_file": str(chunk.raw_file),
            "exists": chunk.raw_file.exists(),
            "size_bytes": chunk.raw_file.stat().st_size if chunk.raw_file.exists() else 0,
            "status": status if chunk.raw_file.exists() and chunk.raw_file.stat().st_size > 0 else "missing",
            "message": message if chunk.raw_file.exists() and chunk.raw_file.stat().st_size > 0 else "scheduled raw file is missing or empty",
        })
    return rows


def scheduled_raw_files_complete(chunks: Sequence[Chunk]) -> bool:
    return all(chunk.raw_file.exists() and chunk.raw_file.stat().st_size > 0 for chunk in chunks)


def discover_existing_raw_files() -> List[Path]:
    """Select the complete existing raw files for the requested time window."""
    if not EXISTING_RAW_DIR.exists():
        return []
    pattern = re.compile(r"^measure_(\d{8})_(\d+)\.txt$")
    candidates: List[Tuple[date, int, Path]] = []
    for path in sorted(EXISTING_RAW_DIR.glob("measure_*.txt")):
        match = pattern.match(path.name)
        if not match or path.stat().st_size <= 0:
            continue
        start = datetime.strptime(match.group(1), "%Y%m%d").date()
        span = int(match.group(2))
        end = start + timedelta(days=span)
        if START_DATE <= start < END_DATE_EXCLUSIVE and end <= END_DATE_EXCLUSIVE:
            candidates.append((start, span, path))
    candidates.sort(key=lambda item: (item[0], item[1], item[2].name))
    files: List[Path] = []
    previous_end: Optional[date] = None
    for start, span, path in candidates:
        end = start + timedelta(days=span)
        if previous_end is not None and start < previous_end:
            raise RuntimeError(f"overlapping existing raw intervals: {path.name}")
        files.append(path)
        previous_end = end
    if not files or files[0].name != "measure_20250601_5.txt":
        raise RuntimeError("existing raw data does not start at 2025-06-01")
    if files[-1].name != "measure_20260501_1.txt":
        raise RuntimeError("existing raw data does not end at the required 2026-05-01 boundary")
    return files


def existing_raw_manifest(raw_files: Sequence[Path]) -> List[Dict[str, Any]]:
    pattern = re.compile(r"^measure_(\d{8})_(\d+)\.txt$")
    rows: List[Dict[str, Any]] = []
    for path in raw_files:
        match = pattern.match(path.name)
        if not match:
            continue
        start = datetime.strptime(match.group(1), "%Y%m%d").date()
        span = int(match.group(2))
        rows.append({
            "start_date": start.isoformat(),
            "span_days": span,
            "raw_file": str(path),
            "exists": True,
            "size_bytes": path.stat().st_size,
            "status": "reused_existing_source",
            "message": "previously downloaded raw file reused; network download skipped",
        })
    return rows


def write_chunk_schedule(chunks: Sequence[Chunk]) -> None:
    rows = [
        {
            "chunk_index": c.index,
            "start_date": c.start.isoformat(),
            "end_date_exclusive": c.end.isoformat(),
            "span_days": c.span_days,
            "raw_file": str(c.raw_file),
        }
        for c in chunks
    ]
    pd.DataFrame(rows).to_csv(OUTPUT_DIR / "chunk_schedule.csv", index=False)


def import_hinet_client():
    """Import HinetPy Client with a local urllib3 compatibility shim.

    Some installed HinetPy releases import ``create_urllib3_context`` from
    ``urllib3.util``. Recent urllib3 builds may expose that symbol only from
    ``urllib3.util.ssl_`` in the runtime environment, causing HinetPy import to
    fail before any task code runs. This shim patches the already-installed
    urllib3 module in memory only; it does not install packages or change the
    global environment.
    """
    try:
        import urllib3.util as urllib3_util  # type: ignore

        if not hasattr(urllib3_util, "create_urllib3_context"):
            from urllib3.util.ssl_ import create_urllib3_context  # type: ignore

            setattr(urllib3_util, "create_urllib3_context", create_urllib3_context)
    except Exception as exc:
        log(f"urllib3 compatibility pre-check failed before HinetPy import: {safe_message(exc)}")
    try:
        from HinetPy import Client  # type: ignore
    except Exception as exc:
        raise RuntimeError("HinetPy is required for Hi-net/JMA arrival-time download but could not be imported") from exc
    return Client


def download_chunk(chunk: Chunk, accounts: Sequence[Account], hinet_client_cls: Any, secrets: Sequence[str]) -> Dict[str, Any]:
    if chunk.raw_file.exists() and chunk.raw_file.stat().st_size > 0:
        return {
            "start_date": chunk.start.isoformat(),
            "span_days": chunk.span_days,
            "raw_file": str(chunk.raw_file),
            "exists": True,
            "size_bytes": chunk.raw_file.stat().st_size,
            "status": "skipped_existing",
            "message": "existing non-empty raw file reused",
        }

    partial_file = chunk.raw_file.with_name(chunk.raw_file.name + ".part")
    last_msg = "not attempted"
    for account in accounts:
        for attempt in range(1, RETRIES_PER_ACCOUNT + 1):
            try:
                if partial_file.exists():
                    partial_file.unlink()
                if chunk.raw_file.exists() and chunk.raw_file.stat().st_size == 0:
                    chunk.raw_file.unlink()
                log(f"Downloading {chunk.start} span={chunk.span_days} days using {account.label}, attempt {attempt}/{RETRIES_PER_ACCOUNT}")
                client = hinet_client_cls(account.username, account.password)
                saved = client.get_arrivaltime(str(chunk.start), chunk.span_days, filename=str(partial_file), os="UNIX")
                saved_path = Path(saved) if saved else partial_file
                if not partial_file.exists() and saved_path.exists() and saved_path.resolve() != partial_file.resolve():
                    raise RuntimeError(
                        "HinetPy saved the raw measure file outside the requested output path "
                        f"(returned {saved_path}); refusing to copy raw data."
                    )
                if partial_file.exists() and partial_file.stat().st_size > 0:
                    partial_file.replace(chunk.raw_file)
                exists = chunk.raw_file.exists()
                size = chunk.raw_file.stat().st_size if exists else 0
                if exists and size > 0:
                    return {
                        "start_date": chunk.start.isoformat(),
                        "span_days": chunk.span_days,
                        "raw_file": str(chunk.raw_file),
                        "exists": True,
                        "size_bytes": size,
                        "status": "downloaded",
                        "message": f"downloaded with {account.label}",
                    }
                last_msg = "download completed but raw file is missing or zero bytes"
                if partial_file.exists() and partial_file.stat().st_size == 0:
                    partial_file.unlink()
                if chunk.raw_file.exists() and chunk.raw_file.stat().st_size == 0:
                    return {
                        "start_date": chunk.start.isoformat(),
                        "span_days": chunk.span_days,
                        "raw_file": str(chunk.raw_file),
                        "exists": True,
                        "size_bytes": 0,
                        "status": "empty_file",
                        "message": last_msg,
                    }
            except Exception as exc:
                last_msg = safe_message(exc, secrets)
                log(f"Download failed for {chunk.start} with {account.label}, attempt {attempt}: {last_msg}")
                if attempt < RETRIES_PER_ACCOUNT:
                    time.sleep(INITIAL_BACKOFF_SECONDS * (2 ** (attempt - 1)))
    exists = chunk.raw_file.exists()
    size = chunk.raw_file.stat().st_size if exists else 0
    return {
        "start_date": chunk.start.isoformat(),
        "span_days": chunk.span_days,
        "raw_file": str(chunk.raw_file),
        "exists": exists,
        "size_bytes": size,
        "status": "failed",
        "message": last_msg,
    }


def write_manifest(rows: Sequence[Dict[str, Any]]) -> None:
    df = pd.DataFrame(rows, columns=MANIFEST_COLUMNS)
    df.to_csv(OUTPUT_DIR / "download_manifest.csv", index=False)


# ----------------------------- fixed width parser -----------------------------
def field(record: bytes, start_1: int, end_1: int) -> str:
    return record[start_1 - 1 : end_1].decode("cp932", errors="replace")


def parse_event_header(record: bytes) -> Dict[str, Any]:
    year = parse_int(field(record, 2, 5))
    month = parse_int(field(record, 6, 7))
    day = parse_int(field(record, 8, 9))
    hour = parse_int(field(record, 10, 11))
    minute = parse_int(field(record, 12, 13))
    second = parse_implied_float(field(record, 14, 17), 2)
    lat_deg = parse_int(field(record, 22, 24))
    lat_min = parse_implied_float(field(record, 25, 28), 2)
    lon_deg = parse_int(field(record, 33, 36))
    lon_min = parse_implied_float(field(record, 37, 40), 2)
    depth = parse_implied_float(field(record, 45, 49), 2)
    mag = parse_implied_float(field(record, 53, 54), 1)
    region = field(record, 69, 92).strip()
    needed = [year, month, day, hour, minute, second, lat_deg, lat_min, lon_deg, lon_min]
    if any(v is None for v in needed):
        raise ValueError("failed to parse required event header numeric fields")
    origin_jst = make_datetime_jst(int(year), int(month), int(day), int(hour), int(minute), float(second))
    return {
        "origin_jst": origin_jst,
        "origin_time": iso_utc(origin_jst),
        "latitude": float(lat_deg) + float(lat_min) / 60.0,
        "longitude": float(lon_deg) + float(lon_min) / 60.0,
        "depth_km": depth if depth is not None else float("nan"),
        "magnitude": mag if mag is not None else float("nan"),
        "region": region,
    }


def two_digit_year_to_full(yy: int, origin_year: int) -> int:
    # JMA files here are modern; keep the century near the event origin.
    century = (origin_year // 100) * 100
    candidate = century + yy
    if candidate - origin_year > 50:
        candidate -= 100
    elif origin_year - candidate > 50:
        candidate += 100
    return candidate


def parse_first_pick_datetime(record: bytes, origin_jst: datetime) -> Optional[datetime]:
    day = parse_int(field(record, 14, 15))
    hour = parse_int(field(record, 20, 21))
    minute = parse_int(field(record, 22, 23))
    second = parse_implied_float(field(record, 24, 27), 2)
    yy = parse_int(field(record, 88, 89))
    month = parse_int(field(record, 90, 91))
    if any(v is None for v in [day, hour, minute, second]):
        return None
    year = two_digit_year_to_full(int(yy), origin_jst.year) if yy is not None else origin_jst.year
    mon = int(month) if month is not None else origin_jst.month
    try:
        dt = make_datetime_jst(year, mon, int(day), int(hour), int(minute), float(second))
    except ValueError:
        return None
    # Normalize rare year/month ambiguity by choosing the date nearest origin.
    while dt - origin_jst > timedelta(days=15):
        dt -= timedelta(days=31)
    while origin_jst - dt > timedelta(days=15):
        dt += timedelta(days=31)
    return dt


def parse_second_pick_datetime(record: bytes, first_dt: Optional[datetime], origin_jst: datetime) -> Optional[datetime]:
    minute = parse_int(field(record, 32, 33))
    second = parse_implied_float(field(record, 34, 37), 2)
    if minute is None or second is None:
        return None
    anchor = first_dt if first_dt is not None else origin_jst
    try:
        dt = make_datetime_jst(anchor.year, anchor.month, anchor.day, anchor.hour, int(minute), float(second))
    except ValueError:
        return None
    if first_dt is not None:
        while dt < first_dt - timedelta(minutes=10):
            dt += timedelta(hours=1)
        while dt - first_dt > timedelta(hours=2):
            dt -= timedelta(hours=1)
    else:
        while dt < origin_jst:
            dt += timedelta(hours=1)
        while dt - origin_jst > timedelta(hours=3):
            dt -= timedelta(hours=1)
    return dt


def parse_station_pick(record: bytes, event_id: str, origin_jst: datetime, source_file: str) -> Dict[str, Any]:
    station_code = field(record, 2, 7).strip()
    station_number = field(record, 8, 11).strip()
    phase1 = field(record, 16, 19).strip()
    phase2 = field(record, 28, 31).strip()
    q1 = field(record, 92, 92).strip()
    q2 = field(record, 93, 93).strip()
    weight = field(record, 96, 96).strip()
    first_dt = parse_first_pick_datetime(record, origin_jst)
    second_dt = parse_second_pick_datetime(record, first_dt, origin_jst)

    p_dt: Optional[datetime] = None
    s_dt: Optional[datetime] = None
    p_quality = q1
    s_quality = q2

    if first_dt is not None:
        if "S" in phase1.upper() and "P" not in phase1.upper():
            s_dt = first_dt
            s_quality = q1
        else:
            p_dt = first_dt
            p_quality = q1
    if second_dt is not None:
        if "P" in phase2.upper() and "S" not in phase2.upper() and p_dt is None:
            p_dt = second_dt
            p_quality = q2
        else:
            s_dt = second_dt
            s_quality = q2

    return {
        "event_id": event_id,
        "station_code": station_code,
        "station_number": station_number,
        "p_pick_time": iso_utc(p_dt) if p_dt is not None else "-1",
        "s_pick_time": iso_utc(s_dt) if s_dt is not None else "-1",
        "p_quality": p_quality,
        "s_quality": s_quality,
        "weight": weight,
        "source_file": source_file,
    }


def stable_event_id(source_name: str, event_sequence: int, origin_time: str) -> str:
    digest = hashlib.sha1(f"{source_name}|{event_sequence}|{origin_time}".encode("utf-8")).hexdigest()[:8]
    return f"{source_name.replace('.txt', '')}_{event_sequence:05d}_{digest}"


def parse_measure_file(raw_file: Path) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], Dict[str, Any], List[Dict[str, Any]]]:
    source = raw_file.name
    events: List[Dict[str, Any]] = []
    picks: List[Dict[str, Any]] = []
    errors: List[Dict[str, Any]] = []
    qc = {
        "source_file": source,
        "size_bytes": raw_file.stat().st_size if raw_file.exists() else 0,
        "total_lines": 0,
        "valid_96_byte_records": 0,
        "invalid_length_records": 0,
        "j_records": 0,
        "pick_records": 0,
        "e_records": 0,
        "auxiliary_records": 0,
        "unrecognized_records": 0,
        "orphan_pick_records": 0,
        "closed_events": 0,
        "skipped_events": 0,
        "skipped_pick_records": 0,
        "unterminated_events": 0,
        "parse_errors": 0,
    }
    current: Optional[Dict[str, Any]] = None
    skip_current_event = False
    current_pick_count = 0
    event_sequence = 0
    with raw_file.open("rb") as f:
        for line_no, raw_line in enumerate(f, start=1):
            body = raw_line.rstrip(b"\r\n")
            if not body:
                continue
            qc["total_lines"] += 1
            if len(body) != 96:
                qc["invalid_length_records"] += 1
                errors.append({"source_file": source, "line_no": line_no, "error": f"record length {len(body)} != 96"})
                continue
            qc["valid_96_byte_records"] += 1
            rtype = chr(body[0])
            try:
                if rtype == "J":
                    qc["j_records"] += 1
                    if current is not None:
                        qc["unterminated_events"] += 1
                        errors.append({"source_file": source, "line_no": line_no, "error": "new J record before E terminator"})
                        current["npicks"] = current_pick_count
                        events.append({k: current[k] for k in EVENT_COLUMNS})
                    event_sequence += 1
                    current = None
                    skip_current_event = False
                    try:
                        parsed = parse_event_header(body)
                    except ValueError as exc:
                        region_text = field(body, 69, 92).strip()
                        lat_text = field(body, 22, 28).strip()
                        lon_text = field(body, 33, 40).strip()
                        if region_text.upper() == "FAR FIELD" and not lat_text and not lon_text:
                            qc["skipped_events"] += 1
                            skip_current_event = True
                            current_pick_count = 0
                            continue
                        raise exc
                    event_id = stable_event_id(source, event_sequence, parsed["origin_time"])
                    current = {
                        "event_id": event_id,
                        "origin_jst": parsed["origin_jst"],
                        "origin_time": parsed["origin_time"],
                        "latitude": parsed["latitude"],
                        "longitude": parsed["longitude"],
                        "depth_km": parsed["depth_km"],
                        "magnitude": parsed["magnitude"],
                        "region": parsed["region"],
                        "npicks": 0,
                        "source_file": source,
                    }
                    current_pick_count = 0
                elif rtype == "_":
                    qc["pick_records"] += 1
                    if skip_current_event:
                        qc["skipped_pick_records"] += 1
                        continue
                    if current is None:
                        qc["orphan_pick_records"] += 1
                        errors.append({"source_file": source, "line_no": line_no, "error": "orphan station pick outside event block"})
                        continue
                    pick = parse_station_pick(body, current["event_id"], current["origin_jst"], source)
                    picks.append(pick)
                    current_pick_count += 1
                elif rtype == "E":
                    qc["e_records"] += 1
                    if skip_current_event:
                        qc["closed_events"] += 1
                        skip_current_event = False
                        current = None
                        current_pick_count = 0
                        continue
                    if current is None:
                        errors.append({"source_file": source, "line_no": line_no, "error": "E terminator without open event"})
                        qc["parse_errors"] += 1
                        continue
                    current["npicks"] = current_pick_count
                    events.append({k: current[k] for k in EVENT_COLUMNS})
                    qc["closed_events"] += 1
                    current = None
                    current_pick_count = 0
                elif rtype in {"j", "W"}:
                    # Documented non-primary/auxiliary JMA-format records can appear
                    # inside JMA event blocks. They are not station P/S arrivals and
                    # are intentionally excluded from the normalized event/pick tables.
                    qc["auxiliary_records"] += 1
                else:
                    qc["unrecognized_records"] += 1
                    errors.append({"source_file": source, "line_no": line_no, "error": f"unrecognized record type {rtype!r}"})
            except Exception as exc:
                qc["parse_errors"] += 1
                errors.append({"source_file": source, "line_no": line_no, "error": safe_message(exc)})
    if current is not None:
        qc["unterminated_events"] += 1
        current["npicks"] = current_pick_count
        events.append({k: current[k] for k in EVENT_COLUMNS})
        errors.append({"source_file": source, "line_no": qc["total_lines"], "error": "file ended before E terminator"})
    if skip_current_event:
        qc["unterminated_events"] += 1
        errors.append({"source_file": source, "line_no": qc["total_lines"], "error": "file ended before E terminator for skipped event"})
    return events, picks, qc, errors


# ----------------------------- validation/export ------------------------------
def dataframe_or_empty(rows: Sequence[Dict[str, Any]], columns: Sequence[str]) -> pd.DataFrame:
    return pd.DataFrame(list(rows), columns=list(columns))


def validate_catalog(events: pd.DataFrame, picks: pd.DataFrame, label: str) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    errors: List[Dict[str, Any]] = []
    summary: Dict[str, Any] = {"label": label, "event_count": int(len(events)), "pick_count": int(len(picks))}
    if list(events.columns) != EVENT_COLUMNS:
        errors.append({"scope": label, "error": "event columns differ from required order"})
    if list(picks.columns) != PICK_COLUMNS:
        errors.append({"scope": label, "error": "pick columns differ from required order"})
    if not events.empty and events["event_id"].duplicated().any():
        errors.append({"scope": label, "error": "duplicate event_id values"})
    event_ids = set(events["event_id"].astype(str)) if "event_id" in events else set()
    pick_ids = set(picks["event_id"].astype(str)) if "event_id" in picks else set()
    missing_fk = sorted(pick_ids - event_ids)
    if missing_fk:
        errors.append({"scope": label, "error": f"{len(missing_fk)} pick event_id values not present in events"})
    if not events.empty:
        counts = picks.groupby("event_id").size() if not picks.empty else pd.Series(dtype=int)
        for _, row in events.iterrows():
            actual = int(counts.get(row["event_id"], 0))
            expected = int(row["npicks"])
            if actual != expected:
                errors.append({"scope": label, "event_id": row["event_id"], "error": f"npicks {expected} != linked picks {actual}"})
                if len(errors) > 100:
                    break
    p_non = int((picks["p_pick_time"].astype(str) != "-1").sum()) if not picks.empty else 0
    s_non = int((picks["s_pick_time"].astype(str) != "-1").sum()) if not picks.empty else 0
    both = int(((picks["p_pick_time"].astype(str) != "-1") & (picks["s_pick_time"].astype(str) != "-1")).sum()) if not picks.empty else 0
    p_only = int(((picks["p_pick_time"].astype(str) != "-1") & (picks["s_pick_time"].astype(str) == "-1")).sum()) if not picks.empty else 0
    s_only = int(((picks["p_pick_time"].astype(str) == "-1") & (picks["s_pick_time"].astype(str) != "-1")).sum()) if not picks.empty else 0
    both_missing = int(((picks["p_pick_time"].astype(str) == "-1") & (picks["s_pick_time"].astype(str) == "-1")).sum()) if not picks.empty else 0
    summary.update({"p_pick_count": p_non, "s_pick_count": s_non, "p_only_rows": p_only, "s_only_rows": s_only, "both_p_s_rows": both, "both_missing_rows": both_missing})
    if both_missing:
        errors.append({"scope": label, "error": f"{both_missing} pick rows have both P and S missing"})
    # Timestamp parseability.
    for col, df in [("origin_time", events), ("p_pick_time", picks), ("s_pick_time", picks)]:
        if df.empty:
            continue
        vals = df[col].astype(str)
        vals = vals[vals != "-1"]
        try:
            pd.to_datetime(vals, utc=True, errors="raise")
        except Exception as exc:
            errors.append({"scope": label, "error": f"non-parseable UTC timestamps in {col}: {safe_message(exc)}"})
    return summary, errors


def apply_regional_subset(events: pd.DataFrame, picks: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    if events.empty:
        return events.copy(), picks.iloc[0:0].copy()
    mask = (
        (events["latitude"] >= SANRIKU["lat_min"]) &
        (events["latitude"] <= SANRIKU["lat_max"]) &
        (events["longitude"] >= SANRIKU["lon_min"]) &
        (events["longitude"] <= SANRIKU["lon_max"])
    )
    reg_events = events.loc[mask].copy()
    reg_ids = set(reg_events["event_id"].astype(str))
    reg_picks = picks[picks["event_id"].astype(str).isin(reg_ids)].copy() if not picks.empty else picks.copy()
    counts = reg_picks.groupby("event_id").size() if not reg_picks.empty else pd.Series(dtype=int)
    if not reg_events.empty:
        reg_events["npicks"] = reg_events["event_id"].map(lambda x: int(counts.get(x, 0)))
    return reg_events[EVENT_COLUMNS], reg_picks[PICK_COLUMNS]


def infer_phase_convention() -> Dict[str, Any]:
    convention = {"delimiter": ",", "event_fields": 6, "pick_fields": 5, "event_line_example": "", "pick_line_example": ""}
    if REFERENCE_PHASE.exists():
        lines = [ln.strip() for ln in REFERENCE_PHASE.read_text(encoding="utf-8", errors="ignore").splitlines() if ln.strip()]
        if lines:
            convention["event_line_example"] = lines[0]
            convention["event_fields"] = len(lines[0].split(","))
        if len(lines) > 1:
            convention["pick_line_example"] = lines[1]
            convention["pick_fields"] = len(lines[1].split(","))
    return convention


def write_phase_dat(events: pd.DataFrame, picks: pd.DataFrame) -> None:
    phase_path = OUTPUT_DIR / "phase.dat"
    trace_rows: List[Dict[str, Any]] = []
    by_event = {eid: grp for eid, grp in picks.groupby("event_id", sort=False)} if not picks.empty else {}
    with phase_path.open("w", encoding="utf-8", newline="") as f:
        for block_idx, ev in enumerate(events.itertuples(index=False), start=1):
            f.write(f"{ev.origin_time},{float(ev.latitude):.6f},{float(ev.longitude):.6f},{float(ev.depth_km):.3f},{float(ev.magnitude):.2f},{int(ev.npicks)}\n")
            trace_rows.append({"block_index": block_idx, "line_type": "event", "event_id": ev.event_id, "source_file": ev.source_file, "station_code": ""})
            grp = by_event.get(ev.event_id)
            if grp is None:
                continue
            for pk in grp.itertuples(index=False):
                f.write(f"{pk.station_code},{pk.p_pick_time},{pk.s_pick_time},0.000e+00,1.00\n")
                trace_rows.append({"block_index": block_idx, "line_type": "pick", "event_id": pk.event_id, "source_file": pk.source_file, "station_code": pk.station_code})
    pd.DataFrame(trace_rows).to_csv(OUTPUT_DIR / "phase_dat_traceability.csv", index=False)


def parse_station_reference() -> pd.DataFrame:
    rows: List[Dict[str, Any]] = []
    if REFERENCE_STATION.exists():
        try:
            df = pd.read_csv(REFERENCE_STATION)
            required_columns = ["station_code", "station_number", "latitude", "longitude", "elevation_m"]
            if set(required_columns).issubset(df.columns):
                out = df[required_columns].copy()
                out["station_number"] = out["station_number"].astype(str)
                return out.drop_duplicates(subset=["station_code", "station_number"])
            log(f"Reference station file lacks required columns and will be skipped: {REFERENCE_STATION}")
        except Exception as exc:
            log(f"Could not read reference station file {REFERENCE_STATION}: {safe_message(exc)}")
    if STATION_TEXT.exists():
        for raw in STATION_TEXT.read_text(encoding="cp932", errors="ignore").splitlines():
            parts = raw.split()
            if len(parts) < 7:
                continue
            if not re.match(r"^[A-Z0-9.]{2,6}$", parts[0]):
                continue
            try:
                code = parts[0]
                number = str(int(parts[1]))
                lat = int(parts[2]) + float(parts[3]) / 60.0
                lon = int(parts[4]) + float(parts[5]) / 60.0
                elev = float(parts[6])
            except (ValueError, IndexError):
                continue
            rows.append({"station_code": code, "station_number": number, "latitude": lat, "longitude": lon, "elevation_m": elev})
    return pd.DataFrame(rows, columns=["station_code", "station_number", "latitude", "longitude", "elevation_m"]).drop_duplicates(subset=["station_code", "station_number"])


def write_station_sta(picks: pd.DataFrame) -> None:
    used = picks[["station_code", "station_number"]].drop_duplicates().copy() if not picks.empty else pd.DataFrame(columns=["station_code", "station_number"])
    used["station_number"] = used["station_number"].astype(str)
    ref = parse_station_reference()
    if ref.empty:
        audit = used.copy()
        audit["latitude"] = pd.NA
        audit["longitude"] = pd.NA
        audit["elevation_m"] = pd.NA
        audit["matched"] = False
    else:
        audit = used.merge(ref, on=["station_code", "station_number"], how="left")
        # Retry by station code only for references that omit or disagree on station number.
        missing = audit["latitude"].isna()
        if missing.any():
            by_code = ref.drop_duplicates("station_code")[["station_code", "latitude", "longitude", "elevation_m"]]
            fill = audit.loc[missing, ["station_code", "station_number"]].merge(by_code, on="station_code", how="left")
            for col in ["latitude", "longitude", "elevation_m"]:
                audit.loc[missing, col] = fill[col].to_numpy()
        audit["matched"] = ~audit["latitude"].isna()
    audit = audit[["station_code", "station_number", "latitude", "longitude", "elevation_m", "matched"]].sort_values(["station_code", "station_number"])
    audit.to_csv(OUTPUT_DIR / "station_metadata_audit.csv", index=False)
    audit[~audit["matched"]].to_csv(OUTPUT_DIR / "station_metadata_missing.csv", index=False)
    audit[audit["matched"]].to_csv(OUTPUT_DIR / "station.sta", index=False)


def parse_files(raw_files: Sequence[Path]) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    all_events: List[Dict[str, Any]] = []
    all_picks: List[Dict[str, Any]] = []
    qc_rows: List[Dict[str, Any]] = []
    err_rows: List[Dict[str, Any]] = []
    for raw in raw_files:
        log(f"Parsing fixed-width JMA measure file {raw}")
        ev, pk, qc, errs = parse_measure_file(raw)
        all_events.extend(ev)
        all_picks.extend(pk)
        qc_rows.append(qc)
        err_rows.extend(errs)
    events = dataframe_or_empty(all_events, EVENT_COLUMNS).sort_values(["source_file", "origin_time", "event_id"], kind="stable").reset_index(drop=True)
    picks = dataframe_or_empty(all_picks, PICK_COLUMNS).sort_values(["source_file", "event_id", "station_code"], kind="stable").reset_index(drop=True)
    qc_df = pd.DataFrame(qc_rows)
    err_df = pd.DataFrame(err_rows, columns=["source_file", "line_no", "error"])
    return events[EVENT_COLUMNS], picks[PICK_COLUMNS], qc_df, err_df


def fatal_if_parser_errors(qc: pd.DataFrame, errors: pd.DataFrame, scope: str) -> None:
    fatal_cols = ["invalid_length_records", "unrecognized_records", "orphan_pick_records", "unterminated_events", "parse_errors"]
    totals = {col: int(qc[col].sum()) if col in qc else 0 for col in fatal_cols}
    if any(v > 0 for v in totals.values()):
        errors.to_csv(OUTPUT_DIR / f"{scope}_parser_errors.csv", index=False)
        raise RuntimeError(f"Fatal fixed-width parser errors in {scope}: {totals}. See {scope}_parser_errors.csv")


def validate_smoke(chunk: Chunk, manifest_row: Dict[str, Any]) -> None:
    if manifest_row["status"] not in {"downloaded", "skipped_existing", "reused_existing_source"} or int(manifest_row["size_bytes"]) <= 0:
        raise RuntimeError(f"Smoke-test raw download/reuse failed: {manifest_row['status']} {manifest_row['message']}")
    events, picks, qc, parse_errors = parse_files([chunk.raw_file])
    qc.to_csv(OUTPUT_DIR / "smoke_parse_qc_by_file.csv", index=False)
    parse_errors.to_csv(OUTPUT_DIR / "smoke_parse_errors.csv", index=False)
    events.to_csv(OUTPUT_DIR / "events_smoke.csv", index=False)
    picks.to_csv(OUTPUT_DIR / "picks_smoke.csv", index=False)
    fatal_if_parser_errors(qc, parse_errors, "smoke")
    summary, val_errors = validate_catalog(events, picks, "smoke")
    summary.update({"raw_file": str(chunk.raw_file), "raw_size_bytes": int(chunk.raw_file.stat().st_size)})
    if int(qc["valid_96_byte_records"].sum()) == 0:
        val_errors.append({"scope": "smoke", "error": "no valid 96-byte records in smoke raw file"})
    if len(events) == 0:
        val_errors.append({"scope": "smoke", "error": "no events parsed from non-empty smoke raw file"})
    pd.DataFrame(val_errors).to_csv(OUTPUT_DIR / "smoke_validation_errors.csv", index=False)
    summary["passed"] = len(val_errors) == 0
    write_json(OUTPUT_DIR / "smoke_qc_summary.json", summary)
    if val_errors:
        raise RuntimeError("Smoke-test validation failed; see smoke_validation_errors.csv and smoke_qc_summary.json")
    log("Smoke test passed.")


def write_product_inventory() -> None:
    rows = []
    for path in sorted(OUTPUT_DIR.iterdir()):
        if path.is_file():
            rows.append({"file": str(path), "size_bytes": path.stat().st_size, "modified_utc": iso_utc(datetime.fromtimestamp(path.stat().st_mtime, tz=UTC))})
    pd.DataFrame(rows).to_csv(OUTPUT_DIR / "product_inventory.csv", index=False)


def main() -> None:
    ensure_output_dir()
    cleanup_stale_derived_outputs()
    log(f"Output directory: {OUTPUT_DIR}")
    chunks = build_chunks()
    write_chunk_schedule(chunks)
    existing_raw_files = discover_existing_raw_files()
    if existing_raw_files:
        log(f"Reusing {len(existing_raw_files)} existing raw file(s) from {EXISTING_RAW_DIR}; network download skipped.")
        manifest_rows = existing_raw_manifest(existing_raw_files)
        write_manifest(manifest_rows)
        smoke_path = existing_raw_files[0]
        smoke_match = re.match(r"^measure_(\d{8})_(\d+)\.txt$", smoke_path.name)
        if not smoke_match:
            raise RuntimeError(f"cannot infer smoke-test span from {smoke_path.name}")
        smoke_start = datetime.strptime(smoke_path.name.split("_")[1], "%Y%m%d").date()
        smoke_span = int(smoke_match.group(2))
        smoke_chunk = Chunk(1, smoke_start, smoke_start + timedelta(days=smoke_span), smoke_span, smoke_path)
        validate_smoke(smoke_chunk, manifest_rows[0])
    else:
        accounts = load_accounts()
        secrets = [a.username for a in accounts] + [a.password for a in accounts]
        hinet_client_cls = import_hinet_client()
        manifest_rows = []
        smoke_chunk = chunks[0]
        smoke_row = download_chunk(smoke_chunk, accounts, hinet_client_cls, secrets)
        manifest_rows.append(smoke_row)
        write_manifest(manifest_rows)
        validate_smoke(smoke_chunk, smoke_row)

        for chunk in chunks[1:]:
            row = download_chunk(chunk, accounts, hinet_client_cls, secrets)
            manifest_rows.append(row)
            write_manifest(manifest_rows)

        write_manifest(manifest_rows)

    manifest = pd.DataFrame(manifest_rows, columns=MANIFEST_COLUMNS)
    if (manifest["span_days"].astype(int) > MAX_SPAN_DAYS).any():
        raise RuntimeError("download manifest contains chunk span > 7 days")

    accepted = manifest[manifest["status"].isin(["downloaded", "skipped_existing", "reused_existing_source"]) & (manifest["size_bytes"].astype(int) > 0)].copy()
    failed = manifest[~manifest.index.isin(accepted.index)]
    if not failed.empty:
        failed.to_csv(OUTPUT_DIR / "failed_download_chunks.csv", index=False)
        raise RuntimeError(f"{len(failed)} chunks failed or were empty; see failed_download_chunks.csv")

    raw_files = [Path(p) for p in accepted["raw_file"].tolist()]
    events_full, picks_full, parse_qc, parse_errors = parse_files(raw_files)
    parse_qc.to_csv(OUTPUT_DIR / "parse_qc_by_file.csv", index=False)
    parse_errors.to_csv(OUTPUT_DIR / "parse_errors.csv", index=False)
    fatal_if_parser_errors(parse_qc, parse_errors, "full")

    full_summary, full_errors = validate_catalog(events_full, picks_full, "full")
    events_regional, picks_regional = apply_regional_subset(events_full, picks_full)
    regional_summary, regional_errors = validate_catalog(events_regional, picks_regional, "regional")
    if not events_regional.empty:
        outside = events_regional[
            ~((events_regional["latitude"] >= SANRIKU["lat_min"]) & (events_regional["latitude"] <= SANRIKU["lat_max"]) &
              (events_regional["longitude"] >= SANRIKU["lon_min"]) & (events_regional["longitude"] <= SANRIKU["lon_max"]))
        ]
        if not outside.empty:
            regional_errors.append({"scope": "regional", "error": "regional events outside Sanriku bounds"})

    events_full.to_csv(OUTPUT_DIR / "events_full.csv", index=False)
    picks_full.to_csv(OUTPUT_DIR / "picks_full.csv", index=False)
    events_regional.to_csv(OUTPUT_DIR / "events_regional.csv", index=False)
    picks_regional.to_csv(OUTPUT_DIR / "picks_regional.csv", index=False)
    # User-facing aliases for the primary Sanriku structured products.
    events_regional.to_csv(OUTPUT_DIR / "events.csv", index=False)
    picks_regional.to_csv(OUTPUT_DIR / "picks.csv", index=False)

    convention = infer_phase_convention()
    write_json(OUTPUT_DIR / "phase_dat_convention.json", convention)
    write_phase_dat(events_regional, picks_regional)
    write_station_sta(picks_regional)

    final_errors = full_errors + regional_errors
    if not existing_raw_files:
        if len(manifest) != len(chunks):
            final_errors.append({"scope": "manifest", "error": f"download_manifest.csv has {len(manifest)} rows, expected {len(chunks)} scheduled chunks"})
        if manifest.iloc[0]["start_date"] != START_DATE.isoformat() or int(manifest.iloc[0]["span_days"]) != 5:
            final_errors.append({"scope": "manifest", "error": "first manifest row is not the required 2025-06-01 five-day smoke chunk"})
        if manifest.iloc[-1]["start_date"] != date(2026, 4, 27).isoformat() or int(manifest.iloc[-1]["span_days"]) != 5:
            final_errors.append({"scope": "manifest", "error": "last manifest row is not the required 2026-04-27 five-day chunk"})
    pd.DataFrame(final_errors).to_csv(OUTPUT_DIR / "final_validation_errors.csv", index=False)

    catalog_summary = {
        "request_start_date": START_DATE.isoformat(),
        "request_end_date_exclusive": END_DATE_EXCLUSIVE.isoformat(),
        "chunk_count": len(chunks),
        "downloaded_or_reused_chunks": int(len(accepted)),
        "full": full_summary,
        "regional": regional_summary,
        "sanriku_bounds": SANRIKU,
        "phase_dat_convention": convention,
        "parse_qc_totals": {col: int(parse_qc[col].sum()) for col in parse_qc.columns if col != "source_file"},
    }
    write_json(OUTPUT_DIR / "catalog_qc_summary.json", catalog_summary)
    final_summary = dict(catalog_summary)
    final_summary["passed"] = len(final_errors) == 0
    final_summary["validation_error_count"] = len(final_errors)
    write_json(OUTPUT_DIR / "final_validation_summary.json", final_summary)
    write_product_inventory()
    if final_errors:
        raise RuntimeError("Final validation failed; see final_validation_errors.csv")
    log("Workflow completed successfully.")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        # Required: surface traceback exactly once in main execution log.
        print(traceback.format_exc(), file=sys.stderr, flush=True)
        sys.exit(1)
