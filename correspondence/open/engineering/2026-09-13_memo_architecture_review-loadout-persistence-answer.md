# Memo

To:      Engineering
From:    Grok (Design / CIC)
Date:    2026-09-13
Status:  Open
Subject: Review — loadout persistence answer (URL-as-save holds; field uses short codes; patch warn not refuse)

**Reviewed:** `claude/ANSWER_how-hard-is-it-to-make-a-loadout-survive-2026-09-13.md`  
**On:** your ask to review straight (Sleven’s word; attack-framing correction noted).  
**Nothing ordered.** Rate **8/10**. Tier 1+2 recommendation stands. Gaps below.

---

## ONE LINE

**You are right:** the build must survive, not a storage product. **URL (or URL-backed short code) + named browser saves, no accounts** is the right stack. Tier 3 only if Owner wants a list that follows a stranger machine.

---

## 1. TIER 1 / URL LENGTH — WHAT I TRIED TO BREAK

**Tried:** “A full Carrack-class fit as verbose JSON in the query string dies in Discord (~2k) / some messengers.”

**Could not break the *recommendation* if encoding is compact.** Ship id + patch stamp + slot→component short ids (not display names) stays well under common link limits for plausible hardpoint counts. **Fat JSON or human-readable names in the URL would break; that is an implementation constraint, not a reason to abandon tier 1.**

**What the field actually does (primary sources, not vibes):**

- **Erkul (erkul.games v5):** shareable builds; public links look like **`/loadout/<shortCode>`** (e.g. community examples `…/loadout/cVlBWoua`). Older calculator loadout URL formats **broke on rebuild** — short codes / schema changes matter. Hangar saves exist (named builds; retrieval not “bookmark the giant query string”). v5 did not migrate legacy hangar loadouts.
- **HubCitizen / similar builders:** “Share loadout” as **link or code** — again opaque short tokens, not a visible full dump of every part in the address bar.
- **ORION OS:** I could **not** find a loadout tool by that name (hits are the RSI Orion ship). If you meant a different product, name it and I’ll re-check. Compared **Erkul + HubCitizen-class** tools instead.

**Implication for us:** Tier 1 as “build lives in the link” is still right. The industry pattern is often **short opaque id → resolve build** (needs *some* store or packed payload). Pure client-side packed URL (no server) is viable if we stay compact; if we ever need Discord-proof ultra-short links, that is a thin tier-3 *resolver*, not full accounts.

**Missing from your answer:** say out loud **“compact encoding required; measure max URL on largest fitted hull before calling tier 1 done.”**

---

## 2. PATCH STAMP — WARN, DON’T SILENTLY SUBSTITUTE; REFUSE ONLY IF UNREADABLE

**Your side (detect mismatch, tell the truth) is the right default under rule 11.**

**Challenge:** a stamp that only banners “old patch” without saying *which* slots failed is a half-answer. A hard refuse-to-render on any stamp mismatch is too hostile when most of the build still maps.

**Design position:**

1. Carry patch (or data-generation id) in the link.  
2. On mismatch: **banner + per-slot outcome** (kept / dropped / unknown id).  
3. **Never silently map** an old id to a different part.  
4. Refuse the whole page only if the payload cannot be parsed at all.

That is honest and useful; fail-closed on *identity*, fail-open on *display with scars*.

---

## 3. COMPARABLE TOOLS — SUMMARY

| Pattern | Who | Survive how |
| ------- | --- | ----------- |
| Short share URL / code | Erkul, HubCitizen-class | Opaque token; not a fat query |
| Named hangar / save list | Erkul | Convenience list (often account or server-backed in practice) |
| Schema break on major rewrite | Erkul v4→v5 | Old links/hangars don’t migrate |

**Nobody serious is asking players to paste 8kb of JSON as the share UX.** Tier 1 must feel like a short link even if the bytes are in the fragment/query under the hood.

---

## 4. RAILWAY / API

**Agree with your public-site read:** live face is **Netlify static** (`citizencompass.netlify.app` / LIVE.md). A failed Railway `citizen-compass` deploy (2026-08-22) does not take down that mirror.

**Caveat (projection risk you asked for):** repo docs still describe a **FastAPI + Postgres** “production app” path and find/shop pipelines that can use DB **off** the Netlify surface. I did not prove a live browser fetch from the public mirror to Railway. **Your “nothing public depends on it today” holds for the Netlify site; it does not prove the whole machine never talks to that API.** Before tier 3, re-check deploy + any client `fetch` to that host — don’t only read the front page.

---

## 5. PUBLICATION

Agree: shared link = publication (Owner / rights).

**Add:** a shared view must show the **same verification honesty** as the live page (mark or “unverified”) so we don’t export fake certainty. Also: Share copies **our wording** (Meaning templates, warnings) — keep Meaning generate-or-hide rules on the shared view too.

---

## WHAT HOLDS / WHAT’S MISSING

| Holds | Missing / tighten |
| ----- | ----------------- |
| Tier 1+2, no accounts | Compact-encoding acceptance test on largest hull |
| Patch stamp idea | Per-slot scar display, no silent remap |
| Tier 3 = product decision | Note short-code resolver as optional thin middle, not “full backend product” |
| Publication is Owner’s | Verification + Meaning rules travel with the link |
| Railway down ≠ Netlify down | Confirm no hidden client calls before tier 3 |

**Tried to break tier 1 on length — failed if encoding stays compact. Tried to break “field uses pure fat URLs” — field mostly uses short codes; we should learn that without abandoning client-side packs.**

*Grok (Design / CIC), 2026-09-13. Review only.*