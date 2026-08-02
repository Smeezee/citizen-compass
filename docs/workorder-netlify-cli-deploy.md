# WORK ORDER — Netlify CLI deploys for the preview site

**Approved by Sleven 2026-08-02.** Goal: a text-only change should deploy in seconds, not by re-uploading 349 MB.

Hard rule 13 applies: file an `inbox/` update on intake, on completion, and on any stop.

## Why

Every preview deploy today is a drag-and-drop of `testing/_deploy` — **349 MB, models and images included, every time**, even when only `index.html` changed. The Netlify CLI hashes files and uploads only what differs, so a layer rebuild becomes a one-second push.

## The one thing that must not go wrong

**There are two Netlify sites: the live Citizen Compass site and the preview site. A deploy aimed at the wrong one replaces the live website.**

Drag-and-drop protected against this by accident — `app.netlify.com/drop` always creates or targets a separate site. A CLI removes that accident. **So the site ID must be pinned in a script, not typed at a prompt.** A human typing a site name at 2am is exactly the failure this order exists to prevent.

## Steps

### 1. Confirm Node and npm on Windows

`testing/_tools/node_modules` exists, so npm has run there — but confirm versions rather than assume:

```
node --version
npm --version
```

Node 18+ required. If it's older or absent, stop and file that; do not upgrade Node without asking.

### 2. Install

```
npm install -g netlify-cli
netlify --version
```

### 3. Authenticate — Sleven does this, not Claude Code

```
netlify login
```

Opens a browser and asks him to authorize. **Claude Code must not attempt to enter credentials.** Stop here, tell him, wait.

### 4. Capture the preview site's ID — the load-bearing step

```
netlify sites:list
```

Record **both** sites' names and API IDs in the completion note. Identify which is live (citizencompass.netlify.app) and which is the preview.

**Verify the ID belongs to the preview site before writing it into anything.** Cross-check the site name against the URL Sleven has been sharing with his friends. If there is any ambiguity at all, stop and ask — a wrong ID here overwrites the live site on the next deploy.

### 5. Write `deploy-preview.ps1` at the repo root

Requirements, all of them safety rather than convenience:

- **Site ID hardcoded** in the script. Not a parameter, not an env var, not a prompt.
- **`--dir` hardcoded** to `testing/_deploy`.
- **Refuse to run if `testing/_deploy/index.html` is missing** — a partial or wrong folder must fail before upload, not after.
- **Refuse to run if `testing/_deploy/models` is missing or holds fewer than 200 files.** A Netlify deploy is a full atomic replacement: pushing a folder without models silently strips every 3D model from the live preview while the page still loads and looks fine. That is the worst failure mode here because nothing announces it.
- **Print the target site name and URL and require a typed confirmation** before uploading.
- **Echo the resulting deploy URL** at the end.

No `--prod` flag anywhere in this script that could be repointed by editing one argument. If a live-site deploy is ever wanted, that is a separate script written deliberately, not a flag on this one.

### 6. Rule 12 — prove the guards fire

A guard that has never rejected anything is not a guard. Demonstrate each:

1. Rename `index.html` aside → script refuses, uploads nothing. Restore.
2. Point `--dir` at an empty temp folder → refuses.
3. Simulate a models folder with 3 files → refuses on the count check.
4. Then a real deploy, and confirm from the deploy log that **only changed files uploaded** — the whole point of the exercise. Record the uploaded-file count and elapsed time against the 349 MB baseline.

### 7. Confirm the preview still works

Open the preview URL in a private window. Password screen → `apples` → matrix loads → a ship page opens with its 3D model. **Models specifically**, because that is what a bad deploy silently removes.

## Boundaries

- The live site is not touched. No script in this order may target it.
- `testing/_deploy/` stays gitignored. `deploy-preview.ps1` gets committed.
- If anything is ambiguous about which site is which, stop and ask.
