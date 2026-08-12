#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
patch_axis_rebind_capture.py - a deliberate stick deflection can now be bound.

THE BUG, root-caused rather than guessed. fireDev() is called from exactly two
places: buttons and hats. The branch handling every other axis was, in full:

    } else {
      var c=(padCenter[p.index]||[])[i]||0;
      if(Math.abs(v-c)>DEADZONE) hot=true;
    }

It sets the "device is alive" indicator and nothing else. So X, Y, Z, throttle,
rudder and the sliders never produced a token, never reached KBREBIND.capture(),
and could not be bound - by any build, ever. Sleven, on a real HOTAS: "it
doesn't recognize the actual y axis or any of the axes as things."

WHY NOT JUST ADD A fireDev CALL HERE

Because the silence is correct for the tester panel. An axis moves continuously;
firing on every sample would flood the live readout at 60 Hz. So the capture is
edge-detected, and it exists ONLY while a rebind is listening. Outside a rebind
this branch behaves exactly as it did - `hot` and nothing more.

THE NUMBERS, AND WHY THESE ONES

    FIRE   0.55 of full deflection from the axis's own centre
    REARM  0.25

DEADZONE is 0.12 and exists to absorb drift and a knocked desk. Binding must
require something nobody does by accident, so the fire threshold is set past
half travel: a resting stick cannot reach it, and neither can a hand brushing
the grip. The 0.30 gap between fire and re-arm is hysteresis - without it a
stick settling back through a single threshold chatters, and "which axis did you
mean" becomes whichever frame won the race.

Re-arm is per axis per device, so pushing Y, letting go, and pushing X binds two
different axes in the order they were pushed rather than latching on the first.

CENTRE COMES FROM padCenter, the panel's existing per-axis rest position, so a
throttle or a rudder pedal that rests at -1.0 rather than 0.0 is handled the way
the panel already handles it. Re-deriving centring here would be a second answer
to a question already answered.

THE TOKEN COMES FROM axName(), WHICH ALREADY EXISTS. It maps an axis index to
the game's own name via JS_AX - x, y, z, rotx, roty, rotz, slider1, slider2 -
and flags the ones past slider2 that have no Star Citizen name at all. Writing a
second axis table beside it is the duplicate-writer defect this project keeps
paying for, so this reads the existing one. An axis with no game name is refused
rather than bound to something invented.

SHAPE OF THE TOKEN: PLAIN, NOT DIRECTIONAL. Read out of the two real profiles in
testing/_src/fixtures/ rather than chosen - they contain js1_x, js1_y, js1_z,
js1_rotz, js2_x, js2_y, js2_rotz and no directional variant of any kind. So an
axis binds as the axis; which way it was pushed is not part of the binding.

Rule 15: encodings stated. Anchors asserted unique.
Run once from testing/_src/:  python patch_axis_rebind_capture.py
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


# The thresholds live next to DEADZONE so the three numbers are read together.
sub("""var DEADZONE=0.12, DRIFT=0.06;""",
    """var DEADZONE=0.12, DRIFT=0.06;

/* Deliberate-deflection thresholds for REBINDING ONLY - see
   patch_axis_rebind_capture.py. AXIS_BIND_FIRE is past half travel so a resting
   or brushed stick can never bind; AXIS_BIND_REARM is far enough below it that
   a stick settling back cannot chatter across a single threshold. */
var AXIS_BIND_FIRE=0.55, AXIS_BIND_REARM=0.25;
var axisArmed={};   /* "padIndex:axisIndex" -> has returned near centre */""",
    "thresholds")

sub("""      } else {
        var c=(padCenter[p.index]||[])[i]||0;
        if(Math.abs(v-c)>DEADZONE) hot=true;
      }""",
    """      } else {
        var c=(padCenter[p.index]||[])[i]||0;
        var off=Math.abs(v-c);
        if(off>DEADZONE) hot=true;

        /* AXIS CAPTURE FOR REBINDING. Only while a cell is listening, so the
           live tester panel is untouched the rest of the time. Edge-detected:
           one deliberate push binds once, and nothing binds again until the
           axis has come back near centre. */
        if(window.KBREBIND && KBREBIND.listening()){
          var akey=p.index+":"+i;
          if(off<AXIS_BIND_REARM) axisArmed[akey]=true;
          if(off>=AXIS_BIND_FIRE && axisArmed[akey]){
            axisArmed[akey]=false;
            var an=axName(p,i);
            /* an[3] is the "no Star Citizen name" flag - past slider2 there is
               no token the game would accept, so refuse rather than invent. */
            if(an[3]){
              if(window.console&&console.warn)
                console.warn('axis '+i+' on "'+p.id+'" has no Star Citizen name, so it '+
                             'cannot be bound');
            } else {
              fireDev(p, an[1], an[0], "DEFLECT");
            }
          }
        }
      }""",
    "axis-capture")

io.open(P, "w", encoding="utf-8", newline="\n").write(s)
print("patched device_engine.js: deliberate axis deflection captures while rebinding")
