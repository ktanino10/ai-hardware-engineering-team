/*
 * dashboard-live.js — fetches this repository's own requirements, findings,
 * change-log, component-selection, mechanical-interface, workflow, and
 * evidence-log files LIVE from GitHub's raw-content CDN at page load, and
 * parses them into plain data in the browser.
 *
 * Deliberately NOT named like circuit-data.js/assembly-data.js: those are
 * static, checked-in, built-once-from-real-source data files. This file is
 * the opposite in kind — nothing here is committed data, every value is
 * re-derived from the live document content on every page load/Refresh
 * click, because that's what "stays current automatically" requires for
 * content that changes as often as this project's requirements/findings/
 * change-log do (68+ ECOs and counting). See README.md for the trade-off
 * this was weighed against (a generated-and-committed data file, matching
 * the other two viewers' pattern) and why that path was rejected here.
 *
 * Parsing philosophy mirrors this repo's own tools/check_id_uniqueness.py:
 * locate a table by its header row's real cell names (never a hardcoded
 * line number or column index), end a table only at the next heading or
 * EOF (tolerate stray blank/malformed lines in between rather than
 * stopping), and map cells to column names from the live header so a
 * future column reorder degrades gracefully instead of silently
 * misattributing data. Every parse function is wrapped so a shape
 * mismatch produces a `{ok:false, error}` result for that section only —
 * never an uncaught exception that would blank the whole page.
 */

const RAW_BASE = 'https://raw.githubusercontent.com/ktanino10/ai-hardware-engineering-team/main/';

const SOURCES = {
  requirements: 'requirements/requirements.md',
  traceability: 'requirements/traceability-matrix.md',
  openIssues: 'validation/open-issues.md',
  changeLog: 'validation/change-log.md',
  componentSelection: 'bom/component-selection.md',
  mechanicalInterface: 'hardware/mechanical-interface.md',
  workflow: 'docs/workflow.md',
  evidenceLog: 'datasheets/evidence-log.md',
};

// ---- small shared helpers (also used by dashboard-render.js) -------------

function truncate(s, n) {
  // Also strips raw Markdown bold/code markers — this page does no Markdown
  // rendering anywhere, so a literal "**"/"`" left in from the source file
  // would otherwise show up as noise rather than emphasis.
  s = (s || '').toString().replace(/\*\*/g, '').replace(/`/g, '').trim();
  return s.length > n ? s.slice(0, n).trim() + '…' : s;
}

function escapeHtml(s) {
  return String(s == null ? '' : s).replace(/[&<>"']/g, c => (
    { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]
  ));
}

function findCol(columns, re) {
  return (columns || []).find(c => re.test(c));
}

// ---- generic, defensive Markdown table extractor --------------------------
//
// Splits a single "| a | b | c |" row into trimmed cells, dropping the
// leading/trailing empty strings produced by the outer pipes.
function splitRow(line) {
  let s = line.trim();
  if (s.startsWith('|')) s = s.slice(1);
  if (s.endsWith('|')) s = s.slice(0, -1);
  return s.split('|').map(c => c.trim());
}

function isSeparatorRow(cells) {
  return cells.length > 0 && cells.every(c => /^:?-+:?$/.test(c.trim()));
}

// Generic-purpose "boilerplate" heading names that recur as the LAST/
// innermost heading right before an Approval table in bom/component-selection.md
// (e.g. "#### Approval") — these are never themselves a useful section label,
// so section-name lookup walks past them to the nearest ancestor heading that
// actually names the component/subsystem/re-evaluation.
const GENERIC_HEADING = /^(approval|escalation flags|recommendation|candidate comparison|cross-check note.*|success-probability ranking.*)$/i;

/**
 * Finds every Markdown table in `text` whose header row's cells contain ALL
 * of `headerMustInclude` (case-insensitive substring match per required
 * term). Returns an array of { heading, columns, rows } — `heading` is the
 * nearest non-boilerplate Markdown heading preceding the table; `columns`
 * is the table's own live header cell text (used as the row-object keys,
 * so a future column rename/reorder is picked up automatically rather than
 * silently misread); `rows` is an array of plain objects keyed by column
 * name, plus `_raw` (the original line, for debugging).
 *
 * A table's data rows end only at the next Markdown heading or EOF — a
 * stray blank line or malformed row in between is skipped, not treated as
 * the table's end (the exact failure class this repo's own
 * tools/check_id_uniqueness.py documents fixing for these same files).
 */
function extractAllTables(text, headerMustInclude) {
  const lines = text.split('\n');
  const tables = [];
  const headingStack = [];

  function updateHeading(line) {
    const m = line.match(/^(#{1,6})\s+(.*)/);
    if (!m) return false;
    const level = m[1].length;
    const name = m[2].replace(/`/g, '').replace(/\*\*/g, '').trim();
    while (headingStack.length && headingStack[headingStack.length - 1].level >= level) headingStack.pop();
    headingStack.push({ level, name });
    return true;
  }
  function sectionName() {
    for (let i = headingStack.length - 1; i >= 0; i--) {
      if (!GENERIC_HEADING.test(headingStack[i].name)) return headingStack[i].name;
    }
    return headingStack.length ? headingStack[headingStack.length - 1].name : '';
  }

  let i = 0;
  while (i < lines.length) {
    const line = lines[i];
    if (updateHeading(line)) { i++; continue; }
    if (line.trim().startsWith('|')) {
      const cells = splitRow(line);
      const lower = cells.map(c => c.toLowerCase());
      const isHeader = !isSeparatorRow(cells) &&
        headerMustInclude.every(h => lower.some(c => c.includes(h.toLowerCase())));
      if (isHeader) {
        const colNames = cells.map(c => c.trim());
        const heading = sectionName();
        i += 1;
        if (i < lines.length && lines[i].trim().startsWith('|') && isSeparatorRow(splitRow(lines[i]))) i++;
        const rows = [];
        while (i < lines.length && !/^#{1,6}\s/.test(lines[i])) {
          const l = lines[i];
          if (l.trim().startsWith('|')) {
            const c = splitRow(l);
            if (!isSeparatorRow(c)) {
              const obj = { _raw: l };
              colNames.forEach((n, idx) => { obj[n] = (c[idx] !== undefined ? c[idx] : '').trim(); });
              rows.push(obj);
            }
          }
          i++;
        }
        tables.push({ heading, columns: colNames, rows });
        continue;
      }
    }
    i++;
  }
  return tables;
}

// ---- per-source parsers ----------------------------------------------------

// bom/component-selection.md — every Approval table's Chief Engineer row;
// PENDING literal Date cell = still awaiting human review.
function parseComponentSelection(text) {
  try {
    const tables = extractAllTables(text, ['Role', 'Name', 'Date', 'Decision']);
    const pending = [];
    let approvedCount = 0;
    for (const t of tables) {
      const roleCol = findCol(t.columns, /^role$/i) || t.columns[0];
      const dateCol = findCol(t.columns, /^date$/i) || t.columns[2];
      const decisionCol = findCol(t.columns, /^decision$/i) || t.columns[t.columns.length - 1];
      for (const row of t.rows) {
        const role = row[roleCol] || '';
        if (!/chief engineer\s*\(human\)/i.test(role)) continue;
        const date = (row[dateCol] || '').trim();
        if (/^pending$/i.test(date)) {
          pending.push({ section: t.heading || '(unnamed section)', decision: truncate(row[decisionCol] || '', 240) });
        } else {
          approvedCount++;
        }
      }
    }
    return { ok: true, pending, approvedCount, totalDecisions: pending.length + approvedCount };
  } catch (e) {
    return { ok: false, error: String((e && e.message) || e) };
  }
}

// validation/open-issues.md — Backlog table: severity x status tally, open
// CRITICAL/HIGH list, ISS/MISS scale counts.
function parseOpenIssues(text) {
  try {
    const tables = extractAllTables(text, ['Severity', 'Status', 'Title']);
    if (!tables.length) throw new Error('Backlog table not found (header shape may have changed)');
    const table = tables.reduce((a, b) => (b.rows.length > a.rows.length ? b : a));
    const idCol = findCol(table.columns, /^id$/i) || table.columns[0];
    const sevCol = findCol(table.columns, /^severity$/i);
    const statCol = findCol(table.columns, /^status$/i);
    const titleCol = findCol(table.columns, /^title$/i);

    const SEVERITIES = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'];
    const STATUSES = ['OPEN', 'RESOLVED', 'ACCEPTED-RISK'];
    const tally = {};
    SEVERITIES.forEach(s => { tally[s] = { OTHER: 0 }; STATUSES.forEach(st => { tally[s][st] = 0; }); });

    const openCriticalHigh = [];
    let issCount = 0, missCount = 0;
    for (const row of table.rows) {
      const id = (row[idCol] || '').trim();
      if (/^ISS-/i.test(id)) issCount++;
      else if (/^MISS-/i.test(id)) missCount++;
      else continue; // not a real finding row — skip defensively, keep scanning
      const sev = (row[sevCol] || '').trim().toUpperCase();
      const stat = (row[statCol] || '').trim().toUpperCase();
      if (SEVERITIES.includes(sev)) {
        tally[sev][STATUSES.includes(stat) ? stat : 'OTHER']++;
      }
      if ((sev === 'CRITICAL' || sev === 'HIGH') && stat === 'OPEN') {
        openCriticalHigh.push({ id, severity: sev, title: truncate(row[titleCol] || '', 170) });
      }
    }
    return { ok: true, tally, issCount, missCount, totalRows: issCount + missCount, openCriticalHigh };
  } catch (e) {
    return { ok: false, error: String((e && e.message) || e) };
  }
}

// validation/change-log.md — Log table: recent ECOs + Design-Complete-Gate
// milestone phrases found in the Revision cell.
function parseChangeLog(text) {
  try {
    const tables = extractAllTables(text, ['ECO ID', 'Date', 'Revision', 'Changed']);
    if (!tables.length) throw new Error('Log table not found (header shape may have changed)');
    const table = tables.reduce((a, b) => (b.rows.length > a.rows.length ? b : a));
    const idCol = findCol(table.columns, /^eco id$/i) || table.columns[0];
    const dateCol = findCol(table.columns, /^date$/i);
    const revCol = findCol(table.columns, /revision/i);
    const changedCol = findCol(table.columns, /^changed$/i);

    const rows = table.rows.map(row => ({
      id: (row[idCol] || '').trim(),
      date: (row[dateCol] || '').trim(),
      revision: truncate(row[revCol] || '', 150),
      changed: truncate(row[changedCol] || '', 240),
    })).filter(r => /^ECO-/i.test(r.id));

    const milestoneRe = /(DESIGN COMPLETE GATE GRANTED[^*|]*|DESIGN COMPLETE NOT GRANTED[^*|]*|FABRICATION DELIBERATELY PAUSED[^*|]*|BOTH HITL GATES GRANTED[^*|]*)/i;
    const milestones = [];
    for (const row of table.rows) {
      const revRaw = row[revCol] || '';
      const m = revRaw.match(milestoneRe);
      if (m) milestones.push({ id: (row[idCol] || '').trim(), date: (row[dateCol] || '').trim(), text: truncate(m[0].replace(/\*/g, ''), 150) });
    }

    return { ok: true, rows, recent: rows.slice(-12).reverse(), total: rows.length, milestones: milestones.slice(-6).reverse() };
  } catch (e) {
    return { ok: false, error: String((e && e.message) || e) };
  }
}

// requirements/traceability-matrix.md — Status bucketing.
function parseTraceability(text) {
  try {
    const tables = extractAllTables(text, ['Requirement ID', 'Status']);
    if (!tables.length) throw new Error('Traceability table not found (header shape may have changed)');
    const table = tables.reduce((a, b) => (b.rows.length > a.rows.length ? b : a));
    const idCol = findCol(table.columns, /requirement id/i) || table.columns[0];
    const statusCol = findCol(table.columns, /^status$/i);
    const counts = { Verified: 0, Pending: 0, Waived: 0, Failed: 0, Other: 0 };
    let total = 0;
    for (const row of table.rows) {
      const id = (row[idCol] || '').trim();
      if (!/^REQ-/i.test(id)) continue;
      total++;
      // Anchor to the START of the (bold-stripped) cell, not "contains
      // anywhere" — real rows here include e.g. "Verified — confirmed
      // waived, not applicable" and "Verified — ...hardware confirmation
      // pending physical build", where an unanchored substring check would
      // wrongly bucket a Verified row as Waived/Pending just because that
      // word appears later in the same explanatory sentence.
      const s = (row[statusCol] || '').replace(/^\*+/, '').trim();
      if (/^waived/i.test(s)) counts.Waived++;
      else if (/^failed/i.test(s)) counts.Failed++;
      else if (/^pending/i.test(s)) counts.Pending++;
      else if (/^verified/i.test(s)) counts.Verified++;
      else counts.Other++;
    }
    return { ok: true, counts, total };
  } catch (e) {
    return { ok: false, error: String((e && e.message) || e) };
  }
}

// hardware/mechanical-interface.md — self-reported Status line, board
// length/width, mounting-hole count.
function parseMechanicalInterface(text) {
  try {
    let statusLine = null;
    const statusMatch = text.match(/\*\*Status\*\*:\s*\*\*([^*]{3,300})\*\*/);
    if (statusMatch) statusLine = truncate(statusMatch[1], 260);

    const geomTables = extractAllTables(text, ['Parameter', 'Value', 'Unit']);
    let length = null, width = null;
    for (const t of geomTables) {
      const paramCol = findCol(t.columns, /parameter/i) || t.columns[0];
      const valueCol = findCol(t.columns, /^value$/i);
      const unitCol = findCol(t.columns, /^unit$/i);
      for (const row of t.rows) {
        const p = (row[paramCol] || '').trim().toLowerCase();
        if (length === null && p.includes('length')) length = { value: (row[valueCol] || '').trim(), unit: (row[unitCol] || '').trim() };
        if (width === null && p.includes('width')) width = { value: (row[valueCol] || '').trim(), unit: (row[unitCol] || '').trim() };
      }
    }

    const holeTables = extractAllTables(text, ['Hole', 'Diameter']);
    let holeCount = 0;
    for (const t of holeTables) {
      const holeCol = findCol(t.columns, /^hole$/i) || t.columns[0];
      for (const row of t.rows) {
        if (/^MH-?\d*/i.test((row[holeCol] || '').trim())) holeCount++;
      }
    }

    return { ok: true, statusLine, length, width, holeCount };
  } catch (e) {
    return { ok: false, error: String((e && e.message) || e) };
  }
}

// requirements/requirements.md — priority tally, Rev-tag breakdown, and a
// hedged "open questions" soft signal.
function parseRequirements(text) {
  try {
    // Self-reported bold status markers near the top of the doc. Convention
    // isn't 100% consistent: sometimes only the value is bold ("Status:
    // **APPROVED**"), sometimes the whole phrase is ("**Rev 5
    // scope-decision status: APPROVED**") — both are matched explicitly
    // (rather than a loose "contains the word status" filter) so incidental
    // prose emphasis elsewhere that merely contains the word "status"
    // (e.g. "**This status line covers only the...**") isn't picked up.
    const head = text.slice(0, 4000);
    const statusLines = [];
    for (const m of head.matchAll(/\*{0,2}((?:[\w-]+\s+){0,3}status)\*{0,2}:\s*\*\*([A-Z][^*\n]{0,60})\*\*/gi)) {
      statusLines.push((m[1].trim() + ': ' + m[2].trim()).replace(/\s+/g, ' '));
    }
    for (const m of head.matchAll(/\*\*([^*]{3,120}\bstatus:\s*[A-Z][^*]{0,60})\*\*/gi)) {
      statusLines.push(m[1].replace(/\s+/g, ' ').trim());
    }

    const tables = extractAllTables(text, ['ID', 'Requirement', 'Priority']);
    const counts = { Must: 0, Should: 0, Could: 0, "Won't": 0, Other: 0 };
    const revCounts = {};
    let totalReq = 0;
    for (const t of tables) {
      const idCol = findCol(t.columns, /^id$/i);
      const prioCol = findCol(t.columns, /priority/i);
      if (!idCol || !prioCol) continue;
      for (const row of t.rows) {
        const id = (row[idCol] || '').trim();
        if (!/^REQ-/i.test(id)) continue;
        totalReq++;
        const p = row[prioCol] || '';
        let bucket = 'Other';
        if (/won/i.test(p)) bucket = "Won't";
        else if (/must/i.test(p)) bucket = 'Must';
        else if (/should/i.test(p)) bucket = 'Should';
        else if (/could/i.test(p)) bucket = 'Could';
        counts[bucket]++;
        const revMatch = id.match(/rev\s*(\d+)/i);
        const revKey = revMatch ? ('Rev ' + revMatch[1]) : 'base (Rev 1/2)';
        revCounts[revKey] = (revCounts[revKey] || 0) + 1;
      }
    }

    // Soft "still open?" signal: headings shaped "## <N><letter>. ... (new,
    // pending confirmation)". A later lettered subsection under the SAME
    // number (e.g. §9i/§9j after §9h) is a strong, not certain, sign the
    // question set has since been addressed — so only a heading with no
    // such follow-up yet is surfaced as "possibly still open". Generalizes
    // to future revisions without new code (doesn't assume "5" is the
    // ceiling).
    const headingRe = /^#{2,3}\s+(\d+)([a-z])\.\s+(.+)$/gim;
    const all = [...text.matchAll(headingRe)].map(m => ({ num: m[1], letter: m[2], title: m[3].trim() }));
    const groups = {};
    all.forEach(h => { (groups[h.num] = groups[h.num] || []).push(h); });
    const possiblyOpenQuestions = [];
    Object.keys(groups).forEach(num => {
      const g = groups[num];
      g.forEach((h, idx) => {
        if (/pending confirmation/i.test(h.title) && idx === g.length - 1) {
          possiblyOpenQuestions.push(truncate(h.title, 140));
        }
      });
    });

    return { ok: true, statusLines, counts, revCounts, totalReq, possiblyOpenQuestions };
  } catch (e) {
    return { ok: false, error: String((e && e.message) || e) };
  }
}

// docs/workflow.md — the live phase pipeline.
function parsePhases(text) {
  try {
    const re = /^###\s+Phase\s+(\d+)\s+—\s+([^\n]+)$/gim;
    const phases = [...text.matchAll(re)].map(m => {
      let name = m[2].trim();
      name = name.replace(/\s*\*\(.*$/, '').trim(); // strip a trailing "*(Phase N of the..." annotation
      return { num: parseInt(m[1], 10), name };
    });
    if (!phases.length) throw new Error('No "### Phase N — Name" headers found (heading format may have changed)');
    return { ok: true, phases };
  } catch (e) {
    return { ok: false, error: String((e && e.message) || e) };
  }
}

// datasheets/evidence-log.md — just a scale count.
function parseEvidenceLog(text) {
  try {
    const matches = text.match(/^\|\s*DS-[A-Z]+-\d+/gim) || [];
    return { ok: true, count: matches.length };
  } catch (e) {
    return { ok: false, error: String((e && e.message) || e) };
  }
}

// ---- orchestration ----------------------------------------------------------

async function fetchText(path) {
  const res = await fetch(RAW_BASE + path, { cache: 'no-store' });
  if (!res.ok) throw new Error('HTTP ' + res.status + ' fetching ' + path);
  return res.text();
}

async function loadDashboardData() {
  const keys = Object.keys(SOURCES);
  const settled = await Promise.allSettled(keys.map(k => fetchText(SOURCES[k])));
  const texts = {};
  const fetchErrors = {};
  keys.forEach((k, idx) => {
    const r = settled[idx];
    if (r.status === 'fulfilled') texts[k] = r.value;
    else fetchErrors[k] = String((r.reason && r.reason.message) || r.reason);
  });

  const missing = (k) => ({ ok: false, error: fetchErrors[k] ? ('Fetch failed: ' + fetchErrors[k]) : 'Fetch failed' });

  return {
    fetchedAt: new Date(),
    fetchErrors,
    sourcePaths: SOURCES,
    componentSelection: texts.componentSelection ? parseComponentSelection(texts.componentSelection) : missing('componentSelection'),
    openIssues: texts.openIssues ? parseOpenIssues(texts.openIssues) : missing('openIssues'),
    changeLog: texts.changeLog ? parseChangeLog(texts.changeLog) : missing('changeLog'),
    traceability: texts.traceability ? parseTraceability(texts.traceability) : missing('traceability'),
    mechanicalInterface: texts.mechanicalInterface ? parseMechanicalInterface(texts.mechanicalInterface) : missing('mechanicalInterface'),
    requirements: texts.requirements ? parseRequirements(texts.requirements) : missing('requirements'),
    phases: texts.workflow ? parsePhases(texts.workflow) : missing('workflow'),
    evidenceLog: texts.evidenceLog ? parseEvidenceLog(texts.evidenceLog) : missing('evidenceLog'),
  };
}

window.loadDashboardData = loadDashboardData;
window.dashboardUtils = { truncate, escapeHtml };
