/*
 * circuit-render.js — renders COMPONENTS/WIRES (circuit-data.js) into the SVG,
 * handles language toggle, mode tabs, and the click-to-inspect info panel.
 */
const SVGNS = "http://www.w3.org/2000/svg";
let currentLang = 'ja';
let currentMode = 'power';
let selectedId = null;

function byId(id){
  return COMPONENTS.find(c => c.id === id) || (FUTURE_BOX.id === id ? FUTURE_BOX : null);
}
function isHoriz(side){ return side === 'left' || side === 'right'; }
function isVert(side){ return side === 'top' || side === 'bottom'; }

function anchor(box, side, off = 0){
  if (side === 'left')   return [box.x, box.y + box.h/2 + off];
  if (side === 'right')  return [box.x + box.w, box.y + box.h/2 + off];
  if (side === 'top')    return [box.x + box.w/2 + off, box.y];
  if (side === 'bottom') return [box.x + box.w/2 + off, box.y + box.h];
}

function pathFor(w){
  const a = byId(w.from), b = byId(w.to);
  if (!a || !b) return null;
  const off1 = w.xoff !== undefined || w.yoff !== undefined
    ? (isHoriz(w.fromSide) ? (w.yoff||0) : (w.xoff||0)) : 0;
  const off2raw = w.toXoff !== undefined ? w.toXoff : (w.toYoff !== undefined ? w.toYoff : (isHoriz(w.toSide) ? w.yoff : w.xoff));
  const off2 = off2raw || 0;
  const [x1,y1] = anchor(a, w.fromSide, off1);
  const [x2,y2] = anchor(b, w.toSide, off2);
  let d;
  if (isHoriz(w.fromSide) && isHoriz(w.toSide)){
    const midx = (x1+x2)/2;
    d = `M ${x1},${y1} L ${midx},${y1} L ${midx},${y2} L ${x2},${y2}`;
  } else if (isVert(w.fromSide) && isVert(w.toSide)){
    const midy = (y1+y2)/2;
    d = `M ${x1},${y1} L ${x1},${midy} L ${x2},${midy} L ${x2},${y2}`;
  } else if (isHoriz(w.fromSide) && isVert(w.toSide)){
    d = `M ${x1},${y1} L ${x2},${y1} L ${x2},${y2}`;
  } else if (isVert(w.fromSide) && isHoriz(w.toSide)){
    d = `M ${x1},${y1} L ${x1},${y2} L ${x2},${y2}`;
  } else {
    d = `M ${x1},${y1} L ${x2},${y2}`;
  }
  return { d, x1, y1, x2, y2 };
}

function el(tag, attrs = {}, parent){
  const e = document.createElementNS(SVGNS, tag);
  for (const k in attrs) e.setAttribute(k, attrs[k]);
  if (parent) parent.appendChild(e);
  return e;
}

function pulseColor(cat){
  return getComputedStyle(document.documentElement).getPropertyValue(
    { power5v:'--pow5', powervm:'--powvm', motorphase:'--motor', i2c:'--i2c',
      uart:'--uart', ctrl:'--ctrl', feedback:'--fb', future:'--future', debug:'--debug' }[cat] || '--dim'
  ).trim();
}

function renderSVG(){
  const svg = document.getElementById('circuit');
  svg.innerHTML = '';
  const wireLayer = el('g', {id:'wires'}, svg);
  const boxLayer  = el('g', {id:'boxes'}, svg);

  // wires + pulses
  WIRES.forEach((w, i) => {
    const p = pathFor(w);
    if (!p) return;
    const pid = `wire-${i}`;
    el('path', { id: pid, class: `wire cat-${w.category}`, d: p.d }, wireLayer);
    if (w.dir){
      const speed = w.category === 'motorphase' ? 0.9 : (w.category === 'uart' ? 2.6 : 1.6);
      const c = el('circle', { r: w.category==='motorphase'?4.5:3.2, class:'pulse', fill: `var(${ {power5v:'--pow5',powervm:'--powvm',motorphase:'--motor',i2c:'--i2c',uart:'--uart',ctrl:'--ctrl',feedback:'--fb',future:'--future'}[w.category] || '--dim' })`, style:`color:${''}` }, wireLayer);
      const anim = el('animateMotion', { dur:`${speed}s`, repeatCount:'indefinite', keyPoints: w.dir===1?'0;1':'1;0', keyTimes:'0;1' }, c);
      const mpath = el('mpath', {}, anim);
      mpath.setAttributeNS('http://www.w3.org/1999/xlink', 'href', `#${pid}`);
      c.dataset.cat = w.category;
    }
  });

  // future ghost box (only meaningful in mode3, still rendered so wires have an anchor)
  [...COMPONENTS, FUTURE_BOX].forEach(box => {
    const isFuture = box.id === 'CTRL';
    const g = el('g', { class:`box${box.hub?' hub':''}${isFuture?' future-box':''}`, 'data-id':box.id }, boxLayer);
    el('rect', { x:box.x, y:box.y, width:box.w, height:box.h, rx:7,
      'stroke-dasharray': isFuture ? '6,4' : null }, g);
    if (isFuture){ g.querySelector('rect').setAttribute('stroke-dasharray','6,4'); g.style.opacity=0; g.classList.add('badge-future'); }
    const refT = el('text', { x:box.x+8, y:box.y+15, class:'ref' }, g);
    refT.textContent = box.ref;
    const nameCharW = box.w > 140 ? 8.6 : 8.2;
    const nameMaxChars = Math.max(6, Math.floor((box.w-16)/nameCharW));
    const nameMaxLines = box.h >= 90 ? 2 : 1;
    const nameLines = wrapText(currentLang==='ja'?box.nameJa:box.nameEn, nameMaxChars, nameMaxLines);
    multilineText(g, box.x+8, box.y+31, nameLines, 14, 'name');
    const roleTop = box.y + 31 + (nameLines.length>1 ? 14 : 0) + 16;
    const roleAvail = box.y + box.h - 6 - roleTop;
    const roleMaxLines = Math.max(0, Math.floor(roleAvail / 11));
    if (roleMaxLines > 0 && box.w > 90){
      const roleMaxChars = Math.max(8, Math.floor((box.w-16)/6.6));
      const roleLines = wrapText((currentLang==='ja'?box.roleJa:box.roleEn), roleMaxChars, roleMaxLines);
      multilineText(g, box.x+8, roleTop, roleLines, 11, 'role');
    }
    g.style.cursor = 'pointer';
    g.addEventListener('click', () => selectComponent(box.id));
  });

  applyModeVisibility();
  highlightSelected();
}

function wrapText(s, maxCharsPerLine, maxLines){
  if (!s || maxCharsPerLine < 3 || maxLines < 1) return [];
  // Prefer word-boundary wrapping (reads naturally for English), but only
  // when every space-split token individually fits the line budget. A pure
  // Japanese sentence has no spaces (one giant "word") and safely falls
  // through to char-chunking below; a mixed JA+EN sentence containing one
  // long JA run also falls through, avoiding the overflow bug that a
  // naive/unconditional word-wrap caused for mixed-language source strings.
  const words = s.split(' ');
  const wordWrapSafe = words.length > 1 && words.every(w => w.length <= maxCharsPerLine);
  let lines = [];
  let joiner = '';
  if (wordWrapSafe){
    joiner = ' ';
    let cur = '';
    for (const w of words){
      const trial = cur ? cur + ' ' + w : w;
      if (trial.length > maxCharsPerLine && cur){
        lines.push(cur);
        cur = w;
      } else {
        cur = trial;
      }
      if (lines.length >= maxLines) break;
    }
    if (cur && lines.length < maxLines) lines.push(cur);
  } else {
    for (let i = 0; i < s.length && lines.length < maxLines; i += maxCharsPerLine){
      lines.push(s.slice(i, i + maxCharsPerLine));
    }
  }
  const consumedLen = lines.join(joiner).length;
  if (consumedLen < s.length && lines.length){
    let last = lines[lines.length - 1];
    last = last.replace(/…$/, '');
    last = last.length > 1 ? last.slice(0, -1) + '…' : last + '…';
    lines[lines.length - 1] = last;
  }
  return lines;
}

function multilineText(parent, x, y, lines, lineHeight, cls){
  const t = el('text', { x, y, class: cls }, parent);
  lines.forEach((line, i) => {
    const tspan = el('tspan', { x, dy: i === 0 ? 0 : lineHeight }, t);
    tspan.textContent = line;
  });
  return t;
}

function selectComponent(id){
  selectedId = id;
  highlightSelected();
  renderInfo(byId(id));
}

function highlightSelected(){
  document.querySelectorAll('#boxes .box').forEach(g => {
    g.classList.toggle('selected', g.dataset.id === selectedId);
  });
}

function renderInfo(box){
  const panel = document.getElementById('info');
  if (!box){ panel.innerHTML = ''; return; }
  const L = currentLang;
  const name = L==='ja' ? box.nameJa : box.nameEn;
  const role = L==='ja' ? box.roleJa : box.roleEn;
  panel.innerHTML = `
    <h2>${name}</h2>
    <div class="ref">${box.ref}${box.ref!=='—' ? ' &middot; ' : ''}${box.part||''}</div>
    <div class="field"><div class="k">${L==='ja'?'役割':'Role in this circuit'}</div><div class="v">${role}</div></div>
    ${box.datasheet ? `<div class="field"><div class="k">Datasheet</div><div class="v"><a href="${box.datasheet}" target="_blank" rel="noopener">${L==='ja'?'一次資料を開く':'Open primary datasheet'} ↗</a></div></div>` : ''}
  `;
}

function applyModeVisibility(){
  const svg = document.getElementById('circuit');
  svg.classList.remove('mode-power','mode-bench','mode-future');
  svg.classList.add(`mode-${currentMode}`);
  document.querySelectorAll('.future-box').forEach(g => g.style.opacity = currentMode==='future' ? 1 : 0);
  // banner
  const b = BANNER[currentMode];
  document.getElementById('banner').innerHTML = currentLang==='ja' ? b.ja : b.en;
}

function applyLanguage(){
  document.querySelectorAll('[data-en]').forEach(elx => {
    elx.textContent = currentLang==='ja' ? elx.dataset.ja : elx.dataset.en;
  });
  document.getElementById('btn-ja').classList.toggle('active', currentLang==='ja');
  document.getElementById('btn-en').classList.toggle('active', currentLang==='en');
  renderSVG();
  renderLegend();
  if (selectedId) renderInfo(byId(selectedId));
  applyModeVisibility();
}

function renderLegend(){
  const foot = document.getElementById('legend');
  foot.innerHTML = '';
  LEGEND.forEach(item => {
    const div = document.createElement('div');
    div.className = 'item';
    div.innerHTML = `<span class="sw" style="background:var(--${ {power5v:'pow5',powervm:'powvm',motorphase:'motor',i2c:'i2c',uart:'uart',ctrl:'ctrl',feedback:'fb',future:'future'}[item.cat] })"></span>${currentLang==='ja'?item.ja:item.en}`;
    foot.appendChild(div);
  });
}

document.getElementById('btn-ja').addEventListener('click', () => { currentLang='ja'; applyLanguage(); });
document.getElementById('btn-en').addEventListener('click', () => { currentLang='en'; applyLanguage(); });
document.querySelectorAll('nav.tabs button').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('nav.tabs button').forEach(b=>b.classList.remove('active'));
    btn.classList.add('active');
    currentMode = btn.dataset.mode;
    applyModeVisibility();
  });
});

renderSVG();
renderLegend();
