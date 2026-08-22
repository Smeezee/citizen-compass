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

/* Ship hull look. Change these five numbers to restyle every ship on the site,
   on both pages, in one place - which is the point of the extraction. */
var CC_HULL = { color: 0x5C6570, metalness: 0.55, roughness: 0.35,
                exposure: 0.70, key: 0.75 };

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
    this.camera = new THREE.PerspectiveCamera(42, 1, 0.01, 10000);
    this.controls = new THREE.OrbitControls(this.camera, this.canvas);
    this.controls.enableDamping = true;
    this.controls.dampingFactor = 0.08;
    this.controls.autoRotate = true;
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
      if (self.renderer) self.renderer.render(self.scene, self.camera);
    })();
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
      self.current.traverse(function (o) {
        if (!o.isMesh || !o.material) return;
        (Array.isArray(o.material) ? o.material : [o.material])
          .forEach(function (m) {
            m.side = THREE.DoubleSide;
            /* glTF default is metalness 1.0. Left alone that is a mirror, and
               with no textures on the file there is nothing else to go on. */
            m.color = new THREE.Color(CC_HULL.color);
            m.metalness = CC_HULL.metalness;
            m.roughness = CC_HULL.roughness;
            m.envMapIntensity = 1.0;
            m.needsUpdate = true;
          });
      });
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
    BLANK: CC_BLANK,
    /* Named so a page can say "the viewer module is missing" rather than
       throwing a ReferenceError somebody has to read a stack trace to explain. */
    VERSION: '1',
    /* So a page or a check can ask whether DRACO actually got wired, rather
       than assuming it from the presence of the globals. */
    hasDraco: function () { return attachedDraco; },
  };
})();
