/* _dracopos.mjs - decode POSITION out of a (possibly Draco-compressed) GLB and
   write raw little-endian float32 xyz triples to a file.

   Rule 15: the GLB is read as bytes; the JSON chunk is decoded UTF-8.

   Exists because the hull models ship Draco-compressed, so the mesh a marker is
   supposed to sit on cannot be read with struct alone. Called by
   _verify_marker_mesh_distance.py; not a control itself.

   usage: node checks/_dracopos.mjs <in.glb> <out.f32>
   exit 2 with a reason on stderr if the decoder is unavailable. */
import { readFileSync, writeFileSync } from "node:fs";
let draco3d;
try { draco3d = (await import("draco3d")).default; }
catch { console.error("NO_DRACO"); process.exit(2); }
const dec = await draco3d.createDecoderModule({});
const [, , inPath, outPath] = process.argv;
const b = readFileSync(inPath);
if (b.subarray(0, 4).toString() !== "glTF") { console.error("NOT_GLB"); process.exit(2); }
let off = 12, js = null, bin = null;
while (off < b.length) {
  const ln = b.readUInt32LE(off), ty = b.readUInt32LE(off + 4); off += 8;
  const ch = b.subarray(off, off + ln); off += ln;
  if (ty === 0x4E4F534A) js = JSON.parse(new TextDecoder().decode(ch));
  else if (ty === 0x004E4942) bin = ch;
}
const all = [];
for (const m of js.meshes || []) for (const pr of m.primitives || []) {
  const d = pr.extensions?.KHR_draco_mesh_compression;
  if (d) {
    const bv = js.bufferViews[d.bufferView];
    const o = bv.byteOffset || 0;
    const seg = bin.subarray(o, o + bv.byteLength);
    const buf = new dec.DecoderBuffer(); buf.Init(new Int8Array(seg), seg.length);
    const decoder = new dec.Decoder(), mesh = new dec.Mesh();
    decoder.DecodeBufferToMesh(buf, mesh);
    const id = decoder.GetAttributeByUniqueId(mesh, d.attributes.POSITION);
    const n = mesh.num_points(), arr = new dec.DracoFloat32Array();
    decoder.GetAttributeFloatForAllPoints(mesh, id, arr);
    for (let i = 0; i < n * 3; i++) all.push(arr.GetValue(i));
    dec.destroy(arr); dec.destroy(mesh); dec.destroy(decoder); dec.destroy(buf);
    continue;
  }
  const ai = pr.attributes?.POSITION; if (ai === undefined) continue;
  const acc = js.accessors[ai]; if (acc.bufferView === undefined) continue;
  const bv = js.bufferViews[acc.bufferView];
  const base = (bv.byteOffset || 0) + (acc.byteOffset || 0);
  const stride = bv.byteStride || 12;
  for (let i = 0; i < acc.count; i++) {
    const o = base + i * stride;
    all.push(bin.readFloatLE(o), bin.readFloatLE(o + 4), bin.readFloatLE(o + 8));
  }
}
if (!all.length) { console.error("NO_POSITIONS"); process.exit(2); }
writeFileSync(outPath, Buffer.from(new Float32Array(all).buffer));
console.log(all.length / 3);
