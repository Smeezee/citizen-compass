#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
patch_btn_limit.py - show 40 buttons, not 128, without losing any.

VKB and VIRPIL firmware reports 128 buttons no matter how many the stick
physically has. The panel drew all 128, so a Gladiator with about 20 real
controls produced a wall of empty tiles and the useful part scrolled off.

The cap is a display cap and nothing else. One rule governs every tile:

    visible  =  showAll
             OR (index < 40 AND NOT (hideUnused AND never pressed))
             OR ever pressed

The last clause is the important one. Press button 87 and tile 87 appears and
stays. Nothing above the cap is silently dropped - which is the same defect as
dropping bindings the board could not draw, and it is not being reintroduced
here in a different coat.

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

# ------------------------------------------------------------------ the cap
sub("var HAT_CENTRE=1.2857",
    "/* Display cap. Sticks report 128 buttons; almost none have 128. A tile\n"
    "   above the cap still appears the moment it is pressed - see applyVis. */\n"
    "var BTN_SHOWN=40, showAll=false, hideUnused=false;\n"
    "var HAT_CENTRE=1.2857", "cap")

# ------------------------------------------------- tiles carry their own index
sub("""    h+='<div class="btn" data-b="'+p.index+':'+i+'">'+""",
    """    h+='<div class="btn'+(i>=BTN_SHOWN?' over':'')+'" data-b="'+p.index+':'+i+'">'+""",
    "tileclass")

# ------------------------------------------------------------- the two buttons
sub("""'<button class="tg" id="'+ID_+'dvhide">Hide unused buttons</button></div>';""",
    """'<button class="tg" id="'+ID_+'dvhide">Hide unused buttons</button>'+
     '<button class="tg" id="'+ID_+'dvall">'+dvAllLabel(list)+'</button>'+
     '<span class="dvcap" id="'+ID_+'dvcapnote"></span></div>';""", "buttons")

# --------------------------------------------------------- index on the record
sub("""    devDom.btn[els[j].getAttribute('data-b')]={
      el:els[j], va:els[j].querySelector('.va'), on:null};""",
    """    devDom.btn[els[j].getAttribute('data-b')]={
      el:els[j], va:els[j].querySelector('.va'), on:null,
      ix:parseInt(els[j].getAttribute('data-b').split(':')[1],10)};""", "ixstore")

# ----------------------------------------------------- one predicate, one place
HELPER = """
/* Total buttons across every connected stick, for an honest button label. */
function dvMaxBtn(list){
  var m=0; (list||[]).forEach(function(p){ if(p.buttons.length>m) m=p.buttons.length; });
  return m;
}
function dvAllLabel(list){
  var m=dvMaxBtn(list);
  return showAll ? ("Show first "+BTN_SHOWN) : ("Show all "+(m||BTN_SHOWN));
}
/* The single rule that decides whether a tile is on screen. Both toggles and
   the press handler call this - there is no second place that sets display. */
function applyVis(){
  if(!devDom) return;
  var k, d, hiddenAbove=0;
  for(k in devDom.btn){
    d=devDom.btn[k];
    var vis = showAll
           || d.everPressed
           || (d.ix < BTN_SHOWN && !(hideUnused && !d.everPressed));
    if(!vis && d.ix >= BTN_SHOWN) hiddenAbove++;
    if(d.vis!==vis){ d.vis=vis; d.el.style.display = vis ? '' : 'none'; }
  }
  var note=$(ID_+'dvcapnote');
  if(note) note.textContent = hiddenAbove
    ? (hiddenAbove+" further buttons hidden - press one and it appears")
    : "";
}
"""
sub("/* Build the DOM once. Everything after this is mutation only. */",
    HELPER + "\n/* Build the DOM once. Everything after this is mutation only. */",
    "helper")

# ------------------------------------------------------- rewire the hide toggle
sub("""  if(hb) hb.onclick=function(){
    var hide=this.classList.toggle('on'), k;
    this.textContent = hide ? "Show all buttons" : "Hide unused buttons";
    for(k in devDom.btn){
      var d=devDom.btn[k];
      d.el.style.display = (hide && !d.everPressed) ? 'none' : '';
    }
  };""",
    """  if(hb) hb.onclick=function(){
    hideUnused=this.classList.toggle('on');
    this.textContent = hideUnused ? "Show unused too" : "Hide unused buttons";
    applyVis();
  };
  var ab=$(ID_+'dvall');
  if(ab) ab.onclick=function(){
    showAll=this.classList.toggle('on');
    this.textContent=dvAllLabel(pads());
    applyVis();
  };
  applyVis();""", "hidetoggle")

# ------------------------------- a press above the cap reveals its tile, for good
sub("""      if(on){ d.everPressed=true; }""",
    """      if(on && !d.everPressed){ d.everPressed=true; applyVis(); }""", "reveal")

io.open(P,"w",encoding="utf-8",newline="\n").write(s)
print("device_engine.js: %d-button display cap, nothing dropped"%40)
