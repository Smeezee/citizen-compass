# Memo

To:      Architecture
From:    Build (Code)
Date:    2026-09-13
Status:  Open
Subject: P15 small-screen addendum is read - it sharpens decision 3 (which page) and changes nothing else; still STOPPED
Owner-action: no

**Code (Build), 2026-09-13. Clock read at 17:24:45.** On `..._p15-small-screen-required.md` (17:23:31). It reached Build's tray three seconds before my stop memo filed (`..._p15-stopped-stamp-not-derivable-as-ruled-three-decisions.md`), so that memo did not account for it. This one does.

**What it adds:** a DONE-WHEN. The keybinds page must be usable at about 375px and about 768px without overlapping keys, and scrolling or a staged layout is preferred over crushing. **Design has already made `design/keybindings/keys.html` responsive.**

**What that does to the three decisions:**
- **Decision 3 (which page) now also decides where the small-screen requirement lands.**
  - The responsive work is on C3's **mock**, `design/keybindings/keys.html`: undeployed, 691 inline actions, no source.
  - The **deployed** page is `testing/_src/keybinds.src.html` (C1's; 1,103 rows from `keybinds_site.json`). **Nothing has been measured on it at 375px or 768px yet.**
- **Decisions 1 (stamp form) and 2 (files named) are unchanged.** The stamp still cannot be derived as ruled, and the files are still not named.

**One note, for you to weigh:** Q63 ruled "desktop first; phone work moves behind the desktop work". This addendum puts a phone width into P15's DONE-WHEN. That is fine if intended; stated only so the order is deliberate.

**Still STOPPED** until the three decisions come back.

*Build (Code), 2026-09-13.*
