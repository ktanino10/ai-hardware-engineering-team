/*
 * dashboard-render.js — takes the parsed state from dashboard-live.js and
 * renders every section into the DOM. Owns the loading state, the Refresh
 * button, and re-rendering when the EN/JA language toggle fires.
 *
 * Every render function checks its own section's `ok` flag first and
 * falls back to a "couldn't parse — see the file directly" box instead of
 * assuming a shape that might not hold.
 *
 * UI chrome text (headings, buttons, my own template sentences/labels) is
 * looked up via window.dashboardI18n.t(key, ...) so it can be toggled
 * EN/JA (see dashboard-i18n.js's own top comment for the exact EN/JA
 * split and why). Everything actually fetched/parsed from this
 * repository's own files — decision text, finding titles, ECO text,
 * status lines, phase names — plus this project's own defined severity/
 * status/priority vocabulary, IDs, and file paths are printed exactly as
 * extracted, in English, regardless of UI language.
 */

// Last successfully loaded data, cached so a language toggle can re-render
// every section from memory — it must never trigger a new network fetch.
let lastData = null;

function statBox(v, l) {
  return `<div class="stat"><div class="v">${v}</div><div class="l">${l}</div></div>`;
}
function gateCond(pass, text) {
  return `<div class="cond ${pass ? 'ok' : 'bad'}">${pass ? '✓' : '✗'} ${text}</div>`;
}
function errBox(labelKey, path) {
  const { t } = window.dashboardI18n;
  return `<div class="err-box">${t('err_message', t(labelKey), path)}</div>`;
}

function renderPending(data) {
  const { escapeHtml } = window.dashboardUtils;
  const { t } = window.dashboardI18n;
  const el = document.getElementById('pending-body');
  const sectionEl = document.getElementById('section-pending');

  let componentHtml = '', findingHtml = '', softHtml = '';
  let hardBlockerCount = 0;

  if (data.componentSelection.ok) {
    data.componentSelection.pending.forEach(p => {
      hardBlockerCount++;
      componentHtml += `<div class="decision-row">
        <div class="decision-tag component">${escapeHtml(t('tag_component'))}</div>
        <div class="decision-main"><div class="t">${escapeHtml(p.section)}</div><div class="d">${escapeHtml(p.decision)}</div></div>
      </div>`;
    });
  } else {
    componentHtml = errBox('err_label_component', 'bom/component-selection.md');
  }

  if (data.openIssues.ok) {
    data.openIssues.openCriticalHigh.forEach(f => {
      hardBlockerCount++;
      const tagClass = f.severity === 'CRITICAL' ? 'finding-critical' : 'finding-high';
      findingHtml += `<div class="decision-row">
        <div class="decision-tag ${tagClass}">${escapeHtml(f.severity)}</div>
        <div class="decision-main"><div class="t">${escapeHtml(f.id)}</div><div class="d">${escapeHtml(f.title)}</div></div>
      </div>`;
    });
  } else {
    findingHtml = errBox('err_label_findings_open', 'validation/open-issues.md');
  }

  if (data.requirements.ok) {
    data.requirements.possiblyOpenQuestions.forEach(q => {
      softHtml += `<div class="decision-row">
        <div class="decision-tag soft">${escapeHtml(t('tag_soft'))}</div>
        <div class="decision-main"><div class="t">${escapeHtml(q)}</div>
          <div class="d">${escapeHtml(t('soft_explain'))}</div>
        </div>
      </div>`;
    });
  }

  let html = '';
  const bothParsedOk = data.componentSelection.ok && data.openIssues.ok;
  if (bothParsedOk && hardBlockerCount === 0) {
    html += `<div class="all-clear">${escapeHtml(t('all_clear_title'))}
      <div class="d">${escapeHtml(t('all_clear_detail', 0, 0))}</div></div>`;
    sectionEl.classList.add('clear');
  } else {
    sectionEl.classList.remove('clear');
  }
  html += componentHtml + findingHtml + softHtml;
  if (data.componentSelection.ok) {
    html += `<div style="margin-top:10px;font-size:11px;color:var(--dim)">${escapeHtml(t('approved_summary', data.componentSelection.approvedCount, data.componentSelection.totalDecisions))}</div>`;
  }
  el.innerHTML = html || '<span class="placeholder">No data.</span>';
}

function renderPhases(data) {
  const { escapeHtml, truncate } = window.dashboardUtils;
  const { t } = window.dashboardI18n;
  const el = document.getElementById('phases-body');

  if (!data.phases.ok) {
    el.innerHTML = errBox('err_label_phase_pipeline', 'docs/workflow.md');
    return;
  }

  const pendingCount = data.componentSelection.ok ? data.componentSelection.pending.length : null;
  const latestMilestone = (data.changeLog.ok && data.changeLog.milestones.length) ? data.changeLog.milestones[0] : null;

  const chips = data.phases.phases.map(p => {
    let badge = '';
    if (/component selection/i.test(p.name) && pendingCount !== null) {
      badge = pendingCount > 0
        ? `<div class="badge">${escapeHtml(t('badge_pending', pendingCount))}</div>`
        : `<div class="badge" style="background:rgba(62,224,138,.15);color:var(--good)">${escapeHtml(t('badge_clear'))}</div>`;
    }
    if (/design complete gate/i.test(p.name) && latestMilestone) {
      // The milestone TEXT itself is live data quoted from change-log.md — kept in English regardless of UI language.
      badge = `<div class="badge" title="${escapeHtml(latestMilestone.id + ' · ' + latestMilestone.date)}">${escapeHtml(truncate(latestMilestone.text, 42))}</div>`;
    }
    // p.name is a phase name extracted live from docs/workflow.md — also kept in English, same rule as the milestone text above.
    return `<div class="phase-chip"><div class="n">${escapeHtml(t('phase_label', p.num))}</div><div class="name">${escapeHtml(p.name)}</div>${badge}</div>`;
  }).join('');

  let statusLines = '';
  if (data.requirements.ok && data.requirements.statusLines.length) {
    statusLines += `<div class="status-line"><span class="doc">requirements/requirements.md</span><br><b>${data.requirements.statusLines.map(escapeHtml).join('</b> &middot; <b>')}</b></div>`;
  }
  if (data.mechanicalInterface.ok && data.mechanicalInterface.statusLine) {
    statusLines += `<div class="status-line"><span class="doc">hardware/mechanical-interface.md</span><br><b>${escapeHtml(data.mechanicalInterface.statusLine)}</b></div>`;
  }

  el.innerHTML = `<div class="phase-row">${chips}</div>` +
    (statusLines ? `<div class="status-lines">${statusLines}</div>` : '') +
    `<div class="placeholder" style="margin-top:12px;font-size:11px">${escapeHtml(t('phase_footnote'))}</div>`;
}

function renderFindings(data) {
  const el = document.getElementById('findings-body');
  const { t } = window.dashboardI18n;
  let html = '';

  if (data.openIssues.ok) {
    // Severity/Status values below (CRITICAL/HIGH/MEDIUM/LOW,
    // OPEN/RESOLVED/ACCEPTED-RISK) are this project's own defined
    // governance vocabulary (docs/architecture.md §7.1/§8) — kept
    // literally in English in both UI languages on purpose.
    const SEVS = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'];
    const STATS = ['OPEN', 'RESOLVED', 'ACCEPTED-RISK'];
    const rows = SEVS.map(s => {
      const tally = data.openIssues.tally[s];
      const cells = STATS.map(st => `<td class="${tally[st] === 0 ? 'zero' : ''}">${tally[st]}</td>`).join('');
      return `<tr><td class="rowhead sev-${s}">${s}</td>${cells}</tr>`;
    }).join('');
    html += `<table class="mini"><thead><tr><th></th>${STATS.map(s => `<th>${s}</th>`).join('')}</tr></thead><tbody>${rows}</tbody></table>`;
  } else {
    html += errBox('err_label_findings_backlog', 'validation/open-issues.md');
  }

  html += '<div class="stat-row">';
  if (data.changeLog.ok) html += statBox(data.changeLog.total, t('stat_ecos'));
  if (data.openIssues.ok) html += statBox(data.openIssues.totalRows, t('stat_findings'));
  if (data.evidenceLog.ok) html += statBox(data.evidenceLog.count, t('stat_evidence'));
  html += '</div>';

  html += `<div class="gate-check">
    <div style="font-size:11px;color:var(--dim);margin-bottom:4px">${t('gate_check_intro_1')}<a href="https://github.com/ktanino10/ai-hardware-engineering-team/blob/main/docs/architecture.md" target="_blank" rel="noopener">docs/architecture.md §8 ↗</a>${t('gate_check_intro_2')}</div>`;
  if (data.openIssues.ok) {
    const critOpen = data.openIssues.tally.CRITICAL.OPEN;
    const highOpen = data.openIssues.tally.HIGH.OPEN;
    html += gateCond(critOpen === 0, t('gate_cond_critical', critOpen));
    html += gateCond(highOpen === 0, t('gate_cond_high', highOpen));
  }
  if (data.traceability.ok) {
    const tr = data.traceability.counts;
    const notDone = tr.Pending + tr.Failed + tr.Other;
    html += gateCond(notDone === 0, t('gate_cond_trace', tr.Verified + tr.Waived, data.traceability.total, tr.Pending));
  }
  html += `<div class="cond na">— ${t('gate_na')} <a href="https://github.com/ktanino10/ai-hardware-engineering-team/blob/main/validation/fmea.md" target="_blank" rel="noopener">validation/fmea.md ↗</a></div>`;
  html += '</div>';

  el.innerHTML = html;
}

function renderRequirements(data) {
  const { escapeHtml } = window.dashboardUtils;
  const { t } = window.dashboardI18n;
  const el = document.getElementById('requirements-body');

  if (!data.requirements.ok) {
    el.innerHTML = errBox('err_label_req_priorities', 'requirements/requirements.md');
    return;
  }

  const c = data.requirements.counts;
  const total = data.requirements.totalReq || 1;
  // Bucket labels (Must/Should/Could/Won't) are this project's own
  // Priority vocabulary from requirements.md's own column — kept
  // literally in English, same rule as Severity/Status above.
  const order = ['Must', 'Should', 'Could', "Won't", 'Other'];
  const bars = order.filter(k => c[k] > 0).map(k => {
    const pct = Math.round((c[k] / total) * 100);
    return `<div class="bar-row"><div class="label">${escapeHtml(k)}</div><div class="bar-bg"><div class="bar-fg" style="width:${pct}%"></div></div><div class="count">${c[k]}</div></div>`;
  }).join('');

  let revTags = '';
  if (data.requirements.revCounts) {
    const entries = Object.entries(data.requirements.revCounts);
    entries.sort((a, b) => {
      if (a[0].startsWith('base')) return -1;
      if (b[0].startsWith('base')) return 1;
      return a[0].localeCompare(b[0], undefined, { numeric: true });
    });
    revTags = entries.map(([k, v]) => `<div class="rev-tag">${escapeHtml(k)}: <span class="v">${v}</span></div>`).join('');
  }

  el.innerHTML = `<div style="font-size:12px;color:var(--dim)">${escapeHtml(t('req_total', data.requirements.totalReq))}</div>` +
    bars +
    `<div class="rev-tags">${revTags}</div>` +
    `<div class="placeholder" style="margin-top:10px;font-size:11px">${escapeHtml(t('req_footnote'))}</div>`;
}

function renderActivity(data) {
  const { escapeHtml } = window.dashboardUtils;
  const { t } = window.dashboardI18n;
  const el = document.getElementById('activity-body');

  if (!data.changeLog.ok) {
    el.innerHTML = errBox('err_label_changelog', 'validation/change-log.md');
    return;
  }

  const rows = data.changeLog.recent.map(r => `
    <div class="eco-row">
      <div class="id">${escapeHtml(r.id)}</div>
      <div class="date">${escapeHtml(r.date)}</div>
      <div class="txt"><span class="rev">${escapeHtml(r.revision)}</span>${escapeHtml(r.changed)}</div>
    </div>`).join('');

  el.innerHTML = `<div style="font-size:11px;color:var(--dim);margin-bottom:6px">${escapeHtml(t('activity_note', data.changeLog.recent.length, data.changeLog.total))}</div>${rows}`;
}

function renderMechanical(data) {
  const { escapeHtml } = window.dashboardUtils;
  const { t } = window.dashboardI18n;
  const el = document.getElementById('mechanical-body');

  let html = `<div class="viewer-cards">
    <a class="viewer-card" href="../circuit-viewer/index.html">
      <div class="t">${escapeHtml(t('viewer_circuit_title'))}</div>
      <div class="d">${escapeHtml(t('viewer_circuit_desc'))}</div>
    </a>
    <a class="viewer-card" href="../assembly-viewer/index.html">
      <div class="t">${escapeHtml(t('viewer_assembly_title'))}</div>
      <div class="d">${escapeHtml(t('viewer_assembly_desc'))}</div>
    </a>
  </div>`;

  if (data.mechanicalInterface.ok) {
    const m = data.mechanicalInterface;
    html += '<div class="fact-row">';
    if (m.length && m.width) {
      html += `<div class="fact"><div class="v">${escapeHtml(m.length.value)}×${escapeHtml(m.width.value)}${escapeHtml(m.length.unit)}</div><div class="l">${escapeHtml(t('fact_board'))}</div></div>`;
    }
    html += `<div class="fact"><div class="v">${m.holeCount}</div><div class="l">${escapeHtml(t('fact_holes'))}</div></div>`;
    html += '</div>';
    if (m.statusLine) {
      html += `<div class="status-line" style="margin-top:12px"><span class="doc">hardware/mechanical-interface.md</span><br><b>${escapeHtml(m.statusLine)}</b></div>`;
    }
  } else {
    html += errBox('err_label_mechanical', 'hardware/mechanical-interface.md');
  }

  el.innerHTML = html;
}

function renderAllSections(data) {
  renderPending(data);
  renderPhases(data);
  renderFindings(data);
  renderRequirements(data);
  renderActivity(data);
  renderMechanical(data);
}

function renderFetchStatus(data) {
  const statusEl = document.getElementById('fetch-status');
  const { t } = window.dashboardI18n;
  const failedCount = Object.keys(data.fetchErrors).length;
  const totalSources = Object.keys(data.sourcePaths).length;
  statusEl.classList.toggle('err', failedCount > 0);
  statusEl.textContent = failedCount > 0
    ? t('fetch_partial', totalSources - failedCount, totalSources, failedCount, data.fetchedAt.toLocaleTimeString())
    : t('fetch_ok', totalSources, data.fetchedAt.toLocaleTimeString());
}

async function refreshDashboard() {
  const btn = document.getElementById('refresh-btn');
  const statusEl = document.getElementById('fetch-status');
  const { t } = window.dashboardI18n;
  btn.disabled = true;
  statusEl.classList.remove('err');
  statusEl.textContent = t('loading');
  try {
    const data = await window.loadDashboardData();
    lastData = data;
    renderFetchStatus(data);
    renderAllSections(data);
  } catch (e) {
    statusEl.classList.add('err');
    statusEl.textContent = t('fetch_fail', (e && e.message) || e);
  } finally {
    btn.disabled = false;
  }
}

document.getElementById('refresh-btn').addEventListener('click', refreshDashboard);

// A language toggle must never trigger a new network fetch — re-render
// everything from the already-fetched cache instead.
document.addEventListener('dashboard-lang-changed', () => {
  if (lastData) {
    renderFetchStatus(lastData);
    renderAllSections(lastData);
  }
});

refreshDashboard();
