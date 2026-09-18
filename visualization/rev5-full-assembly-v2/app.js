(async function () {
  'use strict';
  const byId = id => document.getElementById(id);
  const controls = () => [...document.querySelectorAll('button,input,select')];
  const fail = error => {
    console.error('Rev5 whole assembly:', error);
    byId('error').textContent = '表示できません：' + error.message;
    byId('error').hidden = false; byId('loading').hidden = true;
    byId('visible-count').textContent = '描画エラー';
    controls().forEach(control => { control.disabled = true; });
  };
  try {
    const scene = globalThis.REV5_FULL_SCENE;
    const dependencies = {
      REV5_FULL_SCENE: 'scene-data.js',
      Rev5Whole: 'viewer.js',
      Rev5Interactive: 'interactive-viewer.js',
      REV5_EDGES: 'edge-data.js',
      Rev5Features: 'features.js',
      Rev5Drawings: 'drawings.js',
    };
    const missing = Object.entries(dependencies).filter(([name]) => !globalThis[name])
      .map(([name, file]) => `${file} (${name})`);
    if (missing.length) throw new Error('ローカル JS の依存が読み込めません：' + missing.join('、') + '。同じフォルダー内のファイルを確認してください。');
    const select = byId('part-select');
    const ordered = [...scene.components].sort((a, b) => a.id.localeCompare(b.id));
    const fillParts = query => {
      const matches = ordered.filter(c => c.id.toLowerCase().includes(query.toLowerCase()));
      select.replaceChildren();
      matches.forEach(c => { const option = document.createElement('option'); option.value = c.id; option.textContent = c.id; select.append(option); });
      return matches;
    };
    fillParts('');
    const checks = {};
    Object.entries(scene.groups).forEach(([key, label]) => {
      const wrapper = document.createElement('label'); wrapper.className = 'check';
      const input = document.createElement('input'); input.type = 'checkbox'; input.disabled = true;
      input.dataset.group = key; checks[key] = input;
      wrapper.append(input, `${label} (${scene.group_counts[key]})`); byId('groups').append(wrapper);
    });
    scene.missing_inventory.forEach(gap => {
      const li = document.createElement('li');
      li.textContent = `${gap.id} — ${gap.item} / ${gap.status}。${gap.reason || ''} 担当：${gap.owner}`;
      byId('missing').append(li);
    });
    byId('inventory-count').textContent = `${scene.component_count} 保存メッシュ / ${scene.triangle_count.toLocaleString('ja-JP')} 三角形`;
    byId('source-summary').textContent = `取得コミット ${scene.source_revision} · 文脈ソース ${scene.context_source_revision} · fixed-context SHA-256 ${scene.context_sha256}`;
    let shownId = null;
    const update = state => {
      const component = scene.components.find(c => c.id === state.selected);
      byId('visible-count').textContent = `${state.visibleIds.length} / ${scene.component_count} 形状を表示`;
      byId('selection-status').textContent = `${state.visibleIds.includes(state.selected) ? '表示中' : '非表示のグループ内'} · ${state.isolated ? '単独表示' : '全体表示'} / 外接枠は位置参照（遮蔽未考慮）`;
      for (const [key, input] of Object.entries(checks)) input.checked = state.groups[key];
      byId('show-dimensions').checked = state.dimensions;
      byId('explode').value = String(Math.round(state.explode * 100));
      byId('explode-value').textContent = `${Math.round(state.explode * 100)}%`;
      byId('orbit').setAttribute('aria-pressed', String(state.autoOrbit));
      byId('xray').setAttribute('aria-pressed', String(state.appearance === 'xray'));
      byId('play').disabled = state.reducedMotion; byId('orbit').disabled = state.reducedMotion;
      byId('motion-status').textContent = `${state.playing ? '分解↔組立 再生中' : '分解再生 停止中'} / ${state.autoOrbit ? '旋回中' : '旋回停止'} / ${state.explode ? '分解表示（240 mmは組立時のみ）' : '元の組立姿勢'}${state.reducedMotion ? ' / 動きを減らす設定：連続再生OFF' : ''}`;
      byId('exterior').setAttribute('aria-pressed', String(!state.isolated && state.groups.panels && state.groups.frame));
      byId('interior').setAttribute('aria-pressed', String(!state.isolated && !state.groups.panels && state.groups.frame));
      byId('drive-only').setAttribute('aria-pressed', String(!state.isolated && state.groups.drive && Object.entries(state.groups).every(([k, v]) => k === 'drive' || !v)));
      if (shownId === component.id) return;
      if (![...select.options].some(option => option.value === component.id)) {
        byId('part-search').value = ''; fillParts(''); select.disabled = false;
      }
      shownId = component.id; select.value = component.id;
      byId('part-name').textContent = Rev5Features.name(component); byId('part-role').textContent = component.representation;
      byId('part-source').textContent = component.mesh;
      byId('part-hash').textContent = `STL SHA-256 ${component.sha256}`;
      byId('part-dimensions').replaceChildren();
      component.dimensions_mm.forEach((size, axis) => {
        const cell = document.createElement('div'), label = document.createElement('span'), value = document.createElement('b');
        label.textContent = 'XYZ'[axis] + ' mm'; value.textContent = size.toFixed(2);
        cell.append(label, value); byId('part-dimensions').append(cell);
      });
      currentSheet = Rev5Drawings.show(component, edges.get(component.id), scene, projections.get(component.id));
    };
    let currentSheet = '';
    const { edges, projections } = await Rev5Features.unpackEdges(scene, REV5_EDGES);
    const meshes = await Rev5Whole.unpack(scene);
    const viewer = new Rev5Whole.WholeViewer(byId('whole-canvas'), scene, meshes, edges, update, fail);
    globalThis.rev5FullViewer = viewer;
    globalThis.rev5ReferenceSheet = id => {
      const component = scene.components.find(c => c.id === id);
      if (!component) throw new Error('Unknown source ID');
      return Rev5Drawings.sheet(component, edges.get(id), scene, projections.get(id));
    };
    viewer.onHover = part => {
      const box = byId('hover-info'); box.hidden = !part;
      box.textContent = part ? `${Rev5Features.name(part)}\nID: ${part.id}\nX ${part.dimensions_mm[0].toFixed(2)} / Y ${part.dimensions_mm[1].toFixed(2)} / Z ${part.dimensions_mm[2].toFixed(2)} mm\n${part.representation}\n設置姿勢の外接寸法・製造条件 UNKNOWN` : '';
    };
    controls().forEach(control => { control.disabled = false; });
    byId('loading').hidden = true; update(viewer.getState());
    const patch = changes => viewer.setState({ ...viewer.state, ...changes });
    for (const [key, input] of Object.entries(checks)) input.addEventListener('change', () => patch({ isolated: false, groups: { ...viewer.state.groups, [key]: input.checked } }));
    const mode = name => patch({
      isolated: false,
      groups: Object.fromEntries(Object.keys(scene.groups).map(key => [key,
        name === 'drive' ? key === 'drive' : key !== 'reference' && (key !== 'panels' || name === 'exterior')])),
    });
    byId('exterior').addEventListener('click', () => mode('exterior'));
    byId('interior').addEventListener('click', () => mode('interior'));
    byId('drive-only').addEventListener('click', () => mode('drive'));
    byId('isolate').addEventListener('click', () => patch({ isolated: true }));
    byId('show-dimensions').addEventListener('change', e => patch({ dimensions: e.target.checked }));
    select.addEventListener('change', () => patch({ selected: select.value }));
    byId('part-search').addEventListener('input', event => {
      const matches = fillParts(event.target.value);
      if (!matches.length) {
        byId('selection-status').textContent = '一致するIDがありません。3Dの選択は変更していません。';
        select.disabled = true;
      } else {
        select.disabled = false;
        shownId = null;
        patch({ selected: matches.some(c => c.id === viewer.state.selected) ? viewer.state.selected : matches[0].id });
      }
    });
    document.querySelectorAll('[data-camera]').forEach(button => button.addEventListener('click', () => viewer.preset(button.dataset.camera)));
    byId('reset').addEventListener('click', () => viewer.preset('iso'));
    byId('zoom-in').addEventListener('click', () => viewer.setState(Rev5Interactive.zoomBy(viewer.state, 1.15)));
    byId('zoom-out').addEventListener('click', () => viewer.setState(Rev5Interactive.zoomBy(viewer.state, 1 / 1.15)));
    byId('explode').addEventListener('input', event => {
      const explode = Number(event.target.value) / 100;
      patch({ explode, phase: explode, playing: false });
    });
    byId('play').addEventListener('click', () => { if (!viewer.reducedMotion.matches) patch({ playing: true }); });
    byId('pause').addEventListener('click', () => patch({ playing: false, autoOrbit: false }));
    byId('stop').addEventListener('click', () => viewer.stop());
    byId('orbit').addEventListener('click', () => { if (!viewer.reducedMotion.matches) patch({ autoOrbit: !viewer.state.autoOrbit }); });
    byId('xray').addEventListener('click', () => patch({ appearance: viewer.state.appearance === 'opaque' ? 'xray' : 'opaque' }));
    byId('show-sheet').addEventListener('click', () => byId('sheet-heading').scrollIntoView({ behavior: 'instant' }));
    byId('save-sheet').addEventListener('click', () => Rev5Drawings.save(currentSheet, viewer.state.selected));
  } catch (error) { fail(error); }
})();
