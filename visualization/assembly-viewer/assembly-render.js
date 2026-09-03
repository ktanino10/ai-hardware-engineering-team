import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { OBJLoader } from 'three/addons/loaders/OBJLoader.js';
import { PARTS, SCREWS, CAMERA_START } from './assembly-data.js';

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

const COLOR = { print3d: 0x8fb8d9, purchase: 0xd9a441 };

const selectable = []; // meshes with userData.part
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
  wrapper.position.set(0, part.y, 0);
  wrapper.add(group);
  wrapper.userData.part = part;
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
}

function buildPrimitivesAndScrews(){
  PARTS.filter(p => p.primitive).forEach(part => {
    const group = buildPrimitive(part);
    addSelectableWrapper(group, part);
  });
  SCREWS.forEach(s => {
    const part = PARTS.find(p => p.id === s.group);
    const baseY = part ? part.y : 0;
    for (let i = 0; i < s.count; i++){
      const angle = (i / s.count) * Math.PI * 2 + Math.PI / s.count;
      const x = Math.cos(angle) * s.radius, z = Math.sin(angle) * s.radius;
      const screw = buildScrew(s.dia, s.len);
      screw.position.set(x, baseY + s.y - baseY + 3, z);
      screw.userData.screwInfo = s;
      scene.add(screw);
    }
  });
}

meshParts.forEach(part => {
  loader.load(`models/${part.mesh}`, obj => {
    obj.traverse(child => { if (child.isMesh) child.material = materialFor(part.category); });
    const size = centerGeometry(obj);
    part._measuredSize = size;
    addSelectableWrapper(obj, part);
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
  `;
}

function deselect(){
  selectedGroup = null;
  highlightWrapper(null);
  document.getElementById('info').innerHTML =
    '<div class="placeholder">Click any part in the model to see its real name, dimensions, role in the assembly, and source.</div>';
}

function animate(){
  requestAnimationFrame(animate);
  controls.update();
  renderer.render(scene, camera);
}
animate();
