/*
 * dashboard-i18n.js — bilingual (EN/JA) UI-chrome toggle for this dashboard
 * ONLY (the site's other two viewers stay English-only, per an earlier,
 * explicit user preference recorded in circuit-viewer/README.md — this
 * file does not touch them).
 *
 * Split, agreed with the human Chief Engineer before implementing:
 *   - TRANSLATED: chrome text authored for this dashboard itself — titles,
 *     section headings, buttons, template sentences, my own badge labels
 *     (e.g. "COMPONENT", "SOFT SIGNAL"), stat/fact labels, footnotes, and
 *     error-fallback messages.
 *   - NEVER TRANSLATED, in either language: anything fetched and parsed
 *     from this repository's own files (component-selection.md decision
 *     text, finding titles, ECO revision/changed text, self-reported
 *     status lines, phase names from workflow.md, requirement counts),
 *     PLUS this project's own defined governance vocabulary — severity
 *     (CRITICAL/HIGH/MEDIUM/LOW), status (OPEN/RESOLVED/ACCEPTED-RISK),
 *     and priority (Must/Should/Could/Won't) — since these are precise
 *     terms-of-art defined in docs/architecture.md §7.1/§8 and appear
 *     verbatim in the source files; a translated gloss risks exactly the
 *     mistranslation/meaning-shift concern this split was requested to
 *     avoid. Also never translated: IDs (ISS-005, ECO-068, REQ-021),
 *     file paths, and "Rev N"/"Phase N" designators.
 *
 * Every STRINGS entry is a {en, ja} pair — either a plain string, or a
 * function of the same shape when the sentence needs an interpolated
 * value (kept as a function per language, not string-concatenation,
 * because EN and JA word order around a number often differs).
 */

const STRINGS = {
  title_suffix: { en: 'Project Dashboard', ja: 'プロジェクトダッシュボード' },
  subtitle_bold: { en: 'A live view, not a snapshot.', ja: 'スナップショットではなく、ライブビューです。' },
  subtitle_body_1: {
    en: "Every number below is fetched directly from this repository's own requirements, findings, change-log, and mechanical-interface files on",
    ja: '以下の数値はすべて、ページ読み込み時にこのリポジトリ自身の requirements・findings・change-log・mechanical-interface ファイル（',
  },
  subtitle_body_2: {
    en: 'at page load, and re-parsed in your browser — nothing here is generated ahead of time or committed to git.',
    ja: '）から直接取得し、ブラウザ内で再解析したものです。事前に生成したりgitにコミットしたりしたものは一切ありません。',
  },
  refresh_btn: { en: '⟳ Refresh', ja: '⟳ 更新' },
  back_link: { en: '← back', ja: '← 戻る' },
  src_prefix: { en: 'from', ja: '取得元:' },

  pending_title: { en: 'Pending Human Decisions', ja: '保留中の人間による判断' },
  phases_title: { en: 'Phase / Process Pipeline', ja: 'フェーズ／プロセスパイプライン' },
  findings_title: { en: 'Findings & Quality Snapshot', ja: '課題・品質スナップショット' },
  requirements_title: { en: 'Requirements Snapshot', ja: '要件スナップショット' },
  activity_title: { en: 'Recent Activity', ja: '最近のアクティビティ' },
  mechanical_title: { en: 'Electrical & Mechanical Snapshot', ja: '電気・機構スナップショット' },
  agentorg_title: { en: 'AI Agent Organization', ja: 'AIエージェント組織図' },
  featuremap_title: { en: 'GitHub Feature Map', ja: 'GitHub機能マップ' },

  // ---- AI Agent Organization ----
  // Group labels: chrome I author for this page's own curated grouping
  // (docs/architecture.md §3) — translated. Everything shown INSIDE a
  // group (role/description/relationship lines) is live agent content —
  // never translated, per this file's general split above.
  group_label_electronics: { en: 'Electronics', ja: 'エレクトロニクス' },
  group_label_mechanical: { en: 'Mechanical', ja: 'メカニカル' },
  group_label_firmware: { en: 'Firmware', ja: 'ファームウェア' },
  group_label_cross: { en: 'Cross-discipline', ja: '分野横断' },
  group_label_other: { en: 'Other', ja: 'その他' },

  agentorg_reports_to: { en: '↑ Reports to:', ja: '↑ 報告先:' },
  agentorg_reports_to_human: { en: '↑ Reports to (human):', ja: '↑ 報告先（人間）:' },
  agentorg_delegates_to: { en: '↓ Delegates to:', ja: '↓ 委任先:' },
  agentorg_handoff_from: { en: '← Receives from:', ja: '← 引き継ぎ元:' },
  agentorg_handoff_to: { en: '→ Hands off to:', ja: '→ 引き継ぎ先:' },
  agentorg_skill_tag: { en: 'Skill:', ja: 'スキル:' },
  agentorg_summary: {
    en: (total, groups) => `${total} agent profiles, live-parsed from .github/agents/*.agent.md, organized into ${groups} groups below.`,
    ja: (total, groups) => `.github/agents/*.agent.md からライブ解析した ${total} 件のエージェントプロファイルを、以下の ${groups} グループに分けて表示しています。`,
  },
  agentorg_file_errors: {
    en: (n) => `${n} agent file${n === 1 ? '' : 's'} could not be fetched/parsed — see directly:`,
    ja: (n) => `${n}件のエージェントファイルを取得・解析できませんでした — 直接ご確認ください:`,
  },
  agentorg_footnote: {
    en: 'Which discipline each card is grouped under, and its position within that row, is curated by this page (matching docs/architecture.md §3) for readability. Everything else on every card — role, description, and every "Reports to / Delegates to / Receives from / Hands off to" line — is fetched live from that agent\'s own .agent.md frontmatter on every page load; a line only appears if that field is actually present in the source file.',
    ja: 'どのカードをどの分野グループに含めるか、およびその行内での並び順は、読みやすさのためにこのページが（docs/architecture.md §3に沿って）あらかじめ決めたものです。それ以外のカードの内容 — role・description、および「報告先／委任先／引き継ぎ元／引き継ぎ先」の各行 — は、ページ読み込みのたびにそのエージェント自身の .agent.md frontmatterからライブ取得したものです。該当フィールドが実際にソースファイルに存在する場合のみ、その行が表示されます。',
  },
  err_label_agent_org: { en: 'the AI agent organization', ja: 'AIエージェント組織図' },

  // ---- GitHub Feature Map ----
  badge_live: { en: 'LIVE', ja: 'ライブ' },
  badge_static_confirmed: {
    en: (date) => `STATIC — confirmed ${date} via authenticated API`,
    ja: (date) => `静的 — ${date}時点、認証済みAPIで確認`,
  },
  badge_static_note: { en: 'STATIC — design note', ja: '静的 — 設計メモ' },
  featuremap_live_intro: {
    en: "Fetched live from this repository's own .github/ configuration (GitHub Contents API for directory listings + the same raw-file fetch used throughout this page) on every page load:",
    ja: 'このリポジトリ自身の .github/ 設定から、ページ読み込みのたびにライブ取得したものです（ディレクトリ一覧はGitHub Contents API、ファイル内容はこのページ全体で使用しているものと同じraw取得）:',
  },
  featuremap_col_feature: { en: 'Feature', ja: '機能' },
  featuremap_col_count: { en: 'Live count', ja: 'ライブ件数' },
  featuremap_col_detail: { en: 'Detail', ja: '詳細' },
  featuremap_row_agents_detail: { en: 'agent profiles (see AI Agent Organization above)', ja: 'エージェントプロファイル（上記のAIエージェント組織図を参照）' },
  featuremap_row_skills_detail: { en: 'skill directories (one per .github/skills/<name>/SKILL.md)', ja: 'スキルディレクトリ（.github/skills/<name>/SKILL.md ごとに1件）' },
  featuremap_row_prompts_detail: { en: 'reusable prompt files', ja: '再利用可能なプロンプトファイル' },
  featuremap_row_instructions_detail: { en: 'path-scoped instruction files', ja: 'パス指定のinstructionファイル' },
  featuremap_row_codeowners_detail: { en: 'protected paths (non-comment, non-blank lines)', ja: '保護パス（コメント・空行を除く行数）' },
  featuremap_fetch_failed: { en: 'fetch failed', ja: '取得失敗' },
  featuremap_workflows_suffix: {
    en: (n) => `— ${n} workflow${n === 1 ? '' : 's'}, parsed live (name + trigger types)`,
    ja: (n) => `— ${n}件のワークフローをライブ解析（name + トリガー種別）`,
  },
  err_label_feature_map: { en: 'the GitHub Feature Map workflow list', ja: 'GitHub機能マップのワークフロー一覧' },
  featuremap_static_intro: {
    en: (date) => `Confirmed via authenticated GitHub API as of ${date} — these are repository-admin-only settings and can't be verified live from this (unauthenticated) page. Check the current setting yourself:`,
    ja: (date) => `${date}時点、認証済みGitHub APIで確認済みです — これらはリポジトリ管理者のみが参照できる設定のため、このページ（未認証）からライブに検証することはできません。実際の設定は以下からご自身でご確認ください:`,
  },
  featuremap_link_branches: { en: 'Settings → Branches', ja: '設定 → Branches' },
  featuremap_link_security: { en: 'Settings → Code security', ja: '設定 → Code security' },
  featuremap_link_pages: { en: 'Settings → Pages', ja: '設定 → Pages' },
  featuremap_static_note_intro: {
    en: 'Not gated by authentication — but expressed here as a summary of an observed convention, not a single live-fetched number. Cross-check against the Findings & Recent Activity sections above.',
    ja: '認証は必要ありませんが、単一のライブ取得値ではなく、観察された運用慣習の要約として記載しています。上記のFindings・Recent Activityセクションと突き合わせてご確認ください。',
  },
  featuremap_link_pulls: { en: 'View Pull Requests', ja: 'Pull Requestsを見る' },

  footer_1: {
    en: 'Data sources (fetched live from',
    ja: 'データソース（ページ読み込みのたびに',
  },
  footer_2: {
    en: "on every page load — GitHub's raw-content CDN may serve a cache up to a few minutes old):",
    ja: 'からライブ取得 — GitHubのraw-content CDNは数分程度キャッシュされた内容を返す場合があります）:',
  },
  footer_3: { en: 'This page never writes anything back to the repository.', ja: 'このページはリポジトリに一切書き込みを行いません。' },

  loading: { en: 'Loading live data from GitHub…', ja: 'GitHubからライブデータを読み込み中…' },
  fetch_ok: {
    en: (total, time) => `All ${total} source files fetched live. Last updated ${time}.`,
    ja: (total, time) => `${total}件のソースファイルをすべてライブ取得しました。最終更新: ${time}。`,
  },
  fetch_partial: {
    en: (ok, total, failed, time) => `Fetched ${ok}/${total} source files (${failed} failed — affected sections show a fallback link below). Last attempt ${time}.`,
    ja: (ok, total, failed, time) => `${total}件中${ok}件のソースファイルを取得しました（${failed}件失敗 — 影響を受けたセクションには代替リンクを表示します）。最終試行: ${time}。`,
  },
  fetch_fail: {
    en: (msg) => `Failed to load live data: ${msg}`,
    ja: (msg) => `ライブデータの読み込みに失敗しました: ${msg}`,
  },

  all_clear_title: { en: '✓ Nothing currently blocking a human decision', ja: '✓ 現在、人間の判断を妨げているものはありません' },
  all_clear_detail: {
    en: (a, b) => `${a} pending component/subsystem approvals, ${b} open CRITICAL/HIGH findings.`,
    ja: (a, b) => `保留中のコンポーネント／サブシステム承認 ${a} 件、未解決の CRITICAL/HIGH findings ${b} 件。`,
  },
  tag_component: { en: 'COMPONENT', ja: 'コンポーネント' },
  tag_soft: { en: 'SOFT SIGNAL', ja: '参考シグナル' },
  soft_explain: {
    en: 'Heading marked "pending confirmation" with no later lettered follow-up section found yet in requirements.md — may already be answered elsewhere; not asserted as definitely still open.',
    ja: 'requirements.md内で "pending confirmation" と記載された見出しのうち、後続のレター付きセクションがまだ見つからないものです。他の箇所で既に回答されている可能性があり、確実に未解決とは断定していません。',
  },
  approved_summary: {
    en: (a, total) => `${a} of ${total} component/subsystem decisions already approved.`,
    ja: (a, total) => `コンポーネント／サブシステムの判断 ${total} 件中 ${a} 件が承認済みです。`,
  },

  badge_pending: { en: (n) => `${n} pending`, ja: (n) => `${n}件保留` },
  badge_clear: { en: 'clear', ja: '解消済み' },
  phase_label: { en: (n) => `Phase ${n}`, ja: (n) => `フェーズ ${n}` },
  phase_footnote: {
    en: 'Each document above keeps its own independent revision counter for its own scope — they don\'t line up 1:1 project-wide, so no single "Rev N / current phase" is asserted here on purpose. The badges and self-reported lines are each pulled live from their own source file instead.',
    ja: '上記の各ドキュメントは、それぞれ独自の改訂カウンタをそれぞれのスコープで保持しており、プロジェクト全体で1対1には対応していません。そのため、単一の「Rev N／現在のフェーズ」はあえて断定していません。バッジと自己申告のステータス行は、それぞれの元ファイルからライブで取得したものです。',
  },

  stat_ecos: { en: 'ECOs', ja: 'ECO件数' },
  stat_findings: { en: 'Findings (ISS+MISS)', ja: 'Findings件数 (ISS+MISS)' },
  stat_evidence: { en: 'Evidence IDs (DS)', ja: 'Evidence ID件数 (DS)' },
  gate_check_intro_1: { en: 'Design Complete Gate conditions (', ja: 'Design Complete Gate の条件（' },
  gate_check_intro_2: {
    en: ") — counts are cumulative across this file's whole history, not scoped to one revision:",
    ja: '）: 件数はこのファイルの全履歴の累積であり、特定のリビジョンに限定されていません:',
  },
  gate_cond_critical: {
    en: (n) => `Zero unresolved CRITICAL findings (currently ${n} open)`,
    ja: (n) => `未解決の CRITICAL findings がゼロであること（現在 ${n} 件が OPEN）`,
  },
  gate_cond_high: {
    en: (n) => `Every HIGH finding RESOLVED or ACCEPTED-RISK (currently ${n} open)`,
    ja: (n) => `すべての HIGH findings が RESOLVED または ACCEPTED-RISK であること（現在 ${n} 件が OPEN）`,
  },
  gate_cond_trace: {
    en: (a, total, pending) => `Traceability matrix 100% Verified/Waived (currently ${a} of ${total}; ${pending} Pending)`,
    ja: (a, total, pending) => `Traceability matrix が 100% Verified/Waived であること（現在 ${total} 件中 ${a} 件；${pending} 件が Pending）`,
  },
  gate_na: {
    en: "FMEA-reviewed and a signed change-log entry aren't tracked on this dashboard —",
    ja: 'FMEAレビュー済みかどうか、および署名済みchange-logエントリの有無は、このダッシュボードでは追跡していません —',
  },

  req_total: { en: (n) => `${n} total requirement rows, across every section`, ja: (n) => `全セクション合計で ${n} 件の要件行` },
  req_footnote: {
    en: 'Tagged by the literal "*(Rev N)*" marker on each requirement ID — a requirement with no tag was carried forward unchanged from Rev 1/2.',
    ja: '各要件IDに付与された "*(Rev N)*" という表記でタグ付けしています — タグの無い要件は Rev 1/2 からそのまま引き継がれたものです。',
  },

  activity_note: {
    en: (recent, total) => `Most recent ${recent} of ${total} total ECOs — shown in document order (= chronological authorship order). The "Date" column itself is known to be non-monotonic in places, per this project's own ISS-056 finding, so it is not used for sorting.`,
    ja: (recent, total) => `全 ${total} 件の ECO のうち、直近の ${recent} 件を表示しています（ドキュメント上の並び順＝執筆順）。"Date" 列自体は一部で時系列通りでないことがこのプロジェクト自身の ISS-056 で指摘されているため、並び替えには使用していません。`,
  },

  viewer_circuit_title: { en: 'Circuit & Current-Flow Viewer', ja: '回路・電流フロービューア' },
  viewer_circuit_desc: {
    en: 'Interactive block diagram of power distribution and real (bench-mode) current behavior, built from the real schematic, netlist, and firmware source. Click any component or wire.',
    ja: '実際の回路図・ネットリスト・ファームウェアのソースから作成した、電源分配と実際の（ベンチモード）電流挙動のインタラクティブなブロック図です。任意のコンポーネントやワイヤーをクリックできます。',
  },
  viewer_assembly_title: { en: '3D Assembly & Part Inspector', ja: '3Dアセンブリ・部品インスペクタ' },
  viewer_assembly_desc: {
    en: 'Real mechanical geometry (KiCad PCB export + OpenSCAD-derived STL parts) as an orbit-and-click exploded assembly. No plugin required.',
    ja: '実際の機構ジオメトリ（KiCad PCBエクスポート＋OpenSCAD由来のSTLパーツ）を、回転・クリック操作可能な分解図として表示します。プラグイン不要です。',
  },
  fact_board: { en: 'Board outline', ja: '基板外形' },
  fact_holes: { en: 'Mounting holes', ja: '取付穴' },

  err_label_component: { en: 'component approval status', ja: 'コンポーネント承認状況' },
  err_label_findings_open: { en: 'open findings', ja: '未解決のfindings' },
  err_label_phase_pipeline: { en: 'the phase pipeline', ja: 'フェーズパイプライン' },
  err_label_findings_backlog: { en: 'the findings backlog', ja: 'findingsバックログ' },
  err_label_req_priorities: { en: 'requirement priorities', ja: '要件の優先度' },
  err_label_changelog: { en: 'the change log', ja: 'change log' },
  err_label_mechanical: { en: 'live mechanical facts', ja: '機構情報' },
  err_message: {
    en: (label, path) => `Couldn't parse ${label} — <a href="https://github.com/ktanino10/ai-hardware-engineering-team/blob/main/${path}" target="_blank" rel="noopener">see ${path} directly ↗</a>`,
    ja: (label, path) => `${label}を解析できませんでした — <a href="https://github.com/ktanino10/ai-hardware-engineering-team/blob/main/${path}" target="_blank" rel="noopener">${path} を直接ご確認ください ↗</a>`,
  },
};

const LANG_STORAGE_KEY = 'dashboardLang';

function detectInitialLang() {
  try {
    const saved = window.localStorage.getItem(LANG_STORAGE_KEY);
    if (saved === 'en' || saved === 'ja') return saved;
  } catch (e) { /* localStorage unavailable (private browsing etc.) — fall through to default */ }
  return 'en';
}

let currentLang = detectInitialLang();

function t(key, ...args) {
  const entry = STRINGS[key];
  if (!entry) return key; // defensive: an unknown key shows itself rather than throwing
  const v = entry[currentLang] || entry.en;
  return typeof v === 'function' ? v(...args) : v;
}

function setText(id, value) {
  const el = document.getElementById(id);
  if (el) el.textContent = value;
}

function applyStaticChrome() {
  document.documentElement.lang = currentLang;
  document.querySelectorAll('.lang-toggle button').forEach(b => {
    b.classList.toggle('active', b.dataset.lang === currentLang);
  });

  setText('i18n-title-suffix', t('title_suffix'));
  setText('i18n-subtitle-bold', t('subtitle_bold'));
  setText('i18n-subtitle-body-1', t('subtitle_body_1'));
  setText('i18n-subtitle-body-2', t('subtitle_body_2'));
  setText('refresh-btn', t('refresh_btn'));
  setText('i18n-back-link', t('back_link'));
  document.querySelectorAll('.i18n-src-prefix').forEach(el => { el.textContent = t('src_prefix'); });

  setText('i18n-pending-title', t('pending_title'));
  setText('i18n-phases-title', t('phases_title'));
  setText('i18n-findings-title', t('findings_title'));
  setText('i18n-requirements-title', t('requirements_title'));
  setText('i18n-activity-title', t('activity_title'));
  setText('i18n-mechanical-title', t('mechanical_title'));
  setText('i18n-agentorg-title', t('agentorg_title'));
  setText('i18n-featuremap-title', t('featuremap_title'));

  setText('i18n-footer-1', t('footer_1'));
  setText('i18n-footer-2', t('footer_2'));
  setText('i18n-footer-3', t('footer_3'));
}

function setLang(lang) {
  if (lang !== 'en' && lang !== 'ja') return;
  currentLang = lang;
  try { window.localStorage.setItem(LANG_STORAGE_KEY, lang); } catch (e) { /* best-effort persistence only */ }
  applyStaticChrome();
  document.dispatchEvent(new CustomEvent('dashboard-lang-changed', { detail: { lang } }));
}

document.addEventListener('DOMContentLoaded', () => {
  applyStaticChrome();
  document.querySelectorAll('.lang-toggle button').forEach(btn => {
    btn.addEventListener('click', () => setLang(btn.dataset.lang));
  });
});

window.dashboardI18n = { t, setLang, getLang: () => currentLang };
