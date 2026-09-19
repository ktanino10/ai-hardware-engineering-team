import { readFile } from 'node:fs/promises';
import { createHash, webcrypto } from 'node:crypto';
import vm from 'node:vm';
import assert from 'node:assert/strict';
import { test } from 'node:test';

const context = vm.createContext({ crypto: webcrypto, TextEncoder });
for (const name of ['plan-data.js', 'media-data.js', 'media.js']) {
  vm.runInContext(await readFile(new URL(name, import.meta.url), 'utf8'), context);
}
const plan = JSON.parse(context.REV5_PLAN_SOURCE.text);
const source = context.REV5_MEDIA_SOURCE;
const api = context.Rev5Media;
const data = await api.load(source, plan, context.REV5_PLAN_SOURCE.sha256);
function changed(edit) {
  const copy = JSON.parse(source.text);
  edit(copy);
  const text = JSON.stringify(copy);
  return { text, sha256: createHash('sha256').update(text).digest('hex') };
}

test('canonical portable metadata and file-mode wrapper have identical bytes', async () => {
  const bytes = await readFile(new URL('media-manifest.json', import.meta.url));
  assert.equal(bytes.toString(), source.text);
  assert.equal(createHash('sha256').update(bytes).digest('hex'), source.sha256);
  assert.equal(data.clips.length, 6);
  for (const clip of data.clips) {
    for (const asset of [clip.video, clip.poster]) {
      assert.equal(createHash('sha256').update(await readFile(new URL(asset.path, import.meta.url))).digest('hex'), asset.sha256);
    }
  }
});

test('every source ID maps only to its actual containing movie, never a made-up per-part clip', () => {
  const counts = { unit: 0, whole: 0, none: 0 };
  for (const member of plan.members) {
    const relation = api.related(data, plan, member.id);
    if (!relation) {
      counts.none++;
      assert.equal(member.nonphysical_reference, true);
    } else {
      counts[relation.dedicatedUnit ? 'unit' : 'whole']++;
      assert.ok(api.members(relation.clip, plan).includes(member.id));
      if (relation.dedicatedUnit) assert.equal(relation.clip.unit, member.unit);
    }
  }
  assert.deepEqual(counts, { unit: 66, whole: 233, none: 100 });
  for (const axis of ['X', 'Y', 'Z']) {
    assert.equal(api.related(data, plan, `${axis}_motor`).clip.id, `unit-${axis}`);
    assert.equal(api.related(data, plan, `${axis}_front_screw_1`).clip.id, `unit-${axis}`);
  }
  assert.equal(api.related(data, plan, 'FRAME_LOWER').clip.id, 'whole-interior');
  assert.equal(api.related(data, plan, 'PRINT_panel_X_minus').clip.id, 'whole-exterior');
  assert.throws(() => api.related(data, plan, 'not-a-source-id'), /Unknown source identity/);
});

test('metadata validation rejects corrupt bindings, missing clips and external or escaped media paths', async () => {
  const load = input => api.load(input, plan, context.REV5_PLAN_SOURCE.sha256);
  await assert.rejects(load({ ...source, sha256: '0'.repeat(64) }), /SHA-256/);
  await assert.rejects(load(changed(value => { value.source_plan_sha256 = '0'.repeat(64); })), /source/);
  await assert.rejects(load(changed(value => { value.clips.pop(); })), /coverage/);
  await assert.rejects(load(changed(value => { value.clips[3].unit = 'axis-Y'; })), /membership/);
  for (const path of ['../v2/movie.mp4', 'https://example.invalid/movie.mp4', 'media/../movie.mp4']) {
    await assert.rejects(load(changed(value => { value.clips[0].video.path = path; })), /local media/);
  }
});

test('original timing and camera differences are preserved rather than normalized', () => {
  for (const clip of data.clips.slice(0, 2)) {
    assert.equal(clip.video.frames, 72);
    assert.equal(clip.video.duration_seconds, 6);
    assert.equal(clip.projection, 'perspective');
    assert.equal(clip.camera_rotation_degrees, 360);
  }
  for (const clip of data.clips.slice(2)) {
    assert.equal(clip.video.frames, 145);
    assert.deepEqual(Array.from(clip.video.source_clock_seconds), [0, 12]);
    assert.equal(clip.projection, 'orthographic');
    assert.equal(clip.camera_rotation_degrees, clip.unit ? 180 : 0);
    assert.equal(clip.video.packet_timing.packet_duration_seconds_exact, '145/12');
  }
  const z = data.clips.find(clip => clip.id === 'unit-Z').video;
  assert.equal(z.duration_seconds, 12.083008);
  assert.equal(z.packet_timing.stream_minus_packet_end_ticks, -4);
  assert.equal(z.packet_timing.packet_end_ticks, 148480);
  assert.equal(z.packet_timing.stream_duration_ticks, 148476);
});
