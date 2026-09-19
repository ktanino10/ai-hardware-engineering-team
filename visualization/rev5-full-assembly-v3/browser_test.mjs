import assert from 'node:assert/strict';
import { spawn } from 'node:child_process';
import { createHash } from 'node:crypto';
import { readFile, writeFile, mkdir, mkdtemp, rm } from 'node:fs/promises';
import { fileURLToPath, pathToFileURL } from 'node:url';
import path from 'node:path';
import { parseArgs } from 'node:util';

const root = path.resolve(fileURLToPath(new URL('../..', import.meta.url)));
const { values: options } = parseArgs({ options: {
  entry: { type: 'string' }, 'evidence-dir': { type: 'string' }, 'scratch-dir': { type: 'string' },
  url: { type: 'string' }, browser: { type: 'string' },
} });
const entryPath = path.resolve(root, options.entry || 'visualization/rev5-full-assembly-v3/index.html');
const entryURL = options.url ? new URL(options.url) : pathToFileURL(entryPath);
if (!['https:', 'http:', 'file:'].includes(entryURL.protocol)) throw new Error('Unsupported entry protocol');
const docs = path.resolve(root, options['evidence-dir'] || '.agent-work/rev5-v3-browser-evidence');
const scratch = path.resolve(root, options['scratch-dir'] || path.join(docs, 'scratch'));
await mkdir(path.dirname(docs), { recursive: true });
await mkdir(docs);
await mkdir(scratch, { recursive: true });
const profile = await mkdtemp(path.join(scratch, 'chrome-'));
const binary = options.browser || '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const chrome = spawn(binary, ['--headless=new', '--remote-debugging-port=0', `--user-data-dir=${profile}`,
  '--no-first-run', '--no-default-browser-check', '--disable-background-networking',
  '--disable-component-update', '--disable-sync', '--disable-default-apps', '--no-pings', 'about:blank'],
{ stdio: ['ignore', 'ignore', 'pipe'] });
let stderr = '';
let spawnError;
chrome.on('error', error => { spawnError = error; });
chrome.stderr.on('data', data => { stderr += data; });
const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));
const evidence = { schema_version: 1, started_at: new Date().toISOString(),
  entry: options.url ? entryURL.href : path.relative(root, entryPath),
  browser: 'Installed Chrome; version recorded below', node: process.version,
  host_app_confirmation: 'HOST_APP_CONFIRMATION_PENDING',
  mode: `isolated installed Chrome CDP; ${entryURL.protocol}; no installed packages or shared browser profile`,
  checks: [], exceptions: [], console_errors: [], loader_errors: [], media_request_cancellations: [],
  downloads: [], media_events: [], external_requests: [], screenshots: [], status: 'RUNNING' };
let socket, sequence = 0;
const pending = new Map();
const requests = new Map();
function send(method, params = {}) {
  const id = ++sequence;
  return new Promise((resolve, reject) => {
    const timeout = setTimeout(() => { pending.delete(id); reject(new Error(`CDP timeout: ${method} ${(params.expression || '').slice(0, 160)}`)); }, 60000);
    pending.set(id, { resolve, reject, timeout });
    socket.send(JSON.stringify({ id, method, params }));
  });
}
async function evaluate(expression) {
  const result = await send('Runtime.evaluate', { expression, returnByValue: true, awaitPromise: true });
  if (result.exceptionDetails) throw new Error(JSON.stringify(result.exceptionDetails));
  return result.result.value;
}
async function settle(expression) {
  await evaluate(expression);
  await evaluate('new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)))');
}
async function screenshot(name) {
  const { data } = await send('Page.captureScreenshot', { format: 'png' });
  const bytes = Buffer.from(data, 'base64');
  await writeFile(path.join(docs, name), bytes);
  evidence.screenshots.push({ path: path.relative(root, path.join(docs, name)), sha256: createHash('sha256').update(bytes).digest('hex') });
}
const state = () => evaluate('rev5FullViewer.getState()');
const pixels = () => evaluate(`(() => {
  const gl=rev5FullViewer.gl,c=rev5FullViewer.canvas,p=new Uint8Array(c.width*c.height*4);
  gl.readPixels(0,0,c.width,c.height,gl.RGBA,gl.UNSIGNED_BYTE,p);
  let foreground=0,sum=0; for(let i=0;i<p.length;i+=4){if(p[i]<240||p[i+1]<240||p[i+2]<240)foreground++;sum=(sum+p[i]*3+p[i+1]*7+p[i+2]*11)>>>0;}
  return {foreground,sum,width:c.width,height:c.height,error:gl.getError()};
})()`);
try {
  evidence.runtime_assets = [];
  const media = JSON.parse(await readFile(path.join(path.dirname(entryPath), 'media-manifest.json'), 'utf8'));
  const runtimeNames = ['index.html', 'style.css', 'interactive-viewer.js', 'scene-data.js', 'edge-data.js',
    'features.js', 'viewer.js', 'drawings.js', 'app.js', 'inventory.json', 'plan-data.js',
    'presentation-plan.json', 'runtime-assets.json', 'README.md', 'media-data.js', 'media.js',
    'media-manifest.json', ...media.clips.flatMap(clip => [clip.video.path, clip.poster.path])];
  const allowedRequests = new Set(runtimeNames.map(name => new URL(name, entryURL).href));
  for (const name of runtimeNames) {
    const bytes = await readFile(path.join(path.dirname(entryPath), name));
    const sha256 = createHash('sha256').update(bytes).digest('hex');
    if (options.url) {
      const response = await fetch(new URL(name, entryURL));
      assert.equal(response.status, 200, `Public asset unavailable: ${name}`);
      assert.equal(createHash('sha256').update(Buffer.from(await response.arrayBuffer())).digest('hex'), sha256, `Public asset hash mismatch: ${name}`);
    }
    evidence.runtime_assets.push({ path: name, sha256, bytes: bytes.length });
  }
  let port;
  for (let i = 0; i < 600; i++) {
    if (spawnError) throw spawnError;
    if (chrome.exitCode !== null) throw new Error(`Chrome exited: ${chrome.exitCode}\n${stderr}`);
    try { port = (await readFile(path.join(profile, 'DevToolsActivePort'), 'utf8')).split('\n')[0]; break; }
    catch (error) { if (error.code !== 'ENOENT') throw error; await sleep(100); }
  }
  assert.ok(port, 'Chrome did not expose its isolated debugging endpoint');
  evidence.browser = (await (await fetch(`http://127.0.0.1:${port}/json/version`)).json()).Browser;
  const pages = await (await fetch(`http://127.0.0.1:${port}/json/list`)).json();
  socket = new WebSocket(pages.find(page => page.type === 'page').webSocketDebuggerUrl);
  await new Promise((resolve, reject) => { socket.addEventListener('open', resolve, { once: true }); socket.addEventListener('error', reject, { once: true }); });
  socket.addEventListener('message', event => {
    const message = JSON.parse(event.data);
    if (message.id) {
      const waiter = pending.get(message.id); if (!waiter) return;
      clearTimeout(waiter.timeout); pending.delete(message.id);
      if (message.error) waiter.reject(new Error(JSON.stringify(message.error))); else waiter.resolve(message.result);
    } else if (message.method === 'Runtime.exceptionThrown') evidence.exceptions.push(message.params);
    else if (message.method === 'Runtime.consoleAPICalled' && message.params.type === 'error') evidence.console_errors.push(message.params);
    else if (message.method === 'Network.loadingFailed') {
      const failure = message.params, url = requests.get(failure.requestId);
      const ownedMedia = media.clips.some(clip => new URL(clip.video.path, entryURL).href === url);
      if (ownedMedia && failure.type === 'Media' && failure.canceled && failure.errorText === 'net::ERR_ABORTED') {
        evidence.media_request_cancellations.push({ ...failure, url });
      } else evidence.loader_errors.push(failure);
    } else if (message.method === 'Network.requestWillBeSent') {
      const { requestId, request } = message.params;
      requests.set(requestId, request.url);
      if (/^(https?|file):/.test(request.url) && !allowedRequests.has(request.url)) evidence.external_requests.push(request.url);
    } else if (message.method === 'Browser.downloadWillBegin' || message.method === 'Browser.downloadProgress') {
      evidence.downloads.push({ event: message.method, ...message.params });
    } else if (message.method.startsWith('Media.')) {
      evidence.media_events.push({ event: message.method, ...message.params });
    }
    else if (message.method === 'Log.entryAdded' && message.params.entry.level === 'error') evidence.console_errors.push(message.params.entry);
  });
  await send('Runtime.enable'); await send('Page.enable'); await send('Network.enable'); await send('Log.enable'); await send('Media.enable');
  await send('Emulation.setDeviceMetricsOverride', { width: 1440, height: 1100, deviceScaleFactor: 1, mobile: false });
  await send('Page.navigate', { url: entryURL.href });
  let ready = false, loadError = null;
  for (let i = 0; i < 600; i++) {
    const load = await evaluate(`({ready:document.getElementById('whole-canvas')?.dataset.ready==='true',error:document.getElementById('error')?.hidden===false?document.getElementById('error').textContent:null})`);
    if (load.error) { loadError = load.error; break; }
    if (load.ready) { ready = true; break; }
    await sleep(100);
  }
  if (loadError) throw new Error(loadError);
  assert.ok(ready, 'Page did not finish drawing');
  assert.equal((await state()).playing, false); assert.equal((await state()).autoOrbit, false);
  assert.equal((await state()).visibleIds.length, 299);
  await screenshot('browser-default-exterior.png');
  await settle("document.getElementById('interior').click()");
  const initial = await state();
  assert.equal(initial.componentCount, 399);
  const required = ['FRAME_LOWER', 'FRAME_UPPER', ...['X', 'Y', 'Z'].flatMap(axis => [`${axis}_motor`, `${axis}_wheel`])];
  required.forEach(id => assert.ok(initial.visibleIds.includes(id), `Required visible identity: ${id}`));
  assert.equal(initial.visibleIds.length, 293);
  const interiorPixels = await pixels();
  assert.ok(interiorPixels.foreground > 10000); assert.equal(interiorPixels.error, 0);
  evidence.checks.push({ name: 'initial interior: full frame and all three drives; actual GPU pixels', visible_count: 293, required, pixels: interiorPixels });
  await screenshot('browser-interior.png');
  await settle("document.getElementById('exterior').click()");
  const exterior = await state(), exteriorPixels = await pixels();
  assert.equal(exterior.visibleIds.length, 299);
  assert.equal(exterior.visibleIds.filter(id => id.startsWith('PRINT_panel_')).length, 6);
  assert.notEqual(exteriorPixels.sum, interiorPixels.sum);
  evidence.checks.push({ name: 'exterior reveals all six panels and changes actual framebuffer', pixels: exteriorPixels });
  await screenshot('browser-exterior.png');
  await settle("document.getElementById('drive-only').click()");
  assert.equal((await state()).visibleIds.length, 30);
  await screenshot('browser-three-axes.png');
  await settle("document.getElementById('interior').click()");
  await settle("document.querySelector('[data-group=reference]').click()");
  assert.equal((await state()).visibleIds.length, 393);
  await settle("document.querySelector('[data-group=reference]').click()");
  assert.equal((await state()).visibleIds.length, 293);
  evidence.checks.push({ name: '100 reference/gauge meshes separately toggled; not physical BOM' });
  for (const id of required) {
    await settle(`document.getElementById('part-select').value=${JSON.stringify(id)};document.getElementById('part-select').dispatchEvent(new Event('change'))`);
    const selected = await evaluate(`({id:rev5FullViewer.state.selected, shown:[...document.querySelectorAll('#part-dimensions b')].map(n=>n.textContent), expected:REV5_FULL_SCENE.components.find(c=>c.id===rev5FullViewer.state.selected).dimensions_mm.map(n=>n.toFixed(2))})`);
    assert.equal(selected.id, id); assert.deepEqual(selected.shown, selected.expected);
  }
  assert.deepEqual(await evaluate('REV5_FULL_SCENE.frame_dimensions_mm'), [240, 240, 240]);
  await settle("document.getElementById('isolate').click()");
  assert.deepEqual((await state()).visibleIds, ['Z_wheel']);
  evidence.checks.push({ name: 'all eight required selections show source-derived XYZ mm; selected-only visibility; frame 240/240/240' });
  await settle("document.getElementById('interior').click()");
  const cameraStates = [];
  for (const camera of ['iso', 'front', 'side', 'top']) {
    await settle(`document.querySelector('[data-camera=${camera}]').click()`);
    const s = await state(); cameraStates.push([s.yaw, s.pitch]);
    assert.ok((await pixels()).foreground > 1000);
    assert.ok(await evaluate('rev5FullViewer.matrix.every(Number.isFinite)'));
  }
  assert.equal(new Set(cameraStates.map(JSON.stringify)).size, 4);
  await settle("document.getElementById('reset').click()");
  const before = await state();
  const rect = await evaluate("(()=>{const r=document.getElementById('whole-canvas').getBoundingClientRect();return {x:r.x+150,y:r.y+150}})()");
  await send('Input.dispatchMouseEvent', { type: 'mousePressed', x: rect.x, y: rect.y, button: 'left', clickCount: 1 });
  await send('Input.dispatchMouseEvent', { type: 'mouseMoved', x: rect.x + 55, y: rect.y + 20, button: 'left', buttons: 1 });
  await send('Input.dispatchMouseEvent', { type: 'mouseReleased', x: rect.x + 55, y: rect.y + 20, button: 'left', clickCount: 1 });
  await settle('void 0');
  assert.notEqual((await state()).yaw, before.yaw);
  await send('Input.dispatchMouseEvent', { type: 'mouseWheel', x: rect.x, y: rect.y, deltaY: -150, deltaX: 0 });
  await settle('void 0'); assert.ok((await state()).zoom > 1);
  const beforeKey = await state();
  await send('Input.dispatchKeyEvent', { type: 'keyDown', key: 'ArrowRight', code: 'ArrowRight', windowsVirtualKeyCode: 39 });
  await send('Input.dispatchKeyEvent', { type: 'keyUp', key: 'ArrowRight', code: 'ArrowRight', windowsVirtualKeyCode: 39 });
  await settle('void 0'); assert.notEqual((await state()).yaw, beforeKey.yaw);
  await send('Input.dispatchKeyEvent', { type: 'keyDown', key: 'Home', code: 'Home', windowsVirtualKeyCode: 36 });
  await send('Input.dispatchKeyEvent', { type: 'keyUp', key: 'Home', code: 'Home', windowsVirtualKeyCode: 36 });
  await settle('void 0'); assert.equal((await state()).yaw, before.yaw); assert.equal((await state()).zoom, 1);
  await settle("document.getElementById('reset').click()");
  assert.equal((await state()).zoom, 1);
  assert.equal((await state()).yaw, before.yaw);
  evidence.checks.push({ name: 'four camera presets, pointer drag, wheel zoom, keyboard, reset', cameraStates });
  await settle("document.getElementById('part-search').value='not-a-source-id';document.getElementById('part-search').dispatchEvent(new Event('input'))");
  assert.ok(await evaluate("document.getElementById('part-select').disabled && document.getElementById('selection-status').textContent.includes('一致するIDがありません')"));
  await settle("document.getElementById('part-search').value='X_motor';document.getElementById('part-search').dispatchEvent(new Event('input'))");
  assert.equal((await state()).selected, 'X_motor');
  await settle("document.getElementById('part-search').value='';document.getElementById('part-search').dispatchEvent(new Event('input'))");
  await settle("document.getElementById('show-dimensions').click()");
  assert.equal(await evaluate("document.querySelectorAll('#dimensions .dimension-line').length"), 0);
  await settle("document.getElementById('show-dimensions').click()");
  assert.equal(await evaluate("document.querySelectorAll('#dimensions .dimension-line').length"), 3);
  const rejected = await evaluate(`Rev5Whole.unpack({...REV5_FULL_SCENE,payload_sha256:'0'.repeat(64)}).then(()=>false,e=>e.message.includes('SHA-256'))`);
  assert.ok(rejected);
  evidence.checks.push({ name: 'empty search, search recovery, dimension visibility and corrupt payload rejection' });
  await settle("document.getElementById('stop').click();document.getElementById('interior').click()");
  const geometryBefore = await evaluate("REV5_FULL_SCENE.payload_sha256");
  await settle("document.getElementById('explode').value='100';document.getElementById('explode').dispatchEvent(new Event('input'))");
  assert.equal((await state()).explode, 1);
  assert.equal(await evaluate("document.querySelectorAll('#dimensions .dimension-line').length"), 0);
  assert.ok(await evaluate('rev5FullViewer.parts.every(p=>rev5FullViewer.offset(p.component).every(Number.isFinite))'));
  assert.ok((await pixels()).foreground > 1000);
  await screenshot('browser-exploded.png');
  await settle("document.getElementById('stop').click()");
  assert.equal((await state()).explode, 0);
  assert.ok(await evaluate("rev5FullViewer.parts.every(p=>rev5FullViewer.offset(p.component).every(v=>v===0))"));
  assert.equal(await evaluate("REV5_FULL_SCENE.payload_sha256"), geometryBefore);
  await settle("document.getElementById('play').click()");
  await sleep(400); const moving = await state(); assert.ok(moving.explode > 0);
  await settle("rev5FullViewer.setState({...rev5FullViewer.state,phase:.99,explode:.99})");
  await sleep(300);
  assert.ok((await state()).phase > 1 && (await state()).explode < 1, 'Playback must reverse toward assembly');
  await settle("document.getElementById('pause').click()");
  const paused = await state(); await sleep(150); assert.equal((await state()).explode, paused.explode);
  await settle("document.getElementById('orbit').click()");
  const yawBefore = (await state()).yaw; await sleep(200); assert.notEqual((await state()).yaw, yawBefore);
  await settle("document.getElementById('stop').click()");
  assert.equal((await state()).playing, false); assert.equal((await state()).autoOrbit, false); assert.equal((await state()).explode, 0);
  await send('Emulation.setEmulatedMedia', { features: [{ name: 'prefers-reduced-motion', value: 'reduce' }] });
  await settle('void 0');
  assert.ok(await evaluate("document.getElementById('play').disabled && document.getElementById('orbit').disabled"));
  await send('Emulation.setEmulatedMedia', { features: [{ name: 'prefers-reduced-motion', value: 'no-preference' }] });
  await settle('void 0');
  evidence.checks.push({ name: 'explode100 and exact zero for all399; play reverses, pause/stop and orbit; reduced-motion disables continuous play' });
  const opaque = await pixels();
  await settle("document.getElementById('xray').click()");
  const xray = await pixels(); assert.notEqual(opaque.sum, xray.sum);
  assert.ok(xray.foreground > 1000); assert.equal((await state()).appearance, 'xray');
  await screenshot('browser-xray.png');
  await settle("document.getElementById('xray').click()");
  evidence.checks.push({ name: 'actual opaque versus translucent faces and edge pixels', opaque, xray });
  const findPoint = id => evaluate(`(() => {
    const v=rev5FullViewer,gl=v.gl,c=v.canvas,code=REV5_FULL_SCENE.components.findIndex(p=>p.id===${JSON.stringify(id)})+1;
    v.pick(0,0);gl.bindFramebuffer(gl.FRAMEBUFFER,v.pickBuffer);
    const data=new Uint8Array(c.width*c.height*4);gl.readPixels(0,0,c.width,c.height,gl.RGBA,gl.UNSIGNED_BYTE,data);
    gl.bindFramebuffer(gl.FRAMEBUFFER,null);
    for(let y=4;y<c.height-4;y+=3)for(let x=4;x<c.width-4;x+=3){
      const k=(y*c.width+x)*4;
      if(data[k]+data[k+1]*256===code){
        const rect=c.getBoundingClientRect();return {x:rect.x+(x+.5)*c.clientWidth/c.width,y:rect.y+(c.height-y-.5)*c.clientHeight/c.height};
      }
    } return null;
  })()`);
  for (const [amount, camera] of [[0, 'iso'], [100, 'side']]) {
    await settle(`document.getElementById('part-select').value='X_motor';document.getElementById('part-select').dispatchEvent(new Event('change'));document.getElementById('unit-select').value='axis-X';document.getElementById('unit-select').dispatchEvent(new Event('change'));document.getElementById('focus-unit').click();document.getElementById('explode').value='${amount}';document.getElementById('explode').dispatchEvent(new Event('input'));document.querySelector('[data-camera=${camera === 'side' ? 'front' : camera}]').click()`);
    const point = await findPoint('X_motor'); assert.ok(point);
    await send('Input.dispatchMouseEvent', { type: 'mouseMoved', ...point });
    await settle('void 0'); assert.equal((await state()).hovered, 'X_motor');
    const tooltip = await evaluate("document.getElementById('hover-info').textContent");
    assert.ok(tooltip.includes('X_motor') && tooltip.includes('74.50') && tooltip.includes('REFERENCE'));
    await send('Input.dispatchMouseEvent', { type: 'mousePressed', ...point, button: 'left', clickCount: 1 });
    await send('Input.dispatchMouseEvent', { type: 'mouseReleased', ...point, button: 'left', clickCount: 1 });
    await settle('void 0'); assert.equal((await state()).selected, 'X_motor');
    evidence.checks.push({ name: 'actual pointer hover and click pin at current exploded triangle geometry', amount, camera: camera === 'side' ? 'front' : camera, tooltip });
  }
  await settle("document.getElementById('drive-only').click();document.querySelector('[data-camera=iso]').click();document.getElementById('part-search').value='Y_motor';document.getElementById('part-search').dispatchEvent(new Event('input'))");
  assert.equal((await state()).selected, 'Y_motor');
  const pinPoint = await findPoint('X_motor'); assert.ok(pinPoint);
  await send('Input.dispatchMouseEvent', { type: 'mousePressed', ...pinPoint, button: 'left', clickCount: 1 });
  await send('Input.dispatchMouseEvent', { type: 'mouseReleased', ...pinPoint, button: 'left', clickCount: 1 });
  await settle('void 0');
  assert.equal((await state()).selected, 'X_motor');
  assert.equal(await evaluate("document.getElementById('part-search').value"), '');
  assert.equal(await evaluate("document.getElementById('part-select').value"), 'X_motor');
  await settle("document.getElementById('part-select').value='Y_motor';document.getElementById('part-select').dispatchEvent(new Event('change'))");
  await send('Emulation.setTouchEmulationEnabled', { enabled: true });
  await send('Input.dispatchTouchEvent', { type: 'touchStart', touchPoints: [pinPoint] });
  await send('Input.dispatchTouchEvent', { type: 'touchEnd', touchPoints: [] });
  await settle('void 0'); assert.equal((await state()).selected, 'X_motor');
  await send('Emulation.setTouchEmulationEnabled', { enabled: false });
  evidence.checks.push({ name: 'actual mouse click and touch tap change pinned selection; stale ID filter cleared for keyboard fallback' });
  await settle("document.getElementById('interior').click();document.querySelector('[data-group=drive]').click()");
  assert.equal(await findPoint('X_motor'), null);
  await settle("document.getElementById('stop').click();document.getElementById('part-select').value='FRAME_LOWER';document.getElementById('part-select').dispatchEvent(new Event('change'));document.getElementById('isolate').click();document.querySelector('[data-camera=front]').click()");
  const holeCheck = await evaluate(`(() => {
    const v=rev5FullViewer,p=REV5_FULL_SCENE.components.find(p=>p.id==='FRAME_LOWER');
    const [lo,hi]=p.bounds_mm;
    const a=v.project([lo[0],lo[1],lo[2]]),b=v.project([hi[0],lo[1],hi[2]]);
    let misses=0,hits=0;
    for(let i=1;i<8;i++)for(let j=1;j<8;j++){
      const result=v.pick(a[0]+(b[0]-a[0])*i/8,a[1]+(b[1]-a[1])*j/8);
      if(result)hits++;else misses++;
    }return {hits,misses};
  })()`);
  assert.ok(holeCheck.misses > 0, 'Empty space within projected AABB must not hit');
  assert.ok(await findPoint('FRAME_LOWER'));
  evidence.checks.push({ name: 'hidden group excluded; empty area inside frame AABB rejected by triangle/depth picking', holeCheck });
  const sheets = await evaluate(`(() => {
    const result=[];
    for(const part of REV5_FULL_SCENE.components){
      const svg=rev5ReferenceSheet(part.id),doc=new DOMParser().parseFromString(svg,'image/svg+xml');
      if(doc.querySelector('parsererror')||doc.querySelectorAll('[data-view]').length!==3||
         !svg.includes(part.sha256)||!svg.includes('NOT FOR FABRICATION')||/NaN|Infinity/.test(svg))throw new Error('Invalid sheet '+part.id);
      for(const size of part.dimensions_mm)if(!svg.includes(size.toFixed(3)))throw new Error('Dimension mismatch '+part.id);
      result.push({id:part.id,views:3,bytes:svg.length,source_sha256:part.sha256,dimensions_mm:part.dimensions_mm});
    }return result;
  })()`);
  assert.equal(sheets.length, 399); assert.equal(new Set(sheets.map(s => s.id)).size, 399);
  assert.ok(await evaluate("REV5_EDGES.parts.find(p=>p.id==='X_motor').projection_extras[0].edge_count>0"));
  await writeFile(path.join(docs, 'browser-sheet-coverage.json'), JSON.stringify({ status: 'PASS', sheets }, null, 2) + '\n');
  await settle("document.getElementById('part-select').value='X_motor';document.getElementById('part-select').dispatchEvent(new Event('change'));document.getElementById('show-sheet').click()");
  assert.equal(await evaluate("document.querySelector('#reference-sheet svg').dataset.partId"), 'X_motor');
  await screenshot('browser-reference-sheet.png');
  await send('Browser.setDownloadBehavior', { behavior: 'allow', downloadPath: scratch, eventsEnabled: true });
  const expectedSheetHash = await evaluate("crypto.subtle.digest('SHA-256',new TextEncoder().encode(rev5ReferenceSheet('X_motor'))).then(b=>Array.from(new Uint8Array(b),n=>n.toString(16).padStart(2,'0')).join(''))");
  await settle("document.getElementById('save-sheet').click()");
  let saved;
  for (let i = 0; i < 600; i++) {
    try {
      saved = await readFile(path.join(scratch, 'rev5-X_motor-REF.svg'), 'utf8');
      if (createHash('sha256').update(saved).digest('hex') === expectedSheetHash) break;
    } catch (error) { if (error.code !== 'ENOENT') throw error; }
    await sleep(100);
  }
  assert.ok(saved?.includes('REF / NOT FOR FABRICATION')); assert.ok(saved.includes('74.500'));
  assert.equal(createHash('sha256').update(saved).digest('hex'), expectedSheetHash, 'Wait for complete source-identical SVG download');
  evidence.checks.push({ name: 'all399 source IDs generate valid three-view SVGs with source hashes/dimensions; selected sheet displayed and actual SVG download works', coverage: 'browser-sheet-coverage.json', count: sheets.length, downloaded_sha256: createHash('sha256').update(saved).digest('hex') });
  await settle("scrollTo(0,0);document.getElementById('full-view').click();document.getElementById('stop').click();document.getElementById('reset').click()");
  const stageWitnesses = [];
  for (const amount of [0, .075, .15, .25, .35, .425, .5, .625, .75, .875, 1]) {
    await settle(`document.getElementById('explode').value='${amount*100}';document.getElementById('explode').dispatchEvent(new Event('input'))`);
    const witness = await evaluate(`(() => {
      const v=rev5FullViewer,p=Rev5Features.plan,a=v.state.explode;
      const rows=p.groups.map(g=>{
        const offsets=g.members.map(id=>v.offset(REV5_FULL_SCENE.components.find(c=>c.id===id)));
        if((g.stage===null || a<=p.stages[g.stage].range[0]) && offsets.some(o=>o.some(x=>x!==0)))throw new Error('Early movement '+g.id);
        if(a<=.75 && offsets.some(o=>JSON.stringify(o)!==JSON.stringify(offsets[0])))throw new Error('Small item detached '+g.id);
        return {id:g.id,offset:offsets[0],moved:offsets.some(o=>o.some(x=>x!==0))};
      });
      if(a>=.15){
        const screw=v.offset(REV5_FULL_SCENE.components.find(c=>c.id==='ALLOC_panel_screw_X_minus_1'));
        const panel=v.offset(REV5_FULL_SCENE.components.find(c=>c.id==='PRINT_panel_X_minus'));
        if(Math.abs(screw[0]-panel[0]+22)>1e-10)throw new Error('Panel carry gap drift');
      }
      return {amount:a,stage:document.getElementById('stage-status').textContent,groups:rows};
    })()`);
    stageWitnesses.push(witness);
    if ([.15, .35, .5, .75, 1].includes(amount)) await screenshot(`stage-${Math.round(amount*100)}.png`);
  }
  await writeFile(path.join(docs, 'stage-witnesses.json'), JSON.stringify(stageWitnesses, null, 2) + '\n');
  assert.ok(stageWitnesses[1].groups.some(g => g.id.endsWith('-screws') && g.moved));
  assert.ok(stageWitnesses[1].groups.every(g => !g.moved || g.id.endsWith('-screws')));
  evidence.checks.push({ name: 'actual11 timeline positions: outside first; small members stay grouped; reserves stationary', witnesses: 'stage-witnesses.json' });
  for (const axis of ['X', 'Y', 'Z']) {
    await settle(`document.getElementById('unit-select').value='axis-${axis}';document.getElementById('unit-select').dispatchEvent(new Event('change'));document.getElementById('focus-unit').click()`);
    const unit = await evaluate("Rev5Features.plan.named_units.find(u=>u.id===rev5FullViewer.state.focusUnit)");
    assert.deepEqual((await state()).visibleIds.sort(), unit.members.sort());
    for (const camera of ['iso', 'front', 'side', 'top', 'rear', 'left', 'bottom']) {
      await settle(`document.querySelector('[data-camera=${camera}]').click()`);
      assert.ok((await pixels()).foreground > 1000);
      assert.ok(await evaluate("rev5FullViewer.matrix.every(Number.isFinite)"));
    }
    await settle("document.querySelector('[data-camera=iso]').click()");
    await screenshot(`browser-unit-${axis}.png`);
  }
  evidence.checks.push({ name: 'XYZ exploded unit views: exact source memberships and7 rendered camera angles per unit' });
  await settle("document.getElementById('part-select').value='X_collar_nut';document.getElementById('part-select').dispatchEvent(new Event('change'));document.getElementById('isolate').click()");
  assert.equal((await state()).explode, 0); assert.equal((await state()).visibleIds.length, 1);
  assert.ok((await state()).frameBounds.radius < 10);
  const labels = await evaluate("[...document.querySelectorAll('.part-dimension-label')].map(n=>({text:n.textContent,y:Number(n.getAttribute('y'))}))");
  assert.equal(labels.length, 3); assert.equal(new Set(labels.map(l => l.y)).size, 3);
  for (const camera of ['iso', 'front', 'side', 'top']) {
    await settle(`document.querySelector('[data-camera=${camera}]').click()`); assert.ok((await pixels()).foreground > 1000);
  }
  await settle("document.getElementById('orbit').click()");
  const partYaw = (await state()).yaw; await sleep(200); assert.notEqual((await state()).yaw, partYaw);
  assert.ok(await evaluate("rev5FullViewer.offset(REV5_FULL_SCENE.components.find(p=>p.id==='X_collar_nut')).every(v=>v===0)"));
  await settle("document.getElementById('pause').click();document.querySelector('[data-camera=iso]').click()");
  await screenshot('browser-focused-part.png');
  const frameCoverage = await evaluate(`(() => {
    const v=rev5FullViewer,old=v.state,result=[];
    try{
      for(const p of REV5_FULL_SCENE.components){
        v.state={...old,selected:p.id,isolated:true,focusUnit:null,explode:0,zoom:1};
        const b=v.framedBounds(),expected=p.bounds_mm[0].map((x,i)=>(x+p.bounds_mm[1][i])/2);
        if(b.center.some((x,i)=>x!==expected[i])||!v.camera().every(Number.isFinite))throw new Error('Unframed '+p.id);
        result.push({id:p.id,center:b.center,radius:b.radius});
      }
    }finally{v.state=old;}
    return result;
  })()`);
  assert.equal(frameCoverage.length, 399);
  await writeFile(path.join(docs, 'frame-coverage.json'), JSON.stringify(frameCoverage, null, 2) + '\n');
  assert.equal(await evaluate("document.querySelectorAll('iframe').length"), 0);
  evidence.checks.push({ name: 'small part fills focused view; separated XYZ labels; source-centred turntable; all399 frame centres/matrices', coverage: 'frame-coverage.json' });
  assert.equal(await evaluate("document.querySelectorAll('video').length"), 1);
  assert.equal(await evaluate("document.querySelectorAll('.media-choice').length"), 6);
  assert.ok(await evaluate("(()=>{const v=document.getElementById('media-player');return v.controls&&v.paused&&!v.autoplay&&!v.loop&&v.preload==='metadata'})()"));
  for (const axis of ['X', 'Y', 'Z']) {
    await settle(`document.getElementById('part-select').value='${axis}_motor';document.getElementById('part-select').dispatchEvent(new Event('change'));document.getElementById('related-media').click()`);
    assert.equal(await evaluate("document.getElementById('media-player').dataset.clipId"), `unit-${axis}`);
    assert.ok(await evaluate("document.getElementById('related-media-note').textContent.includes('単体専用のネイティブ動画ではありません')"));
  }
  await settle("document.getElementById('part-select').value='FRAME_LOWER';document.getElementById('part-select').dispatchEvent(new Event('change'));document.getElementById('related-media').click()");
  assert.equal(await evaluate("document.getElementById('media-player').dataset.clipId"), 'whole-interior');
  await settle("document.getElementById('part-select').value=Rev5Features.plan.members.find(m=>m.nonphysical_reference).id;document.getElementById('part-select').dispatchEvent(new Event('change'))");
  assert.ok(await evaluate("document.getElementById('related-media').disabled"));
  evidence.checks.push({ name: 'actual selected XYZ parts link to containing-unit clips; frame links to whole interior; hidden reference has no invented movie' });
  evidence.media = [];
  for (const clip of media.clips) {
    await settle(`document.querySelector('[data-clip="${clip.id}"]').scrollIntoView({block:'center'});document.querySelector('[data-clip="${clip.id}"]').click()`);
    let ready = false;
    for (let i = 0; i < 100; i++) {
      ready = await evaluate("document.getElementById('media-player').readyState>=2");
      if (ready) break;
      await sleep(100);
    }
    assert.ok(ready, `Media failed to load a playable frame: ${clip.id}`);
    const metadata = await evaluate(`(() => {
      const v=document.getElementById('media-player'),img=document.querySelector('[data-clip="${clip.id}"] img');
      return {duration:v.duration,width:v.videoWidth,height:v.videoHeight,paused:v.paused,autoplay:v.autoplay,
        src:v.currentSrc,poster:v.poster,error:v.error?.code??null,
        posterWidth:img.naturalWidth,posterHeight:img.naturalHeight,
        selected:document.querySelectorAll('.media-choice[aria-pressed="true"]').length};
    })()`);
    assert.ok(metadata.paused && !metadata.autoplay);
    assert.equal(metadata.error, null); assert.equal(metadata.selected, 1);
    assert.equal(metadata.src, new URL(clip.video.path, entryURL).href);
    assert.equal(metadata.poster, new URL(clip.poster.path, entryURL).href);
    assert.deepEqual([metadata.width, metadata.height], [960, 640]);
    assert.deepEqual([metadata.posterWidth, metadata.posterHeight], clip.poster.dimensions);
    assert.ok(Math.abs(metadata.duration-clip.video.container_duration_seconds) < 1e-6,
      `Observed browser duration differs from frozen container metadata: ${clip.id} ${metadata.duration}`);
    assert.equal(await evaluate("document.getElementById('media-timing-note').hidden"), clip.id !== 'unit-Z');
    await settle(`(() => {
      const v=document.getElementById('media-player');v.scrollIntoView({block:'center'});
      globalThis.mediaFrame=null;
      v.requestVideoFrameCallback((_,frame)=>{globalThis.mediaFrame={mediaTime:frame.mediaTime,presentedFrames:frame.presentedFrames}});
    })()`);
    const controlPoint = await evaluate("(()=>{const r=document.getElementById('media-player').getBoundingClientRect();return {x:r.x+30,y:r.bottom-28}})()");
    await send('Input.dispatchMouseEvent', { type: 'mouseMoved', ...controlPoint });
    await send('Input.dispatchMouseEvent', { type: 'mousePressed', ...controlPoint, button: 'left', clickCount: 1 });
    await send('Input.dispatchMouseEvent', { type: 'mouseReleased', ...controlPoint, button: 'left', clickCount: 1 });
    let playback;
    for (let i = 0; i < 600; i++) {
      playback = await evaluate("(()=>{const v=document.getElementById('media-player');return {paused:v.paused,time:v.currentTime,frame:globalThis.mediaFrame,decoded:v.getVideoPlaybackQuality().totalVideoFrames,readyState:v.readyState,networkState:v.networkState,error:v.error?.code??null,hidden:document.hidden,buffered:Array.from({length:v.buffered.length},(_,i)=>[v.buffered.start(i),v.buffered.end(i)])}})()");
      if (!playback.paused && playback.time > .15 && playback.frame?.presentedFrames > 0) break;
      await sleep(100);
    }
    if (playback.time <= .15 || !playback.frame) await screenshot(`media-${clip.id}-not-playing.png`);
    assert.ok(!playback.paused && playback.time > .15 && playback.frame?.presentedFrames > 0 && playback.decoded > 0,
      `Native video control did not play actual frames: ${clip.id} ${JSON.stringify(playback)}`);
    await send('Input.dispatchMouseEvent', { type: 'mousePressed', ...controlPoint, button: 'left', clickCount: 1 });
    await send('Input.dispatchMouseEvent', { type: 'mouseReleased', ...controlPoint, button: 'left', clickCount: 1 });
    assert.ok(await evaluate("document.getElementById('media-player').paused"), 'Native pause control failed');
    await screenshot(`media-${clip.id}.png`);
    evidence.media.push({ id: clip.id, metadata, playback, native_controls_play_pause: true,
      video_sha256: clip.video.sha256, poster_sha256: clip.poster.sha256 });
  }
  evidence.checks.push({ name: 'six original MP4s and six posters: native control play/pause, actual presented/decoded frames, source metadata and precise Z observation', clip_count: evidence.media.length });
  assert.ok(await evaluate("document.getElementById('media-error').hidden && !document.getElementById('media-player').error"));
  for (const cancellation of evidence.media_request_cancellations) {
    assert.ok(evidence.media.some(clip => clip.metadata.src === cancellation.url && clip.native_controls_play_pause),
      'A canceled metadata read must still have successful real playback and hash evidence');
  }
  await settle("document.getElementById('stop').click();document.getElementById('interior').click();document.getElementById('reset').click();scrollTo(0,0)");
  for (const width of [320, 768, 1024, 1440]) {
    await send('Emulation.setDeviceMetricsOverride', { width, height: 1100, deviceScaleFactor: 1, mobile: false });
    await settle('void 0');
    assert.ok(await evaluate('document.documentElement.scrollWidth<=innerWidth'), `Horizontal overflow at ${width}`);
    assert.ok((await pixels()).foreground > 1000);
    evidence.checks.push({ name: 'responsive page and GPU draw', width });
  }
  await send('Accessibility.enable');
  const ax = await send('Accessibility.getFullAXTree');
  assert.ok(ax.nodes.some(n => n.role?.value === 'heading' && n.name?.value === '筐体と、3つの駆動軸。'));
  assert.ok(ax.nodes.some(n => n.role?.value === 'button' && n.name?.value === '内部を見る'));
  evidence.checks.push({ name: 'accessible heading and named native controls exposed in Chrome AX tree; not a full accessibility audit' });
  await settle("document.getElementById('play').click();document.getElementById('orbit').click()");
  await send('Page.setWebLifecycleState', { state: 'frozen' });
  await send('Page.setWebLifecycleState', { state: 'active' });
  evidence.lifecycle_after_resume = await evaluate("({hidden:document.hidden,playing:rev5FullViewer.state.playing,autoOrbit:rev5FullViewer.state.autoOrbit})");
  assert.equal(evidence.lifecycle_after_resume.hidden, true);
  assert.equal((await state()).playing, false); assert.equal((await state()).autoOrbit, false);
  await evaluate('rev5FullViewer.stop()');
  evidence.checks.push({ name: 'actual browser hidden lifecycle stops playback and orbit; hidden page correctly does not paint, so tested last without a frame wait' });
  assert.deepEqual(evidence.exceptions, []); assert.deepEqual(evidence.console_errors, []);
  assert.deepEqual(evidence.loader_errors, []); assert.deepEqual(evidence.external_requests, []);
  evidence.source_payload_sha256 = await evaluate('REV5_FULL_SCENE.payload_sha256');
  evidence.source_context_sha256 = await evaluate('REV5_FULL_SCENE.context_sha256');
  evidence.final_state = await state();
  evidence.status = 'PASS';
} catch (error) {
  evidence.status = 'FAIL'; evidence.failure = error.stack;
  process.exitCode = 1;
} finally {
  if (socket?.readyState === WebSocket.OPEN) socket.close();
  for (const waiter of pending.values()) clearTimeout(waiter.timeout);
  if (chrome.exitCode === null) chrome.kill('SIGTERM');
  await Promise.race([new Promise(resolve => { if (chrome.exitCode !== null) resolve(); else chrome.once('exit', resolve); }), sleep(5000)]);
  if (chrome.exitCode === null && chrome.signalCode === null) { chrome.kill('SIGKILL'); await new Promise(resolve => chrome.once('exit', resolve)); }
  evidence.owned_browser = { exit_code: chrome.exitCode, signal: chrome.signalCode, stopped: chrome.exitCode !== null || chrome.signalCode !== null };
  if (evidence.owned_browser.stopped) { await rm(profile, { recursive: true }); evidence.owned_browser.profile_removed = true; }
  evidence.completed_at = new Date().toISOString();
  const portable = JSON.stringify(evidence, null, 2).replaceAll(`file://${root}/`, 'file:///<workspace>/').replaceAll(`${root}/`, '');
  await writeFile(path.join(docs, 'browser-evidence.json'), portable + '\n');
  await writeFile(path.join(scratch, 'chrome-stderr.log'), stderr);
  console.log(JSON.stringify({ status: evidence.status, checks: evidence.checks.length, failure: evidence.failure, owned_browser: evidence.owned_browser }, null, 2));
}
