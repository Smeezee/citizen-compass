/* cc_viewer.js — THE ship viewer. One implementation, two consumers.

   WHY THIS FILE EXISTS (L8)
   =========================
   The Three.js viewer lived inline in index.html. The ship page needs the same
   one, and TWO COPIES OF A VIEWER GUARANTEE DRIFT: the tone-mapping fix, the
   load-token guard and the still-image blanking are each a bug that was found
   once and fixed once, and a second copy is a place for each of them to come
   back quietly. Two concrete consumers exist, so this satisfies the standing
   2-3-cases rule rather than being extracted on principle.

   WHAT IS HERE AND WHAT IS NOT
   ============================
   Here: the renderer, the scene, the lights, the environment map, framing, the
   load path and its cancellation. Everything about SHOWING A SHIP.

   Not here: badges, prices, dealers, hardpoint panels, tabs. Everything about
   what a particular page says AROUND the ship. index.html and loadout.html
   want completely different chrome and always will, so pushing that in here
   would produce one function with two personalities.

   THE THREE BUGS THIS CARRIES, so nobody reintroduces them by writing a second
   viewer that looks simpler:

     1. THE LOAD TOKEN. three.js cannot cancel a load in flight. Without
        `token !== this._tok`, a GLB requested for ship A arrives seconds later
        and is added to ship B's page. Every async callback checks it.

     2. TONE MAPPING AND OUTPUT ENCODING. Without them anything bright clips to
        pure white and the hull becomes a silhouette. The direct lights are
        deliberately low: the old high values were compensating for a missing
        environment map rather than lighting anything.

     3. METALNESS. glTF defaults to 1.0, which with no textures is a mirror.
        The models have NO textures at all - not lost in compression, never
        present - so CC_HULL is an honest stand-in and not an approximation of
        a real paint job.

   NO MODULE SYSTEM. index.html and loadout.html are plain pages loaded from a
   file server with no bundler, exactly like hardpoint_data.gen.js and
   kb_actions.gen.js. This attaches one global and that is the whole contract.
*/
'use strict';

/* Ship hull look. KEPT, though the hologram no longer reads metalness or
   roughness - `exposure` still drives the renderer and the export is part of
   this module's published contract. */
var CC_HULL = { color: 0x5C6570, metalness: 0.55, roughness: 0.35,
                exposure: 0.70, key: 0.75 };

/* ==========================================================================
   H1. THE HOLOGRAM, PORTED FROM docs/holo-viewer-prototype-src/viewer.js.

   Sleven: "I don't see why we can't make all of our ships look like this...
   I don't ever have to worry about the paint." Our 235 models have no
   textures, RSI's have none, Fleetyards' are not ours to take. The texture
   problem is not solved by finding textures - IT IS DISSOLVED BY NOT NEEDING
   THEM.

   TWO OF MY OWN CONSTRAINTS WERE OVERTURNED HERE AND THE REASON IS WORTH
   KEEPING. I shipped three styles and hard-coded the sliders, on the argument
   that a visitor should enjoy the page rather than tune it. Sleven, 2026-08-23:
   "I liked the ability from the prototype to change the shading and all that
   stuff", and "being able to change the line density, being able to change the
   colour... I like this."

   ON THIS PAGE THE TUNING IS THE ENJOYMENT. A developer's tuning panel and a
   visitor's controls look identical in a screenshot; the difference is whether
   anybody wants to touch them, and he does. So: all six styles, all five
   colours, all three sliders.

   THE DEFAULT IS PINNED AND IS NOT THE PROTOTYPE'S. Solid + lines, amber, grid
   on, scanlines off - his capture of the Sabre, "this is how I want all of the
   ships". The prototype opens on panel/cyan; this does not.
   ======================================================================= */
var CC_HOLO = {
  /* All six. `solidlines` is the default; the rest are controls. */
  MODES: [['panel', 'Panel lines'], ['solidlines', 'Solid + lines'],
          ['solid', 'Solid holo'], ['hull', 'Lit hull'],
          ['wire', 'Wireframe'], ['points', 'Points']],
  DEFAULT: 'solidlines',
  /* The prototype's five, in its order. AMBER IS INDEX 2 AND IS THE DEFAULT
     here - the deployed first pass rendered cyan-going-white and that was
     wrong twice over. */
  COLOURS: [0x5fd8ee, 0x7dffb4, 0xffb545, 0xff6b8a, 0xe8f4ff],
  COLOUR_NAMES: ['Cyan', 'Mint', 'Amber', 'Rose', 'Ice'],
  DEFAULT_COLOUR: 0xffb545,
  /* The three sliders, with the ranges the prototype uses. */
  lineInt: 1.0,      /* 0.1 .. 2.0   line intensity */
  detail: 24,        /* 5 .. 80 deg  line detail, the EdgesGeometry threshold */
  glow: 0.55,        /* 0 .. 1.5     glow */
  scan: 0,           /* scanlines OFF by default - available, not on */
  grid: true,
  field: 0x050a12,
  gridA: 0x1d5f72,
  gridB: 0x0f3644,
  gridOpacity: 0.16,
  ringOpacity: 0.20
};

/* THE SHADERS, verbatim from the prototype apart from one added uniform.
   They ARE the look; a shader rewritten from a description is a different
   shader. `uGlow` is the addition and it is declared honestly below. */
var CC_HOLO_VERT = [
  'varying vec3 vN; varying vec3 vV; varying vec3 vW;',
  'void main(){',
  '  vec4 mv = modelViewMatrix*vec4(position,1.0);',
  '  vN = normalize(normalMatrix*normal); vV = normalize(-mv.xyz);',
  '  vW = (modelMatrix*vec4(position,1.0)).xyz;',
  '  gl_Position = projectionMatrix*mv;',
  '}'
].join('\n');

/* SOLID: opaque, depth-writing, key light for form plus a hot fresnel rim.
   OPAQUE IS THE POINT. The prototype's own note: "opaque means the ship
   actually blocks the grid behind it, which is what made the old
   additive-only version read as murky soup."

   uGlow SCALES THE FRESNEL RIM, AND IT IS A STAND-IN, NOT BLOOM. The prototype
   drives its glow slider into an UnrealBloomPass. This repo vendors three's
   build, controls and loaders and NO postprocessing, and adding third-party
   code is not a side effect of a render port. Rather than ship a dead control,
   the slider drives the rim term, which is where most of the visible lift came
   from anyway. It is a different thing wearing the same label and this comment
   is the only place that says so - so do not delete it. */
var CC_HOLO_FRAG = [
  'uniform vec3 uColor; uniform float uTime; uniform float uScan;',
  'uniform float uGlow;',
  'varying vec3 vN; varying vec3 vV; varying vec3 vW;',
  'void main(){',
  '  vec3 N = normalize(vN);',
  '  float ndl  = clamp(dot(N, normalize(vec3(0.35,0.9,0.30))), 0.0, 1.0);',
  '  float ndl2 = clamp(dot(N, normalize(vec3(-0.6,-0.2,-0.5))), 0.0, 1.0);',
  '  float fres = pow(1.0 - abs(dot(N, normalize(vV))), 2.3);',
  '  float sl   = 0.5 + 0.5*sin(vW.y*230.0 - uTime*1.4);',
  '  sl = mix(1.0, sl, uScan*0.20);',
  '  float sweep = fract(vW.y*0.30 - uTime*0.085);',
  '  float band  = smoothstep(0.975,1.0,sweep)*uScan;',
  '  vec3 c = uColor*(0.040 + ndl*0.20 + ndl2*0.055',
  '                   + fres*(1.15*uGlow/0.55) + band*0.55);',
  '  gl_FragColor = vec4(c*sl, 1.0);',
  '}'
].join('\n');

/* HULL: a lit surface rather than a hologram. There is no texture to apply -
   the exports carry geometry and one empty UV map - so a "finish" here is
   shading standing in for plating, not a paint job, and the panel says so. */
var CC_HOLO_FRAG_HULL = [
  'uniform vec3 uColor; uniform float uTime;',
  'varying vec3 vN; varying vec3 vV; varying vec3 vW;',
  'void main(){',
  '  vec3 N = normalize(vN), V = normalize(vV);',
  '  vec3 L1 = normalize(vec3(0.45,0.80,0.40));',
  '  vec3 L2 = normalize(vec3(-0.75,0.20,-0.45));',
  '  vec3 L3 = normalize(vec3(0.0,-1.0,0.0));',
  '  float d1 = clamp(dot(N,L1),0.0,1.0);',
  '  float d2 = clamp(dot(N,L2),0.0,1.0);',
  '  float d3 = clamp(dot(N,L3),0.0,1.0);',
  '  float spec = pow(clamp(dot(reflect(-L1,N), V),0.0,1.0), 34.0);',
  '  float fres = pow(1.0-abs(dot(N,V)), 3.0);',
  '  float band = 0.5 + 0.5*sin(vW.y*54.0 + vW.z*11.0);',
  '  band = 1.0 + (smoothstep(0.90,1.0,band)-0.5)*0.10;',
  '  vec3 grey = vec3(0.30,0.335,0.375);',
  '  vec3 base = mix(grey, uColor*0.55, 0.22) * band;',
  '  vec3 c = base*(0.34 + d1*0.86 + d2*0.34 + d3*0.14)',
  '         + uColor*(spec*0.95 + fres*0.30);',
  '  gl_FragColor = vec4(c, 1.0);',
  '}'
].join('\n');

/* THE LINE OPACITY IS COMPUTED FROM THE MESH, NOT FIXED.
   A dense hull has vastly more edges than a sparse one, and additive lines on
   a dense mesh are how the 63.7%-white-pixels defect happened. Opacity falls
   as the edge count rises - 168,351 edges is the prototype's reference - and
   is clamped into [0.12, 0.55] so neither extreme vanishes nor saturates.

   AND IT IS SCALED BY THE LINE-INTENSITY SLIDER, which is what makes that
   control do something real rather than set a class. */
/* THE PANEL'S STATE, FOR THE SESSION.
   sessionStorage rather than localStorage: this is a preference about how
   somebody wants to look at ships this sitting, not a setting that should
   follow them back next month. Read through a guard, because storage THROWS
   outright in a browser that has it disabled and a page must not fall over
   because it could not remember a colour. Same shape as B4's spin memory. */
var CC_HOLO_KEY = 'ccHolo';
function ccHoloStore() {
  try { return (typeof sessionStorage !== 'undefined') ? sessionStorage : null; }
  catch (e) { return null; }
}
function ccHoloSaved() {
  var s = ccHoloStore();
  if (!s) return {};
  try { return JSON.parse(s.getItem(CC_HOLO_KEY) || '{}') || {}; }
  catch (e) { return {}; }
}
function ccHoloSave(v) {
  var s = ccHoloStore();
  if (!s) return;
  try { s.setItem(CC_HOLO_KEY, JSON.stringify(v)); } catch (e) {}
}

/* ONE DENSITY FACTOR FOR EVERY ADDITIVE PASS, AND WHY THE OLD FLOOR WAS THE
   BUG.

   The prototype's edgeOpacity clamps into [0.12, 0.55]. That was tuned against
   four hand-picked Fan Kit models of roughly 200-350k vertices. On this
   fleet's densest hull - the Liberator, 1,102,122 vertices, ~1.65M edges - the
   formula asks for 0.063 and THE 0.12 FLOOR DOUBLES IT. The floor exists so a
   sparse hull's lines do not vanish, and on a sparse hull the formula already
   returns a high number that the CEILING catches. So the floor never protects
   anything; it only ever bites on the dense hulls, which are exactly the ones
   that saturate.

   Measured, with line fragments counted per pixel rather than assumed to be
   one: panel 30.9% pure white, solid+lines 29.3%, points 34.4%, wire 7.5%.
   That is Sleven's "white line-work" and it is the 63.7% defect returning in a
   quieter form - not a white blob, but every additive pass clipping until the
   amber stops being amber.

   The fix is one factor rather than three tuned numbers: how dense is this
   mesh against the reference the prototype's values were chosen for. Edges,
   wireframe and points all scale by it, so each keeps the prototype's look on
   a prototype-sized hull and none of them saturates on a Liberator. */
function ccDensity(vertexCount) {
  var d = Math.pow(168351 / Math.max(1, vertexCount * 1.5), 0.85);
  return Math.min(1.0, Math.max(0.08, d));
}

function ccEdgeOpacity(edgeCount) {
  /* Kept taking an EDGE count, because that is what the caller has after
     building the EdgesGeometry, and the detail slider changes it - which is
     what makes that slider do something real. */
  var o = 0.44 * Math.pow(168351 / Math.max(1, edgeCount), 0.85);
  return Math.min(0.55, Math.max(0.035, o)) * CC_HOLO.lineInt;
}

/* 1x1 transparent GIF. Assigning '' to img.src makes some browsers re-request
   the document URL, so blanking uses a real image instead. */
var CC_BLANK = 'data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7';

var CCViewer = (function () {

  /* A 64x32 gradient standing in for a studio: cool above, dim warm bounce
     below. Costs nothing to ship and gives reflective surfaces something to
     return. Built once for the whole page, whatever mounts. */
  var _env = null;
  function environment(renderer) {
    if (_env) return _env;
    var W = 64, H = 32, data = new Uint8Array(W * H * 4);
    for (var y = 0; y < H; y++) {
      var t = y / (H - 1);
      var r = Math.round(150 * (1 - t) + 40 * t),
          g = Math.round(175 * (1 - t) + 38 * t),
          b = Math.round(205 * (1 - t) + 34 * t);
      for (var x = 0; x < W; x++) {
        var i = (y * W + x) * 4;
        data[i] = r; data[i + 1] = g; data[i + 2] = b; data[i + 3] = 255;
      }
    }
    var tex = new THREE.DataTexture(data, W, H, THREE.RGBAFormat);
    tex.mapping = THREE.EquirectangularReflectionMapping;
    tex.needsUpdate = true;
    var p = new THREE.PMREMGenerator(renderer);
    p.compileEquirectangularShader();
    _env = p.fromEquirectangular(tex).texture;
    p.dispose(); tex.dispose();
    return _env;
  }

  /* DRACO, ATTACHED HERE RATHER THAN BY THE BUILD.
     The deploy build used to paste the DRACO wiring into the page with a
     string replace, which is silent when its anchor moves - and moving the
     viewer into this file moved that anchor. So the wiring lives with the
     loader it belongs to, and it reads whatever the host page provides:

       THREE.DRACOLoader          the decoder class, from the vendor bundle
       CC_DRACO_WRAPPER           the decoder JS, inlined by the build
       CC_DRACO_WASM_B64          the decoder wasm, inlined by the build

     A page without them gets an undecorated GLTFLoader, which is correct for
     uncompressed models - and `attachedDraco` records which happened, so a
     check can tell "no DRACO because none was offered" from "no DRACO because
     the wiring broke". Those are different answers and they must stay
     different. */
  var attachedDraco = false;
  function attachDraco(loader) {
    if (typeof THREE === 'undefined' || !THREE.DRACOLoader) return false;
    if (typeof CC_DRACO_WRAPPER === 'undefined' ||
        typeof CC_DRACO_WASM_B64 === 'undefined') return false;
    var dl = new THREE.DRACOLoader();
    dl._loadLibrary = function (url) {
      if (url === 'draco_wasm_wrapper.js') return Promise.resolve(CC_DRACO_WRAPPER);
      if (url === 'draco_decoder.wasm') {
        var b = atob(CC_DRACO_WASM_B64), a = new Uint8Array(b.length);
        for (var n = 0; n < b.length; n++) a[n] = b.charCodeAt(n);
        return Promise.resolve(a.buffer);
      }
      return Promise.reject(new Error('unexpected draco asset ' + url));
    };
    loader.setDRACOLoader(dl);
    attachedDraco = true;
    return true;
  }

  /**
   * One viewer bound to one canvas.
   *
   * @param {HTMLCanvasElement} canvas  where to draw
   * @param {HTMLElement} stage         the element whose size the canvas follows
   */
  function Viewer(canvas, stage) {
    this.canvas = canvas;
    this.stage = stage || (canvas && canvas.parentNode);
    this.renderer = null;
    this.scene = null;
    this.camera = null;
    this.controls = null;
    this.loader = null;
    this.current = null;
    this._raf = null;
    this._tok = 0;
    this._onResize = null;
  }

  Viewer.prototype.ready = function () { return !!this.renderer; };

  /* P4: THE ROTATION IS SOMETHING THE PERSON CAN STOP.
     Sleven: "the ship just constantly spins. There's not a way to stop the
     spin. I don't see a stop button anywhere."

     `autoRotate` was set true in boot() and nothing ever exposed it. These two
     make it state rather than a constant, and they READ FROM THE CONTROLS
     rather than from a copy - a second copy of a boolean is a second source of
     truth about what the ship is doing. */
  Viewer.prototype.spinning = function () {
    return !!(this.controls && this.controls.autoRotate);
  };
  Viewer.prototype.setSpin = function (on) {
    if (this.controls) this.controls.autoRotate = !!on;
    return this.spinning();
  };

  Viewer.prototype.boot = function () {
    if (this.renderer) return this;
    if (typeof THREE === 'undefined' || !this.canvas) return this;
    var self = this;
    this.renderer = new THREE.WebGLRenderer(
      { canvas: this.canvas, antialias: true, alpha: true });
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
    /* Without tone mapping, anything bright clips straight to pure white and
       the shape disappears into a silhouette. Half of the white-blob fix. */
    this.renderer.outputEncoding = THREE.sRGBEncoding;
    this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
    this.renderer.toneMappingExposure = CC_HULL.exposure;
    this.scene = new THREE.Scene();
    /* H1: a dark field. A hologram needs something to be bright against. */
    this.scene.background = new THREE.Color(CC_HOLO.field);
    /* THE DEFAULT STATE, PINNED BY SLEVEN: solid + lines, amber, grid on,
       scanlines off. Restored from the session first, so somebody who set
       amber wireframe with scanlines does not re-set it on every ship - the
       same rule B4 applied to the spin control. */
    var saved = ccHoloSaved();
    this.style = this.style || saved.style || CC_HOLO.DEFAULT;
    this._colour = saved.colour || CC_HOLO.DEFAULT_COLOUR;
    if (saved.lineInt != null) CC_HOLO.lineInt = saved.lineInt;
    if (saved.detail != null) CC_HOLO.detail = saved.detail;
    if (saved.glow != null) CC_HOLO.glow = saved.glow;
    if (saved.scan != null) CC_HOLO.scan = saved.scan;
    if (saved.grid != null) CC_HOLO.grid = saved.grid;
    this._holoU = {
      uColor: { value: new THREE.Color(this._colour) },
      uTime: { value: 0 },
      uScan: { value: CC_HOLO.scan },
      uGlow: { value: CC_HOLO.glow }
    };
    this.camera = new THREE.PerspectiveCamera(42, 1, 0.01, 10000);
    this.controls = new THREE.OrbitControls(this.camera, this.canvas);
    this.controls.enableDamping = true;
    this.controls.dampingFactor = 0.08;
    /* Honours a choice made before the model finished loading - somebody who
       hits Stop while it is still streaming means it. */
    this.controls.autoRotate = (this.wantSpin !== false);
    this.controls.autoRotateSpeed = 0.7;
    this.scene.environment = environment(this.renderer);
    /* Direct lights pulled well back. The old values were high because a fully
       metallic surface with no environment reflects almost nothing else - they
       were compensating for the bug rather than lighting the model. */
    this.scene.add(new THREE.HemisphereLight(0xbfe9ff, 0x18324d, 0.30));
    var k = new THREE.DirectionalLight(0xffffff, CC_HULL.key);
    k.position.set(4, 7, 5); this.scene.add(k);
    var r = new THREE.DirectionalLight(0x00c9a7, 0.28);
    r.position.set(-6, 2, -5); this.scene.add(r);
    var f = new THREE.DirectionalLight(0xff6b00, 0.14);
    f.position.set(2, -4, -3); this.scene.add(f);
    var rim = new THREE.DirectionalLight(0xffffff, 0.55);
    rim.position.set(-3, 1, 6); this.scene.add(rim);
    this._buildHoloMaterials();
    this._buildTable();
    this.loader = new THREE.GLTFLoader();
    attachDraco(this.loader);
    this._onResize = function () { self.size(); };
    window.addEventListener('resize', this._onResize);
    return this;
  };

  Viewer.prototype.size = function () {
    if (!this.stage || !this.renderer) return;
    var w = this.stage.clientWidth, h = this.stage.clientHeight;
    if (!w || !h) return;
    this.renderer.setSize(w, h, false);
    this.camera.aspect = w / h;
    this.camera.updateProjectionMatrix();
  };

  Viewer.prototype.start = function () {
    if (this._raf) return;
    var self = this;
    (function loop() {
      self._raf = requestAnimationFrame(loop);
      if (self.controls) self.controls.update();
      /* The scanline and sweep in FRAG_SOLID are functions of time. Without
         this they are a static band across the hull rather than a sweep. */
      if (self._holoU) {
        self._holoU.uTime.value = ((window.performance || Date).now()) / 1000;
      }
      if (self.renderer) self.renderer.render(self.scene, self.camera);
      /* One hook, called after the frame is drawn. A page that overlays
         anything on the model - hull markers, labels - needs to move it when
         the camera does, and giving it a hook is cheaper than giving it the
         render loop. */
      if (self.onFrame) self.onFrame(self);
    })();
  };

  /* WHERE A POINT ON THE HULL IS ON SCREEN.
     Markers are DOM, not sprites, deliberately: a real element can be focused,
     tabbed to and read by a screen reader, and a sprite cannot. So the viewer
     answers "where is this" and the page decides what to put there.
     Returns null when the point is BEHIND the camera - `z > 1` after
     projection - because a marker drawn for a gun on the far side of the hull
     is a marker pointing at the wrong thing. */
  Viewer.prototype.project = function (x, y, z) {
    if (!this.camera || !this.canvas) return null;
    var v = new THREE.Vector3(x, y, z).project(this.camera);
    if (v.z > 1) return null;
    var w = this.canvas.clientWidth, h = this.canvas.clientHeight;
    return { x: (v.x * 0.5 + 0.5) * w, y: (-v.y * 0.5 + 0.5) * h, depth: v.z };
  };

  /* The scalar that turns a NORMALISED hull position into a world one.
     `unit` in the hardpoint dataset is normalised against the hull's longest
     HALF-extent, so this is that half-extent, measured from the mesh actually
     loaded. There is no fixed multiplier that could be right: the fleet spans
     10,000x in model units per metre. */
  Viewer.prototype.unitScale = function () {
    if (!this.current) return 0;
    var box = new THREE.Box3().setFromObject(this.current);
    var s = box.getSize(new THREE.Vector3());
    return (Math.max(s.x, s.y, s.z) || 1) / 2;
  };

  Viewer.prototype.stop = function () {
    if (this._raf) { cancelAnimationFrame(this._raf); this._raf = null; }
  };

  Viewer.prototype.clear = function () {
    if (!this.current) return;
    this.scene.remove(this.current);
    this.current.traverse(function (o) {
      if (o.geometry) o.geometry.dispose();
      if (o.material) {
        (Array.isArray(o.material) ? o.material : [o.material])
          .forEach(function (m) { m.dispose(); });
      }
    });
    this.current = null;
  };

  /* Centre the object and pull the camera back far enough to hold it. */
  Viewer.prototype.frame = function (o) {
    var box = new THREE.Box3().setFromObject(o),
        sz = box.getSize(new THREE.Vector3()),
        c = box.getCenter(new THREE.Vector3());
    o.position.sub(c);
    var max = Math.max(sz.x, sz.y, sz.z) || 1;
    var d = max / (2 * Math.tan(THREE.MathUtils.degToRad(this.camera.fov) / 2)) * 1.55;
    this.camera.position.set(d * 0.75, d * 0.42, d * 0.85);
    this.camera.near = max / 500;
    this.camera.far = max * 60;
    this.camera.updateProjectionMatrix();
    this.controls.target.set(0, 0, 0);
    this.controls.update();
    return { sz: sz };
  };

  /* THE MATERIALS, one set per viewer, built once.
  /* THE MATERIALS. One set per viewer, rebuilt when a slider or colour moves,
     because a ShaderMaterial's uniforms are shared and its compile-time state
     is not. */
  Viewer.prototype._buildHoloMaterials = function () {
    var U = this._holoU;
    if (this._density == null) this._density = 1;
    this._mats = {
      solid: new THREE.ShaderMaterial({
        uniforms: U, vertexShader: CC_HOLO_VERT, fragmentShader: CC_HOLO_FRAG,
        side: THREE.FrontSide, transparent: false, depthWrite: true }),
      hull: new THREE.ShaderMaterial({
        uniforms: U, vertexShader: CC_HOLO_VERT,
        fragmentShader: CC_HOLO_FRAG_HULL,
        side: THREE.FrontSide, transparent: false, depthWrite: true }),
      /* THE DEPTH-ONLY PRE-PASS. Non-negotiable: without it a 353,731-vertex
         mesh went to 63.7% pure white pixels. polygonOffset keeps the lines
         off the surface they trace. */
      depth: new THREE.MeshBasicMaterial({
        colorWrite: false, depthWrite: true,
        polygonOffset: true, polygonOffsetFactor: 1.2,
        polygonOffsetUnits: 1.2 }),
      edges: new THREE.LineBasicMaterial({
        color: this._colour, transparent: true, opacity: 0.44,
        blending: THREE.AdditiveBlending, depthWrite: false }),
      /* Wireframe and points carry the prototype's own base opacities,
         scaled by the same density factor the lines use. On a hull the size
         of the prototype's the factor is 1 and these are unchanged. */
      wire: new THREE.MeshBasicMaterial({
        color: this._colour, wireframe: true, transparent: true,
        opacity: 0.075 * this._density * CC_HOLO.lineInt,
        blending: THREE.AdditiveBlending, depthWrite: false }),
      pts: new THREE.PointsMaterial({
        color: this._colour, size: 0.0055, transparent: true,
        opacity: 0.42 * this._density * CC_HOLO.lineInt,
        blending: THREE.AdditiveBlending, depthWrite: false,
        sizeAttenuation: true })
    };
    return this._mats;
  };

  /* THE HOLO TABLE - grid and ring, at the prototype's own values. */
  Viewer.prototype._buildTable = function () {
    if (this._table || !this.scene) return;
    this._table = new THREE.Group();
    var grid = new THREE.GridHelper(9, 36, CC_HOLO.gridA, CC_HOLO.gridB);
    if (grid.material) {
      grid.material.transparent = true;
      grid.material.opacity = CC_HOLO.gridOpacity;
    }
    this._table.add(grid);
    this._ring = new THREE.Mesh(
      new THREE.RingGeometry(1.45, 1.50, 128),
      new THREE.MeshBasicMaterial({
        color: this._colour, transparent: true, opacity: CC_HOLO.ringOpacity,
        side: THREE.DoubleSide, blending: THREE.AdditiveBlending,
        depthWrite: false }));
    this._ring.rotation.x = -Math.PI / 2;
    this._table.add(this._ring);
    this._table.visible = CC_HOLO.grid;
    this.scene.add(this._table);
  };

  /* ------------------------------------------------------------ the API
     Everything the control panel presses. Each one CHANGES THE RENDER rather
     than setting a class - which is precisely what H1f's negative control
     exists to catch. */
  Viewer.prototype.modes = function () {
    return CC_HOLO.MODES.map(function (m) { return m.slice(); });
  };
  Viewer.prototype.setStyle = function (name) {
    var ok = CC_HOLO.MODES.some(function (m) { return m[0] === name; });
    if (!ok) return this.style;
    this.style = name;
    if (this.current) this._applyHolo(this.current);
    return this.style;
  };
  Viewer.prototype.colours = function () { return CC_HOLO.COLOURS.slice(); };
  Viewer.prototype.setColour = function (hex) {
    if (CC_HOLO.COLOURS.indexOf(hex) === -1) return this._colour;
    this._colour = hex;
    var c = new THREE.Color(hex);
    if (this._holoU) this._holoU.uColor.value = c;
    var m = this._mats;
    if (m) {
      m.edges.color = c; m.wire.color = c; m.pts.color = c;
    }
    if (this._ring && this._ring.material) this._ring.material.color = c;
    if (this.current) this._applyHolo(this.current);
    return this._colour;
  };
  Viewer.prototype.colour = function () { return this._colour; };

  /* THE THREE SLIDERS. `detail` and `lineInt` change the geometry or the
     opacity and so require a rebuild; `glow` is a uniform and does not. */
  Viewer.prototype.setSlider = function (which, value) {
    var v = Number(value);
    if (!isFinite(v)) return null;
    if (which === 'lineInt') { CC_HOLO.lineInt = Math.max(0.1, Math.min(2, v)); }
    else if (which === 'detail') { CC_HOLO.detail = Math.max(5, Math.min(80, Math.round(v))); }
    else if (which === 'glow') {
      CC_HOLO.glow = Math.max(0, Math.min(1.5, v));
      if (this._holoU) this._holoU.uGlow.value = CC_HOLO.glow;
      return CC_HOLO.glow;
    } else { return null; }
    if (this.current) this._applyHolo(this.current);
    return CC_HOLO[which];
  };
  Viewer.prototype.slider = function (which) { return CC_HOLO[which]; };

  /* One place writes the memory, called by every control above. */
  Viewer.prototype.remember = function () {
    ccHoloSave({ style: this.style, colour: this._colour,
                 lineInt: CC_HOLO.lineInt, detail: CC_HOLO.detail,
                 glow: CC_HOLO.glow, scan: CC_HOLO.scan, grid: CC_HOLO.grid });
    return true;
  };

  Viewer.prototype.setScanlines = function (on) {
    CC_HOLO.scan = on ? 1 : 0;
    if (this._holoU) this._holoU.uScan.value = CC_HOLO.scan;
    return !!CC_HOLO.scan;
  };
  Viewer.prototype.scanlines = function () { return !!CC_HOLO.scan; };
  Viewer.prototype.setGrid = function (on) {
    CC_HOLO.grid = !!on;
    if (this._table) this._table.visible = CC_HOLO.grid;
    return CC_HOLO.grid;
  };
  Viewer.prototype.gridOn = function () { return CC_HOLO.grid; };

  /* A SIGNATURE OF WHAT IS ACTUALLY DRAWN.
     Not a class, not the style name: the passes the scene really holds, their
     material kinds, blending, sides, opacities and the colour. Two different
     styles MUST produce different strings, and H1f's negative control asserts
     exactly that - because a build where every button sets a class and nothing
     redraws passes every other assertion in the file. */
  Viewer.prototype.renderSignature = function () {
    var out = [];
    (this._holoPasses || []).forEach(function (p) {
      out.push([p.kind, p.mat, p.blend, p.side, (p.opacity == null ? '-' :
        Number(p.opacity).toFixed(4)), p.colour].join(':'));
    });
    out.push('col=' + this._colour);
    out.push('glow=' + CC_HOLO.glow);
    return out.join('|');
  };

  /* ------------------------------------------------------------------
     BUILD THE PASSES FOR ONE HULL, in the prototype's own order and with its
     own rules about which style gets which.

       pre-pass   panel and wire only. `solid`, `solidlines` and `hull` are
                  opaque and write their own depth; a second depth pass there
                  is redundant, which is what the prototype does.
       surface    solid / solidlines -> the holo shader. hull -> the lit one.
       lines      panel and solidlines -> EdgesGeometry at CC_HOLO.detail, with
                  solidlines at 0.75 of the opacity because there is a lit
                  surface underneath it already.
       wire       a wireframe mesh at 0.075.
       points     a point cloud at 0.42.
     ------------------------------------------------------------------ */
  Viewer.prototype._applyHolo = function (root) {
    var style = this.style || CC_HOLO.DEFAULT;
    var self = this;
    /* MEASURED FROM THE HULL ACTUALLY LOADED, not assumed. A fleet spanning
       30k to 1.1M vertices cannot share one opacity. */
    var verts = 0;
    root.traverse(function (o) {
      if (o.isMesh && o.geometry && o.geometry.attributes
          && o.geometry.attributes.position) {
        verts += o.geometry.attributes.position.count;
      } else if (o.isMesh && o.geometry && o.geometry.__edges) {
        verts += o.geometry.__edges / 1.5;   /* the controls' stub geometry */
      }
    });
    this._density = ccDensity(verts || 224468);
    var mats = this._buildHoloMaterials();

    (this._holoAdded || []).forEach(function (o) {
      if (o.parent) o.parent.remove(o);
      if (o.geometry && o.geometry.dispose && o.userData.ccOwnGeo) {
        o.geometry.dispose();
      }
    });
    this._holoAdded = [];
    this._holoPasses = [];

    var note = function (kind, m) {
      self._holoPasses.push({
        kind: kind,
        mat: (m && m.type) || (m === mats.solid ? 'shader'
              : m === mats.hull ? 'shaderHull' : 'basic'),
        blend: (m && m.blending === THREE.AdditiveBlending) ? 'add' : 'normal',
        side: (m && m.side === THREE.DoubleSide) ? 'double' : 'front',
        opacity: m && m.opacity,
        colour: (m && m.color && m.color.getHex) ? m.color.getHex()
                : self._colour
      });
    };

    root.traverse(function (o) {
      if (!o.isMesh || !o.geometry) return;

      if (style === 'solid' || style === 'solidlines') {
        o.material = mats.solid; o.renderOrder = 1; note('surface', mats.solid);
      } else if (style === 'hull') {
        o.material = mats.hull; o.renderOrder = 1; note('surface', mats.hull);
      } else {
        o.material = mats.depth; o.renderOrder = 0; note('prepass', mats.depth);
      }

      if (style === 'panel' || style === 'solidlines') {
        var eg = new THREE.EdgesGeometry(o.geometry, CC_HOLO.detail);
        var n = (eg.attributes && eg.attributes.position)
          ? eg.attributes.position.count / 2 : 1;
        var lm = mats.edges.clone();
        lm.opacity = ccEdgeOpacity(n) * (style === 'solidlines' ? 0.75 : 1);
        var lines = new THREE.LineSegments(eg, lm);
        lines.renderOrder = 2; lines.userData.ccOwnGeo = true;
        o.add(lines); self._holoAdded.push(lines); note('lines', lm);
      } else if (style === 'wire') {
        var w = new THREE.Mesh(o.geometry, mats.wire);
        w.renderOrder = 2; o.add(w); self._holoAdded.push(w);
        note('wire', mats.wire);
      } else if (style === 'points') {
        var pt = new THREE.Points(o.geometry, mats.pts);
        pt.renderOrder = 2; o.add(pt); self._holoAdded.push(pt);
        note('points', mats.pts);
      }
    });
  };

  /* E4: REFRAME WHEN A PANEL COVERS PART OF THE STAGE.
     Open a panel over the stage and the hull becomes a sliver at the far edge,
     so the marker the panel is ABOUT drifts out from under it. B3's rule that
     a panel must not cover its own marker is defeated just as thoroughly if
     the ship leaves instead.

     `obstruct` is the fraction of the stage width the panel occupies, from the
     page, which is the only thing that knows the panel's size. The camera
     shifts its target so the hull centres in what is LEFT rather than in the
     whole stage. Passing 0 puts it back. */
  Viewer.prototype.setObstruction = function (frac) {
    var f = Math.max(0, Math.min(0.8, Number(frac) || 0));
    if (f === this._obstruct) return f;
    this._obstruct = f;
    this.reframe();
    return f;
  };
  Viewer.prototype.obstruction = function () { return this._obstruct || 0; };

  Viewer.prototype.reframe = function () {
    if (!this.current || !this.camera || !this.controls) return false;
    var box = new THREE.Box3().setFromObject(this.current);
    var c = box.getCenter(new THREE.Vector3());
    var s = box.getSize(new THREE.Vector3());
    var f = this._obstruct || 0;
    /* Shift the look-at point sideways by half the covered width, in world
       units, so the visible half of the stage centres on the hull. */
    var shift = (s.x || 1) * f * 0.5;
    this.controls.target.set(c.x + shift, c.y, c.z);
    /* And pull back enough that the hull still fits the NARROWER viewport. */
    var fit = Math.max(s.x, s.y, s.z) || 1;
    var fov = (this.camera.fov || 42) * Math.PI / 180;
    var dist = (fit / 2) / Math.tan(fov / 2) * (1 + f * 0.9) * 1.35;
    var dir = this.camera.position.clone().sub(this.controls.target);
    if (dir.lengthSq() < 1e-9) dir.set(1, 0.5, 1);
    dir.normalize().multiplyScalar(dist);
    this.camera.position.copy(this.controls.target).add(dir);
    this.camera.updateProjectionMatrix();
    this.controls.update();
    return true;
  };

  /* Invalidate anything in flight. Called when the page moves to another ship
     or closes the viewer - see bug 1 in the header. */
  Viewer.prototype.cancel = function () { return ++this._tok; };

  /**
   * Load a model. Every callback is guarded by the token this call was issued
   * under, so a late arrival for a previous ship is dropped rather than added
   * to whatever is on screen now.
   *
   * @param {string} url
   * @param {{onLoad,onProgress,onError}} cb
   */
  Viewer.prototype.load = function (url, cb) {
    cb = cb || {};
    var self = this, tok = ++this._tok, t0 = (window.performance || Date).now();
    this.boot();
    if (!this.loader) {
      if (cb.onError) cb.onError(new Error('no WebGL loader'));
      return tok;
    }
    this.clear();
    this.loader.load(url, function (g) {
      if (tok !== self._tok) return;      // a later ship owns the stage
      self.clear();
      self.current = g.scene;
      /* H1: THE PBR PASS IS GONE. It set DoubleSide, metalness and roughness
         on files with no textures - which is why the hull read as a grey
         mirror, and why the paint problem looked like something that had to be
         solved rather than dissolved. The hologram's materials are unlit, so
         the scene lights no longer touch the hull at all. */
      self._applyHolo(self.current);
      self.scene.add(self.current);
      var i = self.frame(self.current);
      if (cb.onLoad) {
        cb.onLoad({ size: i.sz,
                    seconds: (((window.performance || Date).now()) - t0) / 1000 });
      }
    }, function (x) {
      if (tok !== self._tok || !cb.onProgress) return;
      cb.onProgress(x);
    }, function (e) {
      if (tok !== self._tok || !cb.onError) return;
      cb.onError(e);
    });
    return tok;
  };

  return {
    Viewer: Viewer,
    HULL: CC_HULL,
    HOLO: CC_HOLO,
    edgeOpacity: ccEdgeOpacity,
    BLANK: CC_BLANK,
    /* Named so a page can say "the viewer module is missing" rather than
       throwing a ReferenceError somebody has to read a stack trace to explain. */
    VERSION: '1',
    /* So a page or a check can ask whether DRACO actually got wired, rather
       than assuming it from the presence of the globals. */
    hasDraco: function () { return attachedDraco; },
  };
})();
