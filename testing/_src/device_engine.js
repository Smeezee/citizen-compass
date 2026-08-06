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
var HAT_CENTRE=1.2857, HAT_TOL=0.06;

var DEADZONE=0.12, DRIFT=0.06;

function pads(){
  var g=navigator.getGamepads?navigator.getGamepads():[], out=[], i;
  for(i=0;i<g.length;i++) if(g[i]) out.push(g[i]);
  return out;
}
function slotOf(p){
  if(padSlot[p.index]) return padSlot[p.index];
  var used={}, k, n;
  for(k in padSlot) used[padSlot[k]]=1;
  for(n=1;n<=8;n++) if(!used[n]){ padSlot[p.index]=n; return n; }
  padSlot[p.index]=1; return 1;
}
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

/* Build the DOM once. Everything after this is mutation only. */
function buildDevice(list){
  var host=$(ID_+'board'), h='', i;
  if(!list.length){ host.innerHTML=emptyPanel(); devDom=null; return; }

  h='<div class="dvhead">';
  list.forEach(function(p){
    h+='<div class="dvchip on" data-chip="'+p.index+'"><div class="sl">'+prefix(p)+
       '</div><div class="nm" title="'+esc(p.id)+'">'+esc(p.id)+'</div>'+
       '<div class="id">'+p.buttons.length+' buttons · '+p.axes.length+' axes · '+
       (p.mapping==="standard"?"standard mapping":"raw / no standard mapping")+
       '</div></div>';
  });
  h+='<button class="tg" id="'+ID_+'dvcal" title="Take the current stick positions as centre">'+
     'Set centre</button><button class="tg" id="'+ID_+'dvcopy">Copy device report</button>'+
     '<button class="tg" id="'+ID_+'dvhide">Hide unused buttons</button></div>';

  list.forEach(function(p){
    h+='<div class="dvsec">'+esc(p.id)+' &mdash; buttons</div><div class="btngrid">';
    if(!p.buttons.length) h+='<div style="color:#93A7B6;font-size:13px">none reported</div>';
    p.buttons.forEach(function(b,i){
      var n=btnName(p,i);
      h+='<div class="btn" data-b="'+p.index+':'+i+'">'+
         '<div class="sc">'+n[0]+'</div><div class="nm">'+n[1]+'</div>'+
         '<div class="va"></div></div>';
    });
    h+='</div><div class="dvsec">'+esc(p.id)+' &mdash; axes</div>';
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
  });

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
      el:els[j], va:els[j].querySelector('.va'), on:null};
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
    var hide=this.classList.toggle('on'), k;
    this.textContent = hide ? "Show all buttons" : "Hide unused buttons";
    for(k in devDom.btn){
      var d=devDom.btn[k];
      d.el.style.display = (hide && !d.everPressed) ? 'none' : '';
    }
  };
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
      if(on){ d.everPressed=true; }
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
  if(dev==="KBM"||(typeof OPEN!=="undefined"&&!OPEN)){ rafId=null; return; }
  var list=pads(), now=Date.now();
  list.forEach(function(p){
    var prev=padPrev[p.index]||{b:[],a:[],hot:false}, hot=false;
    p.buttons.forEach(function(b,i){
      var on=b.pressed||b.value>0.5, was=!!prev.b[i], key, dur, press, n;
      if(on) hot=true;
      if(on!==was){
        key=p.index+":b"+i;
        if(on){ devHeld[key]=now; }
        else if(typeof capture==="undefined"||capture){
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
          if(dir && (typeof capture==="undefined"||capture))
            fireDev(p,"POV hat "+dir.replace('_','-'),
                    prefix(p)+"_hat"+hatAxis[key]+"_"+dir,"PRESS");
          hatLast[hk]=dir;
        }
      } else {
        var c=(padCenter[p.index]||[])[i]||0;
        if(Math.abs(v-c)>DEADZONE) hot=true;
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
function startPoll(){ if(rafId===null&&dev!=="KBM") rafId=requestAnimationFrame(poll); }
window.addEventListener('gamepadconnected',function(){
  if(dev!=="KBM"){ devDom=null; renderDevice(); startPoll(); } });
window.addEventListener('gamepaddisconnected',function(e){
  delete padSlot[e.gamepad.index]; delete padPrev[e.gamepad.index];
  delete padCenter[e.gamepad.index];
  devDom=null;
  if(dev!=="KBM") renderDevice(); });
