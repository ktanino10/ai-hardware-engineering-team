(function (root) {
  'use strict';

  const TAU = Math.PI * 2;
  const PITCH_LIMIT = Math.PI / 2 - 0.02;
  const clamp = (value, low, high) => Math.min(high, Math.max(low, value));
  const finite = (value) => typeof value === 'number' && Number.isFinite(value);
  function requireValue(condition, message) {
    if (!condition) throw new Error(message);
  }
  const dot = (a, b) => a.reduce((sum, value, i) => sum + value * b[i], 0);
  const cross = (a, b) => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];
  function normalize(value) {
    const length = Math.hypot(...value);
    requireValue(length > 0, 'Invalid camera vector');
    return value.map((item) => item / length);
  }
  function cameraPreset(state, direction) {
    requireValue(direction.length === 3 && direction.every(finite), 'Invalid camera preset');
    const unit = normalize(direction);
    return { ...state, yaw: Math.atan2(unit[1], unit[0]), pitch: Math.asin(unit[2]), zoom: 1 };
  }
  function initialState(direction) {
    return cameraPreset({ explode: 0, yaw: 0, pitch: 0, zoom: 1, autoOrbit: false, mode: 'solid' }, direction);
  }
  function setExplosion(state, value) {
    requireValue(finite(value) && value >= 0 && value <= 1, 'Invalid explosion amount');
    return { ...state, explode: value };
  }
  function orbit(state, dx, dy) {
    requireValue(finite(dx) && finite(dy), 'Invalid orbit delta');
    return { ...state, yaw: state.yaw - dx * 0.007, pitch: clamp(state.pitch + dy * 0.007, -PITCH_LIMIT, PITCH_LIMIT) };
  }
  function zoomBy(state, factor) {
    requireValue(finite(factor) && factor > 0, 'Invalid zoom');
    return { ...state, zoom: clamp(state.zoom * factor, 0.45, 4) };
  }
  function componentOffset(component, state) {
    return component.explode.map((value) => value * state.explode);
  }
  function solidGeometry(component) {
    const positions = [], normals = [];
    for (let index = 0; index < component.triangles.length; index += 3) {
      const triangle = component.triangles.slice(index, index + 3).map((vertex) => component.vertices.slice(vertex * 3, vertex * 3 + 3));
      const normal = normalize(cross(triangle[1].map((v, i) => v - triangle[0][i]),
        triangle[2].map((v, i) => v - triangle[0][i])));
      triangle.forEach((point) => { positions.push(...point); normals.push(...normal); });
    }
    return { positions: new Float32Array(positions), normals: new Float32Array(normals) };
  }
  function multiply(a, b) {
    const result = new Array(16).fill(0);
    for (let col = 0; col < 4; col++) {
      for (let row = 0; row < 4; row++) {
        for (let k = 0; k < 4; k++) result[col * 4 + row] += a[k * 4 + row] * b[col * 4 + k];
      }
    }
    return result;
  }
  function viewProjection(state, bounds, aspect) {
    requireValue(finite(aspect) && aspect > 0 && bounds.radius > 0, 'Invalid viewport bounds');
    const direction = [Math.cos(state.pitch) * Math.cos(state.yaw), Math.cos(state.pitch) * Math.sin(state.yaw), Math.sin(state.pitch)];
    const eye = bounds.center.map((value, index) => value + direction[index] * bounds.radius * 3);
    const forward = direction.map((value) => -value);
    const right = normalize(cross(forward, [0, 0, 1]));
    const up = cross(right, forward);
    const view = [
      right[0], up[0], -forward[0], 0,
      right[1], up[1], -forward[1], 0,
      right[2], up[2], -forward[2], 0,
      -dot(right, eye), -dot(up, eye), dot(forward, eye), 1,
    ];
    const halfY = bounds.radius * 1.12 / Math.min(aspect, 1) / state.zoom;
    const halfX = halfY * aspect;
    const near = bounds.radius * 0.1;
    const far = bounds.radius * 6;
    const projection = [
      1 / halfX, 0, 0, 0,
      0, 1 / halfY, 0, 0,
      0, 0, -2 / (far - near), 0,
      0, 0, -(far + near) / (far - near), 1,
    ];
    return multiply(projection, view);
  }
  function validateScene(scene) {
    requireValue(scene && scene.schemaVersion === 1 && scene.kind === 'FREECAD_DERIVED_BROWSER_DISPLAY' && scene.units === 'mm',
      'Unsupported scene metadata');
    requireValue(scene.baselineSha256 === '1e76b6d9ed0ee919e7fcdc2a473fc2a529a66198bc7a28297eee9cf8cda7e494',
      'Unexpected source model');
    requireValue(Array.isArray(scene.components) && scene.components.length === 16 && scene.componentCount === 16,
      'Incomplete component set');
    const names = new Set();
    for (const component of scene.components) {
      requireValue(typeof component.id === 'string' && !names.has(component.id), 'Duplicate component');
      names.add(component.id);
      for (const field of ['vertices', 'triangles', 'edges', 'explode', 'color']) {
        requireValue(Array.isArray(component[field]) && component[field].every(finite), 'Invalid component data: ' + component.id);
      }
      requireValue(component.vertices.length > 0 && component.vertices.length % 3 === 0 &&
        component.vertices.length / 3 <= 65535 && component.edges.length > 0 && component.edges.length % 6 === 0 &&
        component.triangles.length > 0 && component.triangles.length % 3 === 0, 'Invalid mesh buffers');
      requireValue(component.triangles.every((index) => Number.isInteger(index) && index >= 0 && index < component.vertices.length / 3),
        'Invalid triangle index');
      requireValue(component.explode.length === 3 && component.color.length === 3 &&
        component.color.every((value) => value >= 0 && value <= 1) &&
        finite(component.opacity) && component.opacity >= 0 && component.opacity <= 1, 'Invalid display transform/style');
    }
    for (const name of ['HubBase', 'ClampCap', 'MotorReference', 'MountReference', 'WheelReference', 'RetainerReference']) {
      requireValue(names.has(name), 'Required component missing: ' + name);
    }
    for (const name of ['MotorReference', 'MountReference']) {
      requireValue(scene.components.find((component) => component.id === name).explode.every((value) => value === 0),
        'Fixed reference has an explosion offset');
    }
    requireValue(scene.bounds && scene.bounds.center.length === 3 && scene.bounds.center.every(finite) &&
      finite(scene.bounds.radius) && scene.bounds.radius > 0, 'Invalid scene bounds');
    for (const name of ['front', 'rear', 'left', 'right']) {
      requireValue(scene.cameras?.[name]?.direction?.length === 3 && scene.cameras[name].direction.every(finite),
        'Missing camera preset');
    }
    requireValue(scene.presentation?.physicalPermission === 'NOT_GRANTED', 'Unexpected physical approval');
  }

  class Viewer {
    constructor(canvas, scene, onState, onError) {
      validateScene(scene);
      this.canvas = canvas;
      this.scene = scene;
      this.state = initialState(scene.cameras.front.direction);
      this.onState = onState;
      this.onError = onError;
      this.pointers = new Map();
      this.pending = false;
      this.failed = false;
      this.renderCount = 0;
      this.lastTime = 0;
      this.gl = canvas.getContext('webgl', { antialias: true, alpha: false, preserveDrawingBuffer: true });
      requireValue(this.gl, 'WebGL を利用できません。下のアニメーションは引き続き閲覧できます。');
      this.initializeGraphics();
      this.bindInput();
      this.resizeObserver = new ResizeObserver(() => this.redraw());
      this.resizeObserver.observe(canvas);
      this.redraw();
    }
    shader(type, source) {
      const gl = this.gl;
      const shader = gl.createShader(type);
      requireValue(shader, 'Shader allocation failed');
      gl.shaderSource(shader, source);
      gl.compileShader(shader);
      requireValue(gl.getShaderParameter(shader, gl.COMPILE_STATUS), gl.getShaderInfoLog(shader));
      return shader;
    }
    initializeGraphics() {
      const gl = this.gl;
      const vertex = this.shader(gl.VERTEX_SHADER, `
        attribute vec3 position;
        attribute vec3 normal;
        uniform mat4 camera;
        uniform vec3 offset;
        varying vec3 surfaceNormal;
        void main() {
          surfaceNormal = normal;
          gl_Position = camera * vec4(position + offset, 1.0);
        }
      `);
      const fragment = this.shader(gl.FRAGMENT_SHADER, `
        precision mediump float;
        uniform vec4 color;
        uniform bool solidMode;
        varying vec3 surfaceNormal;
        void main() {
          if (solidMode) {
            vec3 n = normalize(surfaceNormal);
            float light = 0.52 + 0.30 * max(dot(n, normalize(vec3(0.5,-0.7,1.0))),0.0)
                               + 0.18 * max(dot(n, normalize(vec3(-0.7,0.5,0.4))),0.0);
            gl_FragColor = vec4(color.rgb * light, 1.0);
          } else {
            gl_FragColor = color;
          }
        }
      `);
      this.program = gl.createProgram();
      requireValue(this.program, 'Shader program allocation failed');
      gl.attachShader(this.program, vertex);
      gl.attachShader(this.program, fragment);
      gl.linkProgram(this.program);
      requireValue(gl.getProgramParameter(this.program, gl.LINK_STATUS), gl.getProgramInfoLog(this.program));
      gl.deleteShader(vertex);
      gl.deleteShader(fragment);
      this.location = {
        position: gl.getAttribLocation(this.program, 'position'),
        normal: gl.getAttribLocation(this.program, 'normal'),
        camera: gl.getUniformLocation(this.program, 'camera'),
        offset: gl.getUniformLocation(this.program, 'offset'),
        color: gl.getUniformLocation(this.program, 'color'),
        solidMode: gl.getUniformLocation(this.program, 'solidMode'),
      };
      this.parts = [...this.scene.components].sort((a, b) =>
        Number(!a.id.includes('Reference')) - Number(!b.id.includes('Reference'))).map((component) => {
          const solid = solidGeometry(component);
          return {
          component,
          vertices: this.buffer(gl.ARRAY_BUFFER, new Float32Array(component.vertices)),
          triangles: this.buffer(gl.ELEMENT_ARRAY_BUFFER, new Uint16Array(component.triangles)),
          edges: this.buffer(gl.ARRAY_BUFFER, new Float32Array(component.edges)),
          solidPositions: this.buffer(gl.ARRAY_BUFFER, solid.positions),
          normals: this.buffer(gl.ARRAY_BUFFER, solid.normals),
        };
        });
      gl.enable(gl.BLEND);
      gl.blendFunc(gl.SRC_ALPHA, gl.ONE_MINUS_SRC_ALPHA);
      gl.enable(gl.DEPTH_TEST);
      gl.depthFunc(gl.LEQUAL);
      requireValue(gl.getError() === gl.NO_ERROR, 'WebGL geometry initialization failed');
    }
    buffer(target, values) {
      const gl = this.gl;
      const buffer = gl.createBuffer();
      requireValue(buffer, 'Geometry buffer allocation failed');
      gl.bindBuffer(target, buffer);
      gl.bufferData(target, values, gl.STATIC_DRAW);
      return buffer;
    }
    setState(state) {
      requireValue(state.mode === 'solid' || state.mode === 'wire', 'Invalid display mode');
      this.state = state;
      this.onState(this.getState());
      this.redraw();
    }
    setExplosion(value) {
      this.setState(setExplosion(this.state, value));
    }
    preset(name) {
      requireValue(this.scene.cameras[name], 'Unknown camera preset');
      this.setState({ ...cameraPreset(this.state, this.scene.cameras[name].direction), autoOrbit: false });
    }
    getState() {
      return { ...this.state, renderer: 'WebGL browser approximation, NOT native Cycles',
        componentCount: this.parts.length, renderCount: this.renderCount, geometryEdited: false };
    }
    bindInput() {
      const canvas = this.canvas;
      canvas.addEventListener('pointerdown', (event) => {
        if (event.pointerType === 'mouse' && event.button !== 0) return;
        canvas.focus({ preventScroll: true });
        canvas.setPointerCapture(event.pointerId);
        this.pointers.set(event.pointerId, [event.clientX, event.clientY]);
      });
      canvas.addEventListener('pointermove', (event) => {
        if (!this.pointers.has(event.pointerId)) return;
        const old = this.pointers.get(event.pointerId);
        const before = [...this.pointers.values()];
        this.pointers.set(event.pointerId, [event.clientX, event.clientY]);
        if (this.pointers.size === 1) {
          this.setState({ ...orbit(this.state, event.clientX - old[0], event.clientY - old[1]), autoOrbit: false });
        } else if (this.pointers.size === 2) {
          const after = [...this.pointers.values()];
          const distance = (points) => Math.hypot(points[0][0] - points[1][0], points[0][1] - points[1][1]);
          if (distance(before) > 1 && distance(after) > 1) this.setState(zoomBy(this.state, distance(after) / distance(before)));
        }
      });
      const release = (event) => {
        this.pointers.delete(event.pointerId);
        if (canvas.hasPointerCapture(event.pointerId)) canvas.releasePointerCapture(event.pointerId);
      };
      canvas.addEventListener('pointerup', release);
      canvas.addEventListener('pointercancel', release);
      canvas.addEventListener('lostpointercapture', (event) => this.pointers.delete(event.pointerId));
      canvas.addEventListener('wheel', (event) => {
        event.preventDefault();
        this.setState(zoomBy(this.state, Math.exp(clamp(-event.deltaY * 0.001, -0.5, 0.5))));
      }, { passive: false });
      canvas.addEventListener('keydown', (event) => {
        const moves = { ArrowLeft: [-15, 0], ArrowRight: [15, 0], ArrowUp: [0, -15], ArrowDown: [0, 15] };
        if (moves[event.key]) {
          event.preventDefault();
          this.setState({ ...orbit(this.state, ...moves[event.key]), autoOrbit: false });
        } else if (event.key === '+' || event.key === '=') {
          event.preventDefault();
          this.setState(zoomBy(this.state, 1.1));
        } else if (event.key === '-') {
          event.preventDefault();
          this.setState(zoomBy(this.state, 1 / 1.1));
        } else if (event.key === 'Home') {
          event.preventDefault();
          this.preset('front');
        }
      });
      canvas.addEventListener('webglcontextlost', (event) => {
        event.preventDefault();
        this.failed = true;
        this.onError(new Error('3D 描画コンテキストが失われました。ページを再読み込みしてください。'));
      });
    }
    redraw() {
      if (this.pending || this.failed) return;
      this.pending = true;
      requestAnimationFrame((time) => {
        this.pending = false;
        if (this.failed) return;
        try {
          this.draw(time);
          if (this.state.autoOrbit && !document.hidden) this.redraw();
        } catch (error) {
          this.failed = true;
          this.onError(error);
        }
      });
    }
    draw(time) {
      const gl = this.gl;
      const dt = Math.min(Math.max((time - this.lastTime) / 1000, 0), 0.05);
      this.lastTime = time;
      if (this.state.autoOrbit) this.state = { ...this.state, yaw: this.state.yaw + dt * TAU / 24 };
      const ratio = Math.min(window.devicePixelRatio || 1, 2);
      const width = Math.max(1, Math.round(this.canvas.clientWidth * ratio));
      const height = Math.max(1, Math.round(this.canvas.clientHeight * ratio));
      if (this.canvas.width !== width || this.canvas.height !== height) {
        this.canvas.width = width;
        this.canvas.height = height;
      }
      gl.viewport(0, 0, width, height);
      gl.colorMask(true, true, true, true);
      gl.depthMask(true);
      gl.clearColor(250 / 255, 251 / 255, 252 / 255, 1);
      gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT);
      gl.useProgram(this.program);
      gl.enableVertexAttribArray(this.location.position);
      gl.uniformMatrix4fv(this.location.camera, false, new Float32Array(viewProjection(this.state, this.scene.bounds, width / height)));
      if (this.state.mode === 'solid') {
        gl.disable(gl.BLEND);
        gl.depthMask(true);
        gl.uniform1i(this.location.solidMode, 1);
        gl.enableVertexAttribArray(this.location.normal);
        const palette = root.REV5_BLENDER_COMPARISON?.interactive_view?.materials;
        requireValue(palette && palette.fastener, 'Bound opaque display colors are unavailable');
        for (const part of this.parts) {
          const color = (palette[part.component.id] || palette.fastener).color;
          gl.uniform4fv(this.location.color, new Float32Array([...color, 1]));
          gl.uniform3fv(this.location.offset, new Float32Array(componentOffset(part.component, this.state)));
          gl.bindBuffer(gl.ARRAY_BUFFER, part.solidPositions);
          gl.vertexAttribPointer(this.location.position, 3, gl.FLOAT, false, 0, 0);
          gl.bindBuffer(gl.ARRAY_BUFFER, part.normals);
          gl.vertexAttribPointer(this.location.normal, 3, gl.FLOAT, false, 0, 0);
          gl.drawArrays(gl.TRIANGLES, 0, part.component.triangles.length);
        }
        requireValue(gl.getError() === gl.NO_ERROR, 'Opaque WebGL drawing failed');
        this.renderCount++;
        this.canvas.dataset.ready = 'true';
        return;
      }
      gl.enable(gl.BLEND);
      gl.uniform1i(this.location.solidMode, 0);
      gl.disableVertexAttribArray(this.location.normal);
      gl.vertexAttrib3f(this.location.normal, 0, 0, 1);
      for (const part of this.parts) {
        const component = part.component;
        // Each part hides its own rear edges; other components remain transparent overlays.
        gl.depthMask(true);
        gl.clear(gl.DEPTH_BUFFER_BIT);
        gl.uniform3fv(this.location.offset, new Float32Array(componentOffset(component, this.state)));
        gl.colorMask(false, false, false, false);
        gl.enable(gl.POLYGON_OFFSET_FILL);
        gl.polygonOffset(1, 1);
        gl.bindBuffer(gl.ARRAY_BUFFER, part.vertices);
        gl.vertexAttribPointer(this.location.position, 3, gl.FLOAT, false, 0, 0);
        gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, part.triangles);
        gl.drawElements(gl.TRIANGLES, component.triangles.length, gl.UNSIGNED_SHORT, 0);
        gl.disable(gl.POLYGON_OFFSET_FILL);
        gl.colorMask(true, true, true, true);
        gl.depthMask(false);
        gl.uniform4fv(this.location.color, new Float32Array([...component.color, component.opacity]));
        gl.bindBuffer(gl.ARRAY_BUFFER, part.edges);
        gl.vertexAttribPointer(this.location.position, 3, gl.FLOAT, false, 0, 0);
        gl.drawArrays(gl.LINES, 0, component.edges.length / 3);
      }
      requireValue(gl.getError() === gl.NO_ERROR, 'WebGL drawing failed');
      this.renderCount++;
      this.canvas.dataset.ready = 'true';
    }
  }

  function start() {
    const canvas = document.getElementById('assembly-canvas');
    if (!canvas) return;
    const slider = document.getElementById('explode-slider');
    const amount = document.getElementById('explode-value');
    const errorBox = document.getElementById('viewer-error');
    const loading = document.getElementById('viewer-loading');
    const autoButton = document.getElementById('auto-orbit');
    const controls = [...document.querySelectorAll('#interactive-controls button, #interactive-controls input')];
    const fail = (error) => {
      console.error('Rev5 interactive viewer:', error);
      errorBox.textContent = '操作ビューを表示できません: ' + error.message;
      errorBox.hidden = false;
      loading.hidden = true;
      controls.forEach((control) => { control.disabled = true; });
    };
    try {
      const viewer = new Viewer(canvas, root.REV5_SCENE, (state) => {
        slider.value = String(Math.round(state.explode * 100));
        amount.textContent = Math.round(state.explode * 100) + '%';
        autoButton.setAttribute('aria-pressed', String(state.autoOrbit));
        autoButton.textContent = state.autoOrbit ? '自動回転を停止' : '360° 自動で見回す';
        document.getElementById('wire-toggle').setAttribute('aria-pressed', String(state.mode === 'wire'));
        document.getElementById('viewer-mode').textContent = state.mode === 'solid'
          ? '不透明ソリッド / 部品間の奥行きあり / 光はブラウザ近似'
          : '任意の旧線画・透過表示 / 部品越しの線あり / 通常表示ではありません';
      }, fail);
      root.rev5Viewer = viewer;
      controls.forEach((control) => { control.disabled = false; });
      slider.addEventListener('input', () => viewer.setExplosion(Number(slider.value) / 100));
      document.getElementById('assemble-reset').addEventListener('click', () => viewer.setExplosion(0));
      document.getElementById('camera-reset').addEventListener('click', () => {
        viewer.setState({ ...cameraPreset(viewer.state, root.REV5_SCENE.cameras.front.direction), autoOrbit: false });
      });
      autoButton.addEventListener('click', () => viewer.setState({ ...viewer.state, autoOrbit: !viewer.state.autoOrbit }));
      document.getElementById('wire-toggle').addEventListener('click', () =>
        viewer.setState({ ...viewer.state, mode: viewer.state.mode === 'solid' ? 'wire' : 'solid', autoOrbit: false }));
      document.querySelectorAll('[data-camera]').forEach((button) => {
        button.addEventListener('click', () => viewer.preset(button.dataset.camera));
      });
      document.addEventListener('visibilitychange', () => { if (!document.hidden) viewer.redraw(); });
      loading.hidden = true;
    } catch (error) {
      fail(error);
    }
  }

  const api = { initialState, setExplosion, orbit, zoomBy, cameraPreset, componentOffset, solidGeometry, viewProjection, multiply, validateScene, Viewer };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  else {
    root.Rev5Interactive = api;
    start();
  }
})(globalThis);
