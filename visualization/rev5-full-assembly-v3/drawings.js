(function (root) {
  'use strict';
  const escape = text => String(text).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&apos;' }[c]));
  function sheet(part, edges, scene, projections) {
    if (!edges || !edges.length || edges.length % 6) throw new Error('選択形状の参照線データがありません。');
    if (projections?.length !== 3 || projections.some(lines => lines.length % 6)) throw new Error('参考投影の輪郭データがありません。');
    const size = part.dimensions_mm, scale = 250 / Math.max(...size, 1);
    const views = [
      { label: '正面 / −Y から', horizontal: 0, vertical: 2 },
      { label: '側面 / ＋X から', horizontal: 1, vertical: 2 },
      { label: '上面 / ＋Z から', horizontal: 0, vertical: 1 },
    ];
    const text = (x, y, value, extra = '') => `<text x="${x}" y="${y}" ${extra}>${escape(value)}</text>`;
    const line = (x1, y1, x2, y2) => `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}"/>`;
    let svg = `<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="680" viewBox="0 0 1100 680" role="img" aria-label="${escape(part.id)} 参考三面図" data-part-id="${escape(part.id)}">
      <title>${escape(root.Rev5Features.name(part))} / REF / NOT FOR FABRICATION</title>
      <desc>Frozen installed global XYZ mesh projection. No hidden-line removal, tolerances, material, process, analytic holes or fabrication permission.</desc>
      <rect width="1100" height="680" fill="#fff"/>
      <g font-family="sans-serif" fill="#24333c" font-size="14">
      ${text(28, 34, 'REV5 / REF — NOT FOR FABRICATION', 'font-size="21" font-weight="bold"')}
      ${text(28, 65, root.Rev5Features.name(part), 'font-size="17"')}
      ${text(28, 91, 'X / Y / Z = ' + size.map(v => v.toFixed(3)).join(' / ') + ' mm · 設置姿勢のメッシュ外接寸法')}
      ${text(28, 117, part.representation)}
      ${text(28, 143, '名目参考投影 / 組立0%の元形状 / 分解表示の移動を含まない / 実測・製造データではない')}`;
    views.forEach((view, index) => {
      const { horizontal: h, vertical: v } = view, cx = 190 + index * 360, cy = 320;
      const center = part.bounds_mm[0].map((x, i) => (x + part.bounds_mm[1][i]) / 2);
      let d = '';
      for (const lines of [edges, projections[index]]) {
        for (let i = 0; i < lines.length; i += 6) {
          d += `M${(cx + (lines[i + h] - center[h]) * scale).toFixed(2)},${(cy - (lines[i + v] - center[v]) * scale).toFixed(2)}L${(cx + (lines[i + 3 + h] - center[h]) * scale).toFixed(2)},${(cy - (lines[i + 3 + v] - center[v]) * scale).toFixed(2)}`;
        }
      }
      const halfW = size[h] * scale / 2, halfH = size[v] * scale / 2;
      svg += `<g data-view="${index}">${text(cx, 180, view.label, 'text-anchor="middle" font-weight="bold"')}
        <path d="${d}" fill="none" stroke="#315763" stroke-width="0.65"/>
        <g stroke="#74848b" fill="none" stroke-width="0.8">
        ${line(cx - halfW, 473, cx + halfW, 473)}
        ${line(cx - halfW, 467, cx - halfW, 479)}${line(cx + halfW, 467, cx + halfW, 479)}
        ${line(cx - 148, cy - halfH, cx - 148, cy + halfH)}
        ${line(cx - 154, cy - halfH, cx - 142, cy - halfH)}${line(cx - 154, cy + halfH, cx - 142, cy + halfH)}
        </g>${text(cx, 495, `${'XYZ'[h]} ${size[h].toFixed(3)} mm`, 'text-anchor="middle"')}
        ${text(cx - 160, cy, `${'XYZ'[v]} ${size[v].toFixed(3)} mm`, `text-anchor="middle" transform="rotate(-90 ${cx - 160} ${cy})"`)}
        ${text(cx, 522, `右 ＋${'XYZ'[h]} / 上 ＋${'XYZ'[v]}`, 'text-anchor="middle"')}</g>`;
    });
    svg += `${text(28, 558, `共通表示縮尺 ${scale.toFixed(4)} SVG unit/mm（印刷縮尺の保証なし） / 隠線除去なし・境界/15°稜線/視点輪郭の重畳投影`)}
      ${text(28, 585, `ID ${part.id} · 元STL SHA-256 ${part.sha256}`, 'font-family="monospace" font-size="11"')}
      ${text(28, 609, `Source revision ${scene.source_revision} · snapshot ${scene.snapshot_date}`, 'font-family="monospace" font-size="12"')}
      ${text(28, 635, '参考・ゲージも原IDで表示。公差・材質・工程・解析的穴径 UNKNOWN。現物の保持/干渉/安全/製造の承認なし。')}
      ${text(28, 660, 'WIP / NOT ASSEMBLY READY — PRESENTATION / REFERENCE ONLY', 'font-weight="bold"')}</g></svg>`;
    return svg;
  }
  function show(part, edges, scene, projections) {
    const svg = sheet(part, edges, scene, projections);
    document.getElementById('reference-sheet').innerHTML = svg;
    document.getElementById('sheet-status').textContent = `${part.id} · 参考三面図 / 元の組立姿勢 / REF / NOT FOR FABRICATION`;
    return svg;
  }
  function save(svg, id) {
    const url = URL.createObjectURL(new Blob([svg], { type: 'image/svg+xml' }));
    const link = document.createElement('a');
    link.href = url; link.download = `rev5-${id.replace(/[^a-zA-Z0-9_-]/g, '_')}-REF.svg`;
    link.click(); setTimeout(() => URL.revokeObjectURL(url), 1000);
  }
  root.Rev5Drawings = { sheet, show, save };
})(globalThis);
