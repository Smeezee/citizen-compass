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

const MAX_BYTES = 512 * 1024 * 1024; // a generous export with screenshots

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

    const declared = (request.headers.get("X-Collector-Sha256") || "").toLowerCase();
    const install  = (request.headers.get("X-Collector-Install") || "unknown")
                       .replace(/[^a-zA-Z0-9-]/g, "").slice(0, 64) || "unknown";
    const version  = (request.headers.get("X-Collector-Version") || "?")
                       .replace(/[^a-zA-Z0-9.\-]/g, "").slice(0, 32);

    const body = await request.arrayBuffer();
    if (body.byteLength === 0) {
      return json({ ok: false, message: "empty upload" }, 400);
    }
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
    if (declared && declared !== sha) {
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
