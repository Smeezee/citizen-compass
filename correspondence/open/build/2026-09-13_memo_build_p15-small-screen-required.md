# Memo

To:      Build
From:    Architecture / Design (Grok)
Date:    2026-09-13
Status:  Open
Subject: P15 addendum — Keyboard First must work on small screens
Owner-action: no

Owner: chat preview looked smashed; mock had almost no responsive CSS. Design patched `design/keybindings/keys.html` with breakpoints (scale keys; horizontal scroll before crush; hide per-key action text only on very narrow phones).

**DONE-WHEN add-on:** keybinds page usable at ~375px and ~768px widths without overlapping/unreadable keys. Prefer scroll or staged layout over smashing the board.

*Grok, 2026-09-13.*