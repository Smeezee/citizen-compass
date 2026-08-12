#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
patch_device_presence.py - notice a stick without needing a page reload.

THE COMPLAINT. Sleven: "I've had troubles getting the joysticks to even
register... It usually takes a couple refreshes... I have to shut the web page
down and back up."

THE CAUSE IS THREE GATES, AND ALL OF THEM HAVE TO BE OPEN

  1. poll() early-returns while the Keyboard/Mouse tab is showing - and that is
     the default tab, so on first load nothing is polling at all.
  2. poll() early-returns when the device panel is closed.
  3. gamepadconnected was itself gated `if(dev!=="KBM")`, so the ONE event that
     could have recovered either situation was discarded on the default tab.

Land on the page, start your stick software afterwards, and the connect event
fires into a handler that throws it away while no loop is running to notice on
its own. A reload was the only reliable recovery.

WHAT THIS DOES NOT DO: remove the gating from the heavy loop. That gating fixed
real lag on the live readout and it stays. The distinction this patch draws is
between SAMPLING INPUT - expensive, 60 Hz, legitimately gated - and KNOWING A
DEVICE EXISTS, which is neither.

THE PRESENCE CHECK: 400ms, setInterval, not rAF

Cheap by construction: it calls navigator.getGamepads() and joins the ids into
a string. Nothing is read per-button or per-axis, no DOM work happens unless the
answer actually changed. 2.5 calls a second against a 60 Hz input loop is noise,
and it is deliberately setInterval rather than requestAnimationFrame so it keeps
running in a background tab, where rAF is throttled to roughly one frame a
minute or stops entirely.

It never trusts a cache - getGamepads() is re-read every tick, which is the
whole point, since the browser populates it lazily.

WHAT CHROME DOES THAT NOBODY TELLS THE USER

navigator.getGamepads() reports NOTHING for a device until a control on it is
pressed while the page has focus. A correctly connected, correctly driven stick
is invisible until touched. That is a browser rule, not a bug here - but the
page showed an empty panel and no explanation, so the site looked broken while
it was in fact waiting for the person. The presence check publishes a state the
page can turn into that one missing sentence.

Rule 15: encodings stated. Anchors asserted unique.
Run once from testing/_src/:  python patch_device_presence.py
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


# ---------------------------------------------------------- ungate connect
sub("""window.addEventListener('gamepadconnected',function(){
  if(dev!=="KBM"){ devDom=null; renderDevice(); startPoll(); } });""",
    """window.addEventListener('gamepadconnected',function(){
  /* ALWAYS notice. Whether to start SAMPLING can depend on what is on screen;
     whether to know a device exists cannot - this handler discarding the event
     on the default tab is why a reload was needed. */
    devDom=null;
    ccPresenceChanged();
    if(dev!=="KBM"){ renderDevice(); startPoll(); } });""",
    "connect-ungate")


# --------------------------------------------- the presence check itself
sub("""function startPoll(){""",
    """/* ---- DEVICE PRESENCE -------------------------------------------------
   Deliberately separate from poll(). poll() samples every button and axis at
   60 Hz and is gated for good reason; this asks one question - "is the set of
   connected devices different from last time?" - and does nothing at all when
   the answer is no. See patch_device_presence.py. */
var ccPresenceSig = null;

function ccDeviceNames(){
  var g = navigator.getGamepads ? navigator.getGamepads() : [], out = [], i;
  for(i=0;i<g.length;i++) if(g[i]) out.push(g[i].id);
  return out;
}

function ccPresenceChanged(){
  var names = ccDeviceNames();
  /* Published for the page's copy. A person must never have to guess whether
     the site can see their hardware - that ambiguity is the whole complaint. */
  try{
    window.dispatchEvent(new CustomEvent('cc-devices', {detail:{names:names}}));
  }catch(e){}
  return names;
}

function ccPresenceTick(){
  /* Re-read every tick. The browser populates getGamepads() lazily, so a cached
     answer is exactly the wrong thing to trust here. */
  var names = ccDeviceNames(), sig = names.length + '|' + names.join('|');
  if(sig === ccPresenceSig) return;          /* nothing changed: do nothing */
  ccPresenceSig = sig;
  devDom = null;
  ccPresenceChanged();
  if(dev !== "KBM" || (window.KBREBIND && KBREBIND.listening())){
    renderDevice();
    startPoll();
  }
}
setInterval(ccPresenceTick, 400);

function startPoll(){""",
    "presence-check")


# ------------------------------------------------- disconnect must also tell
sub("""window.addEventListener('gamepaddisconnected',function(e){
  delete padSlot[e.gamepad.index]; delete padPrev[e.gamepad.index];
  delete padCenter[e.gamepad.index];
  devDom=null;
  if(dev!=="KBM") renderDevice(); });""",
    """window.addEventListener('gamepaddisconnected',function(e){
  delete padSlot[e.gamepad.index]; delete padPrev[e.gamepad.index];
  delete padCenter[e.gamepad.index];
  devDom=null;
  /* Unplugging mid-session is worth saying out loud too, on any tab. */
  ccPresenceChanged();
  if(dev!=="KBM") renderDevice(); });""",
    "disconnect-ungate")

io.open(P, "w", encoding="utf-8", newline="\n").write(s)
print("patched device_engine.js: 400ms presence check, connect/disconnect ungated")
