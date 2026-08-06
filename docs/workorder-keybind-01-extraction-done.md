# WORK ORDER — keybindings: the blocker is broken, here is the data

    id            WO-KEYBIND-01
    raised by     C2 (Cowork), 2026-08-02
    for           C1 -> Claude Code
    status        EXTRACTION DONE. Data is on the machine. Build C is unblocked.
    repo writes   C2 made none

---

## 1. WHAT CHANGED

`defaultProfile.xml` — recorded as the only missing piece for Build C in
`docs/workorder-front-end-build-plan.md` §6, and unresolved since — **has been
extracted, decoded and joined.**

It was inside `LIVE/Data.p4k` (161 GB). No third-party tool was used and nothing
was installed. The file was located by reading the archive's own central
directory and pulling **37,950 bytes** out of it.

**Two output files are on the machine now:**

    Downloads\defaultProfile.plain.xml    218,387 bytes  the decoded profile
    Downloads\keybinds_site.json          311,854 bytes  joined, site-ready

**Move both into the repo where they belong — C2 does not write to the repo.**
Suggested `data-layer/processed/`.

---

## 2. HOW IT WAS DONE — so it can be repeated every patch

Repeatable in about a minute. **This must be re-run on every patch**, because
default bindings change.

1. **Locate the archive.** `LIVE/Data.p4k`. Standard ZIP64 container:
   ZIP64 EOCD at the tail gives **1,364,115 entries** and a **463.6 MB central
   directory**.
2. **Scan the central directory** for `defaultProfile`. Whole scan takes ~4.4 s.
   One hit: `Data\Libs\Config\defaultProfile.xml`.
3. **Read the entry.** Local header signature is `PK\x03\x04`; sizes and offset
   live in the ZIP64 extra field (id `0x0001`), not the base header — the base
   fields are all `0xFFFFFFFF`. Compression **method 100 = ZStandard**.
   Compressed 37,950 → uncompressed 183,915.
4. **Decompress.** Raw zstd frame, magic `28b52ffd`. **`zstd` and `unzstd` are
   already on the machine** — no install needed.
5. **Decode CryXmlB.** The result is *not* text XML. It is CryEngine binary XML,
   magic `CryXmlB\x00`, little-endian header at offset 8:

       fileLength, nodeTableOffset, nodeCount, attrTableOffset, attrCount,
       childTableOffset, childCount, stringTableOffset, stringDataSize

   Node = 28 bytes (`<IIHHIIII`): tagStrOff, contentStrOff, attrCount,
   childCount, parentIdx, firstAttrIdx, firstChildIdx, reserved.
   Attribute = 8 bytes: keyStrOff, valueStrOff. Child table = u32 node indices.
   Strings are null-terminated at `stringTableOffset + offset`.

   **Self-check that confirms the layout parsed correctly:**

       nodeTableOffset + nodeCount*28   == childTableOffset
       childTableOffset + childCount*4  == attrTableOffset
       attrTableOffset  + attrCount*8   == stringTableOffset
       stringTableOffset + stringDataSize == fileLength

   All four held. **Assert them — a wrong endianness or offset produces garbage
   that still parses.**

---

## 3. WHAT IS IN IT — measured

    actionmaps                         50
    actions inside actionmaps       1,103
    actions with a keyboard default   515
    actions with a mouse binding      179
    actions with a joystick binding   836
    actions with a gamepad binding    862
    activation modes defined           21

**Joined against `labels.json` (source 1, 90,121 labels):**

    display name resolved             691  of 753 refs
    group name resolved               940
    category resolved                 849
    description resolved              210  of 674 refs
    descriptions that ADD something
      beyond repeating the label       86

**Categories, by action count:**

    FLIGHT 410 · ON FOOT 197 · Social-General 60 · Vehicle 47 ·
    Quick Keys/Interactions/Inner Thought 39 · CAMERA 32 ·
    Electronic Access-Spectator 28 · E.V.A. 23 · VOIP/FOIP/Head Tracking 13

35 distinct groups.

---

## 4. TWO CORRECTIONS TO THE RECORD

**4a. The description count was wrong, in both directions.**
`docs/workorder-front-end-build-plan.md` §6 says *"130 of them have CIG-written
descriptions."* The profile actually references **674** descriptions, of which
**210 resolve** in source 1's labels — but **only 86 say anything the display
name does not already say.** Many are literal repeats
(`Flight / Systems Ready` → `Flight / Systems Ready`).

**86 is the honest number for "actions with a real explanation."** It is still
more than the competing tool has — Star Binder's developer states most keybinds
are missing descriptions — but **do not quote 674 or 210 as a coverage figure.**

**4b. At least one description contradicts its own binding.**
`v_emergency_exit` is bound to `u+lshift`, and its description reads
*"Press LShift + H to engage emergency exit."* **The prose is stale relative to
the data.** Show the binding from the binding field, never parse it out of the
description text.

---

## 5. THE KEY FORMAT — and the mapping the browser needs

**97 distinct base keys. 9 modifiers:**

    lalt  ralt  lctrl  rctrl  lshift  u  f5  f6  f7

`u` as a modifier is unusual and real — `v_emergency_exit` is `u+lshift`.
`f5`/`f6`/`f7` as modifiers are real too. **Do not assume modifiers are only
alt/ctrl/shift.**

**Base key tokens, complete:**

    letters      a-z (also uppercase K — one entry is 'ralt+K')
    digits       0-9 (no 8 bound by default)
    function     f1-f12
    numpad       np_0-np_9, np_add, np_subtract, np_multiply, np_divide, np_period
    navigation   up down left right home end pgup pgdn
    editing      enter tab space backspace escape pause
    punctuation  comma minus equals slash lbracket rbracket ]
    mouse        mouse1 mouse2 mouse3 mwheel_up mwheel_down
    other        maxis_z, HMD_Pitch, HMD_Roll, HMD_Yaw

**Binding kinds:** 461 plain keys, 34 function keys, 20 mouse.

**Mapping rule, and it is the one that silently breaks otherwise:**
`docs/workorder-front-end-build-plan.md` §6 already establishes that the tester
must use **physical key position (`event.code`)**, never the typed character.
That rule now has a concrete mapping table to satisfy: `comma` → `Comma`,
`lbracket` → `BracketLeft`, `np_add` → `NumpadAdd`, and so on.

**`]` appears as a raw token** alongside `rbracket`. Handle both, and log
anything unmapped rather than silently dropping it.

---

## 6. WHAT TO BUILD

**Replace the invented data in `testing/_src/keybinds.src.html`.** That prototype
was transcribed by eye from screenshots, carries orange `?` marks on uncertain
entries, and covers Flight and On Foot only, keyboard and mouse only. **All of it
is now superseded.**

`keybinds_site.json` rows:

    action      internal name (v_emergency_exit)
    map         actionmap name (seat_general)
    group       resolved group label
    category    resolved category label (FLIGHT, ON FOOT, ...)
    label       resolved display name
    desc        resolved description, or null
    keyboard    default binding, or null
    mouse joystick gamepad
    activation  activation mode name

**Build order suggestion:** categories → groups → actions. That mirrors CIG's own
Advanced Controls screen, which is what people are trying to match.

**Keep:** the live key tester, the visual keyboard map, and the 21 activation
modes (tap / double_tap / hold / delayed_press with real thresholds — that data
is in the profile and nobody else exposes it).

---

## 7. VERIFICATION — HARD RULE 12

    actionmaps                    == 50
    actions                       == 1103
    keyboard defaults             == 515
    labels resolved               == 691
    descriptions resolved         == 210
    descriptions adding info      == 86
    distinct base key tokens      == 97
    the four CryXmlB offset self-checks in §2 all hold

**Assert every base key token maps to an `event.code`.** An unmapped token must
raise, not silently render blank — that is how a keyboard map ends up with holes
nobody notices.

**These numbers are patch-specific.** They will change with 4.10, and that is the
signal to re-extract, not a bug.

---

## 8. NOT VERIFIED

- **Whether `HOTFIX/Data.p4k` differs.** Only LIVE was read. HOTFIX is a
  different build and may carry different defaults.
- **Why 464 description references do not resolve.** They may exist in source 2's
  labels (63,375 entries) or in a localisation file not yet pulled. **Worth
  checking — it could raise the useful-description count well above 86.**
- **Joystick and gamepad token formats.** 836 and 862 bindings exist; only the
  keyboard tokens were enumerated.
- **Whether `optionGroup`, `useAnalogCompare` and the analog fields matter** for
  display. Present in the data, not examined.
- **The `actiongroup` blocks** (e.g. `v_attack` → `v_attack_all`,
  `v_attack_group1`) were not modelled. They may matter for grouping in the UI.
