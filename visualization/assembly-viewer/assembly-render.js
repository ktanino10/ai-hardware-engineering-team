import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { OBJLoader } from 'three/addons/loaders/OBJLoader.js';
import { PARTS, SCREWS, CAMERA_START, RAW_BASE, BLOB_BASE, TREE_BASE, ASSEMBLED_LAYOUT } from './assembly-data.js';

const wrap = document.getElementById('canvas-wrap');
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x0a1628);

const camera = new THREE.PerspectiveCamera(45, 1, 1, 5000);
camera.position.set(...CAMERA_START.pos);

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
wrap.appendChild(renderer.domElement);

const controls = new OrbitControls(camera, renderer.domElement);
controls.target.set(...CAMERA_START.target);
controls.enableDamping = true;
controls.dampingFactor = 0.08;
controls.update();

// lighting — clean, opaque "engineering CAD" look, not a glowing hologram
scene.add(new THREE.AmbientLight(0xffffff, 0.65));
const key = new THREE.DirectionalLight(0xffffff, 0.9);
key.position.set(200, 400, 300);
scene.add(key);
const fill = new THREE.DirectionalLight(0xaecbff, 0.35);
fill.position.set(-250, 150, -200);
scene.add(fill);

function resize(){
  const w = wrap.clientWidth, h = wrap.clientHeight;
  camera.aspect = w / h;
  camera.updateProjectionMatrix();
  renderer.setSize(w, h);
}
window.addEventListener('resize', resize);
resize();

// ---- Static top-of-page "browse source" links + reference thumbnail ----
// Populated from JS (not hardcoded twice in index.html) using the same
// RAW_BASE/TREE_BASE constants assembly-data.js defines for everything
// else, so there's exactly one place the repo owner/branch string lives.
(function initStaticSourceLinks(){
  const sourceLinksEl = document.getElementById('source-links');
  if (sourceLinksEl){
    const dirs = [
      { label:'hardware/mechanical/', path:'hardware/mechanical/' },
      { label:'drawings/', path:'hardware/mechanical/drawings/' },
      { label:'stl/', path:'hardware/mechanical/stl/' },
    ];
    sourceLinksEl.innerHTML = dirs.map(d =>
      `<a href="${TREE_BASE}${d.path}" target="_blank" rel="noopener" title="Browse ${d.path} on GitHub">${d.label} ↗</a>`
    ).join('');
  }
  const refThumb = document.getElementById('ref-thumb');
  const refThumbImg = document.getElementById('ref-thumb-img');
  if (refThumb && refThumbImg){
    const full = `${RAW_BASE}hardware/mechanical/drawings/2d/assembled-unit-iso.png`;
    refThumb.href = full;
    refThumbImg.src = full;
  }
})();

const COLOR = { print3d: 0x8fb8d9, purchase: 0xd9a441 };

const selectable = []; // meshes with userData.part
const partWrappers = {}; // part.id -> its wrapper Group -- used by the new
  // Assemble/Explode layout functions and the part-detail modal's mini 3D
  // viewer (which clones a wrapper's already-loaded child group instead of
  // refetching geometry).
let selectedGroup = null;

function materialFor(cat){
  return new THREE.MeshStandardMaterial({
    color: COLOR[cat] || 0x999999, roughness: 0.55, metalness: cat === 'purchase' ? 0.35 : 0.05,
  });
}

function centerGeometry(object3d){
  const box = new THREE.Box3().setFromObject(object3d);
  const center = box.getCenter(new THREE.Vector3());
  object3d.traverse(child => {
    if (child.isMesh){
      child.geometry = child.geometry.clone();
      child.geometry.translate(-center.x, -center.y, -center.z);
    }
  });
  return box.getSize(new THREE.Vector3());
}

function addSelectableWrapper(group, part){
  const wrapper = new THREE.Group();
  // Position is no longer set here — computeAssembledLayout()/
  // computeExplodedLayout() + setLayout() (below) place every wrapper once
  // ALL parts (mesh-loaded and primitive) exist, since the new "assembled"
  // layout needs every part's real measured size up front, not just the
  // one being added right now. Until then the wrapper sits at the origin,
  // hidden behind the loading overlay.
  wrapper.add(group);
  wrapper.userData.part = part;
  partWrappers[part.id] = wrapper;
  scene.add(wrapper);
  group.traverse(child => { if (child.isMesh) selectable.push(child); child.userData = child.userData || {}; child.userData.rootWrapper = wrapper; });
  return wrapper;
}

function buildPrimitive(part){
  let geo;
  if (part.primitive === 'cylinder'){
    const rOuter = part.dOuter / 2;
    const rInner = part.dInner ? part.dInner / 2 : 0;
    if (rInner > 0){
      // ring (bearing): extrude an annulus shape
      const shape = new THREE.Shape();
      shape.absarc(0, 0, rOuter, 0, Math.PI * 2, false);
      const hole = new THREE.Path();
      hole.absarc(0, 0, rInner, 0, Math.PI * 2, true);
      shape.holes.push(hole);
      geo = new THREE.ExtrudeGeometry(shape, { depth: part.h, bevelEnabled: false, curveSegments: 48 });
      geo.rotateX(Math.PI / 2);
      geo.translate(0, -part.h / 2, 0);
    } else {
      geo = new THREE.CylinderGeometry(rOuter, rOuter, part.h, 48);
    }
  } else if (part.primitive === 'disk'){
    geo = new THREE.CylinderGeometry(part.d / 2, part.d / 2, part.h, 48);
  }
  const mesh = new THREE.Mesh(geo, materialFor(part.category));
  const group = new THREE.Group();
  group.add(mesh);
  return group;
}

function buildScrew(dia, len){
  const group = new THREE.Group();
  const shaftMat = new THREE.MeshStandardMaterial({ color: 0xcaa24a, roughness: 0.4, metalness: 0.7 });
  const shaft = new THREE.Mesh(new THREE.CylinderGeometry(dia / 2 * 0.55, dia / 2 * 0.55, len, 16), shaftMat);
  shaft.position.y = -len / 2;
  const head = new THREE.Mesh(new THREE.CylinderGeometry(dia / 2, dia / 2, dia * 0.55, 16), shaftMat);
  head.position.y = dia * 0.55 / 2;
  group.add(shaft, head);
  return group;
}

const loadingBar = document.getElementById('loading-bar');
const loadingEl = document.getElementById('loading');
const loader = new OBJLoader();

let loaded = 0;
const meshParts = PARTS.filter(p => p.mesh);
const total = meshParts.length;

function afterAllLoaded(){
  loadingEl.style.display = 'none';
  buildPrimitivesAndScrews();
  renderLegendCounts();
  computeAssembledLayout();
  computeExplodedLayout();
  setLayout('assembled', { animate:false }); // default on load = assembled, per spec
  updateLayoutToggleLabel();
}

function buildPrimitivesAndScrews(){
  PARTS.filter(p => p.primitive).forEach(part => {
    const group = buildPrimitive(part);
    // Real measured size for this primitive, from its own defining
    // dimensions (dOuter/d = full diameter, h = height) -- exact, not an
    // approximation, since these primitives are simple solids of
    // revolution built directly from those same numbers (buildPrimitive()
    // above). Mesh-loaded parts get the equivalent `_measuredSize` from
    // centerGeometry()/buildRadialAssembly()'s own real bounding-box
    // computation instead (see the load loop below) -- every part in
    // PARTS ends up with this field, one way or the other, which the new
    // Assemble/Explode layout functions depend on.
    const span = part.dOuter || part.d || 0;
    part._measuredSize = new THREE.Vector3(span, part.h, span);
    addSelectableWrapper(group, part);
  });
  SCREWS.forEach(s => {
    const part = PARTS.find(p => p.id === s.group);
    // LOCAL offset (relative to the parent part's own wrapper), derived
    // from this screw group's original authored world-Y minus its
    // parent's own original static `y` -- preserves the exact same
    // visual joint position this always had, but now expressed relative
    // to the parent instead of an absolute world coordinate, so the screw
    // correctly follows its parent part into whichever layout (assembled/
    // exploded/mid-transition) is currently active instead of staying
    // stuck at its old fixed spot.
    const localY = part ? (s.y - part.y) : s.y;
    const wrapper = partWrappers[s.group];
    for (let i = 0; i < s.count; i++){
      const angle = (i / s.count) * Math.PI * 2 + Math.PI / s.count;
      const x = Math.cos(angle) * s.radius, z = Math.sin(angle) * s.radius;
      const screw = buildScrew(s.dia, s.len);
      screw.position.set(x, localY + 3, z);
      screw.userData.screwInfo = s;
      (wrapper || scene).add(screw);
    }
  });
}

// Bakes a Z-up -> Y-up axis correction into a loaded mesh's own geometry
// (in LOCAL space, before centering/positioning). This project's
// OpenSCAD/STL export pipeline is Z-up (see assembly-data.js's own
// sourceUpAxis comment for the citation), but this scene is Y-up —
// loading such a mesh unrotated puts its real vertical extent on this
// scene's Z (depth) axis and one of its horizontal footprint extents on
// the scene's Y (up) axis instead. Parts NOT marked sourceUpAxis:'z' (the
// PCB, already Y-up from its KiCad glTF/GLB export) are left untouched.
function applyAxisFix(obj, part){
  if (part.sourceUpAxis !== 'z') return;
  obj.traverse(child => {
    if (child.isMesh){
      child.geometry = child.geometry.clone();
      child.geometry.rotateX(-Math.PI / 2);
    }
  });
}

// Some printed parts (e.g. the Pinch Guard) are one physical segment
// printed/molded N times and assembled into a full radially-symmetric
// part — see this part's own `quadrant` count in assembly-data.js. The
// source OBJ is only the single print-ready segment. This builds the
// N-instance assembled whole from that one segment, rotated about the
// vertical (Y) axis, WITHOUT the general centerGeometry() XZ-recentering
// (which would drag the segment's pivot away from the true rotational-
// symmetry axis at local X=0,Z=0 and break the reassembly). Only the
// segment's own vertical (thickness) extent is centered, matching what
// centerGeometry() does on that one axis.
function buildRadialAssembly(obj, part){
  const box = new THREE.Box3().setFromObject(obj);
  const centerY = (box.min.y + box.max.y) / 2;
  obj.traverse(child => { if (child.isMesh) child.geometry.translate(0, -centerY, 0); });
  const ringGroup = new THREE.Group();
  const step = (Math.PI * 2) / part.quadrant;
  for (let i = 0; i < part.quadrant; i++){
    const instance = (i === 0) ? obj : obj.clone(true);
    instance.rotation.y = i * step;
    ringGroup.add(instance);
  }
  return { group: ringGroup, size: box.getSize(new THREE.Vector3()) };
}

// Auto-fit framing: computes the REAL combined bounding box of every
// loaded part (mesh geometry for the printed/PCB parts, defined
// dimensions for the primitive purchased parts) once everything has
// loaded, and positions the camera to frame the whole assembly with a
// comfortable margin — instead of a hardcoded position that only matches
// today's dimensions and silently stops fitting the next time a part's
// geometry changes (e.g. a future enclosure resize or guard-radius
// change). Keeps the existing 45deg PerspectiveCamera and OrbitControls
// untouched — only recomputes where the camera starts and what it orbits
// around. CAMERA_START supplies the preferred VIEWING DIRECTION/ANGLE (so
// this still opens on the same near-isometric angle the original viewer
// used) and is the fallback position/target if the scene is ever empty.
function frameCameraToScene(){
  const box = new THREE.Box3();
  scene.traverse(obj => {
    if (obj.isGroup && obj.userData && obj.userData.part) box.expandByObject(obj);
  });
  if (box.isEmpty()) return;

  const sphere = box.getBoundingSphere(new THREE.Sphere());
  const { center, radius } = sphere;

  const dir = new THREE.Vector3(...CAMERA_START.pos).sub(new THREE.Vector3(...CAMERA_START.target));
  if (dir.lengthSq() < 1e-6) dir.set(1, 0.6, 1);
  dir.normalize();

  const vFov = THREE.MathUtils.degToRad(camera.fov);
  const hFov = 2 * Math.atan(Math.tan(vFov / 2) * camera.aspect);
  const effectiveFov = Math.min(vFov, hFov);
  const margin = 1.25; // breathing room so parts aren't touching the frame edge
  const distance = (radius / Math.sin(effectiveFov / 2)) * margin;

  camera.position.copy(center).addScaledVector(dir, distance);
  camera.near = Math.max(1, distance - radius * 4);
  camera.far = distance + radius * 4;
  camera.updateProjectionMatrix();
  controls.target.copy(center);
  controls.update();
}

// ---- Assemble / Explode layout ----
//
// Two real, source-grounded target positions are computed per part once
// everything has loaded (computeAssembledLayout()/computeExplodedLayout()
// below), stored on each PART OBJECT itself (`part._assembledPos`/
// `part._explodedPos`, same "mutate the real data object" pattern this
// file already uses for `part._measuredSize`). setLayout() then animates
// (or, on first load, jumps) every wrapper from wherever it currently is
// to the target for the requested state, and re-fits the camera once the
// move finishes — see docstrings below for what each layout actually
// means and what it disclosedly simplifies (full detail in README.md).

function partSize(part){
  return part._measuredSize || new THREE.Vector3(10, 10, 10); // fallback only; every real part gets a real _measuredSize from either the mesh-load loop below or buildPrimitivesAndScrews() above
}

// ASSEMBLED layout — a real-measured-height CONTACT STACK (each part's
// actual loaded-geometry bounding-box height, not a hardcoded guess),
// following the real build sequence in
// hardware/mechanical/assembly-instructions.md: a shared vertical "spine"
// (StandPlate -> Bearing -> BaseAssembly), the PinchGuard "guard" sharing
// StandPlate's own height (assembled "around the stand plate" per that
// document's §4.5 step 8), and two branches rising from the spine's own
// top — pcbBay (PCB -> PcbLid) and flywheelBay (Motor -> HubCollar ->
// Flywheel -> ContainmentCap) — separated horizontally by
// ASSEMBLED_LAYOUT.baySeparationHalfZ so they don't visually overlap.
// Disclosed simplification (see README "Known limitations"): this is a
// single-axis stack per branch, not a byte-exact 3D reconstruction — the
// containment cap and PCB lid are shown stacked ABOVE their contents in
// real installation order, not volumetrically nested/enclosing around
// them, and the bay-separation offset is an approximation (see
// ASSEMBLED_LAYOUT's own comment in assembly-data.js for exactly what it
// assumes).
function computeAssembledLayout(){
  const byGroup = { spine: [], guard: [], pcbBay: [], flywheelBay: [] };
  PARTS.forEach(part => { if (part.stackGroup && byGroup[part.stackGroup]) byGroup[part.stackGroup].push(part); });
  Object.values(byGroup).forEach(list => list.sort((a, b) => a.stackIndex - b.stackIndex));

  let y = 0;
  byGroup.spine.forEach(part => {
    const h = partSize(part).y;
    part._assembledPos = { x: 0, y: y + h / 2, z: 0 };
    y += h;
  });
  const spineTopY = y;

  const standPlate = byGroup.spine[0];
  byGroup.guard.forEach(part => {
    part._assembledPos = { x: 0, y: standPlate ? standPlate._assembledPos.y : partSize(part).y / 2, z: 0 };
  });

  [['pcbBay', 1], ['flywheelBay', -1]].forEach(([key, sign]) => {
    let yy = spineTopY;
    byGroup[key].forEach(part => {
      const h = partSize(part).y;
      part._assembledPos = { x: 0, y: yy + h / 2, z: sign * ASSEMBLED_LAYOUT.baySeparationHalfZ };
      yy += h;
    });
  });
}

// EXPLODED layout — NOW a horizontal SINGLE ROW (deliberate change from
// this viewer's original vertical stack, per direct human request). Every
// part's pre-existing `y` field (assembly-data.js — left byte-identical,
// not renumbered) is read ONLY as a relative ORDER key here, exactly
// matching the real, already-reviewed exploded-view PNG's own part order
// — not as a literal world-Y position any more. Parts are laid out
// left-to-right along world X using each part's real measured width plus
// an artistic gap (EXPLODE_GAP, chosen for legibility, same precedent as
// this project's original vertical exploded spacing), then re-centered so
// the whole row straddles x=0 for a balanced camera view. All parts share
// world Y=0 and Z=0 — a true single row, not a grid or a depth stagger.
const EXPLODE_GAP = 20; // mm, artistic — see comment above
function computeExplodedLayout(){
  const ordered = [...PARTS].sort((a, b) => a.y - b.y);
  let x = 0;
  ordered.forEach((part, i) => {
    const w = partSize(part).x;
    if (i === 0){
      x = 0;
    } else {
      const prev = ordered[i - 1];
      x += partSize(prev).x / 2 + EXPLODE_GAP + w / 2;
    }
    part._explodedPos = { x, y: 0, z: 0 };
  });
  const xs = ordered.map(p => p._explodedPos.x);
  const mid = (Math.min(...xs) + Math.max(...xs)) / 2;
  ordered.forEach(part => { part._explodedPos.x -= mid; });
}

let currentLayoutState = 'assembled';
let layoutTransition = null; // { start, duration, entries:[{wrapper, from, to}] }

// Applies the given layout ('assembled'|'exploded') to every part wrapper.
// On first load (opts.animate===false) jumps straight there; otherwise
// tweens over a short, smooth transition (desirable, not mandatory, per
// spec) and re-fits the camera once the move finishes — "the camera
// should presumably re-fit after each state change, not stay stuck
// framing the old layout" is honored by calling frameCameraToScene() here,
// not by trying to keep it continuously updated mid-transition (which
// would fight a user's own manual orbit/zoom while parts are moving).
function setLayout(state, opts = {}){
  const animateIt = opts.animate !== false;
  currentLayoutState = state;
  const entries = [];
  PARTS.forEach(part => {
    const wrapper = partWrappers[part.id];
    const target = state === 'assembled' ? part._assembledPos : part._explodedPos;
    if (!wrapper || !target) return;
    entries.push({ wrapper, from: wrapper.position.clone(), to: new THREE.Vector3(target.x, target.y, target.z) });
  });
  if (!animateIt){
    entries.forEach(e => e.wrapper.position.copy(e.to));
    frameCameraToScene();
    return;
  }
  layoutTransition = { start: performance.now(), duration: 650, entries };
}

function easeInOutQuad(t){
  return t < 0.5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2;
}

function updateLayoutTransition(now){
  if (!layoutTransition) return;
  const t = Math.min(1, (now - layoutTransition.start) / layoutTransition.duration);
  const eased = easeInOutQuad(t);
  layoutTransition.entries.forEach(e => e.wrapper.position.lerpVectors(e.from, e.to, eased));
  if (t >= 1){
    layoutTransition = null;
    frameCameraToScene();
  }
}

function updateLayoutToggleLabel(){
  const btn = document.getElementById('layout-toggle');
  if (!btn) return;
  btn.textContent = currentLayoutState === 'assembled' ? '⛶ Explode View' : '⛝ Assemble View';
}

const layoutToggleBtn = document.getElementById('layout-toggle');
if (layoutToggleBtn){
  layoutToggleBtn.addEventListener('click', () => {
    const next = currentLayoutState === 'assembled' ? 'exploded' : 'assembled';
    setLayout(next, { animate:true });
    updateLayoutToggleLabel();
  });
}

meshParts.forEach(part => {
  loader.load(`models/${part.mesh}`, obj => {
    obj.traverse(child => { if (child.isMesh) child.material = materialFor(part.category); });
    applyAxisFix(obj, part);
    let renderObject, size;
    if (part.quadrant && part.quadrant > 1){
      ({ group: renderObject, size } = buildRadialAssembly(obj, part));
    } else {
      size = centerGeometry(obj);
      renderObject = obj;
    }
    part._measuredSize = size;
    addSelectableWrapper(renderObject, part);
    loaded++;
    loadingBar.style.width = Math.round((loaded / total) * 100) + '%';
    if (loaded === total) afterAllLoaded();
  }, undefined, err => {
    console.error('Failed to load', part.mesh, err);
    loaded++;
    if (loaded === total) afterAllLoaded();
  });
});

function renderLegendCounts(){ /* legend is static in HTML; nothing dynamic needed */ }

// ---- selection / info panel ----
const raycaster = new THREE.Raycaster();
const mouse = new THREE.Vector2();

renderer.domElement.addEventListener('click', (event) => {
  const rect = renderer.domElement.getBoundingClientRect();
  mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
  mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
  raycaster.setFromCamera(mouse, camera);
  const hits = raycaster.intersectObjects(selectable, false);
  if (hits.length > 0){
    const wrapper = hits[0].object.userData.rootWrapper;
    selectPart(wrapper.userData.part, wrapper);
  } else {
    deselect();
  }
});

function highlightWrapper(wrapper){
  scene.traverse(obj => {
    if (obj.isMesh && obj.userData.rootWrapper){
      const isSel = wrapper && obj.userData.rootWrapper === wrapper;
      obj.material.emissive = new THREE.Color(isSel ? 0x2a4a6a : 0x000000);
    }
  });
}

function selectPart(part, wrapper){
  selectedGroup = wrapper;
  highlightWrapper(wrapper);
  const panel = document.getElementById('info');
  panel.innerHTML = `
    <h2>${part.name}</h2>
    <div class="ref">${part.ref}</div>
    <div class="cat ${part.category}">${part.category === 'print3d' ? '3D PRINT' : 'PURCHASE'}</div>
    <div class="field"><div class="k">Dimensions</div><div class="v">${part.dims}</div></div>
    <div class="field"><div class="k">Role in this assembly</div><div class="v">${part.role}</div></div>
    <div class="field"><div class="k">Source</div><div class="v">${part.source}</div></div>
    <button type="button" class="open-modal-btn" id="reopen-modal-btn">🔍 2D drawings, 3D inspector &amp; links</button>
  `;
  document.getElementById('reopen-modal-btn').addEventListener('click', () => openPartModal(part));
  // Opens directly on click, in addition to (not instead of) the sidebar
  // update above — matches "press each part -> its drawings/angles/
  // description/purchase-and-CAD links appear" literally. The sidebar
  // itself is unchanged/still updates every click, same as before this
  // pass, so nothing here regresses its existing behavior.
  openPartModal(part);
}

function deselect(){
  selectedGroup = null;
  highlightWrapper(null);
  document.getElementById('info').innerHTML =
    '<div class="placeholder">Click any part in the model to see its real name, dimensions, role in the assembly, and source.</div>';
  closePartModal();
}

// ---- Part-detail modal ----
//
// Opens directly on click (see selectPart() above), showing: the same
// textual info as the sidebar (auto-linkified — see linkifyRepoPaths()),
// real 2D drawings or an explicit N/A disclosure, a small orbitable mini
// 3D viewer that clones this part's already-loaded geometry (no second
// network fetch — see ensureMiniViewer()/openMiniViewer() below), and
// real GitHub links for its CAD source, drafting sheet, datasheet/
// purchase URL, and evidence-log row.

const REPO_PATH_RE = /\b((?:hardware|bom|datasheets|validation|requirements|docs|firmware)\/[A-Za-z0-9_\-./]+[A-Za-z0-9_\-])/g;
// Turns an already-trusted, developer-authored string's own repo-relative
// path mentions (e.g. "validation/open-issues.md", already present in
// assembly-data.js's role/source text) into real GitHub links — addresses
// the human's original, broader "let me jump from any displayed detail to
// where it's really documented" request across the EXISTING info fields,
// not just the new per-part link fields below. Deliberately conservative:
// only matches a path that already starts with one of this repo's real
// top-level directories, so it can't mis-linkify arbitrary prose.
function linkifyRepoPaths(text){
  if (!text) return text;
  return text.replace(REPO_PATH_RE, (m) => `<a href="${BLOB_BASE}${m}" target="_blank" rel="noopener">${m}</a>`);
}

function modalFieldsHtml(part){
  return `
    <div class="field"><div class="k">Dimensions</div><div class="v">${linkifyRepoPaths(part.dims)}</div></div>
    <div class="field"><div class="k">Role in this assembly</div><div class="v">${linkifyRepoPaths(part.role)}</div></div>
    <div class="field"><div class="k">Source</div><div class="v">${linkifyRepoPaths(part.source)}</div></div>
  `;
}

function cadLinksHtml(part){
  if (part.cadFile){
    return `<div class="modal-link-row"><div class="lbl">CAD source</div>
      <a href="${BLOB_BASE}${part.cadFile.path}" target="_blank" rel="noopener">${part.cadFile.path}</a>
      <div class="na">${part.cadFile.label}</div></div>`;
  }
  if (part.cadModules && part.cadModules.length){
    const rows = part.cadModules.map(m => {
      const link = `<a href="${BLOB_BASE}hardware/mechanical/bench-imu-01-enclosure.scad#L${m.line}" target="_blank" rel="noopener"><code>${m.name}</code></a> (line ${m.line})`;
      const note = m.referenceOnly ? `<div class="na">Reference-only visualization stand-in — ${m.referenceNote}.</div>` : '';
      return `<div>${link}</div>${note}`;
    }).join('');
    return `<div class="modal-link-row"><div class="lbl">OpenSCAD module${part.cadModules.length > 1 ? 's' : ''} — bench-imu-01-enclosure.scad</div>${rows}</div>`;
  }
  return `<div class="modal-link-row"><div class="lbl">CAD source</div><div class="na">No OpenSCAD module models this part.</div></div>`;
}

function draftingSheetHtml(part){
  if (part.draftingSheet){
    const ds = part.draftingSheet;
    return `<div class="modal-link-row"><div class="lbl">Drafting sheet</div>
      <a href="${BLOB_BASE}hardware/mechanical/drawings/drafting-sheets/${ds.pdf}" target="_blank" rel="noopener">PDF ↗</a>
      &middot; <a href="${BLOB_BASE}hardware/mechanical/drawings/drafting-sheets/scad/${ds.scad}" target="_blank" rel="noopener">projection script ↗</a></div>`;
  }
  if (part.drawing2d){
    return `<div class="modal-link-row"><div class="lbl">Drafting sheet</div>
      <div class="na">No formal dimensioned drafting sheet exists for this part — only 3 of the 5 printed parts have one (stand plate, PCB lid, containment cap).</div></div>`;
  }
  return '';
}

function datasheetLinksHtml(part){
  if (part.datasheet){
    return `<div class="modal-link-row"><div class="lbl">Purchase source</div>
      <a href="${part.datasheet.officialUrl}" target="_blank" rel="noopener">${part.datasheet.officialUrl}</a>
      <div class="na">Datasheet metadata record: <a href="${BLOB_BASE}${part.datasheet.file}" target="_blank" rel="noopener">${part.datasheet.file}</a></div></div>`;
  }
  if (part.category === 'purchase'){
    return `<div class="modal-link-row"><div class="lbl">Purchase source</div>
      <div class="na">Not sourced to a specific vendor/MPN anywhere in this repo (disclosed ASSUMPTION — see "Source" above). No datasheet metadata record exists for it.</div></div>`;
  }
  if (part.id === 'PCB'){
    return `<div class="modal-link-row"><div class="lbl">Fabrication source</div>
      <div>Not a purchased catalog part — a real KiCad design, fabricated from
      <a href="${BLOB_BASE}hardware/pcb/bench-imu-01/bench-imu-01.kicad_pcb" target="_blank" rel="noopener">hardware/pcb/bench-imu-01/bench-imu-01.kicad_pcb</a>
      (Gerbers: <a href="${TREE_BASE}hardware/pcb/bench-imu-01/fab" target="_blank" rel="noopener">hardware/pcb/bench-imu-01/fab/</a>).</div></div>`;
  }
  return '';
}

function evidenceLinksHtml(part){
  if (part.evidenceIds && part.evidenceIds.length){
    const rows = part.evidenceIds.map(e => {
      const link = `<a href="${BLOB_BASE}datasheets/evidence-log.md?plain=1#L${e.line}" target="_blank" rel="noopener"><code>${e.id}</code></a> (line ${e.line})`;
      const note = e.note ? `<div class="na">${e.note}</div>` : '';
      return `<div>${link}</div>${note}`;
    }).join('');
    return `<div class="modal-link-row"><div class="lbl">Evidence ID — datasheets/evidence-log.md</div>${rows}</div>`;
  }
  if (part.category === 'purchase'){
    return `<div class="modal-link-row"><div class="lbl">Evidence ID — datasheets/evidence-log.md</div>
      <div class="na">No Evidence ID / vendor on file for this part — confirmed by searching the log, no match
      (<a href="${BLOB_BASE}datasheets/evidence-log.md" target="_blank" rel="noopener">view the log ↗</a>).</div></div>`;
  }
  return `<div class="modal-link-row"><div class="lbl">Evidence ID — datasheets/evidence-log.md</div>
    <div class="na">No Evidence ID is cited in this part's own "Source" field above — its PETG material is a disclosed ASSUMPTION, not independently DS-cited for this specific part
    (<a href="${BLOB_BASE}datasheets/evidence-log.md" target="_blank" rel="noopener">view the log ↗</a>).</div></div>`;
}

function drawingsHtml(part){
  if (part.drawing2d){
    const views = ['front', 'side', 'top'].filter(v => part.drawing2d[v]);
    const grid = views.map(v => {
      const src = `${RAW_BASE}hardware/mechanical/drawings/2d/${part.drawing2d[v]}`;
      return `<div class="modal-drawing-item"><a href="${src}" target="_blank" rel="noopener">
        <img src="${src}" alt="${part.name} — ${v} view" loading="lazy"></a><div class="cap">${v}</div></div>`;
    }).join('');
    const draftingImg = part.draftingSheet
      ? `<div class="modal-drawing-item"><a href="${BLOB_BASE}hardware/mechanical/drawings/drafting-sheets/${part.draftingSheet.pdf}" target="_blank" rel="noopener">
          <img src="${RAW_BASE}hardware/mechanical/drawings/drafting-sheets/${part.draftingSheet.png}" alt="${part.name} — dimensioned drafting sheet" loading="lazy"></a><div class="cap">drafting sheet</div></div>`
      : '';
    return `<h3>2D drawings</h3><div class="modal-drawing-grid">${grid}${draftingImg}</div>`;
  }
  if (part.id === 'PCB'){
    return `<h3>2D drawings</h3><div class="modal-na-box">N/A in hardware/mechanical/drawings/2d/ — that directory covers the 5 printed/enclosure parts only, not the PCB. See its own rendered board view below, and the <a href="../circuit-viewer/index.html">Circuit &amp; Current-Flow Viewer</a> for full schematic/net-level detail.
      <div class="modal-drawing-grid" style="margin-top:10px">
        <div class="modal-drawing-item"><a href="${RAW_BASE}hardware/pcb/bench-imu-01/bench-imu-01-3d.png" target="_blank" rel="noopener">
          <img src="${RAW_BASE}hardware/pcb/bench-imu-01/bench-imu-01-3d.png" alt="PCB rendered board view" loading="lazy"></a><div class="cap">3D render</div></div>
      </div></div>`;
  }
  return `<h3>2D drawings</h3><div class="modal-na-box">N/A — purchased part; no 2D orthographic drawing exists for it (hardware/mechanical/drawings/2d/ covers the 5 printed/enclosure parts only).</div>`;
}

function openPartModal(part){
  document.getElementById('modal-title').textContent = part.name;
  document.getElementById('modal-ref').innerHTML =
    `${part.ref || ''} <span class="cat ${part.category}">${part.category === 'print3d' ? '3D PRINT' : 'PURCHASE'}</span>`;
  document.getElementById('modal-info').innerHTML = modalFieldsHtml(part);
  document.getElementById('modal-links').innerHTML =
    `<h3>Repository links</h3>${cadLinksHtml(part)}${draftingSheetHtml(part)}${datasheetLinksHtml(part)}${evidenceLinksHtml(part)}`;
  document.getElementById('modal-drawings').innerHTML = drawingsHtml(part);
  document.getElementById('modal-backdrop').hidden = false;
  openMiniViewer(part);
}

function closePartModal(){
  const backdrop = document.getElementById('modal-backdrop');
  if (backdrop.hidden) return;
  backdrop.hidden = true;
  closeMiniViewer();
}

document.getElementById('modal-close').addEventListener('click', closePartModal);
document.getElementById('modal-backdrop').addEventListener('click', (e) => {
  if (e.target.id === 'modal-backdrop') closePartModal();
});
window.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') closePartModal();
});

// ---- Mini 3D viewer (inside the modal) ----
//
// Lazily created once, reused across opens. Shows the SAME already-
// loaded/axis-fixed/centered (and, for the Pinch Guard, already radially
// reconstructed) geometry the main scene uses for this part — reusing the
// same geometry/material objects BY REFERENCE (see cloneForMiniViewer()
// below), without a second network fetch or a second copy of vertex data.
// Consequently geometries/materials are NEVER disposed when the modal
// closes (that would free the GPU data the MAIN scene is still using) —
// closeMiniViewer() only removes the cloned Object3D from the mini scene.
//
// A plain THREE.Object3D#clone(true)/#copy() cannot be used for this,
// found (not assumed) by direct testing: every mesh in the main scene
// carries `userData.rootWrapper` (a back-reference to its own wrapper
// Group, set in addSelectableWrapper() above for raycaster hit-testing) —
// three.js's own Object3D.prototype.copy() round-trips userData through
// `JSON.parse(JSON.stringify(source.userData))`, which throws
// "JSON.stringify cannot serialize cyclic structures." the instant it
// meets that back-reference (confirmed via a direct reproduction in the
// browser console, not guessed from the stack trace alone). This is
// three.js's own limitation, not a bug in this codebase's use of
// `userData` — cloneForMiniViewer() below sidesteps it entirely by
// building a fresh Group/Mesh tree by hand (copying only transform +
// SHARED geometry/material references, no userData at all — the mini
// viewer never needs to raycast/select, so it needs none of that).
function cloneForMiniViewer(source){
  const target = source.isMesh ? new THREE.Mesh(source.geometry, source.material) : new THREE.Group();
  target.position.copy(source.position);
  target.quaternion.copy(source.quaternion);
  target.scale.copy(source.scale);
  source.children.forEach(child => target.add(cloneForMiniViewer(child)));
  return target;
}

let miniScene, miniCamera, miniRenderer, miniControls, miniContent;

function ensureMiniViewer(){
  if (miniRenderer) return;
  miniScene = new THREE.Scene();
  miniScene.background = new THREE.Color(0x050c18);
  miniCamera = new THREE.PerspectiveCamera(45, 1, 0.1, 5000);
  const canvas = document.getElementById('modal-3d-canvas');
  miniRenderer = new THREE.WebGLRenderer({ canvas, antialias: true });
  miniRenderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  miniControls = new OrbitControls(miniCamera, miniRenderer.domElement);
  miniControls.enableDamping = true;
  miniControls.dampingFactor = 0.1;
  miniScene.add(new THREE.AmbientLight(0xffffff, 0.7));
  const miniKey = new THREE.DirectionalLight(0xffffff, 0.95);
  miniKey.position.set(2, 4, 3);
  miniScene.add(miniKey);
  const miniFill = new THREE.DirectionalLight(0xaecbff, 0.4);
  miniFill.position.set(-3, 1.5, -2);
  miniScene.add(miniFill);
}

function resizeMiniViewer(){
  if (!miniRenderer) return;
  const wrapEl = document.getElementById('modal-3d-wrap');
  const w = wrapEl.clientWidth, h = wrapEl.clientHeight;
  if (w === 0 || h === 0) return;
  miniCamera.aspect = w / h;
  miniCamera.updateProjectionMatrix();
  miniRenderer.setSize(w, h, false);
}

// Fits the mini camera to `obj`'s real AABB corners (not just a bounding
// SPHERE, unlike the main scene's frameCameraToScene()) — needed because
// this panel's aspect ratio is much more extreme (short and wide) than
// the main viewport's, so a sphere-based fit (rotationally symmetric,
// blind to the panel's actual shape) left the part looking tiny with
// large empty margins on a wide panel (confirmed by direct pixel-coverage
// measurement while testing, not assumed). For each of the object's 8
// world-space bounding-box corners, computes the minimum camera distance
// (along the fixed view `dir`) that keeps that corner inside BOTH the
// horizontal and vertical field of view, then uses the largest such
// distance across all 8 — the tightest distance that still fits the
// whole box, for whatever aspect ratio this panel actually has.
function frameMiniCameraToObject(obj){
  const box = new THREE.Box3().setFromObject(obj);
  if (box.isEmpty()) return;
  const center = box.getCenter(new THREE.Vector3());
  const dir = new THREE.Vector3(1, 0.6, 1).normalize();
  const worldUp = new THREE.Vector3(0, 1, 0);
  const right = new THREE.Vector3().crossVectors(dir, worldUp).normalize();
  const up = new THREE.Vector3().crossVectors(right, dir).normalize();
  const vFov = THREE.MathUtils.degToRad(miniCamera.fov);
  const hFov = 2 * Math.atan(Math.tan(vFov / 2) * miniCamera.aspect);
  const tanH = Math.tan(hFov / 2), tanV = Math.tan(vFov / 2);
  const min = box.min, max = box.max;
  const corners = [
    new THREE.Vector3(min.x, min.y, min.z), new THREE.Vector3(max.x, min.y, min.z),
    new THREE.Vector3(min.x, max.y, min.z), new THREE.Vector3(max.x, max.y, min.z),
    new THREE.Vector3(min.x, min.y, max.z), new THREE.Vector3(max.x, min.y, max.z),
    new THREE.Vector3(min.x, max.y, max.z), new THREE.Vector3(max.x, max.y, max.z),
  ];
  let distance = 0.01;
  const v = new THREE.Vector3();
  corners.forEach(corner => {
    v.copy(corner).sub(center);
    const depth = v.dot(dir);
    const h = Math.abs(v.dot(right));
    const vert = Math.abs(v.dot(up));
    distance = Math.max(distance, depth + h / tanH, depth + vert / tanV);
  });
  distance *= 1.06; // small breathing-room margin (tighter than the main scene's 1.25 — this panel is small, every pixel of the part matters more here)
  const diag = box.getSize(new THREE.Vector3()).length();
  miniCamera.position.copy(center).addScaledVector(dir, distance);
  miniCamera.near = Math.max(0.01, distance - diag * 2);
  miniCamera.far = distance + diag * 2 + 1;
  miniCamera.updateProjectionMatrix();
  miniControls.target.copy(center);
  miniControls.update();
}

function openMiniViewer(part){
  ensureMiniViewer();
  if (miniContent){ miniScene.remove(miniContent); miniContent = null; }
  const wrapper = partWrappers[part.id];
  const source = wrapper && wrapper.children[0];
  if (!source) return;
  miniContent = cloneForMiniViewer(source);
  miniContent.position.set(0, 0, 0);
  miniScene.add(miniContent);
  resizeMiniViewer();
  frameMiniCameraToObject(miniContent);
}

function closeMiniViewer(){
  if (miniContent && miniScene){ miniScene.remove(miniContent); miniContent = null; }
}

window.addEventListener('resize', () => {
  if (!document.getElementById('modal-backdrop').hidden) resizeMiniViewer();
});

function animate(){
  requestAnimationFrame(animate);
  controls.update();
  updateLayoutTransition(performance.now());
  renderer.render(scene, camera);
  if (miniRenderer && !document.getElementById('modal-backdrop').hidden){
    miniControls.update();
    miniRenderer.render(miniScene, miniCamera);
  }
}
animate();
