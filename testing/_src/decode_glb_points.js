/* decode_glb_points.js - the hull's own vertices, out of a .glb, locally.

   WHY THIS EXISTS
   ===============

   The fleet hardpoint derivation (place_fleet.py) ran in a cloud sandbox
   against pre-decoded geometry at /home/claude/fleet/geo. That geometry is not
   in this repo and the sandbox is gone, so nothing here could place a marker on
   a hull - which is why 29 ships whose mount data we already hold could not be
   recovered by editing a name and re-running.

   Every model in testing/_deploy/models is KHR_draco_mesh_compression, so the
   positions cannot be read out of the file directly. The decoder is already
   vendored, in the copy the viewer itself uses:

       testing/_src/vendor/three/examples/js/libs/draco/

   So this reads the same file, with the same decoder, that a visitor's browser
   reads - rather than adding a dependency or trusting a second implementation
   to agree with the first.

   RULE 7. The .wasm here is vendored in this repo and is what the deployed page
   already loads in every visitor's browser. This is not downloaded data being
   executed.

   USAGE
       node testing/_src/decode_glb_points.js <out-dir> <model.glb> [more.glb...]

   Writes <out-dir>/<stem>.json  =  {"model":..., "count":..., "sampled":...,
                                     "min":[x,y,z], "max":[x,y,z], "pts":[...]}

   THE BOUNDING BOX IS COMPUTED FROM EVERY VERTEX, and the point list is
   SUBSAMPLED. Those are two different jobs: the box decides the hull's frame
   and must see all of it, while the points are only used to snap a marker to
   the nearest real surface, where a uniform sample of 80,000 is indistinguishable
   from 400,000 at the scale a marker is drawn. The sampling is recorded in the
   file rather than left for somebody to infer.
*/
'use strict';

const fs = require('fs');
const path = require('path');

const DRACO_DIR = path.join(__dirname, 'vendor', 'three', 'examples', 'js',
                            'libs', 'draco');
const MAX_POINTS = 80000;

function readGlb(file) {
  const buf = fs.readFileSync(file);
  if (buf.readUInt32LE(0) !== 0x46546C67) throw new Error('not a .glb: ' + file);
  let off = 12, json = null, bin = null;
  while (off < buf.length) {
    const len = buf.readUInt32LE(off);
    const type = buf.readUInt32LE(off + 4);
    const start = off + 8;
    if (type === 0x4E4F534A) json = JSON.parse(buf.slice(start, start + len).toString('utf8'));
    else if (type === 0x004E4942) bin = buf.slice(start, start + len);
    off = start + len;
  }
  if (!json) throw new Error('no JSON chunk: ' + file);
  return { json, bin };
}

function loadDraco() {
  // The wrapper is an emscripten module that expects to fetch its .wasm. Handed
  // the bytes directly instead, so nothing reaches the network.
  const src = fs.readFileSync(path.join(DRACO_DIR, 'draco_wasm_wrapper.js'), 'utf8');
  const wasm = fs.readFileSync(path.join(DRACO_DIR, 'draco_decoder.wasm'));
  const mod = { exports: {} };
  // __dirname and __filename are handed in: the wrapper reads them while
  // deciding where its .wasm lives, and inside a `new Function` they do not
  // exist. It never gets to use them - wasmBinary below means it has the bytes
  // already and never looks - but it references them on the way past.
  const factory = new Function(
    'module', 'exports', 'require', '__dirname', '__filename',
    src + '\nreturn typeof DracoDecoderModule !== "undefined" ? DracoDecoderModule : module.exports;'
  )(mod, mod.exports, require, DRACO_DIR, path.join(DRACO_DIR, 'draco_wasm_wrapper.js'));

  // THIS BUILD IS NOT A PROMISE AND ITS CALLBACK IS NOT onModuleLoaded.
  //
  // The vendored wrapper is a browser emscripten build whose tail calls
  // `onModuleParsed` and returns the module object directly. Waiting on a
  // promise that never settles, or on the callback name every DRACOLoader
  // example uses, hangs forever - which it did, for five minutes, with no
  // output. So: take the returned module and wait for the runtime to be usable,
  // with a deadline that FAILS rather than one that waits.
  // `Decoder` EXISTING IS NOT THE RUNTIME BEING READY.
  //
  // The module object carries stub bindings from the moment it is created, so
  // `typeof m.Decoder === "function"` is true immediately - and `new
  // m.Decoder()` then dies with "Cannot read properties of undefined (reading
  // 'apply')" because the wasm exports it forwards to do not exist yet. What
  // readiness actually looks like is decided in the poll below.
  const m = factory({ wasmBinary: wasm });

  // AND THE MODULE IS A THENABLE, WHICH IS WHY THIS HUNG.
  //
  // Emscripten gives its Module a `then` method so it can be awaited. Resolving
  // a promise WITH a thenable makes the promise adopt it - so `resolve(m)` did
  // not hand the module back, it called `m.then(resolve, reject)` and waited for
  // a hook that never fires once the runtime is already up. The result was a
  // process that sat there forever having printed "Decoder function" one line
  // earlier. Two kills and a log file to find it.
  //
  // Removing `then` makes it an ordinary object again. The decoder API is
  // untouched.
  if (m && typeof m.then === 'function') delete m.then;

  return new Promise((resolve, reject) => {
    const deadline = Date.now() + 30000;
    (function poll() {
      // READY MEANS A REAL BINDING EXISTS, not a hook and not a stub.
      //
      // `onRuntimeInitialized` and `onModuleParsed` were both passed in and
      // NEITHER fires in this build - measured, with a probe that recorded every
      // callback it was given. Waiting on them waited the full 30s and then gave
      // up on a runtime that had been usable since 100ms.
      //
      // `_malloc` is a compiled export rather than a forwarding stub, so its
      // presence is the instantiation actually having happened.
      // PROVED BY DOING IT, not by inspecting the module.
      //
      // Every cheaper signal has been wrong here in turn: the callbacks never
      // fire, `Decoder` is a stub from the first millisecond, and even
      // `_malloc` existing is early - the embind classes forward to exports
      // that are still being registered, so a Decoder built at that moment dies
      // with "Cannot read properties of undefined (reading 'apply')".
      //
      // So the check is: construct one. If it constructs, the runtime is up.
      try {
        const probe = new m.Decoder();
        m.destroy(probe);
        return resolve(m);
      } catch (e) {
        /* not ready yet - fall through to the deadline and try again */
      }
      if (Date.now() > deadline) {
        return reject(new Error('the DRACO runtime never became usable within ' +
          '30s. Nothing was decoded - do not read that as "these ships have no ' +
          'hardpoints".'));
      }
      setTimeout(poll, 20);
    })();
  });
}

function decodePositions(draco, bytes) {
  const decoder = new draco.Decoder();
  const buffer = new draco.DecoderBuffer();
  buffer.Init(new Int8Array(bytes), bytes.length);
  const type = decoder.GetEncodedGeometryType(buffer);
  const mesh = type === draco.TRIANGULAR_MESH ? new draco.Mesh() : new draco.PointCloud();
  const status = type === draco.TRIANGULAR_MESH
    ? decoder.DecodeBufferToMesh(buffer, mesh)
    : decoder.DecodeBufferToPointCloud(buffer, mesh);
  if (!status.ok()) throw new Error('draco refused the mesh: ' + status.error_msg());

  const id = decoder.GetAttributeId(mesh, draco.POSITION);
  if (id < 0) throw new Error('this mesh has no POSITION attribute');
  const attr = decoder.GetAttribute(mesh, id);

  // BULK COPY OUT OF THE WASM HEAP, not GetValue() per float.
  //
  // The obvious version - DracoFloat32Array and a loop calling out.GetValue(i)
  // - crosses the JS/wasm boundary once per float. On a 400,000-vertex hull
  // that is 1.2 million crossings and it does not finish in any time worth
  // waiting for: the first run of this looked like a hang and had to be killed
  // twice before the cause was clear, because node buffers writes to a pipe and
  // a blocked event loop never flushes them. One malloc and one memcpy instead.
  const n = mesh.num_points();
  const byteLength = n * 3 * 4;
  const ptr = draco._malloc(byteLength);
  decoder.GetAttributeDataArrayForAllPoints(mesh, attr, draco.DT_FLOAT32,
                                            byteLength, ptr);
  const pts = new Float32Array(draco.HEAPF32.buffer, ptr, n * 3).slice();
  draco._free(ptr);

  draco.destroy(mesh);
  draco.destroy(buffer);
  draco.destroy(decoder);
  return { pts, n };
}

async function main() {
  const args = process.argv.slice(2);
  if (args.length < 2) {
    console.error('usage: node decode_glb_points.js <out-dir> <model.glb> [...]');
    process.exit(2);
  }
  const outDir = args[0];
  const files = args.slice(1);
  if (!fs.existsSync(outDir)) fs.mkdirSync(outDir, { recursive: true });

  process.stdout.write('  loading the DRACO runtime\n');
  const draco = await loadDraco();
  process.stdout.write('  runtime ready\n');

  let failed = 0;
  for (const file of files) {
    const stem = path.basename(file).replace(/\.glb$/i, '');
    try {
      const { json, bin } = readGlb(file);
      let min = [Infinity, Infinity, Infinity], max = [-Infinity, -Infinity, -Infinity];
      let all = [];
      let total = 0;

      for (const mesh of json.meshes || []) {
        for (const prim of mesh.primitives || []) {
          const ext = (prim.extensions || {}).KHR_draco_mesh_compression;
          if (!ext) continue;
          const bv = json.bufferViews[ext.bufferView];
          const start = bv.byteOffset || 0;
          const bytes = bin.slice(start, start + bv.byteLength);
          process.stdout.write('    decoding ' + bv.byteLength + ' bytes\n');
          const { pts, n } = decodePositions(draco, bytes);
          process.stdout.write('    decoded ' + n + ' points\n');
          total += n;
          for (let i = 0; i < n; i++) {
            const x = pts[i * 3], y = pts[i * 3 + 1], z = pts[i * 3 + 2];
            if (x < min[0]) min[0] = x; if (x > max[0]) max[0] = x;
            if (y < min[1]) min[1] = y; if (y > max[1]) max[1] = y;
            if (z < min[2]) min[2] = z; if (z > max[2]) max[2] = z;
          }
          all.push({ pts, n });
        }
      }

      if (!total) throw new Error('no draco-compressed primitive found');

      // Uniform stride, not the first N: taking the first N points of a mesh
      // takes one corner of the ship, and every marker would then snap to that
      // corner.
      const stride = Math.max(1, Math.ceil(total / MAX_POINTS));
      const kept = [];
      let idx = 0;
      for (const chunk of all) {
        for (let i = 0; i < chunk.n; i++, idx++) {
          if (idx % stride) continue;
          kept.push(
            Math.round(chunk.pts[i * 3] * 1e4) / 1e4,
            Math.round(chunk.pts[i * 3 + 1] * 1e4) / 1e4,
            Math.round(chunk.pts[i * 3 + 2] * 1e4) / 1e4
          );
        }
      }

      fs.writeFileSync(path.join(outDir, stem + '.json'), JSON.stringify({
        model: path.basename(file),
        count: total,
        sampled: kept.length / 3,
        stride: stride,
        min: min, max: max,
        pts: kept,
      }));
      console.log('  decoded %s  %d vertices -> %d sampled  box %s',
        stem, total, kept.length / 3,
        JSON.stringify(min.map((v, i) => Math.round((max[i] - v) * 100) / 100)));
    } catch (e) {
      failed++;
      console.log('  FAILED  %s  %s', stem, e.message);
    }
  }
  if (failed) {
    console.error('%d model(s) could not be decoded. Nothing downstream should ' +
                  'treat those as "no hardpoints" - they are "not read".', failed);
    process.exit(1);
  }
}

/* E7b: THE SAME DECODER, LENT OUT, RATHER THAN A SECOND ONE.
   `checks/_verify_edge_detail.mjs` needs positions, normals AND the index
   buffer out of the same files, decoded by the same wasm the browser runs.
   Writing a second decoder for it would be two implementations of the one
   thing whose agreement the whole measurement depends on - rule 14. So this
   file exports its own helpers and stays a CLI: `main()` runs only when it is
   the entry point, which is what the `require.main` guard below is for.

   Returns whatever attributes are asked for, plus the triangle indices.
   Positions are always read because the caller cannot do anything without
   them. */
function decodeMesh(draco, bytes, want) {
  want = want || {};
  const decoder = new draco.Decoder();
  const buffer = new draco.DecoderBuffer();
  buffer.Init(new Int8Array(bytes), bytes.length);
  const type = decoder.GetEncodedGeometryType(buffer);
  if (type !== draco.TRIANGULAR_MESH) {
    draco.destroy(buffer); draco.destroy(decoder);
    throw new Error('not a triangular mesh - there are no faces to find edges '
      + 'between, and reporting an edge count for it would be a number about '
      + 'nothing');
  }
  const mesh = new draco.Mesh();
  const status = decoder.DecodeBufferToMesh(buffer, mesh);
  if (!status.ok()) throw new Error('draco refused the mesh: ' + status.error_msg());

  const n = mesh.num_points();
  const pull = (which) => {
    const id = decoder.GetAttributeId(mesh, which);
    if (id < 0) return null;
    const attr = decoder.GetAttribute(mesh, id);
    const comps = attr.num_components();
    const byteLength = n * comps * 4;
    const ptr = draco._malloc(byteLength);
    decoder.GetAttributeDataArrayForAllPoints(mesh, attr, draco.DT_FLOAT32,
                                              byteLength, ptr);
    const out = new Float32Array(draco.HEAPF32.buffer, ptr, n * comps).slice();
    draco._free(ptr);
    return { data: out, comps };
  };

  const out = { n, pos: pull(draco.POSITION) };
  if (!out.pos) throw new Error('this mesh has no POSITION attribute');
  if (want.normals) out.nrm = pull(draco.NORMAL);

  /* The index buffer, in bulk for the same reason the attributes are. */
  const faces = mesh.num_faces();
  const idxBytes = faces * 3 * 4;
  const iptr = draco._malloc(idxBytes);
  decoder.GetTrianglesUInt32Array(mesh, idxBytes, iptr);
  out.idx = new Uint32Array(draco.HEAPU32.buffer, iptr, faces * 3).slice();
  draco._free(iptr);
  out.faces = faces;

  draco.destroy(mesh);
  draco.destroy(buffer);
  draco.destroy(decoder);
  return out;
}

module.exports = { readGlb, loadDraco, decodePositions, decodeMesh };

// EXIT DELIBERATELY.
//
// The emscripten runtime keeps handles open, so node never returns to the shell
// on its own - the first run of this looked like a five-minute hang, and when it
// was killed the pipe took the output with it. Everything is written to disk
// before this point, so exiting here loses nothing.
if (require.main === module) {
  main().then(
    () => { process.exit(0); },
    (e) => { console.error(String((e && e.message) || e)); process.exit(1); }
  );
}
