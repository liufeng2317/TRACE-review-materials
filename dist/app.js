const tabButtons = document.querySelectorAll(".nav-tab, .tab-button");
const tabTriggers = document.querySelectorAll("[data-tab-target]");
const tabPanels = document.querySelectorAll(".tab-panel");
const tabAliases = {
  agent: "overview",
  cases: "ridgecrest",
  meaning: "evidence"
};

const setActiveTab = (target, { scroll = true, updateHash = true } = {}) => {
  const resolvedTarget = tabAliases[target] || target;
  const panel = document.querySelector(`[data-panel="${resolvedTarget}"]`);
  if (!panel) return;

  tabButtons.forEach((button) => {
    const active = button.dataset.tabTarget === resolvedTarget;
    button.classList.toggle("is-active", active);
    button.setAttribute("aria-selected", active ? "true" : "false");
  });

  tabPanels.forEach((item) => {
    const active = item === panel;
    item.classList.toggle("is-active", active);
    item.hidden = !active;
  });

  if (updateHash) {
    window.history.replaceState(null, "", `#${resolvedTarget}`);
  }

  if (scroll) {
    document.querySelector("#explore").scrollIntoView({ behavior: "smooth", block: "start" });
  }
};

tabTriggers.forEach((trigger) => {
  trigger.addEventListener("click", (event) => {
    const target = trigger.dataset.tabTarget;
    if (trigger.tagName === "A") event.preventDefault();
    setActiveTab(target);
  });
});

document.querySelectorAll('[role="tablist"]').forEach((tablist) => {
  const controls = [...tablist.querySelectorAll('[role="tab"]')];
  controls.forEach((control, index) => {
    control.addEventListener("keydown", (event) => {
      if (!["ArrowLeft", "ArrowRight", "Home", "End"].includes(event.key)) return;
      event.preventDefault();
      const nextIndex = event.key === "Home"
        ? 0
        : event.key === "End"
          ? controls.length - 1
          : (index + (event.key === "ArrowRight" ? 1 : -1) + controls.length) % controls.length;
      controls[nextIndex].focus();
      setActiveTab(controls[nextIndex].dataset.tabTarget);
    });
  });
});

const initialTab = window.location.hash.slice(1);
if (initialTab && (document.querySelector(`[data-panel="${tabAliases[initialTab] || initialTab}"]`))) {
  setActiveTab(initialTab, { scroll: false, updateHash: false });
} else {
  tabPanels.forEach((panel, index) => {
    panel.hidden = index !== 0;
  });
}

const formatScore = (value) => Number(value).toFixed(2);
const formatPercent = (value) => `${(Number(value) * 100).toFixed(1)}%`;

const renderModels = (models) => {
  const rows = document.querySelector("#model-rows");
  rows.innerHTML = models.map((model) => `
    <tr>
      <td>${model.name}</td>
      <td>${formatScore(model.mean_score)}</td>
      <td>${formatPercent(model.success_rate)}</td>
      <td>${Number(model.debug_rounds).toFixed(2)}</td>
    </tr>
  `).join("");
};

const renderSkills = (skills) => {
  const container = document.querySelector("#skill-bars");
  const max = Math.max(...skills.map((skill) => skill.tasks));
  container.innerHTML = skills.map((skill) => `
    <div class="skill-row">
      <span>${skill.name}</span>
      <span class="skill-track"><span style="width: ${(skill.tasks / max) * 100}%"></span></span>
      <span class="skill-count">${skill.tasks}</span>
    </div>
  `).join("");
};

const updateLevel = (data, levelKey) => {
  const level = data.levels[levelKey];
  document.querySelector("#level-name").textContent = levelKey === "L1" ? "Level 1" : "Level 2";
  document.querySelector("#level-score").textContent = formatScore(level.mean_score);
  document.querySelector("#level-description").textContent = level.description;
  document.querySelector("#level-tasks").textContent = level.tasks;
  document.querySelector("#level-pass").textContent = level.pass;
  document.querySelector("#level-success").textContent = formatPercent(level.mean_success_rate);
  document.querySelectorAll(".segment").forEach((button) => {
    const active = button.dataset.level === levelKey;
    button.classList.toggle("is-active", active);
    button.setAttribute("aria-selected", active ? "true" : "false");
  });
};

const loadBenchmark = async () => {
  const response = await fetch("data/benchmark-summary.json");
  const data = await response.json();
  document.querySelector("#mean-score").textContent = formatScore(data.summary.mean_task_score);
  document.querySelector("#passed-runs").textContent = data.summary.passed_runs;
  document.querySelector("#manual-score").textContent = formatScore(data.summary.mean_manual_reference_score);
  renderModels(data.models);
  renderSkills(data.skills);
  updateLevel(data, "L1");
  document.querySelectorAll(".segment").forEach((button) => {
    button.addEventListener("click", () => updateLevel(data, button.dataset.level));
  });
};

loadBenchmark().catch((error) => {
  document.querySelector("#model-rows").innerHTML = `
    <tr><td colspan="4">Benchmark summary unavailable in this preview.</td></tr>
  `;
  console.error(error);
});
