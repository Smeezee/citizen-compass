/* ------------------------------------------------------------------
   Citizen Compass — shared hardpoint viewer engine
   Extracted from tests/testing-site/ships/arrow/index.html (2026-07-29
   prototype) so the hover-highlight + rack-configuration-selector
   pattern can be reused on other ships without copy/pasting the whole
   three.js scene each time.

   STATUS (2026-07-30, later same night): verified. Headless Chromium
   (Playwright) rendering of arrow/index.html wired to this module was
   compared field-by-field against the original inline prototype -
   hover-highlight, click-to-open popup, rack-configuration swap, missile
   total recompute, and the non-missile (turret/gun) popup path all match
   exactly. This DID catch two real regressions on the first pass (two
   hardcoded provenance-note strings had been reworded during extraction -
   one dropped "(arrow_api_raw.json)", the other dropped a trailing
   sentence) - fixed here, see rackSourceLabel below. Full parity confirmed
   after the fix; see run_e2e_test.py's sibling viewer-parity check
   (compare.py, not committed - a one-off sandbox harness) for the method.

   Per-ship usage is meant to look like:

     import { createHardpointViewer } from '../../shared/hardpoint-viewer.js';
     createHardpointViewer({
       modelPath: 'model.glb',
       hardpointsPath: 'hardpoints.json',
       hardpointInfo: { ... },   // same shape as arrow's HARDPOINT_INFO
       rackConfigs: { ... },     // same shape as arrow's RACK_CONFIGS
     });

   A ship with no hardpoints.json (constellation-aquila, gladius as of
   2026-07-30 — see LATEST_HANDOFF.md) cannot use this yet: there is no
   hardpoint position data to load. That's real in-game port/placement
   data that has to be sourced per-ship the same way it was for the
   Arrow (data-layer/raw/<ship>/<ship>_api_raw.json ports tree), it is
   not something this engine can invent.
------------------------------------------------------------------ */
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';

export function createHardpointViewer(opts) {
  const {
    modelPath,
    hardpointsPath,
    hardpointInfo,
    rackConfigs,
    canvasWrapId = 'canvas-wrap',
    popupId = 'popup',
    missileTotalId = 'missile-total',
    modelScale = 0.01,
    // Shown in the rack-configuration popup's provenance note (e.g.
    // "arrow_api_raw.json"). Kept as a per-ship parameter rather than
    // hardcoded, since a shared engine hardcoding one ship's source
    // filename would be wrong for every other ship that uses it.
    rackSourceLabel = 'this ship\'s raw port-tree pull',
  } = opts;

  function infoForGunOrTurret(hp) {
    return hardpointInfo[hp.type];
  }

  /* ---------------- SCENE SETUP ---------------- */
  const wrap = document.getElementById(canvasWrapId);
  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0x0b0d12);

  const camera = new THREE.PerspectiveCamera(50, window.innerWidth / window.innerHeight, 0.1, 2000);
  camera.position.set(15, 10, 15);

  const renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.setPixelRatio(window.devicePixelRatio);
  wrap.appendChild(renderer.domElement);

  const controls = new OrbitControls(camera, renderer.domElement);
  controls.target.set(0, 0, 0);
  controls.enableDamping = true;

  scene.add(new THREE.HemisphereLight(0xffffff, 0x223344, 1.2));
  const key = new THREE.DirectionalLight(0xffffff, 1.4);
  key.position.set(10, 15, 8);
  scene.add(key);
  const rim = new THREE.DirectionalLight(0x88aaff, 0.6);
  rim.position.set(-10, -5, -10);
  scene.add(rim);

  /* ---------------- LOAD MODEL ---------------- */
  const loader = new GLTFLoader();
  const hudEl = document.getElementById('hud');

  loader.load(modelPath, (gltf) => {
    const shipMesh = gltf.scene;
    shipMesh.scale.set(modelScale, modelScale, modelScale);
    shipMesh.traverse((child) => {
      if (child.isMesh) {
        child.material = new THREE.MeshStandardMaterial({
          color: 0xb8bfcc, metalness: 0.4, roughness: 0.55,
        });
      }
    });
    scene.add(shipMesh);
    loadHardpoints();
  }, undefined, (err) => {
    console.error(`Failed to load ${modelPath}`, err);
    if (hudEl) {
      hudEl.innerHTML =
        `<b style="color:#ff7f7f">Could not load ${modelPath}</b><br>` +
        'Serve this folder with a local server, not by double-clicking the file.';
    }
  });

  /* ---------------- HARDPOINTS + MARKERS ----------------
     Axis conversion confirmed correct for the Arrow's model export:
     three.x = blender.x, three.y = blender.z, three.z = -blender.y.
     Re-verify this holds for any new ship's export before trusting it -
     it depends on how that model was exported, not on this engine. */
  const markers = [];
  const markerGeo = new THREE.SphereGeometry(0.12, 16, 16);
  const baseScale = 1;
  const hoverScale = 1.6;
  const selectedRack = {};

  function loadHardpoints() {
    fetch(hardpointsPath)
      .then(r => r.json())
      .then(data => {
        data.hardpoints.forEach((hp) => {
          const isMissile = hp.type === "missile_rack";
          const info = isMissile ? null : infoForGunOrTurret(hp);
          const color = (isMissile || info) ? 0x7fd0ff : 0xff5566;
          const mat = new THREE.MeshBasicMaterial({ color });
          const marker = new THREE.Mesh(markerGeo, mat);

          marker.position.set(hp.position.x, hp.position.z, -hp.position.y);
          marker.userData.hardpoint = hp;
          marker.userData.info = info;
          marker.userData.baseColor = color;
          scene.add(marker);
          markers.push(marker);

          if (isMissile) {
            selectedRack[hp.name] = rackConfigs[hp.label][0].id;
          }

          const ringGeo = new THREE.RingGeometry(0.16, 0.22, 24);
          const ringMat = new THREE.MeshBasicMaterial({
            color, transparent: true, opacity: 0.5, side: THREE.DoubleSide,
          });
          const ring = new THREE.Mesh(ringGeo, ringMat);
          ring.position.copy(marker.position);
          ring.userData.isRing = true;
          scene.add(ring);
          markers.push(ring);
        });
        updateMissileTotal();
      })
      .catch(err => console.error(`Failed to load ${hardpointsPath}`, err));
  }

  function updateMissileTotal() {
    let total = 0;
    Object.entries(selectedRack).forEach(([hpName, configId]) => {
      const hp = markers.find(m => m.userData.hardpoint && m.userData.hardpoint.name === hpName);
      if (!hp) return;
      const config = rackConfigs[hp.userData.hardpoint.label].find(c => c.id === configId);
      if (config) total += config.count;
    });
    const totalEl = document.getElementById(missileTotalId);
    if (totalEl) totalEl.textContent = total;
  }

  /* ---------------- HOVER + CLICK ---------------- */
  const raycaster = new THREE.Raycaster();
  const mouse = new THREE.Vector2();
  const popup = document.getElementById(popupId);
  let hovered = null;
  let pinnedHardpointName = null;

  function pickables() {
    return markers.filter(m => !m.userData.isRing);
  }

  function onPointerMove(e) {
    mouse.x = (e.clientX / window.innerWidth) * 2 - 1;
    mouse.y = -(e.clientY / window.innerHeight) * 2 + 1;

    raycaster.setFromCamera(mouse, camera);
    const hits = raycaster.intersectObjects(pickables(), false);
    const hit = hits.length ? hits[0].object : null;

    if (hit !== hovered) {
      if (hovered) hovered.scale.setScalar(baseScale);
      hovered = hit;
      if (hovered) hovered.scale.setScalar(hoverScale);
      wrap.classList.toggle('hovering', !!hovered);
    }
  }

  function renderPopup(hp) {
    const isMissile = hp.type === "missile_rack";

    if (isMissile) {
      const configs = rackConfigs[hp.label];
      const currentId = selectedRack[hp.name];
      let html = `<span class="close-btn" id="popup-close">&times;</span>`;
      html += `<h3>${hp.name.replace(/hardpoint_/,'').replace(/_/g,' ')}</h3>`;
      html += `<span class="type-tag">missile hardpoint - native size ${hp.label}</span>`;
      html += `<div class="section-label">Rack Configuration</div>`;
      configs.forEach(cfg => {
        const sel = cfg.id === currentId ? ' selected' : '';
        html += `<div class="rack-option${sel}" data-hp="${hp.name}" data-cfg="${cfg.id}">`
              +   `<span>${cfg.label}</span><span class="count">${cfg.count}x ${cfg.size}</span>`
              + `</div>`;
      });
      const activeCfg = configs.find(c => c.id === currentId);
      html += `<div class="note">${activeCfg ? activeCfg.note : ''}</div>`;
      html += `<div class="note">Rack options sourced from ${rackSourceLabel}, not assumed - only configurations the game data actually confirms are shown.</div>`;
      popup.innerHTML = html;

      popup.querySelectorAll('.rack-option').forEach(el => {
        el.addEventListener('click', (ev) => {
          ev.stopPropagation();
          selectedRack[el.dataset.hp] = el.dataset.cfg;
          updateMissileTotal();
          renderPopup(hp);
        });
      });
    } else {
      const info = infoForGunOrTurret(hp);
      let html = `<span class="close-btn" id="popup-close">&times;</span>`;
      if (!info) {
        html += `<h3>${hp.name}</h3><div class="note">No compatibility data wired up for this hardpoint yet.</div>`;
      } else {
        html += `<h3>${info.title}</h3><span class="type-tag">${hp.type.replace(/_/g,' ')}</span>`;
        html += `<div class="section-label">Currently Equipped</div>`;
        info.equipped.forEach(item => {
          html += `<div class="item-row equipped"><div class="item-name equipped-tag">${item.name}</div><div class="item-meta">${item.meta}</div></div>`;
        });
        if (info.variants && info.variants.length) {
          html += `<div class="section-label">Other Same-Size Options</div>`;
          info.variants.forEach(v => {
            html += `<div class="variant-row">${v}</div>`;
          });
        }
        html += `<div class="note">Variant list is unverified against in-game grade/fit compatibility - reference only until confirmed. Buy-location data not wired up yet.</div>`;
      }
      popup.innerHTML = html;
    }

    document.getElementById('popup-close').addEventListener('click', (ev) => {
      ev.stopPropagation();
      popup.style.display = 'none';
      pinnedHardpointName = null;
    });
  }

  function onClick(e) {
    raycaster.setFromCamera(mouse, camera);
    const hits = raycaster.intersectObjects(pickables(), false);

    if (hits.length === 0) {
      popup.style.display = 'none';
      pinnedHardpointName = null;
      return;
    }

    const hp = hits[0].object.userData.hardpoint;
    pinnedHardpointName = hp.name;
    renderPopup(hp);

    popup.style.display = 'block';
    const popupWidth = 340;
    const popupEstHeight = 380;
    popup.style.left = Math.min(e.clientX + 16, window.innerWidth - popupWidth - 8) + 'px';
    popup.style.top = Math.min(e.clientY + 16, window.innerHeight - popupEstHeight - 8) + 'px';
  }

  window.addEventListener('pointermove', onPointerMove);
  window.addEventListener('click', onClick);

  window.addEventListener('resize', () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
  });

  /* ---------------- RENDER LOOP ---------------- */
  let t = 0;
  function animate() {
    requestAnimationFrame(animate);
    t += 0.02;
    const pulse = 0.5 + Math.sin(t * 3) * 0.15;
    markers.forEach(m => {
      if (m.userData.isRing) m.material.opacity = pulse;
    });
    controls.update();
    renderer.render(scene, camera);
  }
  animate();

  return { scene, camera, renderer, controls };
}
