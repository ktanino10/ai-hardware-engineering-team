import { readFile } from 'node:fs/promises';
import { webcrypto } from 'node:crypto';
import vm from 'node:vm';
import assert from 'node:assert/strict';
import { test } from 'node:test';

const c = vm.createContext({ crypto: webcrypto, TextEncoder, atob, Blob, Response, DecompressionStream });
for (const name of ['scene-data.js', 'plan-data.js', 'edge-data.js', 'features.js', 'drawings.js']) {
  vm.runInContext(await readFile(new URL(name, import.meta.url), 'utf8'), c);
}
const f = c.Rev5Features, s = c.REV5_FULL_SCENE;
const plan = await f.loadPlan(c.REV5_PLAN_SOURCE, s);
const part = id => s.components.find(p => p.id === id);
const state = { detailUnit: 'axis-X', isolated: false };

test('exact zero, stationary reserves and no mutation of all399 source poses', () => {
  const before = JSON.stringify(s);
  for (const p of s.components) {
    assert.ok(f.offset(p, 0, state).every(v => v === 0));
    assert.ok(f.offset(p, 1, { ...state, isolated: true }).every(v => v === 0));
  }
  for (const m of plan.members.filter(m => m.nonphysical_reference)) {
    for (const a of [0, .1, .3, .45, .7, 1]) assert.ok(f.offset(part(m.id), a, state).every(v => v === 0));
  }
  assert.equal(JSON.stringify(s), before);
});

test('stages hold all future groups; associated small objects travel together', () => {
  for (const group of plan.groups.filter(g => g.stage !== null)) {
    const [start, end] = plan.stages[group.stage].range;
    for (const id of group.members) {
      assert.ok(f.offset(part(id), start, state).every(v => v === 0), id);
      assert.deepEqual(Array.from(f.offset(part(id), end, state)), Array.from(group.offset_mm));
    }
  }
  assert.ok(f.offset(part('ALLOC_panel_screw_X_minus_1'), .1, state).some(v => v !== 0));
  assert.ok(f.offset(part('PRINT_panel_X_minus'), .1, state).every(v => v === 0));
  assert.ok(f.offset(part('X_front_screw_1'), .5, state).every(v => v === 0));
  for (const amount of [.15, .25, .35, 1]) {
    const screw = f.offset(part('ALLOC_panel_screw_X_minus_1'), amount, state);
    const panel = f.offset(part('PRINT_panel_X_minus'), amount, state);
    assert.ok(Math.abs(screw[0]-panel[0]+22)<1e-10);
  }
});

test('only selected unit members separate at final stage; source board not split', () => {
  assert.notDeepEqual(Array.from(f.offset(part('X_motor'), 1, state)), Array.from(f.offset(part('X_wheel'), 1, state)));
  assert.deepEqual(Array.from(f.offset(part('Y_motor'), 1, state)), Array.from(f.offset(part('Y_front_screw_1'), 1, state)));
  assert.deepEqual(Array.from(f.offset(part('U101'), 1, { detailUnit: 'pcb' })), Array.from(f.offset(part('PCB_A76_laminate'), 1, { detailUnit: 'pcb' })));
  const base = { phase: 0, explode: 0, yaw: 0, playing: true, autoOrbit: false };
  assert.equal(f.step(base, 12).explode, 1);
  assert.equal(f.step(f.step(base, 12), 12).explode, 0);
});

test('source-bound plan rejects missing integrity or source identity', async () => {
  await assert.rejects(f.loadPlan({ ...c.REV5_PLAN_SOURCE, sha256: '0'.repeat(64) }, s), /SHA-256/);
  await assert.rejects(f.loadPlan(c.REV5_PLAN_SOURCE, { ...s, payload_sha256: '0'.repeat(64) }), /source mismatch/);
});

test('unchanged edge data still generates all399 three-view source sheets', async () => {
  const { edges, projections } = await f.unpackEdges(s, c.REV5_EDGES);
  for (const p of s.components) {
    const svg = c.Rev5Drawings.sheet(p, edges.get(p.id), s, projections.get(p.id));
    assert.equal((svg.match(/data-view=/g) || []).length, 3);
    assert.ok(svg.includes(p.sha256) && svg.includes('NOT FOR FABRICATION'));
  }
});
