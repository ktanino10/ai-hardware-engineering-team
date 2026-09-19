(function (root) {
  'use strict';
  const math = root.Rev5Interactive;
  const failIf = (bad, message) => { if (bad) throw new Error(message); };
  let cameras;
  const colors = {
    frame: [.58, .65, .67], panels: [.77, .81, .80], electronics: [.24, .52, .40],
    mounts: [.52, .61, .63], hardware: [.67, .70, .72], reference: [.72, .52, .32],
    X: [.10, .57, .54], Y: [.85, .48, .22], Z: [.28, .52, .77],
  };
  async function unpack(scene) {
    failIf(scene?.component_count !== 399 || scene.units !== 'mm' ||
      scene.coordinates !== 'ALREADY_INSTALLED_GLOBAL_COORDINATES' ||
      scene.physical_permission !== 'NOT_GRANTED', '保存ソースのメタデータが一致しません。');
    failIf(typeof DecompressionStream !== 'function', 'このブラウザーはローカル圧縮データの展開に対応していません。');
    const compressed = Uint8Array.from(atob(scene.payload), c => c.charCodeAt(0));
    const stream = new Blob([compressed]).stream().pipeThrough(new DecompressionStream('gzip'));
    const buffer = await new Response(stream).arrayBuffer();
    failIf(buffer.byteLength !== scene.payload_bytes, '形状データの長さが一致しません。');
    const digest = await crypto.subtle.digest('SHA-256', buffer);
    const hash = Array.from(new Uint8Array(digest), n => n.toString(16).padStart(2, '0')).join('');
    failIf(hash !== scene.payload_sha256, '形状データの SHA-256 が一致しません。');
    const data = new DataView(buffer);
    let expectedOffset = 0;
    const ids = new Set();
    const meshes = scene.components.map(component => {
      failIf(ids.has(component.id) || component.offset !== expectedOffset ||
        component.coordinate_count !== component.triangles * 9, '形状一覧の範囲が不正です。');
      ids.add(component.id);
      expectedOffset += component.coordinate_count * 8;
      const positions = new Float32Array(component.coordinate_count);
      for (let i = 0; i < positions.length; i++) {
        const value = data.getFloat64(component.offset + i * 8, true);
        failIf(!Number.isFinite(value), '非有限の座標があります。');
        positions[i] = value;
      }
      const normals = new Float32Array(positions.length);
      for (let i = 0; i < positions.length; i += 9) {
        const u = [0, 1, 2].map(k => positions[i + 3 + k] - positions[i + k]);
        const v = [0, 1, 2].map(k => positions[i + 6 + k] - positions[i + k]);
        const n = [u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0]];
        const length = Math.hypot(...n);
        // Keep even degenerate source triangles; zero normals do not change topology.
        for (let j = 0; j < 9; j++) normals[i + j] = length ? n[j % 3] / length : 0;
      }
      return { component, positions, normals };
    });
    failIf(expectedOffset !== buffer.byteLength, '未対応の形状データが残っています。');
    for (const id of ['FRAME_LOWER', 'FRAME_UPPER', 'X_motor', 'Y_motor', 'Z_motor', 'X_wheel', 'Y_wheel', 'Z_wheel']) {
      failIf(!ids.has(id), '必須の形状がありません: ' + id);
    }
    return meshes;
  }
  class WholeViewer {
    constructor(canvas, scene, meshes, edges, onState, onError) {
      this.canvas = canvas;
      this.scene = scene;
      this.plan = root.Rev5Features.plan; cameras = this.plan.cameras.presets;
      this.state = { ...math.initialState(cameras.iso), selected: 'X_motor', isolated: false, dimensions: true,
        phase: 0, playing: false, appearance: 'opaque', focusUnit: null, detailUnit: this.plan.default.detail_unit,
        groups: Object.fromEntries(Object.keys(scene.groups).map(key => [key, this.plan.whole_modes.exterior.groups.includes(key)])) };
      this.bounds = { center: [0, 0, 0], radius: 205 };
      this.onState = onState; this.onError = onError;
      this.pointers = new Map(); this.pending = false; this.failed = false; this.renderCount = 0;
      this.lastTime = 0; this.hoverId = null; this.hoverPoint = null; this.edgeData = edges;
      this.reducedMotion = matchMedia('(prefers-reduced-motion: reduce)');
      this.gl = canvas.getContext('webgl', { antialias: true, alpha: false, preserveDrawingBuffer: true });
      failIf(!this.gl, 'WebGL を利用できません。別の対応ブラウザーで開いてください。');
      const gl = this.gl;
      const vertex = this.shader(gl.VERTEX_SHADER, `
        attribute vec3 position; attribute vec3 normal; uniform mat4 camera; uniform vec3 offset;
        varying vec3 surfaceNormal;
        void main(){ surfaceNormal=normal; gl_Position=camera*vec4(position+offset,1.0); }
      `);
      const fragment = this.shader(gl.FRAGMENT_SHADER, `
        precision mediump float; uniform vec3 color; uniform float alpha; uniform bool flatColor; varying vec3 surfaceNormal;
        void main(){
          if(flatColor){gl_FragColor=vec4(color,alpha);return;}
          vec3 n=surfaceNormal/max(length(surfaceNormal),0.000001);
          if(!gl_FrontFacing) n=-n;
          float light=0.52+0.30*max(dot(n,normalize(vec3(0.5,-0.7,1.0))),0.0)
                          +0.18*max(dot(n,normalize(vec3(-0.7,0.5,0.4))),0.0);
          gl_FragColor=vec4(color*light,alpha);
        }
      `);
      this.program = gl.createProgram();
      failIf(!this.program, 'WebGL プログラムを確保できません。');
      gl.attachShader(this.program, vertex); gl.attachShader(this.program, fragment); gl.linkProgram(this.program);
      failIf(!gl.getProgramParameter(this.program, gl.LINK_STATUS), gl.getProgramInfoLog(this.program));
      gl.deleteShader(vertex); gl.deleteShader(fragment);
      this.location = Object.fromEntries(['position', 'normal'].map(key => [key, gl.getAttribLocation(this.program, key)]));
      for (const key of ['camera', 'color', 'offset', 'alpha', 'flatColor']) this.location[key] = gl.getUniformLocation(this.program, key);
      this.parts = meshes.map(({ component, positions, normals }) => ({
        component, positions: this.buffer(gl.ARRAY_BUFFER, positions), normals: this.buffer(gl.ARRAY_BUFFER, normals),
        edges: this.buffer(gl.ARRAY_BUFFER, new Float32Array(edges.get(component.id))),
        edgeCount: edges.get(component.id).length / 3,
      }));
      this.pickBuffer = gl.createFramebuffer(); this.pickTexture = gl.createTexture(); this.pickDepth = gl.createRenderbuffer();
      failIf(!this.pickBuffer || !this.pickTexture || !this.pickDepth, 'ピッキング用バッファーを確保できません。');
      gl.enable(gl.DEPTH_TEST); gl.depthFunc(gl.LEQUAL);
      failIf(gl.getError() !== gl.NO_ERROR, 'WebGL 形状の初期化に失敗しました。');
      canvas.addEventListener('keydown', event => {
        if (event.key === 'Home') {
          event.preventDefault(); event.stopImmediatePropagation(); this.preset('iso');
        }
      });
      math.Viewer.prototype.bindInput.call(this);
      this.bindPicking();
      document.addEventListener('visibilitychange', () => {
        if (document.hidden) this.setState({ ...this.state, playing: false, autoOrbit: false });
        else this.redraw();
      });
      this.reducedMotion.addEventListener('change', () => {
        if (this.reducedMotion.matches) this.setState({ ...this.state, playing: false, autoOrbit: false });
        this.onState(this.getState());
      });
      this.resizeObserver = new ResizeObserver(() => this.redraw());
      this.resizeObserver.observe(canvas);
      this.redraw();
    }
    shader(...args) { return math.Viewer.prototype.shader.apply(this, args); }
    buffer(...args) { return math.Viewer.prototype.buffer.apply(this, args); }
    redraw() {
      if (this.pending || this.failed || document.hidden) return;
      this.pending = true;
      requestAnimationFrame(time => {
        this.pending = false;
        if (this.failed || document.hidden) return;
        try {
          const dt = Math.min(Math.max((time - this.lastTime) / 1000, 0), .1);
          this.lastTime = time;
          this.state = root.Rev5Features.step(this.state, dt);
          this.draw();
          if (this.state.playing || this.state.autoOrbit) this.redraw();
        } catch (error) { this.failed = true; this.onError(error); }
      });
    }
    setState(state) {
      failIf(state.explode < 0 || state.explode > 1 || !Number.isFinite(state.explode), '分解量が不正です。');
      this.state = state; this.lastTime = performance.now(); this.onState(this.getState()); this.redraw();
    }
    stop() { this.setState({ ...this.state, explode: 0, phase: 0, playing: false, autoOrbit: false }); }
    offset(component) { return root.Rev5Features.offset(component, this.state.explode, this.state); }
    framedBounds() {
      const lo = [Infinity, Infinity, Infinity], hi = [-Infinity, -Infinity, -Infinity];
      let count = 0;
      for (const { component: c } of this.parts) {
        if (!this.visible(c)) continue;
        const offset = this.offset(c); count++;
        for (let i = 0; i < 3; i++) {
          lo[i] = Math.min(lo[i], c.bounds_mm[0][i] + offset[i]);
          hi[i] = Math.max(hi[i], c.bounds_mm[1][i] + offset[i]);
        }
      }
      if (!count) return { center: [0, 0, 0], radius: 205, empty: true };
      return { center: lo.map((v, i) => (v + hi[i])/2), radius: Math.max(Math.hypot(...hi.map((v, i) => v-lo[i]))/2, 1), min: lo, max: hi };
    }
    camera() {
      return math.viewProjection(this.state, this.framedBounds(), this.canvas.width / this.canvas.height);
    }
    preset(name) {
      failIf(!cameras[name], '不明な視点です。');
      this.setState({ ...math.cameraPreset(this.state, cameras[name]), autoOrbit: false });
    }
    visible(component) {
      if (this.state.isolated) return component.id === this.state.selected;
      if (this.state.focusUnit) return this.plan.named_units.find(u => u.id === this.state.focusUnit).members.includes(component.id);
      return this.state.groups[component.group];
    }
    getState() {
      return { ...this.state, componentCount: this.parts.length, renderCount: this.renderCount, hovered: this.hoverId,
        reducedMotion: this.reducedMotion.matches,
        frameBounds: this.framedBounds(), stage: root.Rev5Features.stage(this.state.explode),
        visibleIds: this.parts.filter(part => this.visible(part.component)).map(part => part.component.id),
        geometryEdited: false, renderer: 'Local WebGL / browser rasterization only' };
    }
    draw() {
      const gl = this.gl, ratio = Math.min(root.devicePixelRatio || 1, 2);
      const width = Math.max(1, Math.round(this.canvas.clientWidth * ratio));
      const height = Math.max(1, Math.round(this.canvas.clientHeight * ratio));
      if (this.canvas.width !== width || this.canvas.height !== height) { this.canvas.width = width; this.canvas.height = height; }
      gl.viewport(0, 0, width, height); gl.clearColor(250 / 255, 251 / 255, 252 / 255, 1);
      gl.bindFramebuffer(gl.FRAMEBUFFER, null); gl.depthMask(true);
      gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT); gl.useProgram(this.program);
      this.matrix = this.camera();
      gl.uniformMatrix4fv(this.location.camera, false, new Float32Array(this.matrix));
      gl.enableVertexAttribArray(this.location.position); gl.enableVertexAttribArray(this.location.normal);
      const xray = this.state.appearance === 'xray';
      gl.uniform1i(this.location.flatColor, 0); gl.uniform1f(this.location.alpha, xray ? .12 : 1);
      if (xray) { gl.enable(gl.BLEND); gl.blendFunc(gl.SRC_ALPHA, gl.ONE_MINUS_SRC_ALPHA); gl.depthMask(false); }
      else gl.disable(gl.BLEND);
      for (const part of this.parts) {
        const c = part.component;
        if (!this.visible(c)) continue;
        const base = c.group === 'drive' ? colors[c.id[0]] : colors[c.group];
        const color = c.id === this.hoverId ? [.96, .55, .13] : c.id === this.state.selected ? base.map(v => Math.min(1, v * 1.15 + .06)) : base;
        gl.uniform3fv(this.location.color, new Float32Array(color));
        gl.uniform3fv(this.location.offset, new Float32Array(this.offset(c)));
        for (const [field, attribute] of [['positions', 'position'], ['normals', 'normal']]) {
          gl.bindBuffer(gl.ARRAY_BUFFER, part[field]); gl.vertexAttribPointer(this.location[attribute], 3, gl.FLOAT, false, 0, 0);
        }
        gl.drawArrays(gl.TRIANGLES, 0, c.coordinate_count / 3);
      }
      if (xray) {
        gl.uniform1i(this.location.flatColor, 1); gl.uniform1f(this.location.alpha, .65);
        gl.disableVertexAttribArray(this.location.normal); gl.vertexAttrib3f(this.location.normal, 0, 0, 1);
        for (const part of this.parts) {
          if (!this.visible(part.component)) continue;
          const highlighted = [this.hoverId, this.state.selected].includes(part.component.id);
          gl.uniform3fv(this.location.color, new Float32Array(highlighted ? [.7, .33, .05] : [.23, .36, .42]));
          gl.uniform3fv(this.location.offset, new Float32Array(this.offset(part.component)));
          gl.bindBuffer(gl.ARRAY_BUFFER, part.edges); gl.vertexAttribPointer(this.location.position, 3, gl.FLOAT, false, 0, 0);
          gl.drawArrays(gl.LINES, 0, part.edgeCount);
        }
      }
      gl.depthMask(true); gl.disable(gl.BLEND);
      failIf(gl.getError() !== gl.NO_ERROR, 'WebGL の描画に失敗しました。');
      this.renderCount++; this.canvas.dataset.ready = 'true';
      this.drawDimensions();
      if (this.hoverPoint && !this.pointers.size) this.updateHover(this.pick(...this.hoverPoint));
      this.onState(this.getState());
    }
    bindPicking() {
      let tap = null;
      const position = event => {
        const r = this.canvas.getBoundingClientRect();
        return [event.clientX - r.left, event.clientY - r.top];
      };
      this.canvas.addEventListener('pointerdown', event => {
        tap = this.pointers.size === 1 ? { id: event.pointerId, point: position(event) } : null;
      });
      this.canvas.addEventListener('pointermove', event => {
        const point = position(event);
        if (tap && Math.hypot(point[0] - tap.point[0], point[1] - tap.point[1]) > 5) tap = null;
        if (!this.pointers.size) { this.hoverPoint = point; this.redraw(); }
      });
      this.canvas.addEventListener('pointerup', event => {
        try {
          if (!this.failed && tap && tap.id === event.pointerId) {
            const hit = this.pick(...position(event));
            if (hit) this.setState({ ...this.state, selected: hit.id });
          }
        } catch (error) { this.failed = true; this.onError(error); }
        tap = null;
      });
      this.canvas.addEventListener('pointercancel', () => { tap = null; });
      this.canvas.addEventListener('pointerleave', () => { this.hoverPoint = null; this.updateHover(null); this.redraw(); });
    }
    updateHover(part) {
      const next = part?.id || null;
      if (next === this.hoverId) return;
      this.hoverId = next; this.onHover?.(part); this.redraw();
    }
    pick(x, y) {
      const gl = this.gl, width = this.canvas.width, height = this.canvas.height;
      if (x < 0 || y < 0 || x >= this.canvas.clientWidth || y >= this.canvas.clientHeight) return null;
      gl.bindFramebuffer(gl.FRAMEBUFFER, this.pickBuffer);
      if (this.pickWidth !== width || this.pickHeight !== height) {
        gl.bindTexture(gl.TEXTURE_2D, this.pickTexture);
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.NEAREST);
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.NEAREST);
        gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, width, height, 0, gl.RGBA, gl.UNSIGNED_BYTE, null);
        gl.framebufferTexture2D(gl.FRAMEBUFFER, gl.COLOR_ATTACHMENT0, gl.TEXTURE_2D, this.pickTexture, 0);
        gl.bindRenderbuffer(gl.RENDERBUFFER, this.pickDepth);
        gl.renderbufferStorage(gl.RENDERBUFFER, gl.DEPTH_COMPONENT16, width, height);
        gl.framebufferRenderbuffer(gl.FRAMEBUFFER, gl.DEPTH_ATTACHMENT, gl.RENDERBUFFER, this.pickDepth);
        failIf(gl.checkFramebufferStatus(gl.FRAMEBUFFER) !== gl.FRAMEBUFFER_COMPLETE, 'ピッキングバッファーが不完全です。');
        this.pickWidth = width; this.pickHeight = height;
      }
      gl.viewport(0, 0, width, height); gl.disable(gl.BLEND); gl.disable(gl.DITHER); gl.depthMask(true);
      gl.clearColor(0, 0, 0, 1); gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT);
      gl.useProgram(this.program); gl.uniformMatrix4fv(this.location.camera, false, new Float32Array(this.camera()));
      gl.uniform1i(this.location.flatColor, 1); gl.uniform1f(this.location.alpha, 1);
      gl.enableVertexAttribArray(this.location.position); gl.disableVertexAttribArray(this.location.normal);
      gl.vertexAttrib3f(this.location.normal, 0, 0, 1);
      this.parts.forEach((part, index) => {
        if (!this.visible(part.component)) return;
        const code = index + 1;
        gl.uniform3f(this.location.color, (code & 255) / 255, ((code >> 8) & 255) / 255, 0);
        gl.uniform3fv(this.location.offset, new Float32Array(this.offset(part.component)));
        gl.bindBuffer(gl.ARRAY_BUFFER, part.positions);
        gl.vertexAttribPointer(this.location.position, 3, gl.FLOAT, false, 0, 0);
        gl.drawArrays(gl.TRIANGLES, 0, part.component.coordinate_count / 3);
      });
      const pixel = new Uint8Array(4);
      gl.readPixels(Math.floor(x * width / this.canvas.clientWidth), height - 1 - Math.floor(y * height / this.canvas.clientHeight),
        1, 1, gl.RGBA, gl.UNSIGNED_BYTE, pixel);
      gl.bindFramebuffer(gl.FRAMEBUFFER, null); gl.enable(gl.DITHER);
      failIf(gl.getError() !== gl.NO_ERROR, '形状のピッキングに失敗しました。');
      return this.parts[pixel[0] + pixel[1] * 256 - 1]?.component || null;
    }
    project(point) {
      const m = this.matrix;
      const p = [0, 1].map(row => m[row] * point[0] + m[4 + row] * point[1] + m[8 + row] * point[2] + m[12 + row]);
      return [(p[0] + 1) * this.canvas.clientWidth / 2, (1 - p[1]) * this.canvas.clientHeight / 2];
    }
    drawDimensions() {
      const svg = document.getElementById('dimensions');
      svg.replaceChildren(); svg.setAttribute('viewBox', `0 0 ${this.canvas.clientWidth} ${this.canvas.clientHeight}`);
      const add = (tag, attrs, text) => {
        const node = document.createElementNS('http://www.w3.org/2000/svg', tag);
        Object.entries(attrs).forEach(([key, value]) => node.setAttribute(key, value));
        if (text) node.textContent = text;
        svg.append(node);
      };
      const line = (a, b, label, css) => {
        const [x1, y1] = this.project(a), [x2, y2] = this.project(b);
        add('line', { x1, y1, x2, y2, class: css });
        if (label && Math.hypot(x1 - x2, y1 - y2) > 24) {
          add('text', { x: (x1 + x2) / 2 + 6, y: (y1 + y2) / 2 - 6 }, label);
        }
      };
      if (this.state.dimensions && this.state.explode === 0 && !this.state.isolated && !this.state.focusUnit) {
        for (let axis = 0; axis < 3; axis++) {
          const a = [-135, -135, -135], b = [...a]; a[axis] = -120; b[axis] = 120;
          line(a, b, `${'XYZ'[axis]} 240 mm · 名目`, 'dimension-line');
        }
      }
      const c = this.scene.components.find(c => c.id === this.state.selected);
      if (!c || !this.visible(c)) return;
      const offset = this.offset(c);
      const [lo, hi] = c.bounds_mm.map(p => p.map((v, i) => v + offset[i]));
      for (let axis = 0; axis < 3; axis++) {
        const others = [0, 1, 2].filter(i => i !== axis);
        for (let side = 0; side < 4; side++) {
          const a = [...lo], b = [...lo]; b[axis] = hi[axis];
          others.forEach((k, j) => { a[k] = b[k] = (side & (1 << j)) ? hi[k] : lo[k]; });
          line(a, b, '', 'selection-line');
        }
        const anchor = lo.map((v, i) => (v + hi[i])/2);
        anchor[axis] = hi[axis];
        const projected = this.project(anchor);
        const x = Math.max(12, this.canvas.clientWidth - 175), y = this.canvas.clientHeight - 100 + axis*24;
        add('line', { x1: projected[0], y1: projected[1], x2: x-5, y2: y-5, class: 'selection-line' });
        add('text', { x, y, class: 'part-dimension-label' }, `${'XYZ'[axis]} ${c.dimensions_mm[axis].toFixed(2)} mm`);
      }
    }
  }
  root.Rev5Whole = { unpack, WholeViewer };
})(globalThis);
