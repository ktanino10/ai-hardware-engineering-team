/*
 * dashboard-render.js — takes the parsed state from dashboard-live.js and
 * renders every section into the DOM. Owns the loading state and the
 * Refresh button. Every render function checks its own section's `ok` flag
 * first and falls back to a "couldn't parse — see the file directly" box
 * instead of assuming a shape that might not hold.
 */

function statBox(v, l) {
  return `<div class="stat"><div class="v">${v}</div><div class="l">${l}</div></div>`;
}
function gateCond(pass, text) {
  return `<div class="cond ${pass ? 'ok' : 'bad'}">${pass ? '✓' : '✗'} ${text}</div>`;
}
function errBox(label, path) {
  return `<div class="err-box">Couldn't parse ${label} — ` +
    `<a href="https://github.com/ktanino10/ai-hardware-engineering-team/blob/main/${path}" target="_blank" rel="noopener">see ${path} directly ↗</a></div>`;
}

function renderPending(data) {
  const { escapeHtml } = window.dashboardUtils;
  const el = document.getElementById('pending-body');
  const sectionEl = document.getElementById('section-pending');

  let componentHtml = '', findingHtml = '', softHtml = '';
  let hardBlockerCount = 0;

  if (data.componentSelection.ok) {
    data.componentSelection.pending.forEach(p => {
      hardBlockerCount++;
      componentHtml += `<div class="decision-row">
        <div class="decision-tag component">COMPONENT</div>
        <div class="decision-main"><div class="t">${escapeHtml(p.section)}</div><div class="d">${escapeHtml(p.decision)}</div></div>
      </div>`;
    });
  } else {
    componentHtml = errBox('component approval status', 'bom/component-selection.md');
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
    findingHtml = errBox('open findings', 'validation/open-issues.md');
  }

  if (data.requirements.ok) {
    data.requirements.possiblyOpenQuestions.forEach(q => {
      softHtml += `<div class="decision-row">
        <div class="decision-tag soft">SOFT SIGNAL</div>
        <div class="decision-main"><div class="t">${escapeHtml(q)}</div>
          <div class="d">Heading marked "pending confirmation" with no later lettered follow-up section found yet in requirements.md — may already be answered elsewhere; not asserted as definitely still open.</div>
        </div>
      </div>`;
    });
  }

  let html = '';
  const bothParsedOk = data.componentSelection.ok && data.openIssues.ok;
  if (bothParsedOk && hardBlockerCount === 0) {
    html += `<div class="all-clear">✓ Nothing currently blocking a human decision
      <div class="d">0 pending component/subsystem approvals, 0 open CRITICAL/HIGH findings.</div></div>`;
    sectionEl.classList.add('clear');
  } else {
    sectionEl.classList.remove('clear');
  }
  html += componentHtml + findingHtml + softHtml;
  if (data.componentSelection.ok) {
    html += `<div style="margin-top:10px;font-size:11px;color:var(--dim)">${data.componentSelection.approvedCount} of ${data.componentSelection.totalDecisions} component/subsystem decisions already approved.</div>`;
  }
  el.innerHTML = html || '<span class="placeholder">No data.</span>';
}

function renderPhases(data) {
  const { escapeHtml, truncate } = window.dashboardUtils;
  const el = document.getElementById('phases-body');

  if (!data.phases.ok) {
    el.innerHTML = errBox('the phase pipeline', 'docs/workflow.md');
    return;
  }

  const pendingCount = data.componentSelection.ok ? data.componentSelection.pending.length : null;
  const latestMilestone = (data.changeLog.ok && data.changeLog.milestones.length) ? data.changeLog.milestones[0] : null;

  const chips = data.phases.phases.map(p => {
    let badge = '';
    if (/component selection/i.test(p.name) && pendingCount !== null) {
      badge = pendingCount > 0
        ? `<div class="badge">${pendingCount} pending</div>`
        : `<div class="badge" style="background:rgba(62,224,138,.15);color:var(--good)">clear</div>`;
    }
    if (/design complete gate/i.test(p.name) && latestMilestone) {
      badge = `<div class="badge" title="${escapeHtml(latestMilestone.id + ' · ' + latestMilestone.date)}">${escapeHtml(truncate(latestMilestone.text, 42))}</div>`;
    }
    return `<div class="phase-chip"><div class="n">Phase ${p.num}</div><div class="name">${escapeHtml(p.name)}</div>${badge}</div>`;
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
    `<div class="placeholder" style="margin-top:12px;font-size:11px">Each document above keeps its own independent revision counter for its own scope — they don't line up 1:1 project-wide, so no single "Rev N / current phase" is asserted here on purpose. The badges and self-reported lines are each pulled live from their own source file instead.</div>`;
}

function renderFindings(data) {
  const el = document.getElementById('findings-body');
  let html = '';

  if (data.openIssues.ok) {
    const SEVS = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'];
    const STATS = ['OPEN', 'RESOLVED', 'ACCEPTED-RISK'];
    const rows = SEVS.map(s => {
      const t = data.openIssues.tally[s];
      const cells = STATS.map(st => `<td class="${t[st] === 0 ? 'zero' : ''}">${t[st]}</td>`).join('');
      return `<tr><td class="rowhead sev-${s}">${s}</td>${cells}</tr>`;
    }).join('');
    html += `<table class="mini"><thead><tr><th></th>${STATS.map(s => `<th>${s}</th>`).join('')}</tr></thead><tbody>${rows}</tbody></table>`;
  } else {
    html += errBox('the findings backlog', 'validation/open-issues.md');
  }

  html += '<div class="stat-row">';
  if (data.changeLog.ok) html += statBox(data.changeLog.total, 'ECOs');
  if (data.openIssues.ok) html += statBox(data.openIssues.totalRows, 'Findings (ISS+MISS)');
  if (data.evidenceLog.ok) html += statBox(data.evidenceLog.count, 'Evidence IDs (DS)');
  html += '</div>';

  html += `<div class="gate-check">
    <div style="font-size:11px;color:var(--dim);margin-bottom:4px">Design Complete Gate conditions
      (<a href="https://github.com/ktanino10/ai-hardware-engineering-team/blob/main/docs/architecture.md" target="_blank" rel="noopener">docs/architecture.md §8 ↗</a>) —
      counts are cumulative across this file's whole history, not scoped to one revision:</div>`;
  if (data.openIssues.ok) {
    const critOpen = data.openIssues.tally.CRITICAL.OPEN;
    const highOpen = data.openIssues.tally.HIGH.OPEN;
    html += gateCond(critOpen === 0, `Zero unresolved CRITICAL findings (currently ${critOpen} open)`);
    html += gateCond(highOpen === 0, `Every HIGH finding RESOLVED or ACCEPTED-RISK (currently ${highOpen} open)`);
  }
  if (data.traceability.ok) {
    const t = data.traceability.counts;
    const notDone = t.Pending + t.Failed + t.Other;
    html += gateCond(notDone === 0, `Traceability matrix 100% Verified/Waived (currently ${t.Verified + t.Waived} of ${data.traceability.total}; ${t.Pending} Pending)`);
  }
  html += `<div class="cond na">— FMEA-reviewed and a signed change-log entry aren't tracked on this dashboard —
    <a href="https://github.com/ktanino10/ai-hardware-engineering-team/blob/main/validation/fmea.md" target="_blank" rel="noopener">see validation/fmea.md ↗</a></div>`;
  html += '</div>';

  el.innerHTML = html;
}

function renderRequirements(data) {
  const { escapeHtml } = window.dashboardUtils;
  const el = document.getElementById('requirements-body');

  if (!data.requirements.ok) {
    el.innerHTML = errBox('requirement priorities', 'requirements/requirements.md');
    return;
  }

  const c = data.requirements.counts;
  const total = data.requirements.totalReq || 1;
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

  el.innerHTML = `<div style="font-size:12px;color:var(--dim)">${data.requirements.totalReq} total requirement rows, across every section</div>` +
    bars +
    `<div class="rev-tags">${revTags}</div>` +
    `<div class="placeholder" style="margin-top:10px;font-size:11px">Tagged by the literal "*(Rev N)*" marker on each requirement ID — a requirement with no tag was carried forward unchanged from Rev 1/2.</div>`;
}

function renderActivity(data) {
  const { escapeHtml } = window.dashboardUtils;
  const el = document.getElementById('activity-body');

  if (!data.changeLog.ok) {
    el.innerHTML = errBox('the change log', 'validation/change-log.md');
    return;
  }

  const rows = data.changeLog.recent.map(r => `
    <div class="eco-row">
      <div class="id">${escapeHtml(r.id)}</div>
      <div class="date">${escapeHtml(r.date)}</div>
      <div class="txt"><span class="rev">${escapeHtml(r.revision)}</span>${escapeHtml(r.changed)}</div>
    </div>`).join('');

  el.innerHTML = `<div style="font-size:11px;color:var(--dim);margin-bottom:6px">
      Most recent ${data.changeLog.recent.length} of ${data.changeLog.total} total ECOs — shown in document order (= chronological
      authorship order). The "Date" column itself is known to be non-monotonic in places, per this project's own ISS-056 finding, so it
      is not used for sorting.</div>${rows}`;
}

function renderMechanical(data) {
  const { escapeHtml } = window.dashboardUtils;
  const el = document.getElementById('mechanical-body');

  let html = `<div class="viewer-cards">
    <a class="viewer-card" href="../circuit-viewer/index.html">
      <div class="t">Circuit &amp; Current-Flow Viewer</div>
      <div class="d">Interactive block diagram of power distribution and real (bench-mode) current behavior, built from the real schematic, netlist, and firmware source. Click any component or wire.</div>
    </a>
    <a class="viewer-card" href="../assembly-viewer/index.html">
      <div class="t">3D Assembly &amp; Part Inspector</div>
      <div class="d">Real mechanical geometry (KiCad PCB export + OpenSCAD-derived STL parts) as an orbit-and-click exploded assembly. No plugin required.</div>
    </a>
  </div>`;

  if (data.mechanicalInterface.ok) {
    const m = data.mechanicalInterface;
    html += '<div class="fact-row">';
    if (m.length && m.width) {
      html += `<div class="fact"><div class="v">${escapeHtml(m.length.value)}×${escapeHtml(m.width.value)}${escapeHtml(m.length.unit)}</div><div class="l">Board outline</div></div>`;
    }
    html += `<div class="fact"><div class="v">${m.holeCount}</div><div class="l">Mounting holes</div></div>`;
    html += '</div>';
    if (m.statusLine) {
      html += `<div class="status-line" style="margin-top:12px"><span class="doc">hardware/mechanical-interface.md</span><br><b>${escapeHtml(m.statusLine)}</b></div>`;
    }
  } else {
    html += errBox('live mechanical facts', 'hardware/mechanical-interface.md');
  }

  el.innerHTML = html;
}

async function refreshDashboard() {
  const btn = document.getElementById('refresh-btn');
  const statusEl = document.getElementById('fetch-status');
  btn.disabled = true;
  statusEl.classList.remove('err');
  statusEl.textContent = 'Loading live data from GitHub…';
  try {
    const data = await window.loadDashboardData();
    const failedCount = Object.keys(data.fetchErrors).length;
    const totalSources = Object.keys(data.sourcePaths).length;
    if (failedCount > 0) {
      statusEl.classList.add('err');
      statusEl.textContent = `Fetched ${totalSources - failedCount}/${totalSources} source files (${failedCount} failed — affected sections show a fallback link below). Last attempt ${data.fetchedAt.toLocaleTimeString()}.`;
    } else {
      statusEl.textContent = `All ${totalSources} source files fetched live. Last updated ${data.fetchedAt.toLocaleTimeString()}.`;
    }
    renderPending(data);
    renderPhases(data);
    renderFindings(data);
    renderRequirements(data);
    renderActivity(data);
    renderMechanical(data);
  } catch (e) {
    statusEl.classList.add('err');
    statusEl.textContent = 'Failed to load live data: ' + ((e && e.message) || e);
  } finally {
    btn.disabled = false;
  }
}

document.getElementById('refresh-btn').addEventListener('click', refreshDashboard);
refreshDashboard();
