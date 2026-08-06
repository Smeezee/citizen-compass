#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
patch_modes_wire.py - stop hand-typing keybinds, start reading them.

The page carried FLIGHT and ONFOOT as hand-typed JavaScript and showed
"not entered yet" for the other three modes. Both halves of that were wrong:
the transcription could drift from the game silently, and the missing modes
were never missing from the data - only from the page.

After this, every mode comes from kb_modes.gen.js, which comes from the
extracted default profile. One writer per fact.

Also adds:
 - a Social mode, because gestures are a real part of the game and 34 of the
   40 emotes have no key at all. A page that shows only bound keys would tell
   a new player those emotes do not exist.
 - an M4 layer for Right Ctrl, because 4 scanning bindings use it and dropping
   bindings we cannot draw is the exact defect being fixed here.
 - a list under each board of everything in that mode with no default key.

Rule 15: encodings stated. Anchors asserted unique.
"""
import io, sys, os, re

P = "keybinds.src.html"
s = io.open(P, encoding="utf-8").read()

def sub(old, new, why, count=1):
    global s
    n = s.count(old)
    if n != count:
        sys.exit("ANCHOR %s appears %d times, expected %d" % (why, n, count))
    s = s.replace(old, new)

# --------------------------------------------------- 1. load the generated data
sub('<div class="modes" id="modes"></div>',
    '<script src="kb_modes.gen.js"></script>\n'
    '<div class="modes" id="modes"></div>', "loadgen")

# ------------------------------------- 2. delete the hand-typed FLIGHT + ONFOOT
m = re.search(r"/\* -+ MODES -+ \*/\nconst FLIGHT=\{.*?\nconst MODES=\[",
              s, re.S)
if not m:
    sys.exit("could not find the hand-typed mode block")
s = s[:m.start()] + "/* ---------- MODES ---------- */\n/* FLIGHT and ONFOOT used to be typed out by hand here. They are now\n   generated from the game's own default profile like every other mode,\n   because two copies of one fact drift and only one of them is checked. */\nconst MODES=[" + s[m.end():]

# ------------------------------------------------------------ 3. the mode table
old_modes = re.search(r"const MODES=\[.*?\n\];", s, re.S).group(0)
new_modes = """const MODES=[
 {id:"FLIGHT", label:"Flight",  sub:"in a ship",         data:FLIGHT,  unbound:FLIGHT_UNBOUND,  legend:FLIGHT_LEGEND},
 {id:"ONFOOT", label:"On Foot", sub:"walking around",    data:ONFOOT,  unbound:ONFOOT_UNBOUND,  legend:ONFOOT_LEGEND},
 {id:"EVA",    label:"E.V.A.",  sub:"zero-G",            data:EVA,     unbound:EVA_UNBOUND,     legend:EVA_LEGEND},
 {id:"VEHICLE",label:"Vehicle", sub:"ground vehicles",   data:VEHICLE, unbound:VEHICLE_UNBOUND, legend:VEHICLE_LEGEND},
 {id:"CAMERA", label:"Camera",  sub:"views and free cam",data:CAMERA,  unbound:CAMERA_UNBOUND,  legend:CAMERA_LEGEND},
 {id:"SOCIAL", label:"Social",  sub:"gestures and emotes",data:SOCIAL, unbound:SOCIAL_UNBOUND,  legend:SOCIAL_LEGEND}
];"""
s = s.replace(old_modes, new_modes, 1)

# ------------------------------------------------------------- 4. the M4 layer
sub('  <span class="lamp" id="layerlbl">Layer: none</span>',
    '  <span class="lamp"><span class="dot m4" id="d4"></span>M4 Right Ctrl</span>\n'
    '  <span class="lamp" id="layerlbl">Layer: none</span>', "lamp4")
sub('if(down.has("RAlt"))nm=3;else if(down.has("LAlt"))nm=1;else if(down.has("LShift"))nm=2;',
    'if(down.has("RCtrl"))nm=4;else if(down.has("RAlt"))nm=3;'
    'else if(down.has("LAlt"))nm=1;else if(down.has("LShift"))nm=2;', "setmods")
sub("""  $('d3').classList.toggle('on',down.has("RAlt"));""",
    """  $('d3').classList.toggle('on',down.has("RAlt"));
  $('d4').classList.toggle('on',down.has("RCtrl"));""", "lampdot4")
sub("""{0:"none",1:"M1 (Left Alt)",2:"M2 (Left Shift)",3:"M3 (Right Alt)"}[mod]""",
    """{0:"none",1:"M1 (Left Alt)",2:"M2 (Left Shift)",3:"M3 (Right Alt)",4:"M4 (Right Ctrl)"}[mod]""",
    "layerlbl")
sub("""{0:"no modifier",1:"M1 Left Alt",2:"M2 Left Shift",3:"M3 Right Alt"}[mod]""",
    """{0:"no modifier",1:"M1 Left Alt",2:"M2 Left Shift",3:"M3 Right Alt",4:"M4 Right Ctrl"}[mod]""",
    "firelbl")
sub('if(id==="LAlt")c+=" mod1";if(id==="LShift")c+=" mod2";if(id==="RAlt")c+=" mod3";',
    'if(id==="LAlt")c+=" mod1";if(id==="LShift")c+=" mod2";if(id==="RAlt")c+=" mod3";'
    'if(id==="RCtrl")c+=" mod4";', "modclass")
sub('.key.mod1{border-color:var(--m1)}.key.mod2{border-color:var(--m2)}.key.mod3{border-color:var(--m3)}',
    '.key.mod1{border-color:var(--m1)}.key.mod2{border-color:var(--m2)}'
    '.key.mod3{border-color:var(--m3)}.key.mod4{border-color:#00A8FF}\n'
    '.dot.m4{background:#00A8FF}\n'
    '/* things the game ships with no key at all - shown, never hidden */\n'
    '.nokey{margin-top:16px;padding:12px 14px;background:#0B1626;'
    'border:1px solid #22364F;border-radius:9px}\n'
    '.nokey h3{margin:0 0 4px;font:800 13px/1.3 inherit;color:var(--accent);'
    'letter-spacing:.05em;text-transform:uppercase}\n'
    '.nokey p{margin:0 0 9px;font-size:12.5px;color:var(--muted);line-height:1.5}\n'
    '.nokey .tags{display:flex;flex-wrap:wrap;gap:5px}\n'
    '.nokey .tags span{background:#12233A;border:1px solid #22364F;border-radius:4px;'
    'padding:3px 8px;font-size:11.5px;color:#B9C9D6}', "mod4css")

# --------------------------------- 5. the board no longer says "not entered yet"
sub("""  if(!MODES[modeIx].data){""", """  if(!MODES[modeIx].data){""", "blankguard")

# ------------------------------------- 6. render the unbound list under the board
sub("""    '</div>'+
    '';""",
    """    '</div>'+
    ccNoKey();""", "nokeycall")

HELPER = """
/* Every mode has actions the game ships with no key bound. Emotes are the
   extreme case: 34 of 40. Hiding them would tell a new player they do not
   exist, so they are listed with how you actually reach them. */
function ccNoKey(){
  var u=MODES[modeIx].unbound||[];
  if(!u.length) return '';
  var how = MODES[modeIx].id==="SOCIAL"
    ? 'Type the name into chat, or hold <strong>Left Alt + F</strong> and pick '+
      'Emotes from the wheel. Chat-command spelling is not in the game files '+
      'and has not been verified here.'
    : 'These exist in the game but ship with no key on the keyboard. Bind them '+
      'yourself in Options &rarr; Keybindings, or reach them through the '+
      'in-game menus.';
  return '<div class="nokey"><h3>'+u.length+' with no default key</h3>'+
    '<p>'+how+'</p><div class="tags"><span>'+
    u.map(function(n){return String(n).replace(/</g,'&lt;');}).join('</span><span>')+
    '</span></div></div>';
}
"""
sub("function render(){", HELPER + "function render(){", "helper")

# --------------------------------------------- 7. the header claim is now false
sub("""Keybinding Tester &mdash; <strong>Keyboard/Mouse</strong> bindings are
  transcribed from in-game screenshots and not yet verified against game files.
  <strong>Gamepad</strong> and <strong>Joystick / HOTAS</strong> read your controller
  live and are accurate now.""",
    """Keybinding Tester &mdash; <strong>Keyboard/Mouse</strong> bindings are read
  from the game's own default profile. <strong>Gamepad</strong> and
  <strong>Joystick / HOTAS</strong> read your controller live.""", "header")

io.open(P, "w", encoding="utf-8", newline="\n").write(s)
print("keybinds.src.html wired to kb_modes.gen.js")
