const state = {
  summary: null,
  migration: [],
  governance: [],
  validation: [],
  roadmap: [],
};

const surfaceCopy = {
  migration: {
    eyebrow: "Surface 1",
    title: "Migration Portfolio",
    deck: "Prioritize Tableau assets by business criticality, stakeholder exposure, metric complexity, validation risk, and cutover readiness.",
  },
  governance: {
    eyebrow: "Surface 2",
    title: "LookML Governance",
    deck: "Review semantic-model risk before migration work ships, including join pattern, PDT strategy, datagroup, cache policy, Liquid parameters, and Git review state.",
  },
  rollout: {
    eyebrow: "Surface 3",
    title: "Validation And Rollout",
    deck: "Track metric parity, dashboard performance, enablement, open incidents, and roadmap sequencing before retiring duplicate Tableau content.",
  },
};

function parseCsv(text) {
  const rows = [];
  let row = [];
  let field = "";
  let quoted = false;

  for (let i = 0; i < text.length; i += 1) {
    const char = text[i];
    const next = text[i + 1];

    if (char === '"' && quoted && next === '"') {
      field += '"';
      i += 1;
    } else if (char === '"') {
      quoted = !quoted;
    } else if (char === "," && !quoted) {
      row.push(field);
      field = "";
    } else if ((char === "\n" || char === "\r") && !quoted) {
      if (field || row.length) {
        row.push(field);
        rows.push(row);
        row = [];
        field = "";
      }
      if (char === "\r" && next === "\n") i += 1;
    } else {
      field += char;
    }
  }

  if (field || row.length) {
    row.push(field);
    rows.push(row);
  }

  const [headers, ...records] = rows;
  return records.map((record) =>
    headers.reduce((memo, header, index) => {
      memo[header] = record[index] ?? "";
      return memo;
    }, {})
  );
}

async function loadCsv(path) {
  const response = await fetch(path);
  return parseCsv(await response.text());
}

async function init() {
  const [summary, migration, governance, validation, roadmap] = await Promise.all([
    fetch("analysis/outputs/summary.json").then((response) => response.json()),
    loadCsv("analysis/outputs/migration_priority_queue.csv"),
    loadCsv("analysis/outputs/lookml_governance_queue.csv"),
    loadCsv("analysis/outputs/validation_rollout_queue.csv"),
    loadCsv("data/roadmap_backlog.csv"),
  ]);

  Object.assign(state, { summary, migration, governance, validation, roadmap });
  bindNavigation();
  renderSurface(activeSurface());
}

function bindNavigation() {
  document.querySelectorAll("[data-surface]").forEach((button) => {
    button.addEventListener("click", () => {
      window.location.hash = button.dataset.surface;
      renderSurface(button.dataset.surface);
    });
  });
  window.addEventListener("hashchange", () => renderSurface(activeSurface()));
}

function activeSurface() {
  const surface = window.location.hash.replace("#", "");
  return surfaceCopy[surface] ? surface : "migration";
}

function renderSurface(surface) {
  document.querySelectorAll("[data-surface]").forEach((button) => {
    button.classList.toggle("is-active", button.dataset.surface === surface);
  });

  const copy = surfaceCopy[surface];
  document.querySelector("#surfaceEyebrow").textContent = copy.eyebrow;
  document.querySelector("#surfaceTitle").textContent = copy.title;
  document.querySelector("#surfaceDeck").textContent = copy.deck;

  if (surface === "migration") renderMigration();
  if (surface === "governance") renderGovernance();
  if (surface === "rollout") renderRollout();
}

function renderMigration() {
  const topRows = state.migration.slice(0, 8);
  const ready = Number(state.summary.ready_for_cutover);
  const blockers = Number(state.summary.blocker_remediation);
  const avgParity = state.summary.avg_parity_pass_rate;

  document.querySelector("#metrics").innerHTML = metricCards([
    ["Workbook portfolio", state.summary.workbooks, "Tableau assets"],
    ["KPI mappings", state.summary.metrics, "to LookML"],
    ["Parity pass rate", `${avgParity}%`, "current"],
    ["Cutover blockers", blockers, "need remediation"],
  ]);

  document.querySelector("#content").innerHTML = `
    <section class="surface-grid migration-grid">
      <article class="panel wide">
        <div class="panel-heading">
          <p class="eyebrow">Ranked queue</p>
          <h2>Tableau To Looker Migration Priority</h2>
        </div>
        ${table(topRows, [
          ["workbook_name", "Workbook"],
          ["criticality", "Tier"],
          ["priority_score", "Priority"],
          ["readiness_score", "Ready"],
          ["parity_pass_rate", "Parity"],
          ["cutover_lane", "Lane"],
        ], {
          priority_score: (value) => Number(value).toFixed(1),
          readiness_score: (value) => Number(value).toFixed(1),
          parity_pass_rate: (value) => `${Number(value).toFixed(1)}%`,
        })}
      </article>
      <article class="panel">
        <p class="eyebrow">Operating decision</p>
        <h2>${topRows[0].workbook_id}</h2>
        <dl class="decision-list">
          <div><dt>Next action</dt><dd>${topRows[0].next_action}</dd></div>
          <div><dt>Domain</dt><dd>${topRows[0].domain}</dd></div>
          <div><dt>Monthly views</dt><dd>${formatNumber(topRows[0].monthly_views)}</dd></div>
          <div><dt>Expected load improvement</dt><dd>${topRows[0].load_improvement_pct}%</dd></div>
        </dl>
      </article>
      <article class="panel lane-panel">
        <p class="eyebrow">Cutover lanes</p>
        <h2>Release Readiness</h2>
        ${laneBar([
          ["Ready", ready, "#237a57"],
          ["Owner validation", state.migration.length - ready - blockers, "#9b6b00"],
          ["Blockers", blockers, "#b42318"],
        ])}
      </article>
    </section>
  `;
}

function renderGovernance() {
  const risky = state.governance.slice(0, 7);
  const pdtCount = state.governance.filter((row) => row.pdt_strategy !== "None").length;
  const openComments = state.governance.reduce((sum, row) => sum + Number(row.open_review_comments), 0);
  const fanoutRisk = state.governance.filter((row) => row.join_pattern !== "many_to_one").length;

  document.querySelector("#metrics").innerHTML = metricCards([
    ["Explores reviewed", state.governance.length, "semantic layer"],
    ["PDT candidates", pdtCount, "performance"],
    ["Join reviews", fanoutRisk, "fanout risk"],
    ["Open Git comments", openComments, "review queue"],
  ]);

  document.querySelector("#content").innerHTML = `
    <section class="surface-grid governance-grid">
      <article class="panel wide">
        <div class="panel-heading">
          <p class="eyebrow">Semantic risk</p>
          <h2>LookML Review Queue</h2>
        </div>
        ${table(risky, [
          ["explore_name", "Explore"],
          ["join_pattern", "Join pattern"],
          ["pdt_strategy", "PDT"],
          ["datagroup", "Datagroup"],
          ["cache_policy", "Cache"],
          ["semantic_risk_score", "Risk"],
        ], {
          semantic_risk_score: (value) => Number(value).toFixed(1),
        })}
      </article>
      <article class="panel code-panel">
        <p class="eyebrow">Reference LookML</p>
        <h2>Governed Explore Pattern</h2>
        <pre><code>explore: commerce_performance {
  persist_with: commerce_hourly
  always_filter: {
    filters: [client_id: "-NULL"]
  }
  join: campaigns {
    type: left_outer
    relationship: many_to_one
    sql_on: \${commerce_performance.campaign_id} =
      \${campaigns.campaign_id} ;;
  }
}</code></pre>
      </article>
      <article class="panel">
        <p class="eyebrow">Release gate</p>
        <h2>${risky[0].explore_name}</h2>
        <dl class="decision-list">
          <div><dt>Primary view</dt><dd>${risky[0].primary_view}</dd></div>
          <div><dt>Liquid parameter</dt><dd>${risky[0].liquid_parameter}</dd></div>
          <div><dt>Git status</dt><dd>${risky[0].git_review_status}</dd></div>
          <div><dt>Style findings</dt><dd>${risky[0].style_guide_findings}</dd></div>
        </dl>
      </article>
    </section>
  `;
}

function renderRollout() {
  const validationRows = state.validation.slice(0, 8);
  const failCount = state.validation.reduce((sum, row) => sum + Number(row.failed_tests), 0);
  const incidentCount = state.validation.reduce((sum, row) => sum + Number(row.open_incidents), 0);
  const completeTraining = state.validation.filter((row) => row.training_status === "Complete").length;
  const roadmapReady = state.roadmap.filter((row) => row.status === "Ready").length;

  document.querySelector("#metrics").innerHTML = metricCards([
    ["Validation tests", state.summary.validation_tests, "evidence rows"],
    ["Failed tests", failCount, "before cutover"],
    ["Training complete", completeTraining, "workbooks"],
    ["Ready stories", roadmapReady, "roadmap backlog"],
  ]);

  document.querySelector("#content").innerHTML = `
    <section class="surface-grid rollout-grid">
      <article class="panel wide">
        <div class="panel-heading">
          <p class="eyebrow">Quality evidence</p>
          <h2>Validation And Rollout Queue</h2>
        </div>
        ${table(validationRows, [
          ["workbook_name", "Workbook"],
          ["failed_tests", "Fails"],
          ["tolerance_reviews", "Reviews"],
          ["parity_pass_rate", "Parity"],
          ["load_improvement_pct", "Load delta"],
          ["cutover_readiness", "Cutover"],
        ], {
          parity_pass_rate: (value) => `${Number(value).toFixed(1)}%`,
          load_improvement_pct: (value) => `${Number(value).toFixed(1)}%`,
        })}
      </article>
      <article class="panel">
        <p class="eyebrow">Roadmap mix</p>
        <h2>Product Backlog</h2>
        ${roadmapList()}
      </article>
      <article class="panel">
        <p class="eyebrow">Migration closeout</p>
        <h2>${validationRows[0].workbook_id}</h2>
        <dl class="decision-list">
          <div><dt>Tableau baseline</dt><dd>${validationRows[0].avg_tableau_load_seconds}s</dd></div>
          <div><dt>Looker target</dt><dd>${validationRows[0].avg_looker_load_seconds}s</dd></div>
          <div><dt>Cache hit rate</dt><dd>${validationRows[0].avg_cache_hit_rate_pct}%</dd></div>
          <div><dt>Adoption</dt><dd>${validationRows[0].adoption_status}</dd></div>
        </dl>
      </article>
    </section>
  `;
}

function metricCards(items) {
  return items.map(([label, value, meta]) => `
    <article>
      <span>${label}</span>
      <strong>${formatNumber(value)}</strong>
      <em>${meta}</em>
    </article>
  `).join("");
}

function table(rows, columns, formatters = {}) {
  return `
    <div class="table-wrap">
      <table>
        <thead>
          <tr>${columns.map(([, label]) => `<th>${label}</th>`).join("")}</tr>
        </thead>
        <tbody>
          ${rows.map((row) => `
            <tr>
              ${columns.map(([key]) => `<td>${formatCell(row[key], formatters[key])}</td>`).join("")}
            </tr>
          `).join("")}
        </tbody>
      </table>
    </div>
  `;
}

function formatCell(value, formatter) {
  if (formatter) return formatter(value);
  if (String(value).length > 30) return `<span class="truncate">${value}</span>`;
  return value;
}

function laneBar(items) {
  const total = items.reduce((sum, [, value]) => sum + Number(value), 0);
  return `
    <div class="lane-stack">
      ${items.map(([label, value, color]) => `
        <div>
          <span>${label}</span>
          <strong>${value}</strong>
          <i style="--w:${(Number(value) / total) * 100}%;--c:${color}"></i>
        </div>
      `).join("")}
    </div>
  `;
}

function roadmapList() {
  const counts = state.roadmap.reduce((memo, row) => {
    memo[row.epic] = (memo[row.epic] || 0) + 1;
    return memo;
  }, {});

  return `
    <ul class="roadmap-list">
      ${Object.entries(counts)
        .sort((a, b) => b[1] - a[1])
        .map(([epic, count]) => `<li><span>${epic}</span><strong>${count}</strong></li>`)
        .join("")}
    </ul>
  `;
}

function formatNumber(value) {
  const numeric = Number(value);
  if (!Number.isFinite(numeric)) return value;
  return new Intl.NumberFormat("en-US").format(numeric);
}

init().catch((error) => {
  document.querySelector("#content").innerHTML = `<section class="panel"><h2>Data load failed</h2><p>${error.message}</p></section>`;
});
