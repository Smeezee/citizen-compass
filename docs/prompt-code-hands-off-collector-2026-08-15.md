# PROMPT FOR CODE — the collector starts with the game, sends when the game closes, and asks nobody anything. One order, four parts.

    from    C1, 2026-08-15
    for     Code
    status  GO-AHEAD. Ruled by Sleven this session:
              docs/DECISION_hands-off-collector-and-public-download-2026-08-15.md
    order   ONE consolidated order, per Sleven's standing instruction. Do not
              expect a follow-up amending it.

    QUEUE   This is LAST. Ahead of it, in order:
              1. prompt-code-never-run-from-the-desktop-2026-08-15.md
              2. prompt-code-loadout-entry-point-2026-08-15.md
            Both are smaller and both are already hurting somebody.

---

## 0. The shape Sleven asked for

> "here's the program. every time you play Star Citizen it runs collects the
> information. collects this folder and sends it back to our database"

**Nothing to launch, nothing to press, nothing to configure.** The destination
already arrives down the feed as of 0.3.1, so the last manual steps left are
starting it and sending.

---

## 1. It starts when Star Citizen does

**This is not a new architecture decision.** Sleven's standing rule already
covers it: long-running components run as real background services — auto-start,
silent, no visible console window, survive reboot. Build to that rule.

- **A small resident component starts with Windows** and watches for the game or
  its launcher. When the game appears, the collector runs. **Removing it must be
  one obvious action**, not registry surgery — a program that is hard to uninstall
  has changed category.
- **It must not fight the single-instance guard.** `single_instance.go` exists
  because double-clicking the icon started a second collector, and the restart
  handover has already been mis-diagnosed once this project. Auto-start plus a
  manual double-click is now an ordinary daily occurrence, not an edge case.
- **Idle cost has to be near zero.** This sits on a gaming machine forever. If
  the watcher costs measurable CPU while nothing is happening, it is wrong.
- **Report what it does on a machine where the game is never installed.** It must
  sit quiet and harmless, not log an error every few seconds for a year.

## 2. It sends when the game closes — if the person chose that

**Sleven's ruling, in full, is in the decision doc. The short form:** the consent
screen offers a choice and the person picks.

```
send automatically when I finish playing
ask me every time
```

- **The choice is made at install, on the consent screen, in those plain words.**
  Not buried in a settings file.
- **It is changeable later** from the window, without editing anything.
- **EXISTING INSTALLS DEFAULT TO ASK-EVERY-TIME.** Sleven's wife and his friend
  agreed to a README that says *"It never sends anything on its own. Not on a
  timer, not in the background, not when you are not looking."* **Flipping them to
  automatic would make that sentence false on machines where somebody already said
  yes to it.** They get asked, once, and then it is their answer.
- **Update `README-FOR-TESTERS.txt` in the same commit.** That paragraph is the
  promise; if the behaviour gains an option, the promise gains the same option, in
  the same plain language. **A README that no longer describes the program is
  worse than no README** — it is a written statement the product contradicts.
- The trigger is the game-exit edge, which `auto.go` already has.

## 3. A successful send wipes the SCREENSHOTS only

- **Pictures go. The extracted dataset stays**, so a contributor can see what they
  gave.
- **Nothing is deleted that the server has not confirmed receiving.**
  `clear_after_send` already works this way. **That is the rule, not an
  implementation detail** — a dropped connection must never cost somebody their
  session. Rule 5: destructive steps prove themselves first.
- **The 64 MB ceiling is now load-bearing and it is going to be hit.** Sleven's
  friend has 76 frames sitting on one machine. If an automatic send is refused for
  size, the person is not watching — so it must **retry sensibly, or split, or
  keep the frames and say so next time the window is opened.** It must never
  silently drop data because an unattended send failed, and it must never delete
  after a refusal.

## 4. The public download page

**Sleven ruled: ships UNSIGNED.** Signing costs a few hundred a year and the
project is free by standing ruling.

**So the page's job is to make the warning survivable.** A person who was told
what they are about to see reads it as honesty; the same box unannounced reads as
malware.

- **Say exactly what Windows will show them, before they click** — the blue
  "Windows protected your PC" box, More info, Run anyway — and why it appears: the
  program is not signed, because signing costs money the project does not take.
- **Say antivirus may quarantine it**, and why the behaviour looks the way it does
  to a scanner: it reads files, takes screenshots and uploads. **Do not talk
  anyone out of their scanner.** State it and link the source so a suspicious
  person can read the code instead of trusting a paragraph.
- **Lead with what it does NOT do.** `README-FOR-TESTERS.txt` already has the
  right list and the right tone — no game modification, no injection, no memory
  reading, no chat, no automation. Reuse that voice; do not write a new one.
- **No signup. No email box. No "register your interest" form.** Ruled out
  explicitly. GitHub's own download count is the interest signal.
- The page is a testing-site page and goes through the normal build. **Verify it
  by fetching it back off the live URL**, not by a successful deploy.

## 5. What NOT to do

- **Do not auto-send on an existing install without asking.** §2. This is the one
  that matters most.
- **Do not delete anything the server has not confirmed.** §3.
- **Do not collect email addresses.** §4.
- **Do not make this the thing you do first.** §QUEUE.
- **Do not `git add -A`.**

## 6. Acceptance

1. Game launches → collector runs, with nothing clicked. Game closes → it acts on
   the person's stated choice, and only that choice.
2. A machine that chose ask-every-time never sends unattended. **Negative control:
   a machine that chose automatic does.** Without both, neither is proven.
3. An install upgraded from 0.3.1 is on ask-every-time until it is asked.
4. A refused or failed automatic send deletes nothing and is visible to the person
   afterwards.
5. Screenshots clear after a confirmed send; the dataset survives.
6. The resident watcher survives a reboot, shows no console window, and is
   removable in one obvious action.
7. On a machine with no Star Citizen installed, it idles quietly and logs nothing
   repetitive.
8. The download page states the SmartScreen warning and the antivirus possibility
   before the download link, and is confirmed present on the live URL.
9. `README-FOR-TESTERS.txt` describes the program that now exists.
10. `-selftest` passes, with a negative control for each of 1-5.

## 7. Report back

- Whether the auto-start mechanism you chose can be removed by an ordinary person,
  and how.
- Measured idle cost of the watcher.
- What an automatic send does when it is refused for size, observed rather than
  intended.
- Anything in §1 you think is unsafe on somebody else's machine. **That section
  puts a resident process on computers belonging to people who are not in this
  conversation**, and it is the part most worth arguing with.
