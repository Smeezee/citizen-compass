# PROMPT FOR CODE — publish the stick diagnostic as a page. Small and urgent.

    from    C1, 2026-08-12
    for     Code
    why     Sleven has no flight sticks of his own. The hardware is on a
              friend's machine in another room. I handed him a local HTML file
              to run — useless, since the file is on the wrong computer. It has
              to be a URL he can open over there.
    scope   one file into testing/_src/, one line in PAGES, build, deploy.

---

## 1. The job

`stick-test.html` is already on disk at the repo root — I wrote it, it's
self-contained, no dependencies, and it uses **none** of the site's code. That
independence is the entire point: it answers "can this browser see the stick at
all" without any of our detection logic in the way.

1. Move it to `testing/_src/stick-test.src.html` (or whatever matches the
   `PAGES` convention — follow what's there, don't invent).
2. Add it to `PAGES` so it copies verbatim.
3. **Check `check_deploy_clean.py`'s `DEFAULT_ALLOWED_FILES`** — the standalone
   list that does not update itself from `PAGES`. Adding a page without it
   gives a false failure against a clean build.
4. Build and deploy.

Do not restyle it, do not wire it into the nav, do not make it depend on
anything. A diagnostic that shares code with the thing it is diagnosing is
worthless.

## 2. Why this jumps the queue

Everything else on the keybind page is currently blocked behind one unanswered
question: **does Chrome see his VKB sticks at all?**

- If yes → our detection has a bug and there is real work to do.
- If no → nothing we build on that page will ever help, and the problem is a
  VKB mode or browser-level issue.

Three rounds of fixes have shipped without anyone knowing which of those is
true. That is the thing to stop doing. **This page is the cheapest possible
answer and it costs one deploy.**

## 3. What it reports

Device count and names, `mapping` (standard vs raw HID — worth knowing for a
VKB), live axis values, and live button states with an event log. So if it does
work, the same page hands us the real axis indices and button numbers for his
friend's actual hardware — which is exactly what the "be prescriptive about
what each button does" work needs and what nobody has.

## 4. Acceptance

1. Reachable at a plain URL on the testing site, no password.
2. Works on a machine that has never opened the site before.
3. Contains no reference to `device_engine.js`, `KBREBIND`, or any site script.
4. `build_deploy.py` and `check_deploy_clean.py` pass clean.

## 5. Report back

The URL, and confirmation it loads clean in a fresh browser profile.

## Commands

```
python testing/_src/build_deploy.py
```

```
python testing/_src/check_deploy_clean.py
```
