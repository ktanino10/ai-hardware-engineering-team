(function (root) {
  'use strict';
  const expectedIds = ['whole-exterior', 'whole-interior', 'outside-first', 'unit-X', 'unit-Y', 'unit-Z'];
  function members(clip, plan) {
    return clip.unit ? plan.named_units.find(unit => unit.id === clip.unit)?.members :
      plan.whole_modes[clip.whole_mode]?.members;
  }
  async function load(source, plan, planHash) {
    const hash = Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',
      new TextEncoder().encode(source.text))), n => n.toString(16).padStart(2, '0')).join('');
    if (hash !== source.sha256) throw new Error('Media metadata SHA-256 mismatch');
    const data = JSON.parse(source.text);
    if (data.schema_version !== 1 || data.source_scene_sha256 !== plan.source_scene_sha256 ||
      data.source_plan_sha256 !== planHash || data.per_part_movie !== false ||
      JSON.stringify(data.clips.map(clip => clip.id)) !== JSON.stringify(expectedIds)) {
      throw new Error('Media source or six-clip coverage mismatch');
    }
    const paths = new Set();
    for (const clip of data.clips) {
      const ids = members(clip, plan);
      if (!ids || ids.length !== clip.member_count ||
        clip.unit !== (clip.id.startsWith('unit-') ? `axis-${clip.id.at(-1)}` : null) ||
        clip.whole_mode !== (clip.unit ? null : clip.id === 'whole-interior' ? 'interior' : 'exterior')) {
        throw new Error('Invalid containing-view membership: ' + clip.id);
      }
      for (const [kind, extension] of [['video', 'mp4'], ['poster', 'png']]) {
        const asset = clip[kind];
        if (!new RegExp(`^media/[A-Za-z0-9-]+\\.${extension}$`).test(asset.path) ||
          !/^[a-f0-9]{64}$/.test(asset.sha256) || paths.has(asset.path)) {
          throw new Error('Invalid local media asset: ' + clip.id);
        }
        paths.add(asset.path);
      }
      const video = clip.video, base = clip.id.startsWith('whole-');
      if (video.fps !== 12 || video.frames !== (base ? 72 : 145) ||
        video.width !== 960 || video.height !== 640 || video.codec !== 'h264' ||
        video.pixel_format !== 'yuv420p' || !Number.isFinite(video.duration_seconds) ||
        video.duration_seconds <= 0 || video.reencoded_in_release !== false) {
        throw new Error('Invalid frozen media metadata: ' + clip.id);
      }
    }
    return data;
  }
  function related(data, plan, id) {
    const member = plan.members.find(item => item.id === id);
    if (!member) throw new Error('Unknown source identity: ' + id);
    const unit = data.clips.find(clip => clip.unit === member.unit && members(clip, plan).includes(id));
    if (unit) return { clip: unit, dedicatedUnit: true };
    for (const clipId of ['whole-interior', 'whole-exterior']) {
      const clip = data.clips.find(item => item.id === clipId);
      if (members(clip, plan).includes(id)) return { clip, dedicatedUnit: false };
    }
    return null;
  }
  function mount(data, plan) {
    const byId = id => document.getElementById(id);
    const video = byId('media-player'), choices = byId('media-choices');
    const buttons = new Map();
    let selected = null, selection = null;
    const show = id => {
      const clip = data.clips.find(item => item.id === id);
      if (!clip) throw new Error('Unknown native clip: ' + id);
      if (selected === id) return;
      video.pause();
      selected = id;
      video.dataset.clipId = id;
      video.poster = clip.poster.path;
      video.src = clip.video.path;
      video.load();
      byId('media-error').hidden = true;
      byId('media-title').textContent = clip.title;
      byId('media-details').textContent = `${clip.video.duration_seconds.toFixed(6)}秒 / ${clip.video.frames}フレーム / ${clip.video.fps} fps / ${clip.camera_label}`;
      byId('media-motion').textContent = clip.motion_label;
      byId('media-source').textContent = `収録 ${data.producer} · MP4 SHA-256 ${clip.video.sha256}`;
      byId('media-timing-note').hidden = id !== 'unit-Z';
      for (const [key, button] of buttons) button.setAttribute('aria-pressed', String(key === id));
      byId('media-file').href = clip.video.path;
      byId('media-file').textContent = `${clip.title} のMP4を開く`;
    };
    for (const clip of data.clips) {
      const button = document.createElement('button');
      button.type = 'button'; button.className = 'media-choice'; button.dataset.clip = clip.id;
      button.disabled = true; button.setAttribute('aria-pressed', 'false');
      button.setAttribute('aria-controls', 'media-player');
      const image = document.createElement('img');
      image.src = clip.poster.path; image.alt = ''; image.loading = 'lazy';
      [image.width, image.height] = clip.poster.dimensions;
      const title = document.createElement('strong'), detail = document.createElement('span');
      title.textContent = clip.title;
      detail.textContent = `${clip.video.frames} frames / ${clip.projection} / ${clip.camera_rotation_degrees}°`;
      button.append(image, title, detail); button.addEventListener('click', () => show(clip.id));
      choices.append(button); buttons.set(clip.id, button);
    }
    video.addEventListener('error', () => {
      const message = `CG動画を読み込めません (${selected}, media error ${video.error?.code ?? 'UNKNOWN'})。MP4と対応する同梱ファイルを確認してください。`;
      byId('media-error').textContent = message; byId('media-error').hidden = false;
      console.error(message);
    });
    document.addEventListener('visibilitychange', () => { if (document.hidden) video.pause(); });
    window.addEventListener('pagehide', () => video.pause());
    byId('related-media').addEventListener('click', () => {
      if (!selection) return;
      show(selection.clip.id);
      byId('media-gallery').scrollIntoView({ block: 'start', behavior: 'instant' });
      video.focus({ preventScroll: true });
    });
    show('whole-exterior');
    return {
      updateSelection(id) {
        selection = related(data, plan, id);
        byId('related-media').disabled = !selection;
        byId('related-media').textContent = selection ? `関連CG：${selection.clip.title}` : 'この参照形状のCG動画はありません';
        byId('related-media-note').textContent = selection ?
          `${id}を含む${selection.dedicatedUnit ? 'ユニット' : '全体'}動画です。${selection.dedicatedUnit ? '' : 'このまとまりの専用動画はありません。'}単体専用のネイティブ動画ではありません。` :
          `${id}は6本の収録対象外です。個別のブラウザー表示・SVG参考図は利用できます。`;
      },
    };
  }
  root.Rev5Media = { load, members, related, mount };
})(globalThis);
