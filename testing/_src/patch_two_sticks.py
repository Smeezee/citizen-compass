#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
patch_two_sticks.py - both sticks on screen at once, same view for every device.

HOSAS is two sticks. The panel drew them one after the other, so with a left
and a right stick connected you could see one or the other and never the pair.
Setting up a HOSAS is entirely about the relationship between the two hands,
so a layout that hides one of them is the wrong layout.

Each device now gets its own column. Two columns side by side on a normal
screen, stacking on a narrow one. The presentation is identical for every
device - the panel reads what the browser reports and lays it out the same
way whether it is a Gladiator, a VIRPIL, a T.16000M or something neither of
us has heard of. There is no per-device artwork to be missing, so nothing
degrades to a blank panel for an unrecognised stick.

Rule 15: encodings stated. Anchors asserted unique.
"""
import io, sys
P="device_engine.js"
s=io.open(P, encoding="utf-8").read()
def sub(old,new,why):
    global s
    n=s.count(old)
    if n!=1: sys.exit("ANCHOR %s appears %d times, expected 1"%(why,n))
    s=s.replace(old,new)

# ------------------------------------------------ each device becomes a column
sub("""  list.forEach(function(p){
    h+='<div class="dvsec">'+esc(p.id)+' &mdash; buttons</div><div class="btngrid">';""",
    """  h+='<div class="dvcols'+(list.length>1?' pair':'')+'">';
  list.forEach(function(p){
    h+='<div class="dvcol"><div class="dvcolhd">'+prefix(p)+' &mdash; '+esc(p.id)+
       '<small>'+p.buttons.length+' buttons &middot; '+p.axes.length+' axes</small></div>';
    h+='<div class="dvsec">buttons</div><div class="btngrid">';""", "col-open")

sub("""    h+='</div><div class="dvsec">'+esc(p.id)+' &mdash; axes</div>';""",
    """    h+='</div><div class="dvsec">axes and hats</div>';""", "axes-head")

# close the column after the axis loop, and close the wrapper after the list
sub("""      '<div class="axval">0.000</div></div>';
    });
  });""",
    """      '<div class="axval">0.000</div></div>';
    });
    h+='</div>';                      /* .dvcol */
  });
  h+='</div>';                        /* .dvcols */""", "col-close")

# ------------------------------------------------------------------ the styles
CSS = """
/* Two sticks are a pair, not a list. Side by side on a normal screen,
   stacked only when there is genuinely no room. */
.dvcols{display:grid;gap:14px;grid-template-columns:1fr}
.dvcols.pair{grid-template-columns:repeat(auto-fit,minmax(330px,1fr))}
.dvcol{background:#0B1626;border:1px solid #1B2C42;border-radius:10px;padding:11px 12px}
.dvcolhd{font:800 13px/1.3 'Segoe UI',system-ui,sans-serif;color:#FF6B00;
  letter-spacing:.04em;margin-bottom:9px;padding-bottom:7px;
  border-bottom:1px solid #1B2C42}
.dvcolhd small{display:block;font:600 11px/1.4 inherit;color:#93A7B6;
  letter-spacing:.02em;margin-top:2px}
"""
sub("var HAT_CENTRE=1.2857",
    "var DVCOL_CSS=" + repr(CSS).replace("'", '"').replace("\\n", "\\n") + ";\n"
    "var HAT_CENTRE=1.2857", "css")

# inject the stylesheet once, on first build, so both hosts get it without
# either host having to know the panel's internals
sub("""function buildDevice(list){
  var host=$(ID_+'board'), h='', i;""",
    """function buildDevice(list){
  var host=$(ID_+'board'), h='', i;
  if(!document.getElementById('cc-dvcol-css')){
    var st=document.createElement('style');
    st.id='cc-dvcol-css'; st.textContent=DVCOL_CSS;
    document.head.appendChild(st);
  }""", "cssinject")

io.open(P,"w",encoding="utf-8",newline="\n").write(s)
print("device_engine.js: one column per device, identical view for any stick")
