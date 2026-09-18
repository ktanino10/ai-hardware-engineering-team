(function (root) {
  'use strict';
  const labels = {
    structure: '筐体フレーム', panel: '外装パネル', motor: 'モーター参照外形', wheel: 'ホイール参照外形',
    pcb: '保存時点の基板／実装形状', equipment: '機器外形', carrier: '支持部', guide: 'ガイド',
    clamp: 'クリップ／保持部', retention_cap: '保持キャップ', retention_liner: 'ライナー',
    new_print: 'カセット支持形状', hardware: '締結外形', rotating_hardware: '回転部締結外形',
    retention_hardware: '保持締結外形',
  };
  function name(part) { return `${labels[part.kind] || '予約・ゲージ・参照外形'} · ${part.id}`; }
  function displacement(part) {
    if (part.id === 'FRAME_LOWER') return [0, 0, -100];
    if (part.id === 'FRAME_UPPER') return [0, 0, 100];
    return part.bounds_mm[0].map((v, i) => (v + part.bounds_mm[1][i]) * 0.55);
  }
  function offset(part, amount) {
    if (!Number.isFinite(amount) || amount < 0 || amount > 1) throw new Error('Invalid presentation amount');
    return amount === 0 ? [0, 0, 0] : displacement(part).map(v => v * amount);
  }
  function step(state, dt) {
    let phase = state.phase;
    if (state.playing) phase = (phase + dt / 4) % 2;
    return { ...state, phase, explode: state.playing ? 1 - Math.abs(1 - phase) : state.explode,
      yaw: state.autoOrbit ? state.yaw + dt * Math.PI / 12 : state.yaw };
  }
  async function unpackEdges(scene, data) {
    if (data.scene_sha256 !== '8f55ba45dcd688c0253ec7c81628ce0ccedf7cedd79e7752191f2d8978eeedd0' ||
      data.parts.length !== scene.components.length) throw new Error('Edge source binding mismatch');
    const bytes = Uint8Array.from(atob(data.payload), c => c.charCodeAt(0));
    const buffer = await new Response(new Blob([bytes]).stream().pipeThrough(new DecompressionStream('gzip'))).arrayBuffer();
    const hash = Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256', buffer)), n => n.toString(16).padStart(2, '0')).join('');
    if (hash !== data.payload_sha256 || buffer.byteLength !== data.payload_bytes) throw new Error('Edge payload integrity mismatch');
    const view = new DataView(buffer), result = new Map(), projections = new Map();
    let end = 0;
    const read = item => {
      if (item.offset !== end || !Number.isInteger(item.coordinate_count) || item.coordinate_count < 0 ||
        item.coordinate_count !== item.edge_count * 6) throw new Error('Edge range mismatch');
      end += item.coordinate_count * 8;
      if (end > buffer.byteLength) throw new Error('Edge range exceeds payload');
      const coords = new Float64Array(item.coordinate_count);
      for (let i = 0; i < coords.length; i++) {
        coords[i] = view.getFloat64(item.offset + i * 8, true);
        if (!Number.isFinite(coords[i])) throw new Error('Invalid source edge');
      }
      return coords;
    };
    data.parts.forEach((item, index) => {
      const part = scene.components[index];
      if (item.id !== part.id || item.source_sha256 !== part.sha256 || item.offset !== end ||
        item.coordinate_count !== item.edge_count * 6) throw new Error('Edge inventory mismatch');
      result.set(item.id, read(item));
      if (item.projection_extras?.length !== 3) throw new Error('Missing reference projections');
      projections.set(item.id, item.projection_extras.map((projection, i) => {
        if (projection.view_axis !== 'YXZ'[i]) throw new Error('Reference projection axis mismatch');
        return read(projection);
      }));
    });
    if (end !== buffer.byteLength) throw new Error('Unconsumed edge data');
    return { edges: result, projections };
  }
  root.Rev5Features = { name, displacement, offset, step, unpackEdges };
})(globalThis);
