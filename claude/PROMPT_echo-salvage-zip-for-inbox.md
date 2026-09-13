# Echo instructions — salvage zip for the Citizen Compass inbox

**Sleven drops this zip on his desktop inbox shortcut.** The watcher already unpacks `.zip` files from `inbox/`, sorts each file inside, then archives the zip under `_zip_archive/`.

You cannot see his disk. Your job is to **build the zip with the right labels** so sorting works.

---

## Zip file name (required)

```
echo-salvage_YYYY-MM-DD_short-slug.zip
```

Examples:
- `echo-salvage_2026-09-12_design-chat.zip`
- `echo-salvage_2026-09-12_before-reboot.zip`

Use **today’s date**. Lowercase. Underscores. No spaces.

---

## What goes INSIDE the zip (rules)

1. **Only `.md` files** when possible.  
   `.txt`, `.docx`, `.pdf` are unrecognized and get dumped in `_needs_review/` — almost useless.

2. **Every important note is a memo** with this header at the top (exact field names):

```markdown
# Memo

To:      Design
From:    Echo
Date:    YYYY-MM-DD
Status:  Open
Subject: short plain subject — what this piece is

<body>
```

- **To:** must be a real desk: `Design`, `Architecture`, `Build`, `Research`, `Audit`, or `Owner`.  
  For chat salvage that is design work, default **To: Design**.  
  If it is for Sleven’s decisions only, **To: Owner**.  
  If it is a technical finding for C1, **To: Architecture**.
- **From:** always `Echo` for this pack.
- **Subject:** unique per file; no two files share the same subject.

3. **One cover memo** (required), filename like:

`memo_design_echo-salvage-cover-YYYY-MM-DD.md`

Subject example: `Echo chat salvage — cover list of what is in this zip`

Body: bullet list of every other file in the zip and one line on why it matters.

4. **Split the chat** into separate memos by topic (decisions, open questions, copy drafts, research notes). Do not put the entire transcript in one giant file unless he asks.

5. **No nested zips** inside the zip.

---

## What Sleven does

1. Downloads your zip.  
2. Drops it on his **inbox** desktop shortcut (folder `citizen-compass/inbox/`).  
3. Watcher unpacks → each memo files to `correspondence/open/<desk>/` → original zip goes to `_zip_archive/`.

He does **not** need a second drop folder for this path.

---

## Quick checklist before you zip

- [ ] Zip name starts with `echo-salvage_` + date  
- [ ] Cover memo present, To: Design, From: Echo  
- [ ] Every other file is `.md` with To / From / Date / Status / Subject  
- [ ] No .txt / .docx unless he explicitly wants `_needs_review`  
- [ ] Subjects are unique  

When done, tell him the exact zip filename to drop.
