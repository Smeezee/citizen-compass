# Update — HOTAS rebinding pushed and live

Sleven: "push it". Commit **`0f0409c`** — "Rebinding now hears a flight stick,
not just a keyboard". 4 files, 194 insertions. Pushed `6a4edbf..0f0409c`,
`origin/main` confirmed after a re-fetch.

Deployed: 2 assets changed (`keybinds.html`, `index.html`), version
`48a01ce0-f2f1-4124-ba74-ca333af2eb03`.

## Live verification

```
/keybinds   local 95,438     live 95,438     EXACT   guard x3, ungated poll x2
/ (index)   local 1,591,306  live 1,591,306  EXACT   guard x3
```

**The index needed a cache-buster to verify.** The first fetch came back
1,590,139 with zero occurrences of the fix, which looked exactly like a failed
publish. It was `CF-Cache-Status: HIT` — a stale edge copy. Re-fetched with a
cache-buster it is byte-identical and carries the fix.

Worth knowing before anybody reports the fix "not working": **the index page may
serve from cache for a while. Ctrl+F5.** `/keybinds` was current immediately.

## What is now testable with a real stick

Click a binding, press a stick button — it should take `js1_button3` and
friends, from any tab, without switching to Joystick/HOTAS first. Hats give
their full compound token. Axes work as well as buttons.

**Gamepads still will not rebind** — `xi_a` is refused with a readable reason,
because the tester and the exporter disagree about the prefix and there is no
evidence here to settle which is right. Joystick and HOTAS are unaffected.

## Still outstanding, unchanged

- The two shortcuts my earlier test overwrote — Sleven has to repoint them; the
  write was blocked when I tried.
- The cloud-upload order is queued behind
  `prompt-code-MASTER-clear-the-queue-2026-08-10.md`, which I have never
  received.
- Collector self-update remains broken for everyone until 0.2.0 is published
  (`gh` not installed).
