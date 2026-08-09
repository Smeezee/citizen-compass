#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
patch_device_identity.py - which physical stick is js1?

THE BUG, in one function. slotOf() assigned slot numbers 1-8 keyed on
`p.index`, which is navigator.getGamepads()'s array position - the browser's
USB enumeration order. Nothing read VID/PID, nothing survived a session, and
nothing deferred to an imported profile. So unplugging a stick and putting it
in a different port silently renamed it, and a profile the game itself wrote
could disagree with the panel about which stick was which while both looked
equally confident.

THE RESOLUTION ORDER, from FINDING_exporter-round-trip-passes-2026-08-09.md
section 5, proven on the real machine with both sticks handed to the page in
the wrong plug order:

  1. AN IMPORTED PROFILE WINS. The game wrote those <options> GUIDs; they
     outrank anything we could infer. Matched by deriving the GUID from the
     gamepad's own VID/PID and finding it in the profile's device list.
  2. OTHERWISE THE PLAYER'S OWN CHOICE, remembered per VID/PID - not per
     p.index, so it survives a replug and a different USB port.
  3. OTHERWISE A GUESS from plug order, exactly as before - AND THE PANEL
     SAYS SO. A guess presented as fact is the actual defect here; the old
     code had no way for a caller to tell the two apart.

WHY THE GUESS ALSO HAD TO CHANGE. The old free-slot scan only avoided slots
held by other guesses. With resolution in play it must also avoid slots
already claimed by a profile or a remembered choice, or a guessed stick could
be handed a number a resolved stick already owns and two devices would both
call themselves js1.

WHY THERE IS A SETTER. Without a way to record a choice, priority 2 could
never fire - dead code wearing the appearance of a feature, which is this
project's silent-success shape. Clicking the slot chip cycles js1..js8 and
remembers it against that device's VID/PID.

SCX MAY NOT BE THERE, AND THAT IS FINE. device_engine.js is injected into
BOTH keybinds.src.html and _layer.src.html, but only the keybind page loads
sc_export.js. On the index page SCX is undefined, so VID/PID parsing is
unavailable and every device falls to priority 3 - which is exactly the old
behaviour, correctly labelled as a guess. Every SCX call site is guarded.

Rule 15: encodings stated. Anchors asserted unique.
Run once from testing/_src/:  python patch_device_identity.py
"""
import io
import sys

P = "device_engine.js"
s = io.open(P, encoding="utf-8", newline="").read()


def sub(old, new, why):
    global s
    n = s.count(old)
    if n != 1:
        sys.exit("ANCHOR %s appears %d times, expected 1" % (why, n))
    s = s.replace(old, new)


# --------------------------------------------------- 1. the resolution itself
sub("""function slotOf(p){
  if(padSlot[p.index]) return padSlot[p.index];
  var used={}, k, n;
  for(k in padSlot) used[padSlot[k]]=1;
  for(n=1;n<=8;n++) if(!used[n]){ padSlot[p.index]=n; return n; }
  padSlot[p.index]=1; return 1;
}
function isStd(p){ return p.mapping==="standard" && dev==="PAD"; }
function prefix(p){ return isStd(p) ? "xi" : "js"+slotOf(p); }""",
    """/* ---- DEVICE IDENTITY ------------------------------------------------
   Which physical stick is js1? Three sources, in priority order:
     1 an imported profile's <options> GUIDs  - the game wrote them
     2 the player's own choice, per VID/PID   - survives a replug
     3 a guess from plug order                - AND WE SAY IT IS A GUESS
   See patch_device_identity.py for the full reasoning. */
var profileDevices=null;          /* set by CCDEV.setProfileDevices() */
var choiceCache=null;             /* "vid:pid" -> slot, from localStorage */
var CC_SLOT_KEY="cc.js.slots.v1";

/* SCX ships with the keybind page but NOT with the index page, so every use
   of it is guarded and its absence simply means we cannot read VID/PID. */
function haveSCX(){ return typeof SCX!=="undefined" && !!SCX.parseGamepadId; }
function vidpid(p){
  if(!haveSCX()) return null;
  var r=null; try{ r=SCX.parseGamepadId(p.id); }catch(e){ return null; }
  return (r&&r.vid&&r.pid)?r:null;
}
function padKey(p){ var v=vidpid(p); return v?(v.vid+":"+v.pid):null; }

function choices(){
  if(choiceCache) return choiceCache;
  choiceCache={};
  try{ var raw=window.localStorage&&localStorage.getItem(CC_SLOT_KEY);
       if(raw) choiceCache=JSON.parse(raw)||{}; }catch(e){ choiceCache={}; }
  return choiceCache;
}
function rememberSlot(p,n){
  var k=padKey(p);
  if(!k) return false;               /* no VID/PID - nothing stable to key on */
  choices()[k]=n;
  try{ localStorage.setItem(CC_SLOT_KEY,JSON.stringify(choiceCache)); }catch(e){}
  padSlot[p.index]=n;
  return true;
}

/* An imported profile decides. Derive this pad's GUID from its own VID/PID
   and look for it among the profile's joystick <options> lines. */
function fromProfile(p){
  if(!profileDevices||!profileDevices.length) return 0;
  var v=vidpid(p);
  if(!v||!SCX.guidFromVidPid) return 0;
  var guid=null; try{ guid=SCX.guidFromVidPid(v.vid,v.pid); }catch(e){ return 0; }
  if(!guid) return 0;
  for(var i=0;i<profileDevices.length;i++){
    var d=profileDevices[i];
    if(d&&d.type==="joystick"&&String(d.product||"").indexOf(guid)>=0)
      return d.instance||0;
  }
  return 0;
}
function fromChoice(p){
  var k=padKey(p);
  return (k&&choices()[k])?choices()[k]:0;
}

/* Slots already spoken for by a RESOLVED device. A guess must not be handed
   a number a profile or a remembered choice already owns. */
function claimedSlots(){
  var used={}, list=pads(), i, q, n;
  for(i=0;i<list.length;i++){
    q=list[i];
    if(isStd(q)) continue;
    n=fromProfile(q)||fromChoice(q);
    if(n) used[n]=1;
  }
  return used;
}
function guessSlot(p){
  if(padSlot[p.index]) return padSlot[p.index];
  var used=claimedSlots(), k, n;
  for(k in padSlot) used[padSlot[k]]=1;
  for(n=1;n<=8;n++) if(!used[n]){ padSlot[p.index]=n; return n; }
  padSlot[p.index]=1; return 1;
}

/* The one function that answers both questions: which slot, and how sure. */
function identityOf(p){
  var n=fromProfile(p);
  if(n) return {slot:n, source:"profile"};
  n=fromChoice(p);
  if(n) return {slot:n, source:"remembered"};
  return {slot:guessSlot(p), source:"guessed"};
}
function slotOf(p){ return identityOf(p).slot; }
function slotSource(p){ return identityOf(p).source; }
function isStd(p){ return p.mapping==="standard" && dev==="PAD"; }
function prefix(p){ return isStd(p) ? "xi" : "js"+slotOf(p); }""",
    "identity-core")

# ------------------------------------------- 2. the panel must show the source
sub("""    h+='<div class="dvchip on" data-chip="'+p.index+'"><div class="sl">'+prefix(p)+
       '</div><div class="nm" title="'+esc(p.id)+'">'+esc(p.id)+'</div>'+""",
    """    var _src=isStd(p)?"":slotSource(p);
    var _note={profile:"from the imported profile",
               remembered:"your choice, remembered for this device",
               guessed:"guessed from plug order - click to set"}[_src]||"";
    h+='<div class="dvchip on" data-chip="'+p.index+'"><div class="sl cc-slot'+
       (_src?' cc-src-'+_src:'')+'" data-slot="'+p.index+'" title="'+esc(_note)+
       '">'+prefix(p)+'</div>'+
       (_note?'<div class="srcnote cc-src-'+_src+'">'+esc(_note)+'</div>':'')+
       '<div class="nm" title="'+esc(p.id)+'">'+esc(p.id)+'</div>'+""",
    "chip-source")

# --------------------------------- 3. a way to record a choice, and the API
#
# INSERTED BEFORE the gamepaddisconnected listener, not after it. That
# listener's last line is inject_engine.py's END boundary marker, and the
# injector refuses to run if device_engine.js stops ending with it. Appending
# past it fails the build loudly - which is the guard working, and is how this
# was caught rather than shipped.
sub("""window.addEventListener('gamepaddisconnected',function(e){
  delete padSlot[e.gamepad.index]; delete padPrev[e.gamepad.index];
  delete padCenter[e.gamepad.index];
  devDom=null;
  if(dev!=="KBM") renderDevice(); });""",
    """/* Clicking a slot cycles js1..js8 and remembers it against that device's
   VID/PID. Without this, priority 2 could never fire. Delegated, because the
   panel is re-rendered wholesale on every frame. */
document.addEventListener('click',function(e){
  var el=e.target&&e.target.closest?e.target.closest('.cc-slot'):null;
  if(!el) return;
  var idx=parseInt(el.getAttribute('data-slot'),10);
  var list=pads(), i, p=null;
  for(i=0;i<list.length;i++) if(list[i].index===idx) p=list[i];
  if(!p||isStd(p)) return;
  if(fromProfile(p)) return;   /* the game's own answer is not ours to cycle */
  if(!rememberSlot(p,(slotOf(p)%8)+1)){
    /* No VID/PID means nothing stable to remember it against. Say so rather
       than appearing to accept the click. */
    if(window.console&&console.warn)
      console.warn('cannot remember a slot for this device: the browser '+
                   'reports no Vendor/Product id for "'+p.id+'"');
    return;
  }
  devDom=null; renderDevice();
});

/* The page tells the engine what an imported profile said. */
window.CCDEV=window.CCDEV||{};
window.CCDEV.setProfileDevices=function(devices){
  profileDevices=(devices&&devices.length)?devices:null;
  devDom=null;
  if(typeof renderDevice==="function") renderDevice();
};
window.CCDEV.identityOf=identityOf;
window.CCDEV.joysticks=function(){
  /* [{instance,vid,pid,name}] for SCX.build's opts.joysticks. */
  var out=[], list=pads(), i, p, v;
  for(i=0;i<list.length;i++){
    p=list[i];
    if(isStd(p)) continue;
    v=vidpid(p);
    out.push({instance:slotOf(p), vid:v?v.vid:"", pid:v?v.pid:"",
              name:v&&v.name?v.name:p.id});
  }
  return out;
};

window.addEventListener('gamepaddisconnected',function(e){
  delete padSlot[e.gamepad.index]; delete padPrev[e.gamepad.index];
  delete padCenter[e.gamepad.index];
  devDom=null;
  if(dev!=="KBM") renderDevice(); });""",
    "slot-setter-and-api")

io.open(P, "w", encoding="utf-8", newline="\n").write(s)
print("patched device_engine.js: identity resolution, source label, slot setter, CCDEV API")
