# UPDATE — testing site deployed and verified from served bytes

## Pre-stage re-hash — all three matched

Re-hashed immediately before staging, per instruction:

| file | result |
|---|---|
| `testing/_src/_layer.src.html` | `c26caed…6167634` **match** |
| `testing/_layer.html` | `058d9ce…3582c65` **match** |
| `testing/_deploy/index.html` | `be79501…8de8fb08` **match** |

Landed 00:19:25-27, re-hashed 00:29:56 — stable, no drift.

## Deploy

Cloudflare Workers static assets, worker **`citizencompasstesting`** — the name
matched `wrangler.toml`, so this updated the existing site rather than creating
a second one at a second URL.

```
482 files read from _deploy
1 new or modified asset uploaded: /index.html   (479 already uploaded)
Uploaded citizencompasstesting (8.46 sec)
https://citizencompasstesting.citizencompass-contact.workers.dev
Version ID: 7adec060-3a72-4c1c-857a-adbf967d1d1f
```

Only `index.html` changed, which is consistent with a layout-only edit.

**One blocker cleared on the way:** `wrangler whoami` reported "not
authenticated". `CLOUDFLARE_API_TOKEN` **is** in `.env` (53 chars) — wrangler
simply does not read `.env`. Loaded it into the environment for the invocation.
I did **not** use `wrangler deploy --temporary`, which wrangler suggested: that
publishes to a temporary preview account, which is exactly the
two-URLs-in-circulation failure `wrangler.toml` warns about at length.

My first check of that token was also wrong — a `grep -o` truncated at the `=`
and made a populated value look empty. Corrected before acting on it.

## Verified from the served bytes, not the exit code

| check | result |
|---|---|
| index serves | **HTTP 200**, `text/html`, 1,513,625 bytes |
| served index == local | **sha256 identical** (`be79501e…`) |
| model serves | `100i.glb` **HTTP 200**, 1,487,156 bytes |
| model byte count vs local | **exact match** |
| model is a real glTF | magic bytes `glTF` |

Required markers, all present in the **served** HTML:

| marker | occurrences |
|---|---:|
| `cc-ldock` | 10 |
| `cc-kb-tab` | 8 |
| `cc-fi-tab` | 7 |
| `cc-mtab` | 10 |
| `id="cc-kb"` | 1 |
| `cc-ship::after` | 2 |

The exit code was 0, but it is not what any of the above rests on.

## Observation on the leftover positioning rule

`calc(44% + 430px)` — LOADOUT's old slot — is **gone**. `calc(44% + 570px)`
still appears once, in the *first* `#cc-fi-tab` rule.

It is inert. There are five `#cc-fi-tab` rules, and the fourth overrides it:

```css
#cc-fi-tab{top:auto !important;bottom:10px;right:376px; …}
```

`top:auto !important` beats the earlier `top:calc(44% + 570px)`, so FIND is
never placed at 1045px.

Worth knowing how the dock actually works: the tabs are moved into `#cc-ldock`
by **JavaScript at runtime**, with a retry loop ("keep looking until the
late-built ones arrive"), not by static markup — `cc-fi-tab` is not inside the
dock element in the served HTML. `#cc-ldock` itself is
`transform:translateY(-50%)`, i.e. genuinely vertically centred rather than
stacked from 44%.

**The failure mode if that script does not run is benign:** the CSS fallback
puts FIND at `bottom:10px; right:376px` — on screen, not off it. That is a
better degradation than the old stack had.

No action taken on the stale rule; it changes nothing and is not in scope.

## Not committed

No commit-and-push go-ahead was given for this task, and rule 2 requires it per
change. The `build_deploy.py` edit from the previous order also remains
uncommitted in the working tree.

Live Netlify site untouched.
