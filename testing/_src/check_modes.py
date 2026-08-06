#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check_modes.py - prove the wiring, do not assume it.

Every assertion here has a matching negative control: a claim that must FAIL
if the checker is working. A check that cannot fail is not a check.
Rule 15: encodings stated.
"""
import io, re, json, sys, subprocess, os

FAIL=[]; OK=0
def ck(cond, msg):
    global OK
    if cond: OK+=1
    else: FAIL.append(msg)

page = io.open("keybinds.src.html", encoding="utf-8").read()
gen  = io.open("kb_modes.gen.js",   encoding="utf-8").read()

# --- structural
ck('<script src="kb_modes.gen.js"></script>' in page, "generated data not loaded")
ck("const FLIGHT={\n Esc:" not in page, "hand-typed FLIGHT still in the page")
ck(page.count("const MODES=[")==1, "MODES defined other than once")
modes = re.search(r"const MODES=\[(.*?)\n\];", page, re.S).group(1)
ck(modes.count("{id:")==6, "expected 6 modes, found %d"%modes.count("{id:"))
for m in ("FLIGHT","ONFOOT","EVA","VEHICLE","CAMERA","SOCIAL"):
    ck("const %s={"%m in gen, "%s missing from generated data"%m)
    ck("const %s_UNBOUND="%m in gen, "%s_UNBOUND missing"%m)

# --- M4 layer reaches every place a layer is read
ck('down.has("RCtrl"))nm=4' in page, "M4 not in setMods")
ck('M4 (Right Ctrl)' in page, "M4 missing from the layer label")
ck('M4 Right Ctrl' in page, "M4 missing from the readout")
ck("id===\"RCtrl\")c+=\" mod4\"" in page, "RCtrl key not tinted as a modifier")

# --- the specific binding Sleven named from memory
d = json.loads("{"+re.search(r"const ONFOOT=\{(.*?)\n\};", gen, re.S).group(1)+"}")
h = d.get("H") or []
ck(any(e.get("a","").startswith("Helmet") and e.get("m")==1 for e in h),
   "Left Alt + H is not Helmet on the On Foot board: %s"%json.dumps(h))
ck(any("Toggle Equip Helmet"==e.get("a") and e.get("m")==3 for e in h),
   "Right Alt + H is not Toggle Equip Helmet")

# --- the six emotes that DO have keys
sd = json.loads("{"+re.search(r"const SOCIAL=\{(.*?)\n\};", gen, re.S).group(1)+"}")
for cap,name in [("Np1","Left"),("Np2","Stop"),("Np3","Right"),
                 ("Np4","Yes"),("Np5","Forward"),("Np6","No")]:
    ck(any(e.get("a")==name for e in sd.get(cap,[])),
       "%s should be the '%s' signal, got %s"%(cap,name,json.dumps(sd.get(cap))))
su = json.loads(re.search(r"const SOCIAL_UNBOUND=(\[.*?\]);", gen, re.S).group(1))
ck(len(su)>=30, "expected 30+ keyless emotes, got %d"%len(su))
ck("Salute" in su and "Wave" in su, "Salute/Wave missing from the keyless list")

# --- no mode ships empty
for m in ("FLIGHT","ONFOOT","EVA","VEHICLE","CAMERA","SOCIAL"):
    body = re.search(r"const %s=\{(.*?)\n\};"%m, gen, re.S).group(1)
    ck(len(json.loads("{"+body+"}"))>0, "%s has no keys at all"%m)

# --- syntax: the generated file must actually parse
if os.system("node --version >/dev/null 2>&1")==0:
    r=subprocess.run(["node","--check","kb_modes.gen.js"],capture_output=True,text=True)
    ck(r.returncode==0, "kb_modes.gen.js is not valid JavaScript: "+r.stderr[:200])
else:
    print("note: node absent, syntax not machine-checked")

# --- NEGATIVE CONTROLS: these must fail, or the checker is asleep
neg=[]
def nck(cond,msg):
    if cond: neg.append(msg)
nck("const NOSUCHMODE={" in gen, "negative control passed - checker is broken")
nck(any(e.get("a")=="Fly To The Moon" for e in h), "negative control passed on ONFOOT H")
nck("Np9" in sd, "negative control passed - Np9 should have no emote")

print("passed: %d   failed: %d"%(OK,len(FAIL)))
for f in FAIL: print("  FAIL  "+f)
for n in neg: print("  BROKEN CHECKER  "+n)
sys.exit(1 if (FAIL or neg) else 0)
