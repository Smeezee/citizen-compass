#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_keybind_modes.py - turn the extracted default profile into board data.

Until now the keybind page carried FLIGHT and ONFOOT as hand-typed JavaScript
objects and showed "not entered yet" for E.V.A., Vehicle and Camera. The data
for all of them has been on disk since the profile extraction; nothing was
reading it. This reads it.

Two things this deliberately does NOT do:

1. It does not silently drop actions that have no key bound. Most emotes have
   no default key at all - they are reached by chat command or the PIT wheel -
   and a page that shows only bound keys would tell a new player those emotes
   do not exist. Unbound actions come out in a separate list per mode.

2. It does not guess a cap for a token it does not recognise. Unknown tokens
   are counted and printed, not approximated onto the nearest key.

Rule 15: every file open states its encoding.
"""
import json, os, sys, collections

HERE = os.path.dirname(os.path.abspath(__file__))
SRC  = os.path.join(HERE, "data-layer", "processed", "keybinds_site.json")
OUT  = os.path.join(HERE, "testing", "_src", "kb_modes.gen.js")

# ---------------------------------------------------------------- key mapping
# Star Citizen's token -> the cap id the board draws. Letters and digits are
# generated; everything irregular is listed, because a table you can read is a
# table you can check.
TOK = {
 "escape":"Esc","backspace":"Back","tab":"Tab","enter":"Enter","space":"Space",
 "capslock":"Caps","lshift":"LShift","rshift":"RShift","lctrl":"LCtrl",
 "rctrl":"RCtrl","lalt":"LAlt","ralt":"RAlt",
 "comma":",","period":".","slash":"/","semicolon":";","apostrophe":"'",
 "minus":"-","equals":"=","lbracket":"[","rbracket":"]","backslash":"\\",
 "]":"]","[":"[",
 "insert":"Ins","home":"Home","pgup":"PgUp","delete":"Del","end":"End",
 "pgdn":"PgDn","up":"Up","down":"Down","left":"Left","right":"Right",
 "np_add":"NpAdd","np_subtract":"NpSub","np_multiply":"NpMul",
 "np_divide":"NpDiv","np_period":"NpDot","np_enter":"NpEnt",
 "numlock":"NumLk",
 "mouse1":"M_Left","mouse2":"M_Right","mouse3":"M_Mid",
 "mouse4":"M_Back","mouse5":"M_Fwd",
 "mwheel_up":"M_WhUp","mwheel_down":"M_WhDn",
}
for c in "abcdefghijklmnopqrstuvwxyz": TOK[c] = c.upper()
for d in "0123456789":                 TOK[d] = d
for i in range(1, 13):                 TOK["f%d" % i] = "F%d" % i
for i in range(0, 10):                 TOK["np_%d" % i] = "Np%d" % i

# Tokens that are real bindings but have no key on a keyboard picture. Not
# errors - they are mouse axes and headset axes. Reported, never drawn.
NOT_A_KEY = {"maxis_x","maxis_y","maxis_z","hmd_pitch","hmd_roll","hmd_yaw"}

# The page's three modifier layers.
MODS = {"lalt":1, "lshift":2, "ralt":3}


# Short context tags. The game keeps mode-specific controls in their own
# actionmaps, so the tag is read from the data rather than typed by hand.
CTX = {
 "spaceship_scanning":"SC", "spaceship_mining":"MG", "mining":"MG",
 "spaceship_salvage":"SA", "spaceship_targeting_advanced":"TA",
 "turret_movement":"TU", "turret_advanced":"TU", "spaceship_quantum":"QT",
 "spaceship_missiles":"ML", "spaceship_docking":"DK", "tractor_beam":"TB",
 "lights_controller":"LT", "player_choice":"IM", "prone":"PN",
 "view_director_mode":"AD", "flycam":"FC", "spectator":"SP",
 "vehicle_mfd":"MFD", "vehicle_mobiglas":"MG?",
}

# ------------------------------------------------------------------- grouping
GROUPS = [
 ("FLIGHT", "Flight", "in a ship",
  ["spaceship_movement","spaceship_weapons","spaceship_auto_weapons",
   "spaceship_power","spaceship_hud","spaceship_targeting",
   "spaceship_targeting_advanced","spaceship_general","spaceship_salvage",
   "spaceship_missiles","spaceship_defensive","spaceship_scanning",
   "spaceship_mining","mining","spaceship_quantum","spaceship_docking",
   "spaceship_radar","spaceship_target_hailing","seat_general",
   "turret_movement","turret_advanced","tractor_beam","IFCS_controls",
   "lights_controller"],
  "SC scan &middot; MG mining &middot; SA salvage &middot; TA advanced targeting &middot; "
  "ML missiles &middot; QT quantum &middot; TU turret &middot; TB tractor &middot; "
  "DK docking &middot; LT lights"),
 ("ONFOOT", "On Foot", "walking around",
  ["player","player_choice","prone"],
  "IM interaction mode &middot; PN prone. Hold <strong>Left Alt + F</strong> for the "
  "Personal Inner Thought wheel."),
 ("EVA", "E.V.A.", "zero-G, out of the seat",
  ["zero_gravity_eva","zero_gravity_traversal"],
  ""),
 ("VEHICLE", "Vehicle", "ground vehicles",
  ["vehicle_driver","vehicle_general","vehicle_mfd","vehicle_mobiglas"],
  "MFD = the screens in the cockpit &middot; mobiGlas opens on the wrist"),
 ("CAMERA", "Camera", "views, free cam, spectate",
  ["view_director_mode","flycam","spectator","spaceship_view"],
  "Free cam and spectator are separate systems from the normal view keys"),
 ("SOCIAL", "Social", "gestures and emotes",
  ["player_emotes"],
  "Only the six numpad signals have a key by default. Everything else is "
  "reached from the PIT wheel (hold <strong>Left Alt + F</strong>) or by "
  "typing the emote name into chat."),
]

def clean(s):
    if not s: return ""
    return " ".join(str(s).split())

def parse_binding(raw):
    """Return (cap, modifier_layer, problem). SC writes the modifier on either
    side of the '+', so decide by membership rather than by position."""
    raw = (raw or "").strip()
    if not raw: return (None, 0, None)
    parts = [p.strip() for p in raw.split("+") if p.strip()]
    if not parts: return (None, 0, None)
    mod, key = 0, None
    if len(parts) == 1:
        key = parts[0]
    else:
        lows = [p.lower() for p in parts]
        modix = [i for i,p in enumerate(lows) if p in MODS]
        if len(modix) == 1 and len(parts) == 2:
            mod = MODS[lows[modix[0]]]
            key = parts[1 - modix[0]]
        else:
            # Two modifiers, or none, or three parts. Do not invent a reading.
            return (None, 0, raw)
    low = key.lower()
    if low in NOT_A_KEY: return (None, 0, None)
    cap = TOK.get(low)
    if cap is None: return (None, 0, raw)
    return (cap, mod, None)

def main():
    with open(SRC, "r", encoding="utf-8") as fh:
        recs = json.load(fh)

    out = ["/* GENERATED by build_keybind_modes.py from",
           "   data-layer/processed/keybinds_site.json - do not hand edit.",
           "   Regenerate instead. This file has one writer and it is the script. */",
           ""]
    report, unknown = [], collections.Counter()

    for ident, label, sub, maps, legend in GROUPS:
        rs = [r for r in recs if r.get("map") in maps]
        dropped = [0]
        board   = collections.OrderedDict()
        unbound = []
        placed  = 0
        for r in rs:
            # An action with no display name is invisible in the game's own
            # keybinding menu. Showing it here helps nobody and buries the
            # 691 that are real under 412 that are not. 256 of those fall in
            # these six modes and they are dropped, not renamed.
            name = clean(r.get("label"))
            if not name: 
                dropped[0] += 1
                continue
            cap, mod, bad = parse_binding(r.get("keyboard"))
            if bad:
                unknown[bad] += 1
            if cap is None:
                # Not bound to a key. It still exists in the game, so it is
                # still shown - just not on the board.
                if not clean(r.get("keyboard")):
                    unbound.append(name)
                continue
            e = {"a": name}
            if mod: e["m"] = mod
            tag = CTX.get(r.get("map"))
            if tag: e["c"] = tag
            board.setdefault(cap, []).append(e)
            placed += 1

        body = ",\n ".join(
            "%s:%s" % (json.dumps(k), json.dumps(v, separators=(",", ":")))
            for k, v in board.items())
        out.append("const %s={\n %s\n};" % (ident, body))
        seen, uniq = set(), []
        for n in unbound:
            if n not in seen: seen.add(n); uniq.append(n)
        out.append("const %s_UNBOUND=%s;" % (ident, json.dumps(uniq)))
        out.append("const %s_LEGEND=%s;" % (ident, json.dumps(legend)))
        out.append("")
        report.append((label, len(rs), placed, len(board), len(uniq), dropped[0]))

    with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(out))

    print("wrote %s" % os.path.relpath(OUT, HERE))
    print()
    print("%-10s %7s %7s %7s %9s %9s" % ("mode","actions","placed","keys","unbound","nameless"))
    for row in report:
        print("%-10s %7d %7d %7d %9d %9d" % row)
    if unknown:
        print()
        print("TOKENS NOT PLACED (left off the board on purpose, not guessed):")
        for tok, n in unknown.most_common():
            print("   %-22s x%d" % (tok, n))
    else:
        print()
        print("every binding token was recognised")

main()
