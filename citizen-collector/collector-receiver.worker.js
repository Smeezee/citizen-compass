// collector-receiver.worker.js - the thing that receives an export.
//
// DEPLOY ONCE, ON CLOUDFLARE'S FREE TIER. No running cost, and Citizen Compass
// is already on Cloudflare.
//
//   1. Create an R2 bucket, e.g. "collector-uploads".
//   2. Create a Worker, paste this in.
//   3. Bind the bucket to the Worker as BUCKET.
//   4. Set a secret named UPLOAD_KEY to a long random string.
//   5. Put the Worker's URL and that key into each collector's settings:
//        send_url = https://<your-worker>.workers.dev/upload
//        send_key = <the same long random string>
//
// # WHAT THIS DELIBERATELY CANNOT DO
//
// It accepts uploads. That is all. It cannot list, read, or delete anything,
// and no route exists that would let it - not even with the key.
//
// That is not caution for its own sake. The key lives in a settings file on a
// machine somebody else owns, so it must be assumed to be public eventually.
// A key that can only ADD is a key whose leak costs you junk in a bucket. A key
// that could read would leak every contributor's data to whoever found it.
//
// # THE KEY IS NOW PUBLISHED, SO IT IS NOT A SECRET - 2026-08-15
//
// send_key ships in releases/collector-latest.json, a public file, so that a
// contributor never has to type a 51-character password. That is a deliberate
// trade, written up in docs/ROTATING-THE-UPLOAD-KEY.md.
//
// What it means HERE: the key stops casual abuse and nothing more. It is a
// revocable channel identifier, not an authentication secret, and calling it
// one would be exactly the comfortable lie this project keeps finding.
// Everything below the key check is what actually bounds the damage:
//
//   - a size ceiling a real export cannot exceed, checked BEFORE the body is
//     read into memory
//   - a per-install rate limit
//   - a total-storage brake, so a flood cannot run up a bill
//   - shape checks that reject anything a collector would not have built
//
// Those are the controls. The key only keeps honest people honest.
//
// # WHY IT HASHES WHAT IT STORED RATHER THAN ECHOING WHAT IT WAS TOLD
//
// The client sends a SHA256 and only clears its local copy when the reply
// matches. If this endpoint simply echoed the header back, that check would
// confirm nothing - it would be the sender agreeing with itself, and a
// truncated upload would still clear the sender's data.
//
// So the hash is computed HERE, over the bytes that actually arrived and were
// actually written. A short upload produces a different hash, the client
// refuses to clear, and the contributor keeps their data. That is the only
// direction this is allowed to fail in.

// A REAL EXPORT HAS A CEILING, AND 512 MB WAS NOT IT.
//
// The largest export seen in the field is 27 MB, with screenshots. 512 MB was
// set when the endpoint was private and the only sender was a collector; with a
// published key it is an invitation to fill a bucket at somebody else's expense.
const MAX_BYTES = 64 * 1024 * 1024;

// A zip carrying a dataset and a README cannot be smaller than this. Anything
// under it is not a truncated export, it is somebody poking.
const MIN_BYTES = 256;

// Per install, per hour. People play; they do not send twelve exports an hour.
// Evadable by inventing new install ids - which is exactly why the storage
// brake below does not depend on it.
const MAX_PER_INSTALL_HOUR = 12;

// THE BRAKE THAT DOES NOT CARE WHO YOU SAY YOU ARE.
//
// R2's free tier is 10 GB and Sleven pays for whatever goes over. This refuses
// new uploads once the bucket carries more than this, whoever is sending, so
// the worst case is a full bucket rather than a bill. Clearing it is
// scripts/pull_and_clear.py, which is what the refusal tells the sender.
const SOFT_TOTAL_BYTES = 6 * 1024 * 1024 * 1024;

// The shapes a collector genuinely produces. Anything else is not a collector.
const RE_INSTALL = /^[A-Za-z0-9-]{8,64}$/;
const RE_VERSION = /^[0-9]+(\.[0-9]+)*$/;
const RE_SHA256 = /^[0-9a-f]{64}$/;

export default {
  async fetch(request, env) {
    if (request.method !== "POST") {
      return json({ ok: false, message: "POST an export here." }, 405);
    }

    // Constant-time-ish compare. Not a real defence on its own, but there is no
    // reason to hand out a timing signal for free.
    const key = request.headers.get("X-Collector-Key") || "";
    if (!env.UPLOAD_KEY || !safeEqual(key, env.UPLOAD_KEY)) {
      return json({ ok: false, message: "no" }, 403);
    }

    // SHAPE FIRST, AND STRICTLY.
    //
    // These used to be sanitised into something usable - a missing install id
    // became "unknown", a junk version was filtered down to whatever survived.
    // That is the right instinct for a trusted sender and the wrong one now: it
    // turned malformed requests into stored objects. A real collector always
    // sends all three, so a request that does not is not one.
    const declared = (request.headers.get("X-Collector-Sha256") || "").toLowerCase();
    const install = (request.headers.get("X-Collector-Install") || "").trim();
    const version = (request.headers.get("X-Collector-Version") || "").trim();

    if (!RE_INSTALL.test(install)) {
      return json({ ok: false, message: "no usable install id" }, 400);
    }
    if (!RE_VERSION.test(version)) {
      return json({ ok: false, message: "no usable version" }, 400);
    }
    // The hash is REQUIRED now, not optional. It is what lets the sender decide
    // whether it is safe to clear its only copy, and an upload declining to
    // declare one is not an upload this endpoint has reason to accept.
    if (!RE_SHA256.test(declared)) {
      return json({ ok: false, message: "no declared sha256" }, 400);
    }

    // REFUSE ON THE DECLARED LENGTH BEFORE READING THE BODY.
    //
    // The old order called arrayBuffer() first and checked size after, so a
    // caller could make this Worker buffer half a gigabyte just by saying it was
    // coming. Refusing on Content-Length costs nothing and never touches the
    // payload.
    const declaredLen = Number(request.headers.get("content-length") || "0");
    if (declaredLen > MAX_BYTES) {
      return json({ ok: false, message: "too large" }, 413);
    }

    // RATE LIMIT, then the storage brake. Both read the bucket rather than any
    // external service, so there is nothing extra to deploy or pay for.
    const now = Date.now();
    const recent = await env.BUCKET.list({ prefix: "uploads/" + install + "/", limit: 1000 });
    const lastHour = recent.objects.filter(
      (o) => now - new Date(o.uploaded).getTime() < 3600 * 1000).length;
    if (lastHour >= MAX_PER_INSTALL_HOUR) {
      return json({
        ok: false,
        message: "too many uploads from this install in the last hour - try later",
      }, 429);
    }

    const all = await env.BUCKET.list({ prefix: "uploads/", limit: 1000 });
    const stored = all.objects.reduce((n, o) => n + (o.size || 0), 0);
    if (stored > SOFT_TOTAL_BYTES) {
      // 507, and it says what to do about it. A refusal nobody can act on is a
      // fault report addressed to nobody.
      return json({
        ok: false,
        message: "the receiving bucket is full - the operator needs to run " +
                 "pull_and_clear before it can accept more. Your data is still " +
                 "on your machine and nothing was lost.",
      }, 507);
    }

    const body = await request.arrayBuffer();
    if (body.byteLength < MIN_BYTES) {
      return json({ ok: false, message: "too small to be an export" }, 400);
    }
    // Checked AGAIN against what actually arrived. Content-Length is a claim;
    // this is the measurement.
    if (body.byteLength > MAX_BYTES) {
      return json({ ok: false, message: "too large" }, 413);
    }

    // It must actually be a zip. PK\x03\x04. This is not security - it is
    // refusing to store something that cannot be what it claims to be.
    const head = new Uint8Array(body.slice(0, 4));
    if (!(head[0] === 0x50 && head[1] === 0x4b && head[2] === 0x03 && head[3] === 0x04)) {
      return json({ ok: false, message: "that is not a zip" }, 415);
    }

    // OUR OWN hash, over what arrived.
    const digest = await crypto.subtle.digest("SHA-256", body);
    const sha = [...new Uint8Array(digest)]
      .map((b) => b.toString(16).padStart(2, "0")).join("");

    // If the sender told us a hash and it does not match, store nothing. The
    // sender will not clear its copy, which is correct.
    if (declared !== sha) {
      return json({
        ok: false, sha256: sha, bytes: body.byteLength,
        message: "what arrived does not match what you said you sent - nothing stored",
      }, 409);
    }

    const stamp = new Date().toISOString().replace(/[:.]/g, "-");
    const objectKey = `uploads/${install}/${stamp}-${sha.slice(0, 12)}.zip`;

    await env.BUCKET.put(objectKey, body, {
      httpMetadata: { contentType: "application/zip" },
      customMetadata: { install, version, sha256: sha, bytes: String(body.byteLength) },
    });

    // Confirm only AFTER the write resolves. Confirming before it lands would
    // tell a contributor it is safe to delete their only copy.
    return json({
      ok: true, sha256: sha, bytes: body.byteLength, stored_as: objectKey,
      message: "received and stored",
    });
  },
};

function json(obj, status = 200) {
  return new Response(JSON.stringify(obj), {
    status, headers: { "content-type": "application/json" },
  });
}

function safeEqual(a, b) {
  if (a.length !== b.length) return false;
  let diff = 0;
  for (let i = 0; i < a.length; i++) diff |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return diff === 0;
}
