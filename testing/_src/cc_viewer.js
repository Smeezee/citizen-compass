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
   H1. THE HOLOGRAM, PORTED FROM THE PROTOTYPE'S OWN SOURCE.

   Sleven: "I don't see why we can't make all of our ships look like this...
   I don't ever have to worry about the paint and trying to get that right."

   The second half is the engineering point. Our 235 models have no textures,
   RSI's have none, and Fleetyards' materials are not ours to take. The texture
   problem is not solved by finding textures - IT IS DISSOLVED BY NOT NEEDING
   THEM. A hologram does not want a texture; the absence of one is the
   material.

   PORTED, NOT REIMPLEMENTED. Source is docs/holo-viewer-prototype-src/
   viewer.js, extracted 2026-08-23. The first version of this file was written
   from the living document's PROSE and got the central thing backwards: it
   made the solid style additive. The prototype's own comment says why that is
   wrong -

       "opaque means the ship actually blocks the grid behind it, which is
        what made the old additive-only version read as murky soup"

   - so `solid` is an OPAQUE, DEPTH-WRITING ShaderMaterial and only the lines
   and the wireframe are additive. Reading the source changed the answer.

   THREE STYLES, NOT SIX. `panel`, `solid`, `wire`. The prototype's other three
   - solidlines, hull, points - stay in the prototype and in section 3 of the
   living document rather than being deleted.

   NO SLIDERS. Line intensity, line detail and glow were tunable there; here
   they are the constants the captures use. Sleven's rule is that a visitor
   should enjoy the page, not tune it.

   NOT PORTED, AND SAID RATHER THAN QUIETLY DROPPED: the UnrealBloomPass. The
   prototype runs an EffectComposer with bloom at 0.55/0.55/0.30, and this repo
   vendors three.js `build`, `controls` and `loaders` but NO `postprocessing`.
   Adding it means vendoring new third-party code, which is not something to do
   as a side effect of a render port. FRAG_SOLID's fresnel rim carries a good
   part of the same lift; the difference is a softer halo, and it is a known
   gap rather than an unnoticed one.
   ======================================================================= */
var CC_HOLO = {
  STYLES: ['panel', 'solid', 'wire'],
  DEFAULT: 'panel',
  /* The prototype's own colour, not the site accent. Changing it is a design
     decision and this is a port. */
  colour: 0x5fd8ee,
  /* Formerly the three sliders, at the values the captures use. */
  detail: 24,        /* EdgesGeometry threshold, degrees - "line detail" */
  lineInt: 1.0,      /* "line intensity" - scales edgeOpacity() below */
  scan: 1.0,         /* the scanline/sweep term in FRAG_SOLID */
  wireOpacity: 0.075,
  /* The holo table. */
  field: 0x050a12,
  gridA: 0x1d5f72,
  gridB: 0x0f3644,
  gridOpacity: 0.16,
  ringOpacity: 0.20
};

/* THE SHADERS, verbatim from the prototype. Not paraphrased: they ARE the
   look, and a shader rewritten from a description is a different shader. */
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
   OPAQUE IS THE POINT - see the note above about murky soup. */
var CC_HOLO_FRAG = [
  'uniform vec3 uColor; uniform float uTime; uniform float uScan;',
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
  '  vec3 c = uColor*(0.040 + ndl*0.20 + ndl2*0.055 + fres*1.15 + band*0.55);',
  '  gl_FragColor = vec4(c*sl, 1.0);',
  '}'
].join('\n');

/* THE LINE OPACITY IS COMPUTED FROM THE MESH, NOT FIXED, and this is the piece
   the prose version of this port missed entirely.
   A dense hull has vastly more edges than a sparse one, and additive lines on
   a dense mesh are exactly how the 63.7%-white-pixels defect happened. So the
   opacity falls as the edge count rises - 168,351 edges is the prototype's
   reference mesh - and is clamped into [0.12, 0.55] so neither extreme
   disappears nor saturates. Hard-coding one opacity would white out the
   Liberator and leave the Cyclone invisible. */
function ccEdgeOpacity(edgeCount) {
  var o = 0.44 * Math.pow(168351 / Math.max(1, edgeCount), 0.85);
  return Math.min(0.55, Math.max(0.12, o)) * CC_HOLO.lineInt;
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
    this.style = this.style || CC_HOLO.DEFAULT;
    this._holoU = {
      uColor: { value: new THREE.Color(CC_HOLO.colour) },
      uTime: { value: 0 },
      uScan: { value: CC_HOLO.scan }
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
     Shared across every hull the viewer loads, exactly as the prototype does -
     they carry no per-mesh state except matEdges' opacity, which is set from
     the edge count each time a hull is shown. */
  Viewer.prototype._buildHoloMaterials = function () {
    if (this._mats) return;
    var U = this._holoU;
    this._mats = {
      /* SOLID - opaque and depth-writing. See CC_HOLO_FRAG. */
      solid: new THREE.ShaderMaterial({
        uniforms: U, vertexShader: CC_HOLO_VERT, fragmentShader: CC_HOLO_FRAG,
        side: THREE.FrontSide, transparent: false, depthWrite: true
      }),
      /* THE DEPTH-ONLY PRE-PASS. Non-negotiable, and the reason is measured:
         without it a 353,731-vertex mesh went to 63.7% pure white pixels,
         because every surface behind every other surface added its light.
         polygonOffset keeps the lines off the surface they trace. */
      depth: new THREE.MeshBasicMaterial({
        colorWrite: false, depthWrite: true,
        polygonOffset: true, polygonOffsetFactor: 1.2, polygonOffsetUnits: 1.2
      }),
      edges: new THREE.LineBasicMaterial({
        color: CC_HOLO.colour, transparent: true, opacity: 0.44,
        blending: THREE.AdditiveBlending, depthWrite: false
      }),
      wire: new THREE.MeshBasicMaterial({
        color: CC_HOLO.colour, wireframe: true, transparent: true,
        opacity: CC_HOLO.wireOpacity,
        blending: THREE.AdditiveBlending, depthWrite: false
      })
    };
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
    var ring = new THREE.Mesh(
      new THREE.RingGeometry(1.45, 1.50, 128),
      new THREE.MeshBasicMaterial({
        color: CC_HOLO.colour, transparent: true,
        opacity: CC_HOLO.ringOpacity, side: THREE.DoubleSide,
        blending: THREE.AdditiveBlending, depthWrite: false }));
    ring.rotation.x = -Math.PI / 2;
    this._table.add(ring);
    this.scene.add(this._table);
  };

  /* WHICH OF THE THREE. Anything else is refused rather than silently
     defaulted - a typo that quietly renders the wrong style is a bug nobody
     sees until they look at a capture. */
  Viewer.prototype.setStyle = function (name) {
    if (CC_HOLO.STYLES.indexOf(name) === -1) return this.style;
    this.style = name;
    if (this.current) this._applyHolo(this.current);
    return this.style;
  };
  Viewer.prototype.styles = function () { return CC_HOLO.STYLES.slice(); };

  /* BUILD THE PASSES FOR ONE HULL, in the prototype's own order.

       pre-pass   panel and wire only. `solid` is opaque and writes its own
                  depth, so a second depth pass would be redundant there -
                  which is exactly what the prototype does and what reading
                  the source corrected.
       fill       solid only, opaque.
       lines      panel: EdgesGeometry at CC_HOLO.detail degrees, additive,
                  opacity from the EDGE COUNT.
                  wire:  a wireframe mesh at 0.075, additive.
  */
  Viewer.prototype._applyHolo = function (root) {
    var style = this.style || CC_HOLO.DEFAULT;
    var mats = this._mats, self = this;

    (this._holoAdded || []).forEach(function (o) {
      if (o.parent) o.parent.remove(o);
      if (o.geometry && o.geometry.dispose && o.userData.ccOwnGeo) {
        o.geometry.dispose();
      }
    });
    this._holoAdded = [];

    root.traverse(function (o) {
      if (!o.isMesh || !o.geometry) return;

      /* The mesh itself becomes the pass that writes depth, or the opaque
         surface, depending on the style. */
      if (style === 'solid') {
        o.material = mats.solid;
        o.renderOrder = 1;
      } else {
        o.material = mats.depth;
        o.renderOrder = 0;
      }

      if (style === 'panel') {
        var eg = new THREE.EdgesGeometry(o.geometry, CC_HOLO.detail);
        var n = (eg.attributes && eg.attributes.position)
          ? eg.attributes.position.count / 2 : 1;
        var lm = mats.edges.clone();
        lm.opacity = ccEdgeOpacity(n);
        var lines = new THREE.LineSegments(eg, lm);
        lines.renderOrder = 2;
        lines.userData.ccOwnGeo = true;
        o.add(lines);
        self._holoAdded.push(lines);
      } else if (style === 'wire') {
        var w = new THREE.Mesh(o.geometry, mats.wire);
        w.renderOrder = 2;
        o.add(w);
        self._holoAdded.push(w);
      }
    });
  };

  /* E4: REFRAME WHEN A PANEL COVERS PART OF THE STAGE.
     The prototype has an Auto-frame control for this. On the live page the
     defect Sleven caught is the other half of B3: open a panel over the stage
     and the hull becomes a sliver at the far edge, so the marker the panel is
     ABOUT drifts out from under it. B3's rule that a panel must not cover its
     own marker is defeated if the ship leaves.

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
