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

// ---- AI Agent Organization --------------------------------------------------
//
// Which discipline each agent belongs to, and its display order within
// that group, is curated by this page and matches docs/architecture.md
// section 3 — deliberately hardcoded, since the 12-agent structure
// itself doesn't change often and grouping is a display concern, not
// content. Nothing about an agent's CONTENT is hardcoded: role,
// description, and every relationship line on its card come from
// data.agentOrg (live frontmatter, fetched+parsed in dashboard-live.js).
// An agent whose name isn't listed in any group below still renders —
// in an auto "Other" group built by buildAgentGroups() — so a future
// agent addition/removal degrades gracefully (still counted, still
// shown) instead of silently vanishing.
const AGENT_GROUPS = [
  { key: 'electronics', labelKey: 'group_label_electronics',
    members: ['hardware-lead', 'component-engineer', 'power-engineer', 'circuit-engineer', 'pcb-engineer', 'hardware-reviewer'] },
  { key: 'mechanical', labelKey: 'group_label_mechanical',
    members: ['mechanical-lead', 'manufacturing-engineer', 'mechanical-reviewer'] },
  { key: 'firmware', labelKey: 'group_label_firmware',
    members: ['firmware-engineer', 'firmware-reviewer'] },
  { key: 'cross', labelKey: 'group_label_cross',
    members: ['systems-engineer'] },
];

// `delegates_to` is the one frontmatter field written as a flow-style
// YAML list (`[a, b, c]`) — display-only unwrap, parsing stays raw in
// dashboard-live.js.
function stripBracketList(s) {
  return (s || '').replace(/^\[\s*/, '').replace(/\s*\]$/, '');
}

function buildAgentGroups(agents) {
  const byName = {};
  agents.forEach(a => { byName[a.name] = a; });
  const assigned = new Set();
  const groups = AGENT_GROUPS.map(g => {
    const members = g.members.filter(n => byName[n]).map(n => { assigned.add(n); return byName[n]; });
    return { key: g.key, labelKey: g.labelKey, members };
  }).filter(g => g.members.length > 0);
  const leftover = agents.filter(a => !assigned.has(a.name));
  if (leftover.length) groups.push({ key: 'other', labelKey: 'group_label_other', members: leftover });
  return groups;
}

function renderAgentCard(agent, agentNames) {
  const { escapeHtml, truncate } = window.dashboardUtils;
  const { t } = window.dashboardI18n;

  // An agent whose reports_to doesn't match any OTHER live-fetched agent
  // name reports to a human, not a peer — detected from the data itself
  // (never a hardcoded "hardware-lead is special" check), which is what
  // marks it as the apex of the chart.
  const reportsToHuman = !!agent.reports_to && !agentNames.has(agent.reports_to.trim());

  const rel = [];
  if (agent.reports_to) {
    const label = reportsToHuman ? t('agentorg_reports_to_human') : t('agentorg_reports_to');
    rel.push(`<div>${escapeHtml(label)} <b>${escapeHtml(agent.reports_to)}</b></div>`);
  }
  if (agent.delegates_to) {
    rel.push(`<div>${escapeHtml(t('agentorg_delegates_to'))} <b>${escapeHtml(stripBracketList(agent.delegates_to))}</b></div>`);
  }
  if (agent.handoff_from) {
    rel.push(`<div>${escapeHtml(t('agentorg_handoff_from'))} <b>${escapeHtml(truncate(agent.handoff_from, 130))}</b></div>`);
  }
  if (agent.handoff_to) {
    rel.push(`<div>${escapeHtml(t('agentorg_handoff_to'))} <b>${escapeHtml(truncate(agent.handoff_to, 130))}</b></div>`);
  }

  return `<div class="org-card${reportsToHuman ? ' apex' : ''}" title="${escapeHtml('.github/agents/' + agent.file)}">
    <div class="role">${escapeHtml(agent.role || agent.name)}</div>
    <div class="name">${escapeHtml(agent.name)}</div>
    ${agent.description ? `<div class="desc">${escapeHtml(truncate(agent.description, 150))}</div>` : ''}
    ${rel.length ? `<div class="rel">${rel.join('')}</div>` : ''}
    ${agent.skill ? `<span class="skill-tag">${escapeHtml(t('agentorg_skill_tag'))} ${escapeHtml(agent.skill)}</span>` : ''}
    ${agent.independence ? `<div class="indep">⚖ ${escapeHtml(truncate(agent.independence, 130))}</div>` : ''}
  </div>`;
}

function renderAgentOrg(data) {
  const { escapeHtml } = window.dashboardUtils;
  const { t } = window.dashboardI18n;
  const el = document.getElementById('agent-org-body');

  if (!data.agentOrg.ok) {
    el.innerHTML = errBox('err_label_agent_org', '.github/agents');
    return;
  }

  const okAgents = data.agentOrg.agents.filter(a => a.ok);
  const agentNames = new Set(okAgents.map(a => a.name));
  const groups = buildAgentGroups(okAgents);

  const summary = `<div class="org-summary">${escapeHtml(t('agentorg_summary', data.agentOrg.total, groups.length))}</div>`;

  const groupsHtml = groups.map(g => {
    const cards = g.members.map((agent, idx) => {
      const card = renderAgentCard(agent, agentNames);
      return idx === 0 ? card : `<div class="org-arrow">&rarr;</div>${card}`;
    }).join('');
    return `<div class="org-group"><h3>${escapeHtml(t(g.labelKey))}</h3><div class="org-cards">${cards}</div></div>`;
  }).join('');

  let fileErrorsHtml = '';
  if (data.agentOrg.fileErrors.length) {
    const links = data.agentOrg.fileErrors.map(fe =>
      `<a href="https://github.com/ktanino10/ai-hardware-engineering-team/blob/main/.github/agents/${encodeURIComponent(fe.file)}" target="_blank" rel="noopener">${escapeHtml(fe.file)}</a>`
    ).join(', ');
    fileErrorsHtml = `<div class="err-box">${escapeHtml(t('agentorg_file_errors', data.agentOrg.fileErrors.length))} ${links}</div>`;
  }

  el.innerHTML = summary + groupsHtml + fileErrorsHtml +
    `<div class="placeholder" style="margin-top:12px;font-size:11px">${escapeHtml(t('agentorg_footnote'))}</div>`;
}

// ---- GitHub Feature Map -----------------------------------------------------
//
// LIVE vs. STATIC content is kept visibly separate on purpose (badges +
// distinct intro sentences) — see dashboard-i18n.js's own top comment
// for this dashboard's general translation-scope split; the same
// don't-blend-fact-classes principle applies here between what this
// unauthenticated page can and can't verify for itself.
//
// This confirmed-date constant is a deliberate fixed literal, NEVER
// `new Date()`: the 5 settings below require repository-admin
// authentication this public page doesn't have, so they were captured
// once (via an authenticated `gh api` call, see the PR description) and
// must read as "confirmed on this specific date", not silently imply a
// same-day re-check that never happened on every future page load.
// Revisit this date (and the values below it) by hand if these
// settings are ever intentionally changed.
const STATIC_FACTS_CONFIRMED_DATE = '2026-09-05';

function fmapLiveCell(metric, treePath) {
  const { escapeHtml } = window.dashboardUtils;
  const { t } = window.dashboardI18n;
  if (metric && metric.ok) return String(metric.count);
  return `<a href="https://github.com/ktanino10/ai-hardware-engineering-team/tree/main/${treePath}" target="_blank" rel="noopener" title="${escapeHtml((metric && metric.error) || '')}">${escapeHtml(t('featuremap_fetch_failed'))}</a>`;
}

function renderWorkflowList(workflows) {
  const { escapeHtml } = window.dashboardUtils;
  const { t } = window.dashboardI18n;
  if (!workflows || !workflows.ok) {
    return errBox('err_label_feature_map', '.github/workflows');
  }
  const rows = workflows.items.map(w => {
    if (w.ok) {
      // w.name and w.triggers are live-parsed literal repo/workflow
      // content (this workflow's own configured name and trigger
      // keywords) — kept in English regardless of UI language, same
      // rule this dashboard already applies to phase names/finding
      // titles/ECO text elsewhere.
      return `<div class="wf-row"><b>${escapeHtml(w.name)}</b> <span class="wf-triggers">${escapeHtml(w.triggers.join(', ') || '(none detected)')}</span></div>`;
    }
    return `<div class="wf-row err"><a href="https://github.com/ktanino10/ai-hardware-engineering-team/blob/main/.github/workflows/${encodeURIComponent(w.file)}" target="_blank" rel="noopener" title="${escapeHtml(w.error || '')}">${escapeHtml(w.file)}</a> — ${escapeHtml(t('featuremap_fetch_failed'))}</div>`;
  }).join('');
  return `<div class="wf-list">
    <div class="wf-list-title"><code>.github/workflows/</code> ${escapeHtml(t('featuremap_workflows_suffix', workflows.count))}</div>
    ${rows}
  </div>`;
}

// Every static-row feature name + detail sentence below is deliberately
// English-only in both UI languages (see this function's own callers) —
// only the link label passed in is translated chrome.
function staticRow(featureName, detail, link, linkLabel) {
  const { escapeHtml } = window.dashboardUtils;
  return `<div class="static-row"><b>${escapeHtml(featureName)}</b>: ${escapeHtml(detail)} — <a href="${link}" target="_blank" rel="noopener">${escapeHtml(linkLabel)} &#8599;</a></div>`;
}

function renderFeatureMap(data) {
  const { escapeHtml } = window.dashboardUtils;
  const { t } = window.dashboardI18n;
  const el = document.getElementById('feature-map-body');
  const fm = data.featureMap;

  const branchesLink = 'https://github.com/ktanino10/ai-hardware-engineering-team/settings/branches';
  const securityLink = 'https://github.com/ktanino10/ai-hardware-engineering-team/settings/security_analysis';
  const pagesLink = 'https://github.com/ktanino10/ai-hardware-engineering-team/settings/pages';
  const pullsLink = 'https://github.com/ktanino10/ai-hardware-engineering-team/pulls';

  let html = `<div class="fmap-block">
    <div class="fmap-heading"><span class="badge badge-live">${escapeHtml(t('badge_live'))}</span> ${escapeHtml(t('featuremap_live_intro'))}</div>
    <table class="mini">
      <thead><tr><th>${escapeHtml(t('featuremap_col_feature'))}</th><th>${escapeHtml(t('featuremap_col_count'))}</th><th>${escapeHtml(t('featuremap_col_detail'))}</th></tr></thead>
      <tbody>
        <tr><td class="rowhead"><code>.github/agents/</code></td><td>${fmapLiveCell(fm.agents, '.github/agents')}</td><td>${escapeHtml(t('featuremap_row_agents_detail'))}</td></tr>
        <tr><td class="rowhead"><code>.github/skills/</code></td><td>${fmapLiveCell(fm.skills, '.github/skills')}</td><td>${escapeHtml(t('featuremap_row_skills_detail'))}</td></tr>
        <tr><td class="rowhead"><code>.github/prompts/</code></td><td>${fmapLiveCell(fm.prompts, '.github/prompts')}</td><td>${escapeHtml(t('featuremap_row_prompts_detail'))}</td></tr>
        <tr><td class="rowhead"><code>.github/instructions/</code></td><td>${fmapLiveCell(fm.instructions, '.github/instructions')}</td><td>${escapeHtml(t('featuremap_row_instructions_detail'))}</td></tr>
        <tr><td class="rowhead"><code>CODEOWNERS</code></td><td>${fmapLiveCell(fm.codeowners, '.github')}</td><td>${escapeHtml(t('featuremap_row_codeowners_detail'))}</td></tr>
      </tbody>
    </table>
    ${renderWorkflowList(fm.workflows)}
  </div>`;

  html += `<div class="fmap-block static">
    <div class="fmap-heading"><span class="badge badge-static">${escapeHtml(t('badge_static_confirmed', STATIC_FACTS_CONFIRMED_DATE))}</span></div>
    <div class="static-intro">${escapeHtml(t('featuremap_static_intro', STATIC_FACTS_CONFIRMED_DATE))}</div>
    ${staticRow('Branch Protection (main)',
      '3 required status checks ("Check open-issues.md for unresolved CRITICAL/HIGH findings", "Check ECO/Issue/Evidence IDs for cross-branch duplicates", "Check agent/skill frontmatter"); force-push: disabled; branch deletion: disabled',
      branchesLink, t('featuremap_link_branches'))}
    ${staticRow('Secret Scanning + Push Protection', 'both: enabled', securityLink, t('featuremap_link_security'))}
    ${staticRow('Dependabot Security Updates', 'enabled', securityLink, t('featuremap_link_security'))}
    ${staticRow('Code Scanning (CodeQL)',
      'default setup: configured (languages: Actions, C/C++, JavaScript/TypeScript, Python; weekly schedule) — not defined under .github/workflows/, configured directly in repository security settings',
      securityLink, t('featuremap_link_security'))}
    ${staticRow('GitHub Pages', 'visibility: public; build type: workflow (GitHub Actions — see deploy-pages.yml above)', pagesLink, t('featuremap_link_pages'))}
  </div>`;

  html += `<div class="fmap-block static-note">
    <div class="fmap-heading"><span class="badge badge-static-note">${escapeHtml(t('badge_static_note'))}</span></div>
    <div class="static-intro">${escapeHtml(t('featuremap_static_note_intro'))}</div>
    ${staticRow('Pull Requests / Issues',
      'GitHub Issues intentionally unused for this project — every change merges via Pull Request (direct pushes to main blocked by the branch protection above); findings, ECOs, and decisions are instead tracked as traceable Markdown ledgers under validation/ (open-issues.md, change-log.md, and others — see Findings & Recent Activity above)',
      pullsLink, t('featuremap_link_pulls'))}
  </div>`;

  el.innerHTML = html;
}

function renderAllSections(data) {
  renderPending(data);
  renderPhases(data);
  renderFindings(data);
  renderRequirements(data);
  renderActivity(data);
  renderMechanical(data);
  renderAgentOrg(data);
  renderFeatureMap(data);
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
