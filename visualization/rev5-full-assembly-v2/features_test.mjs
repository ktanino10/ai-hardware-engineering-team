import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import vm from 'node:vm';
import { webcrypto } from 'node:crypto';
import { test } from 'node:test';

const context = vm.createContext({ atob, Blob, Response, DecompressionStream, crypto: webcrypto });
for (const name of ['scene-data.js', 'edge-data.js', 'features.js', 'drawings.js']) {
  vm.runInContext(await readFile(new URL(name, import.meta.url), 'utf8'), context);
}
const { Rev5Features: features, REV5_FULL_SCENE: scene, REV5_EDGES: edges } = context;

test('all399 exact assembled offsets; deterministic non-mutating display displacement', () => {
  const before = JSON.stringify(scene.components);
  for (const part of scene.components) {
    assert.ok(features.offset(part, 0).every(v => v === 0));
    assert.ok(features.offset(part, .5).every((v, i) => v === features.offset(part, 1)[i] / 2));
  }
  assert.equal(JSON.stringify(scene.components), before);
  for (const bad of [-1, 2, NaN]) assert.throws(() => features.offset(scene.components[0], bad));
});

test('triangle-wave animation returns exactly to assembled zero and pause is stable', () => {
  const state = { phase: 0, explode: 0, yaw: 0, playing: true, autoOrbit: false };
  const expanded = features.step(state, 4);
  assert.equal(expanded.explode, 1);
  assert.equal(features.step(expanded, 4).explode, 0);
  assert.equal(features.step({ ...expanded, playing: false }, 100).explode, 1);
  assert.equal(features.step({ ...state, autoOrbit: true }, 1).yaw, Math.PI / 12);
});

test('edge payload validates before all399 reference projections; corrupt binding fails closed', async () => {
  const decoded = await features.unpackEdges(scene, edges);
  assert.equal(decoded.edges.size, 399); assert.equal(decoded.projections.size, 399);
  await assert.rejects(features.unpackEdges(scene, { ...edges, payload_sha256: '0'.repeat(64) }), /integrity/);
  await assert.rejects(features.unpackEdges(scene, { ...edges, scene_sha256: '0'.repeat(64) }), /binding/);
  const parts = edges.parts.map((p, i) => i === 0 ? { ...p, id: 'wrong' } : p);
  await assert.rejects(features.unpackEdges(scene, { ...edges, parts }), /inventory/);
  for (const part of scene.components) {
    const svg = context.Rev5Drawings.sheet(part, decoded.edges.get(part.id), scene, decoded.projections.get(part.id));
    assert.equal((svg.match(/data-view=/g) || []).length, 3);
    assert.ok(svg.includes(part.sha256) && svg.includes('NOT FOR FABRICATION'));
    assert.ok(!svg.includes('NaN'));
  }
});
