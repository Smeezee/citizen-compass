/* ================================================================
   DEVICE PANEL rev 2 — gamepad, joystick, HOTAS, pedals, throttle.

   ES5 on purpose: this exact source is used by both the standalone page
   and the in-site overlay. One engine, two hosts — the alternative is two
   copies drifting apart, which this project has paid for repeatedly.
   ID_ is set by the host before this block.

   WHAT CHANGED IN REV 2, and why. All three found on real VKB hardware,
   not in a harness:

   1. THE LAG. Rev 1 called renderDevice() whenever any axis moved more
      than 0.015, and renderDevice() rebuilt the entire panel with
      innerHTML — 256 button tiles across two sticks, potentially every
      frame. Paint fell behind input and releasing the stick left a stale
      value on screen. The DOM is now built ONCE per device set and only
      text, classes and widths are mutated. No innerHTML after first build.

   2. HATS. Rev 1 emitted names like js2_axis9. Star Citizen has no such
      name — its joystick vocabulary is buttonN, hat1_up/down/left/right,
      and x y z rotx roty rotz slider1 slider2. Anything past index 7 fell
      through to a label the game rejects.

      A POV hat reports in sevenths, and CENTRED is 9/7 = 1.2857 —
      deliberately outside the -1..1 range every real axis is clamped to.
      That makes hat detection a proof, not a guess: only a hat can read
      above 1.0. The flag is sticky once seen, because a hat being pressed
      reads inside the normal range.

   3. ONE CONTROL, TWO IDENTITIES. The Gladiator's main trigger is a
      two-stage control: stage one is analog, the detent fires a button.
      So a physical control can be an axis AND a button at once, and
      nothing here may assume the two sets are exclusive.

   HONESTY RULE, unchanged: the browser tells the truth about index and
   value. It does not say what an axis is called. SC names are a
   convention mapped onto indices, and on a HOTAS that mapping is a guess.
   Raw index always shown; guesses marked; anything we cannot name in SC's
   vocabulary is flagged as unusable rather than given a plausible label.
   ================================================================ */
var padSlot={}, padPrev={}, padCenter={}, rafId=null, devHeld={};
var hatAxis={};      /* "padIndex:axisIndex" -> hat ordinal (1,2,...) */
var hatSeen={};      /* padIndex -> how many hats identified so far    */
var devDom=null;     /* built DOM references; null = needs a build     */
var devSig="";       /* signature of the current device set            */

var XI_BTN=["A","B","X","Y","Left Bumper","Right Bumper","Left Trigger",
  "Right Trigger","Back / View","Start / Menu","Left Stick Click","Right Stick Click",
  "D-Pad Up","D-Pad Down","D-Pad Left","D-Pad Right","Guide"];
var XI_SC=["xi_a","xi_b","xi_x","xi_y","xi_shoulderl","xi_shoulderr","xi_triggerl_btn",
  "xi_triggerr_btn","xi_back","xi_start","xi_thumbl","xi_thumbr","xi_dpad_up",
  "xi_dpad_down","xi_dpad_left","xi_dpad_right","xi_guide"];
var XI_AX=[["xi_thumblx","Left stick, horizontal"],["xi_thumbly","Left stick, vertical"],
  ["xi_thumbrx","Right stick, horizontal"],["xi_thumbry","Right stick, vertical"]];
/* Star Citizen's complete joystick axis vocabulary. There is no ninth name. */
var JS_AX=["x","y","z","rotx","roty","rotz","slider1","slider2"];

/* A POV hat in sevenths. Centre is 9/7, outside the range of any real axis. */
var HAT_DIRS=[
  [-1.000,"up"],        [-0.714,"up_right"],   [-0.429,"right"],
  [-0.143,"down_right"],[ 0.143,"down"],       [ 0.429,"down_left"],
  [ 0.714,"left"],      [ 1.000,"up_left"]];
/* Display cap. Sticks report 128 buttons; almost none have 128. A tile
   above the cap still appears the moment it is pressed - see applyVis. */
var BTN_SHOWN=40, showAll=false, hideUnused=false;
var DVCOL_CSS="\n/* The slot swap was a title= attribute nobody could find. Sleven asked\n   for \"a way to swap it or something\" - it existed, invisibly. */\n.slotswap{display:inline-block;margin-top:4px;font:600 10.5px/1.3 inherit;\n  color:#FFB259;background:#1A1206;border:1px solid #6B4C12;\n  border-radius:4px;padding:2px 6px;cursor:pointer}\n.slotswap:hover{border-color:#FF6B00;color:#FFD9A8}\n/* Two sticks are a pair, not a list. Side by side on a normal screen,\n   stacked only when there is genuinely no room. */\n.dvcols{display:grid;gap:14px;grid-template-columns:1fr}\n.dvcols.pair{grid-template-columns:repeat(auto-fit,minmax(330px,1fr))}\n.dvcol{background:#0B1626;border:1px solid #1B2C42;border-radius:10px;padding:11px 12px}\n.dvcolhd{font:800 13px/1.3 'Segoe UI',system-ui,sans-serif;color:#FF6B00;\n  letter-spacing:.04em;margin-bottom:9px;padding-bottom:7px;\n  border-bottom:1px solid #1B2C42}\n.dvcolhd small{display:block;font:600 11px/1.4 inherit;color:#93A7B6;\n  letter-spacing:.02em;margin-top:2px}\n";
var HAT_CENTRE=1.2857, HAT_TOL=0.06;

var DEADZONE=0.12, DRIFT=0.06;

/* Deliberate-deflection thresholds for REBINDING ONLY - see
   patch_axis_rebind_capture.py. AXIS_BIND_FIRE is past half travel so a resting
   or brushed stick can never bind; AXIS_BIND_REARM is far enough below it that
   a stick settling back cannot chatter across a single threshold. */
var AXIS_BIND_FIRE=0.55, AXIS_BIND_REARM=0.25;
var axisArmed={};   /* "padIndex:axisIndex" -> has returned near centre */

function pads(){
  var g=navigator.getGamepads?navigator.getGamepads():[], out=[], i;
  for(i=0;i<g.length;i++) if(g[i]) out.push(g[i]);
  return out;
}
/* ---- DEVICE IDENTITY ------------------------------------------------
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
function prefix(p){ return isStd(p) ? "xi" : "js"+slotOf(p); }
function esc(t){ return String(t).replace(/[&<>"]/g,function(c){
  return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]; }); }

/* A reading above 1.0 is physically impossible for a clamped axis, so it is
   proof of a hat rather than an inference. Sticky: a hat being held reads
   inside the normal range and would otherwise be misclassified back. */
function noteHat(p,i,v){
  var key=p.index+":"+i;
  if(hatAxis[key]) return true;
  if(v>1.05){
    hatSeen[p.index]=(hatSeen[p.index]||0)+1;
    hatAxis[key]=hatSeen[p.index];
    devDom=null;                 /* naming changed - the panel must rebuild */
    return true;
  }
  return false;
}
function hatDir(v){
  if(Math.abs(v-HAT_CENTRE)<HAT_TOL) return null;      /* centred */
  var best=null, bd=HAT_TOL, i, d;
  for(i=0;i<HAT_DIRS.length;i++){
    d=Math.abs(v-HAT_DIRS[i][0]);
    if(d<bd){ bd=d; best=HAT_DIRS[i][1]; }
  }
  return best;
}
function btnName(p,i){
  if(isStd(p)) return [XI_SC[i]||("xi_button"+i), XI_BTN[i]||("Button "+i), false];
  /* SC numbers joystick buttons from 1; the browser numbers from 0. */
  return [prefix(p)+"_button"+(i+1),
          "Button "+(i+1)+"  (browser index "+i+")", false];
}
/* returns [scName, rawLabel, isGuess, isUnusable] */
function axName(p,i){
  var key=p.index+":"+i;
  if(hatAxis[key])
    return [prefix(p)+"_hat"+hatAxis[key], "POV hat  (browser axes["+i+"])", false, false];
  if(isStd(p)&&XI_AX[i]) return [XI_AX[i][0], XI_AX[i][1], false, false];
  if(JS_AX[i]) return [prefix(p)+"_"+JS_AX[i], "browser axes["+i+"]", true, false];
  /* Past slider2 there is no Star Citizen name. Saying "axis8" would send
     someone to type a binding the game refuses. Say so instead. */
  return ["no Star Citizen name", "browser axes["+i+"]", false, true];
}

function signature(list){
  var s=[], i;
  for(i=0;i<list.length;i++)
    s.push(list[i].index+"|"+list[i].id+"|"+list[i].buttons.length+"|"+
           list[i].axes.length+"|"+prefix(list[i]));
  return s.join("~");
}

function emptyPanel(){
  return '<div class="dvempty"><strong>No controller detected yet</strong>'+
    'Plug the stick in, then <b>press a button on it</b>.<br>'+
    'Browsers deliberately hide controllers until one is used, so nothing '+
    'appears here until you press something.<br><br>'+
    'Works with anything Windows sees: sticks, throttles, pedals, gamepads, '+
    'button boxes. Up to eight at once, numbered <kbd>js1</kbd> <kbd>js2</kbd> '+
    '<kbd>js3</kbd> in the order you press them.</div>';
}


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

/* Build the DOM once. Everything after this is mutation only. */
function buildDevice(list){
  var host=$(ID_+'board'), h='', i;
  if(!document.getElementById('cc-dvcol-css')){
    var st=document.createElement('style');
    st.id='cc-dvcol-css'; st.textContent=DVCOL_CSS;
    document.head.appendChild(st);
  }
  if(!list.length){ host.innerHTML=emptyPanel(); devDom=null; return; }

  /* RENDER IN SLOT ORDER, NOT PLUG ORDER. pads() returns
     navigator.getGamepads() order, which is OS enumeration - so js1 could be
     drawn on the right of js2 while both were labelled correctly. Sorting here
     changes only the layout; identity is still resolved by profile GUID, then
     remembered choice, then an admitted guess. Standard-mapping gamepads have
     no js slot and settle after the sticks without displacing them. */
  list = list.slice().sort(function(a,b){
    var sa = isStd(a) ? 99 : slotOf(a), sb = isStd(b) ? 99 : slotOf(b);
    if(sa !== sb) return sa - sb;
    return a.index - b.index;
  });

  h='<div class="dvhead">';
  list.forEach(function(p){
    var _src=isStd(p)?"":slotSource(p);
    var _note={profile:"from the imported profile",
               remembered:"your choice, remembered for this device",
               guessed:"guessed from plug order - click to set"}[_src]||"";
    h+='<div class="dvchip on" data-chip="'+p.index+'"><div class="sl cc-slot'+
       (_src?' cc-src-'+_src:'')+'" data-slot="'+p.index+'" title="'+esc(_note)+
       '">'+prefix(p)+'</div>'+
       (_note?'<div class="srcnote cc-src-'+_src+'">'+esc(_note)+'</div>':'')+
       (_src&&_src!=='profile'
         ? '<button class="slotswap cc-slot" data-slot="'+p.index+
           '" title="Click to change which stick this is">wrong stick? click to swap</button>'
         : '')+
       '<div class="nm" title="'+esc(p.id)+'">'+esc(p.id)+'</div>'+
       '<div class="id">'+p.buttons.length+' buttons · '+p.axes.length+' axes · '+
       (p.mapping==="standard"?"standard mapping":"raw / no standard mapping")+
       '</div></div>';
  });
  h+='<button class="tg" id="'+ID_+'dvcal" title="Take the current stick positions as centre">'+
     'Set centre</button><button class="tg" id="'+ID_+'dvcopy">Copy device report</button>'+
     '<button class="tg" id="'+ID_+'dvhide">Hide unused buttons</button>'+
     '<button class="tg" id="'+ID_+'dvall">'+dvAllLabel(list)+'</button>'+
     '<span class="dvcap" id="'+ID_+'dvcapnote"></span></div>';

  h+='<div class="dvcols'+(list.length>1?' pair':'')+'">';
  list.forEach(function(p){
    h+='<div class="dvcol"><div class="dvcolhd">'+prefix(p)+' &mdash; '+esc(p.id)+
       '<small>'+p.buttons.length+' buttons &middot; '+p.axes.length+' axes</small></div>';
    h+='<div class="dvsec">buttons</div><div class="btngrid">';
    if(!p.buttons.length) h+='<div style="color:#93A7B6;font-size:13px">none reported</div>';
    p.buttons.forEach(function(b,i){
      var n=btnName(p,i);
      h+='<div class="btn'+(i>=BTN_SHOWN?' over':'')+'" data-b="'+p.index+':'+i+'">'+
         '<div class="sc">'+n[0]+'</div><div class="nm">'+n[1]+'</div>'+
         '<div class="va"></div></div>';
    });
    h+='</div><div class="dvsec">axes and hats</div>';
    if(!p.axes.length) h+='<div style="color:#93A7B6;font-size:13px">none reported</div>';
    p.axes.forEach(function(v,i){
      var n=axName(p,i);
      h+='<div class="axrow" data-a="'+p.index+':'+i+'">'+
         '<div class="axnm"'+(n[3]?' style="color:#FF6B00"':'')+'>'+n[0]+
         (n[2]?' <span style="color:#FF6B00">?</span>':'')+
         '<small>'+n[1]+'</small></div>'+
         '<div class="axbar"><u></u><i></i><b></b></div>'+
         '<div class="axval">0.000</div></div>';
    });
    h+='</div>';                      /* .dvcol */
  });
  h+='</div>';                        /* .dvcols */

  h+='<div class="dvwarn"><strong>Reading this panel.</strong> '+
     'The <b>name in the left column</b> is what Star Citizen calls that input — '+
     'type it straight into a binding. The <b>grey line under it</b> is what the '+
     'browser actually reported, which is the part that cannot be wrong.<br>'+
     'An orange <span style="color:#FF6B00">?</span> means the axis order is the '+
     'usual one but <b>not confirmed for your stick</b> — move one axis at a time '+
     'and check the right row lights up.<br>'+
     '<b>POV hats are detected, not guessed</b>: a hat reports 1.286 at rest, '+
     'which no ordinary axis can reach.<br>'+
     'A value in orange at rest is <b>drift</b>. <code>Set centre</code> zeroes it '+
     'on this page only, never in the game — and it is deliberately refused on a '+
     'hat, where a resting 1.286 is correct.</div>';
  host.innerHTML=h;

  /* cache references once */
  devDom={btn:{}, ax:{}, chip:{}};
  var els=host.querySelectorAll('.btn[data-b]'), j;
  for(j=0;j<els.length;j++)
    devDom.btn[els[j].getAttribute('data-b')]={
      el:els[j], va:els[j].querySelector('.va'), on:null,
      ix:parseInt(els[j].getAttribute('data-b').split(':')[1],10)};
  els=host.querySelectorAll('.axrow[data-a]');
  for(j=0;j<els.length;j++)
    devDom.ax[els[j].getAttribute('data-a')]={
      row:els[j], fill:els[j].querySelector('.axbar i'),
      dot:els[j].querySelector('.axbar b'), val:els[j].querySelector('.axval'),
      cls:null, last:null};
  els=host.querySelectorAll('.dvchip[data-chip]');
  for(j=0;j<els.length;j++)
    devDom.chip[els[j].getAttribute('data-chip')]={el:els[j], hot:null};

  var cal=$(ID_+'dvcal');
  if(cal) cal.onclick=function(){
    pads().forEach(function(p){
      var arr=[], i;
      for(i=0;i<p.axes.length;i++)
        /* Never "zero" a hat: 1.286 at rest is the correct reading, and
           subtracting it would make every direction look like drift. */
        arr.push(hatAxis[p.index+":"+i] ? 0 : p.axes[i]);
      padCenter[p.index]=arr;
    });
  };
  var cp=$(ID_+'dvcopy'); if(cp) cp.onclick=copyReport;
  var hb=$(ID_+'dvhide');
  if(hb) hb.onclick=function(){
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
  applyVis();
}

/* Mutation only. Called every frame; must touch nothing structural. */
function paintDevice(list){
  if(!devDom) return;
  list.forEach(function(p){
    var i, k, d;
    for(i=0;i<p.buttons.length;i++){
      k=p.index+":"+i; d=devDom.btn[k]; if(!d) continue;
      var b=p.buttons[i], on=b.pressed||b.value>0.5;
      var an=(b.value>0.02&&b.value<0.98);
      if(on && !d.everPressed){ d.everPressed=true; applyVis(); }
      if(d.on!==on){ d.on=on;
        if(on) d.el.classList.add('down'); else d.el.classList.remove('down'); }
      if(d.an!==an){ d.an=an;
        if(an) d.el.classList.add('analog'); else d.el.classList.remove('analog'); }
      var vt = an ? b.value.toFixed(2) : "";
      if(d.va && d.vaLast!==vt){ d.vaLast=vt; d.va.textContent=vt; }
    }
    for(i=0;i<p.axes.length;i++){
      k=p.index+":"+i; d=devDom.ax[k]; if(!d) continue;
      var v=p.axes[i];
      var isHat=noteHat(p,i,v);
      if(!devDom) return;                 /* a hat was just identified */
      var c=(padCenter[p.index]||[])[i]||0;
      var adj=v-c, txt, cls="axrow", pct;
      if(isHat){
        var dir=hatDir(v);
        txt = dir ? dir.replace('_','-') : "centred";
        if(dir) cls="axrow hot";
        pct = dir ? 90 : 50;
      } else {
        txt = adj.toFixed(3);
        pct = ((Math.max(-1,Math.min(1,adj))+1)/2)*100;
        if(Math.abs(adj)>DEADZONE) cls="axrow hot";
        else if(Math.abs(adj)>DRIFT) cls="axrow drift";
      }
      if(d.cls!==cls){ d.cls=cls; d.row.className=cls; }
      if(d.last!==txt){ d.last=txt; d.val.textContent=txt; }
      d.dot.style.left=pct+"%";
      d.fill.style.left=Math.min(50,pct)+"%";
      d.fill.style.width=Math.abs(pct-50)+"%";
    }
    var ch=devDom.chip[p.index];
    if(ch){
      var hot=(padPrev[p.index]&&padPrev[p.index].hot)||false;
      if(ch.hot!==hot){ ch.hot=hot;
        if(hot) ch.el.classList.add('live'); else ch.el.classList.remove('live'); }
    }
  });
}

function renderDevice(){
  var list=pads(), sig=signature(list);
  if(sig!==devSig || !devDom){ devSig=sig; buildDevice(list); }
  paintDevice(list);
}

function copyReport(){
  var out=[];
  pads().forEach(function(p){
    out.push("DEVICE  "+p.id);
    out.push("  slot "+prefix(p)+"   mapping: "+(p.mapping||"none")+
             "   "+p.buttons.length+" buttons, "+p.axes.length+" axes");
    p.buttons.forEach(function(b,i){ var n=btnName(p,i);
      out.push("  "+pad18(n[0])+n[1]); });
    p.axes.forEach(function(v,i){ var n=axName(p,i);
      out.push("  "+pad18(n[0])+n[1]+
               (n[3]?"   (NO Star Citizen name - unusable in a binding)":"")+
               (n[2]?"   (order not confirmed)":"")+
               "   resting "+v.toFixed(3)); });
    out.push("");
  });
  var txt=out.join("\n")||"no devices", b=$(ID_+'dvcopy');
  function done(){ if(b){ b.textContent="Copied";
    setTimeout(function(){ var x=$(ID_+'dvcopy'); if(x)x.textContent="Copy device report"; },1400); } }
  if(navigator.clipboard&&navigator.clipboard.writeText)
    navigator.clipboard.writeText(txt).then(done,function(){ fallbackCopy(txt); done(); });
  else { fallbackCopy(txt); done(); }
}
function pad18(t){ t=String(t); while(t.length<18) t+=" "; return t; }
function fallbackCopy(txt){
  var ta=document.createElement('textarea');
  ta.value=txt; ta.style.position='fixed'; ta.style.left='-9999px';
  document.body.appendChild(ta); ta.select();
  try{ document.execCommand('copy'); }catch(e){}
  document.body.removeChild(ta);
}

function fireDev(p,label,sc,press){
  /* REBIND FIRST, LIVE DISPLAY SECOND.
     This is the one place a joystick, HOTAS or gamepad press has already become
     the game's own token. A rebind needs exactly that string, so it is taken
     from here rather than reimplemented - which is also why hats arrive as
     their full compound token (js1_hat1_up) without special handling. */
  if(window.KBREBIND && KBREBIND.listening()){
    KBREBIND.capture(sc);
    return;
  }
  var ro=$(ID_+'ro');
  if(ro){ ro.classList.add('hot'); clearTimeout(fireDev._t);
    fireDev._t=setTimeout(function(){ ro.classList.remove('hot'); },450); }
  $(ID_+'rk').textContent=sc;
  $(ID_+'rmeta').textContent=esc(p.id)+" · "+label+" · "+press;
  $(ID_+'ract').className="ract";
  $(ID_+'ract').textContent="Type "+sc+" into a Star Citizen binding to use this input.";
  $(ID_+'rwarn').textContent="";
  var l=$(ID_+'log');
  if(l.dataset.v!=="1"){ l.innerHTML=""; l.dataset.v="1"; }
  var d=document.createElement('div');
  d.innerHTML='<strong>'+sc+'</strong> <span class="t">· '+label+' · '+press+
    '</span><br><span style="color:#93A7B6">'+esc(p.id)+'</span>';
  l.insertBefore(d,l.firstChild);
  while(l.children.length>14) l.removeChild(l.lastChild);
}

var hatLast={};
function poll(){
  /* A REBIND POLLS REGARDLESS OF THE SELECTED TAB. The action browser lists
     keyboard, mouse, joystick and gamepad bindings in ONE list, and nothing in
     the UI tells anybody to switch tabs before rebinding a stick input.
     Requiring it would be an undocumented precondition; not requiring it means
     this gate cannot depend on `dev` alone. */
  var rebinding = !!(window.KBREBIND && KBREBIND.listening());
  if((dev==="KBM"&&!rebinding)||(typeof OPEN!=="undefined"&&!OPEN&&!rebinding)){
    rafId=null; return; }
  var list=pads(), now=Date.now();
  list.forEach(function(p){
    var prev=padPrev[p.index]||{b:[],a:[],hot:false}, hot=false;
    p.buttons.forEach(function(b,i){
      var on=b.pressed||b.value>0.5, was=!!prev.b[i], key, dur, press, n;
      if(on) hot=true;
      if(on!==was){
        key=p.index+":b"+i;
        if(on){ devHeld[key]=now; }
        /* A REBIND IS NOT SUBJECT TO THE CAPTURE TOGGLE. That toggle governs
           the live tester readout; nothing in the UI ever said it also
           disables rebinding, and with it OFF the panel named both sticks
           while relaying nothing from them. */
        else if(ccInputAllowed()){
          dur=now-(devHeld[key]||now); delete devHeld[key];
          press=dur>=400?"HOLD":"TAP";
          if(press==="TAP"&&lastTap[key]&&now-lastTap[key]<320) press="DOUBLE TAP";
          lastTap[key]=now; n=btnName(p,i);
          fireDev(p,n[1],n[0],press+" ("+dur+"ms)");
        }
      }
      prev.b[i]=on;
    });
    p.axes.forEach(function(v,i){
      var key=p.index+":"+i;
      if(hatAxis[key]){
        /* Report a hat like a button: it has discrete positions, and a
           direction is what someone actually wants to bind. */
        var dir=hatDir(v), hk=p.index+":h"+i;
        if(dir) hot=true;
        if(hatLast[hk]!==dir){
          if(dir && ccInputAllowed())
            fireDev(p,"POV hat "+dir.replace('_','-'),
                    prefix(p)+"_hat"+hatAxis[key]+"_"+dir,"PRESS");
          hatLast[hk]=dir;
        }
      } else {
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
      }
      prev.a[i]=v;
    });
    prev.hot=hot; padPrev[p.index]=prev;
  });
  /* Unconditional. Painting is now cheap - text, classes and two style
     properties - so there is no reason to gate it on a change threshold,
     and gating it was what made the readout lag behind the stick. */
  renderDevice();
  rafId=requestAnimationFrame(poll);
}
/* Is device input allowed to fire right now?
   Two reasons it may be: the Capture toggle is on (live tester readout), or a
   rebind is listening (which the toggle has no business affecting). One
   function so the button and hat call sites cannot drift apart. */
function ccInputAllowed(){
  if(window.KBREBIND && KBREBIND.listening()) return true;
  return (typeof capture === "undefined" || capture);
}

/* ---- DEVICE PRESENCE -------------------------------------------------
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

function startPoll(){
  /* Same reasoning as poll(): a rebind needs the loop running even on the
     Keyboard/Mouse tab, or the first stick press is never sampled and the cell
     simply sits there listening forever. */
  var rebinding = !!(window.KBREBIND && KBREBIND.listening());
  if(rafId===null&&(dev!=="KBM"||rebinding)) rafId=requestAnimationFrame(poll);
}
window.addEventListener('gamepadconnected',function(){
  /* ALWAYS notice. Whether to start SAMPLING can depend on what is on screen;
     whether to know a device exists cannot - this handler discarding the event
     on the default tab is why a reload was needed. */
    devDom=null;
    ccPresenceChanged();
    if(dev!=="KBM"){ renderDevice(); startPoll(); } });
/* Clicking a slot cycles js1..js8 and remembers it against that device's
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
  /* Unplugging mid-session is worth saying out loud too, on any tab. */
  ccPresenceChanged();
  if(dev!=="KBM") renderDevice(); });
