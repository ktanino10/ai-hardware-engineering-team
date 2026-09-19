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
  let plan, members, groups, units;
  async function loadPlan(source, scene) {
    const hash = Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256', new TextEncoder().encode(source.text))), n => n.toString(16).padStart(2, '0')).join('');
    if (hash !== source.sha256) throw new Error('Presentation plan SHA-256 mismatch');
    const candidate = JSON.parse(source.text);
    if (candidate.source_scene_sha256 !== '8f55ba45dcd688c0253ec7c81628ce0ccedf7cedd79e7752191f2d8978eeedd0' ||
      candidate.source_payload_sha256 !== scene.payload_sha256 || candidate.units !== 'mm' ||
      candidate.component_count !== scene.components.length || candidate.stages.length !== 5 ||
      candidate.physical_permission !== 'NOT_GRANTED') throw new Error('Presentation source mismatch');
    const mm = new Map(candidate.members.map(p => [p.id, p]));
    const gg = new Map(candidate.groups.map(g => [g.id, g]));
    const uu = new Map(candidate.named_units.map(u => [u.id, u]));
    const vector = v => Array.isArray(v) && v.length === 3 && v.every(Number.isFinite);
    if (mm.size !== 399 || candidate.members.length !== 399) throw new Error('Presentation ID coverage mismatch');
    candidate.stages.forEach((s, i) => {
      if (s.range[0] !== (i ? candidate.stages[i-1].range[1] : 0) ||
        s.range[1] <= s.range[0] || s.easing !== 'smoothstep') throw new Error('Invalid stage ranges');
    });
    if (candidate.stages[4].range[1] !== 1) throw new Error('Incomplete stage range');
    const groupIds = candidate.groups.flatMap(g => g.members);
    const unitIds = candidate.named_units.flatMap(u => u.members);
    if (groupIds.length !== 399 || new Set(groupIds).size !== 399 ||
      unitIds.length !== 399 || new Set(unitIds).size !== 399) throw new Error('Duplicate or missing presentation membership');
    for (const p of scene.components) {
      const m = mm.get(p.id), g = gg.get(m?.group), u = uu.get(m?.unit);
      if (!g || !u || m.source_sha256 !== p.sha256 || !g.members.includes(p.id) ||
        !u.members.includes(p.id) || !vector(g.offset_mm) ||
        (g.stage !== null && (!Number.isInteger(g.stage) || g.stage < 0 || g.stage > 3)) ||
        (m.nonphysical_reference && (g.stage !== null || g.offset_mm.some(v => v !== 0)))) throw new Error('Invalid source membership: ' + p.id);
      const details = u.detail_groups.filter(d => d.members.includes(p.id));
      if (details.length !== 1 || !vector(details[0].offset_mm)) throw new Error('Invalid member offset: ' + p.id);
    }
    for (const mode of Object.values(candidate.whole_modes)) {
      const ids = scene.components.filter(p => mode.groups.includes(p.group)).map(p => p.id);
      if (JSON.stringify(ids) !== JSON.stringify(mode.members)) throw new Error('Whole-view membership mismatch');
    }
    for (const group of candidate.groups) {
      if (group.carry_with) {
        const carry = gg.get(group.carry_with);
        if (!carry || carry.carry_with || carry.unit !== group.unit || carry.stage <= group.stage) throw new Error('Invalid staged carry group');
      }
    }
    plan = candidate; members = mm; groups = gg; units = uu;
    root.Rev5Features.plan = plan;
    return plan;
  }
  function weight(index, amount) {
    const [start, end] = plan.stages[index].range;
    const t = Math.max(0, Math.min(1, (amount-start)/(end-start)));
    return t*t*(3-2*t);
  }
  function offset(part, amount, state = {}) {
    if (!Number.isFinite(amount) || amount < 0 || amount > 1) throw new Error('Invalid presentation amount');
    const member = members.get(part.id);
    if (!member) throw new Error('Unmapped presentation identity: ' + part.id);
    if (amount === 0 || state.isolated || member.nonphysical_reference) return [0, 0, 0];
    const group = groups.get(member.group), base = group.offset_mm.map(v => v * weight(group.stage, amount));
    if (group.carry_with) {
      const carry = groups.get(group.carry_with);
      base.forEach((v, i) => { base[i] = v + carry.offset_mm[i]*weight(carry.stage, amount); });
    }
    if (state.detailUnit === member.unit) {
      const detail = units.get(member.unit).detail_groups.find(d => d.members.includes(part.id));
      return base.map((v, i) => v + detail.offset_mm[i]*weight(4, amount));
    }
    return base;
  }
  function stage(amount) {
    return amount === 0 ? '0% · 元の組立姿勢' :
      plan.stages.find(s => amount <= s.range[1]).name;
  }
  function step(state, dt) {
    let phase = state.phase;
    if (state.playing) phase = (phase + dt / plan.playback.half_cycle_seconds) % 2;
    return { ...state, phase, explode: state.playing ? 1 - Math.abs(1 - phase) : state.explode,
      yaw: state.autoOrbit ? state.yaw + dt * plan.playback.camera_orbit_radians_per_second : state.yaw };
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
  root.Rev5Features = { name, loadPlan, weight, stage, offset, step, unpackEdges };
})(globalThis);
