#!/usr/bin/env python3
"""
build_next_frontpage.py - builds the NEW Citizen Compass front page.

This is the ONLY thing that can rebuild that page. It lived in scratch for a
day, which meant one reboot away from being gone; that is why it is here now.

Writes two files from one source of truth:
  data-layer/derived/main-page-concepts/the-index.html
      working copy - every picture inlined as a data: URI, so the file opens
      anywhere on its own with no folder next to it.
  testing/_src/next.src.html  (+ testing/_src/images/)
      build source - pictures written out as real files named by the SHA-256 of
      their own bytes, so identical pictures collapse to one file and a name
      never changes between rebuilds. ~95% smaller page.

Stale images in testing/_src/images/ are REPORTED, never deleted (rule 1).

Run it with no arguments.
"""
import json, re, os, html, collections

BASE=os.path.expanduser('~/mnt/citizen-compass/data-layer/derived')
OUT=os.path.expanduser('~/mnt/citizen-compass/data-layer/derived/main-page-concepts/the-index.html')
f=json.load(open(BASE+'/main-page-concepts/frontpage_data.json',encoding='utf-8'))
THUMBS=json.load(open(BASE+'/main-page-concepts/ship_thumbs.json',encoding='utf-8')).get('thumbs',{})
RENDERS=json.load(open(BASE+'/ship-renders/by_ship_name.json',encoding='utf-8')).get('renders',{})
import os.path as _op
_ed=BASE+'/main-page-concepts/editions.json'
_EDJ=json.load(open(_ed,encoding='utf-8')).get('editions',{}) if _op.isfile(_ed) else {}
EDITIONS={p:[dict(x) for x in v] for p,v in _EDJ.items()}
FOLDED={x['from_row']:p for p,v in EDITIONS.items() for x in v if x.get('from_row')}
_pc=BASE+'/main-page-concepts/price_corrections.json'
CORR={c['ship']:c for c in (json.load(open(_pc,encoding='utf-8')).get('corrections',[]) if _op.isfile(_pc) else [])}
_sl=BASE+'/main-page-concepts/card_pictures.json'   # built by build_card_pictures.py
SLEVEN=json.load(open(_sl,encoding='utf-8')).get('thumbs',{}) if _op.isfile(_sl) else {}
EX=json.load(open('/tmp/cc/extra.json',encoding='utf-8'))

PLACE={d['k']:d.get('place','') for d in f.get('dealers',[])}
BODY ={d['k']:d.get('body','')  for d in f.get('dealers',[])}

def compact(d):
    if not d: return None,None,None
    raw=re.findall(r'[MLZ]|-?\d+\.?\d*',d); cmds=[];pts=[];i=0
    while i<len(raw):
        t=raw[i]
        if t in 'ML': x,y=float(raw[i+1]),float(raw[i+2]);cmds.append((t,x,y));pts.append((x,y));i+=3
        elif t=='Z': cmds.append(('Z',0,0));i+=1
        else: i+=1
    if not pts: return None,None,None
    xs=[p[0] for p in pts];ys=[p[1] for p in pts]
    x0,y0,x1,y1=min(xs),min(ys),max(xs),max(ys)
    TOL=9.0;o=[];lx=ly=None
    for c,x,y in cmds:
        if c=='Z': o.append(('Z',0,0));lx=ly=None;continue
        if c=='M': o.append((c,x,y));lx,ly=x,y;continue
        if lx is None or abs(x-lx)+abs(y-ly)>=TOL: o.append((c,x,y));lx,ly=x,y
    return ''.join('Z' if c=='Z' else f'{c}{round(x-x0)} {round(y-y0)}' for c,x,y in o), round(x1-x0,1), round(y1-y0,1)

ships=[]
for s in f['ships']:
    if s.get('n') in FOLDED: continue          # an edition of another hull. shows on that hull's card.
    _c=CORR.get(s.get('n'))
    if _c:
        if _c.get('usd') is not None: s['usd']=_c['usd']
        if _c.get('auec') is not None: s['auec']=_c['auec']
        if _c.get('clear_note'): s['note']=''

    d,w,h=compact(s.get('d'))
    img=SLEVEN.get(s.get('n')) or THUMBS.get(s.get('n')) or RENDERS.get(s.get('n'))
    if img: d,w,h=None,None,None
    ships.append({'img':img,'n':s.get('n'),'m':s.get('m') or 'Other','c':s.get('career') or '',
      'r':s.get('role') or '','st':s.get('status'),'a':s.get('auec'),'u':s.get('usd'),
      'dl':s.get('deal') or [],'dp':s.get('dprice') or None,'no':s.get('note') or '',
      'L':s.get('L'),'cr':s.get('crew'),'cg':s.get('cargo'),'url':s.get('url') or '',
      'd':d,'w':w,'h':h,'hull':s.get('hull') or None,
      'pl':sorted({PLACE.get(k,'') for k in (s.get('deal') or [])} - {''}) or None,

      'ed':[{'name':x['name'],'usd':x.get('usd')} for x in EDITIONS.get(s.get('n'),[])] or None})
careers=[k for k,_ in collections.Counter(x['c'] for x in ships if x['c']).most_common()]
payload=json.dumps({'ships':ships,'place':PLACE,'body':BODY,'dev':EX['dev'],'cal':EX['cal']},separators=(',',':'))

CSS=r"""
*{box-sizing:border-box}
body{margin:0;background:#05070a;color:#dbe4ee;
 font:14px/1.45 ui-sans-serif,-apple-system,"Segoe UI",Roboto,sans-serif;-webkit-font-smoothing:antialiased}
.mono{font-family:ui-monospace,"JetBrains Mono","SF Mono",Menlo,Consolas,monospace;font-variant-numeric:tabular-nums}
.wrap{max-width:1680px;margin:0 auto;padding:0 22px}
a{color:#7fc4e8}

header{position:sticky;top:0;z-index:30;background:rgba(6,9,13,.95);backdrop-filter:blur(14px);
 border-bottom:1px solid #111a24}
#top{display:flex;align-items:baseline;gap:12px;padding:12px 0 4px;flex-wrap:wrap}
#top b{font-size:14px;letter-spacing:.18em;text-transform:uppercase;color:#eaf2fb;font-weight:600}
#top span{font-size:11.5px;color:#54657a}

/* THE MASTHEAD. Sleven asked for the name "big bold on the top" with "some
   facts and stuff". It sits ABOVE the sticky bar and scrolls away, because a
   banner this size stuck to the top would eat a third of the screen on every
   scroll. The small wordmark in the sticky bar is what remains once it goes.
   Every number in the facts strip is counted from the same array the cards
   are drawn from, at render time - there is no second copy to go stale. */
#mast{border-bottom:1px solid #10171f;background:
  radial-gradient(1100px 300px at 18% -40%,rgba(79,209,255,.10),transparent 70%),
  radial-gradient(900px 260px at 82% -30%,rgba(120,90,255,.07),transparent 70%),#070b10}
#mast .wrap{padding-top:34px;padding-bottom:24px}
#brand{font-size:clamp(34px,6.2vw,68px);line-height:.96;font-weight:800;letter-spacing:-.02em;
 color:#f2f8ff;margin:0}
#brand em{font-style:normal;color:#4fd1ff}
#tag{margin:11px 0 0;font-size:clamp(13px,1.5vw,17px);color:#7f93a8;letter-spacing:.01em}
#facts{display:grid;grid-template-columns:repeat(auto-fit,minmax(132px,1fr));gap:9px;margin-top:22px}
.fact{border:1px solid #16202b;background:rgba(10,15,22,.72);border-radius:11px;padding:11px 13px}
.fact b{display:block;font-size:23px;font-weight:700;color:#eaf2fb;letter-spacing:-.01em;
 font-variant-numeric:tabular-nums}
.fact span{display:block;margin-top:3px;font-size:10.5px;letter-spacing:.10em;text-transform:uppercase;
 color:#56697d}
.fact.hi b{color:#4fd1ff}
@media(max-width:640px){#mast .wrap{padding-top:22px;padding-bottom:18px}
 #facts{grid-template-columns:repeat(2,1fr)}.fact b{font-size:19px}}
#ver{margin-left:auto;font-size:11px;color:#4a5c6d;letter-spacing:.04em}
#patch{display:flex;gap:14px;align-items:center;padding-bottom:9px;font-size:11.5px;color:#66798d;flex-wrap:wrap}
.dot{display:inline-flex;align-items:center;gap:6px}
.dot i{width:7px;height:7px;border-radius:50%;background:#4fae63;display:inline-block;font-style:normal}
.dot.ptu i{background:#3a4757}
#tabs{display:flex;gap:2px;padding-bottom:8px;overflow-x:auto;scrollbar-width:none}
#tabs::-webkit-scrollbar{display:none}
.tab{flex:0 0 auto;background:none;border:0;border-bottom:2px solid transparent;color:#697d92;
 padding:7px 13px;font-size:13px;cursor:pointer;white-space:nowrap}
.tab:hover{color:#cfe0f0}
.tab.on{color:#9fe2ff;border-bottom-color:#3d7f9e}
#find{padding-bottom:9px}
#q{width:100%;background:#0a0f16;border:1px solid #1b2634;color:#eaf2fa;border-radius:9px;
 padding:12px 15px;font-size:15px;line-height:21.75px;outline:none;
 font-family:ui-sans-serif,-apple-system,"Segoe UI",Roboto,sans-serif;letter-spacing:normal}
#q::placeholder{color:#4b5c6e}
/* THE GHOST. Sleven asked for "a predicted kinda, like, ghost view of the word".
   It is a layer UNDER the input, not inside it: the typed part is drawn
   transparent so the real input's own text shows through unchanged, and only
   the completion is painted. Nothing is written into the input, so backspace,
   selection and the caret all behave exactly as they did. Tab or the right
   arrow accepts it.
   Every font and spacing value here MUST equal #q's or the letters drift
   apart by a pixel per character and it looks broken at the end of a word. */
#q{position:relative;background:transparent;z-index:2}
#ghost{position:absolute;left:0;right:0;top:0;bottom:0;z-index:1;pointer-events:none;
 padding:12px 15px;font-size:15px;line-height:21.75px;letter-spacing:normal;
 font-family:ui-sans-serif,-apple-system,"Segoe UI",Roboto,sans-serif;
 white-space:pre;overflow:hidden;border:1px solid transparent;border-radius:9px;
 background:#0a0f16}
#gtyped{color:transparent}
#grest{color:#43586b}
#q:focus{border-color:#2f6d8c;box-shadow:0 0 0 3px rgba(79,209,255,.08)}
#chips{display:flex;gap:6px;overflow-x:auto;padding-bottom:11px;scrollbar-width:none}
#chips::-webkit-scrollbar{display:none}
.chip{flex:0 0 auto;border:1px solid #1b2634;background:#0a0f16;color:#8296aa;border-radius:999px;
 padding:6px 13px;font-size:12.5px;cursor:pointer;white-space:nowrap;user-select:none}
.chip:hover{border-color:#2c3d50;color:#cfe0f0}
.chip.on{background:#11232e;border-color:#3d7f9e;color:#9fe2ff}
.chip.buy.on{background:#102019;border-color:#3f8050;color:#8fd99a}
#cur{background:#0a0f16;border:1px solid #1b2634;color:#8296aa;border-radius:999px;padding:6px 10px;font-size:12.5px}

main{padding:4px 0 70px}
.view{display:none}.view.on{display:block}
.grp{display:flex;align-items:baseline;gap:10px;margin:22px 0 9px;padding-bottom:7px;border-bottom:1px solid #121b25}
.grp h2{margin:0;font-size:12.5px;letter-spacing:.15em;text-transform:uppercase;color:#8fb4cc;font-weight:600}
.grp em{font-style:normal;font-size:11.5px;color:#4a5c6d}
.cols{display:grid;grid-template-columns:repeat(auto-fill,minmax(330px,1fr));gap:8px;align-items:stretch}

.ship{display:grid;grid-template-columns:104px 1fr;gap:12px;padding:10px 11px;border-radius:9px;
 cursor:pointer;border:1px solid #101821;background:#080c12;height:152px;overflow:hidden;align-content:start}
.body{display:flex;flex-direction:column;height:100%;min-width:0}
.spacer{flex:1 1 auto;min-height:2px}
/* THE CARD IS A FLASHCARD. Sleven: "each section of the card where this is
   gonna be listed, what this price is gonna be". So every zone is drawn on
   every card even when it is empty - an em dash rather than a collapsed row -
   because a card that changes shape when a fact is missing cannot be read by
   position, and reading by position is the whole point. */
.spec{display:flex;gap:0;margin:1px 0 3px;font-size:11.5px;color:#6f8496;font-variant-numeric:tabular-nums}
.spec span{flex:1 1 0;min-width:0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.spec span+span{padding-left:8px;border-left:1px solid #141d27}
.pr{border-top:1px solid #131c26;padding-top:4px}
#find{position:relative}
#sug{display:none;position:absolute;left:0;right:0;top:calc(100% + 4px);z-index:40;
 background:#080d14;border:1px solid #1b2634;border-radius:9px;overflow:hidden;
 box-shadow:0 18px 40px rgba(0,0,0,.55)}
#sug.on{display:block}
.sg{display:flex;align-items:center;gap:9px;padding:8px 11px;cursor:pointer;font-size:13.5px;color:#c8d6e3}
.sg:hover,.sg.at{background:#0f1823}
.sgk{font-size:10px;letter-spacing:.09em;text-transform:uppercase;padding:2px 6px;border-radius:4px;
 background:#131d29;color:#7d90a4;min-width:44px;text-align:center}
.k-ship{color:#9fd2ff}.k-maker{color:#b7a3ff}.k-job{color:#8fe0b4}.k-shop{color:#ffd08a}.k-place{color:#ff9fb0}
a.ship{text-decoration:none;color:inherit;display:grid}
a.ship:hover{background:#0c131b;border-color:#2b3d50}
.ship.dead{cursor:default}
.ed{display:flex;align-items:baseline;gap:7px;font-size:11.5px;color:#7d90a4;
 border-top:1px solid #131c26;padding-top:5px;margin-bottom:2px}
.ed .edn{color:#9fb6cb}.ed .edp{color:#6f8496;margin-left:auto}
.ship:hover{background:#0c131b;border-color:#22303f}
.pic{width:104px;height:60px;object-fit:cover;border-radius:6px;display:block;align-self:center;background:#0b1119}
.sil{width:104px;height:60px;display:block;align-self:center}
.sil path{fill:#8ba1b8}
.noimg{width:104px;height:60px;border-radius:6px;background:#0a0f16;border:1px dashed #1b2634;
 display:grid;place-items:center;font-size:9px;letter-spacing:.08em;color:#3f5163;text-transform:uppercase}
.hd{display:flex;align-items:baseline;gap:7px;flex-wrap:nowrap;min-width:0}
.nm{font-size:14.5px;font-weight:600;color:#eef5fb;letter-spacing:-.01em;
 min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.pill{font-size:8.5px;letter-spacing:.1em;text-transform:uppercase;padding:2px 6px;border-radius:3px;
 flex:0 0 auto;white-space:nowrap}
.p-buy{background:#102019;color:#7fc98d;border:1px solid #24452e}
.p-pl{background:#20190f;color:#d0a05f;border:1px solid #453824}
.sub{font-size:11.5px;color:#697d92;margin-top:2px}
.pr{display:flex;align-items:baseline;gap:8px;margin-top:6px;flex-wrap:wrap}
.auec{font-size:15px;font-weight:600;color:#ffc266}
.auec small{font-size:9.5px;color:#8a7350;font-weight:400;margin-left:2px}
.usd{font-size:12px;color:#8ea3b8;margin-left:auto}
.none{font-size:12.5px;color:#4f6070}
.at{font-size:11px;color:#6f8296;margin-top:3px}
.at b{color:#8fd99a;font-weight:500}
.at u{text-decoration:none;color:#c9954f}
.at s{text-decoration:none;color:#55677b}
.note{font-size:11px;color:#5f7185;font-style:italic;
 display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;min-height:15px}
.at{min-height:16px}

.panel{max-width:920px;margin:18px 0 0}
.panel h2{font-size:13px;letter-spacing:.15em;text-transform:uppercase;color:#8fb4cc;margin:0 0 10px}
.lead{font-size:12.5px;color:#7d8fa3;line-height:1.6;margin-bottom:16px;
 border-left:2px solid #1e2b3a;padding-left:13px}
.item{padding:13px 0;border-top:1px solid #121b25}
.item h3{margin:0 0 3px;font-size:14.5px;color:#eef5fb;font-weight:600}
.item .meta{font-size:11.5px;color:#6f8296;margin-bottom:5px}
.item .meta b{color:#9fe2ff;font-weight:500}
.item p{margin:0;font-size:12.5px;color:#8296aa;line-height:1.55}
.defs{display:grid;gap:9px;margin-bottom:16px}
.def{display:grid;grid-template-columns:190px 1fr;gap:12px;font-size:12.5px}
.def b{color:#cfe0f0;font-weight:600}
.def span{color:#8296aa}
.srcs{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:14px}
.srcs a{font-size:12px;padding:6px 11px;border:1px solid #1b2634;border-radius:7px;
 background:#0a0f16;text-decoration:none;color:#8fb4cc}
.srcs a:hover{border-color:#3d7f9e;color:#9fe2ff}
.warn{font-size:12.5px;color:#c9954f;border-left:2px solid #453824;padding-left:13px}

#none{display:none;padding:60px 0;text-align:center;color:#4a5c6d}
#none.show{display:block}
footer{border-top:1px solid #111a24;background:#070a0e;padding:16px 0;font-size:11.5px;color:#54657a;line-height:1.6}
footer b{color:#9fb3c8}
@media(max-width:560px){.cols{grid-template-columns:1fr}.ship{grid-template-columns:88px 1fr}
 .pic,.sil,.noimg{width:88px;height:52px}.def{grid-template-columns:1fr;gap:2px}#top span{display:none}}
"""

JS=r"""
const S=DATA.ships, PLACE=DATA.place, q=document.getElementById('q'), out=document.getElementById('list');
const filt={t:'',career:null,buy:false};
let cur='USD', rates={USD:1}, sym={USD:'$',EUR:'€',GBP:'£',CAD:'C$',AUD:'A$',JPY:'¥'};
const fmt=n=>n==null?null:n.toLocaleString('en-US');
const esc=x=>(x==null?'':String(x)).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const money=u=>{const r=rates[cur]; if(!r) return '$'+fmt(u);
  const v=u*r; return (sym[cur]||'')+ (cur==='JPY'? Math.round(v).toLocaleString('en-US') : v.toLocaleString('en-US',{maximumFractionDigits:0}));};

function shopLine(s){
  if(!s.a) return '';
  if(s.dp){
    const e=Object.entries(s.dp).sort((a,b)=>a[1]-b[1]);
    const p=PLACE[e[0][0]]?` <s>&middot; ${esc(PLACE[e[0][0]])}</s>`:'';
    let t=`at <b>${esc(e[0][0])}</b>${p}`;
    if(e.length>1){const d=e[e.length-1][1]-e[0][1];
      t += d>0 ? ` &middot; <u>+${fmt(d)} at ${esc(e[e.length-1][0])}</u>` : ` &middot; same at ${e.length} shops`;}
    return t;
  }
  if(s.dl.length){
    const p=PLACE[s.dl[0]]?` <s>&middot; ${esc(PLACE[s.dl[0]])}</s>`:'';
    return s.dl.length===1?`at <b>${esc(s.dl[0])}</b>${p}`
      :`at <b>${esc(s.dl[0])}</b>${p} &middot; <s>${s.dl.length} shops</s>`;
  }
  return '';
}
function card(s){
  const pic = s.img ? `<img class="pic" loading="lazy" alt="" src="${s.img}">`
    : s.d ? `<svg class="sil" viewBox="0 0 ${s.w} ${s.h}" preserveAspectRatio="xMidYMid meet"><path d="${s.d}"/></svg>`
    : `<div class="noimg">no image</div>`;
  const pill=s.st==='purchasable'?'<span class="pill p-buy">in game</span>':'<span class="pill p-pl">pledge</span>';
  const price=s.a?`<span class="auec mono">${fmt(s.a)}<small>aUEC</small></span>`:`<span class="none">not sold in game</span>`;
  const usd=s.u?`<span class="usd mono">${money(s.u)}</span>`:'';
  const at=shopLine(s);
  const href = s.hull ? 'loadout.html#'+encodeURIComponent(s.hull) : (s.url||'');
  const tag  = href ? 'a' : 'div';
  const attr = href ? ` href="${esc(href)}"${s.hull?'':' target="_blank" rel="noopener"'}` : '';
  return `<${tag} class="ship${href?'':' dead'}" data-n="${esc(s.n)}"${attr}><div>${pic}</div><div class="body">
    <div class="hd"><span class="nm">${esc(s.n)}</span>${pill}</div>
    <div class="sub">${esc(s.r||s.c)||'&mdash;'}</div>
    <div class="spec"><span>${s.L?s.L+' m':'&mdash;'}</span><span>${s.cr?'crew '+s.cr:'&mdash;'}</span><span>${s.cg!=null?s.cg+' SCU':'&mdash;'}</span></div>
    <div class="pr">${price}${usd}</div>
    <div class="at">${at||'&mdash;'}</div>
    <div class="spacer"></div>
    ${s.ed?`<div class="ed">${s.ed.map(e=>`<span class="edn">${esc(e.name)}</span>${e.usd?`<span class="edp mono">${money(e.usd)}</span>`:''}`).join('')}</div>`:''}
    <div class="note">${s.no?esc(s.no):''}</div></div></${tag}>`;
}
function match(s){
  if(filt.t){const t=filt.t.toLowerCase();
    if(s.ed&&s.ed.some(e=>(s.n+' '+e.name).toLowerCase().includes(t)||e.name.toLowerCase().includes(t)))return true;
    const hay=[s.n,s.m,s.r,s.c,...(s.dl||[]),...(s.pl||[])].join(' ').toLowerCase();
    if(!hay.includes(t))return false;}
  if(filt.career&&s.c!==filt.career)return false;
  if(filt.buy&&!(s.a&&s.dl.length))return false;
  return true;
}
function render(){
  const hits=S.filter(match), by=new Map();
  for(const s of hits){ if(!by.has(s.m))by.set(s.m,[]); by.get(s.m).push(s); }
  const coll=new Intl.Collator('en',{numeric:true,sensitivity:'base'});
  const order=[...by.keys()].sort((a,b)=>coll.compare(a,b));
  let h='';
  for(const k of order){
    const g=by.get(k).sort((a,b)=>coll.compare(a.n,b.n));
    const ig=g.filter(s=>s.a&&s.dl.length).length;
    h+=`<div class="grp"><h2>${esc(k)}</h2><em>${g.length} ship${g.length>1?'s':''} &middot; ${ig} buyable in game</em></div>
        <div class="cols">${g.map(card).join('')}</div>`;
  }
  out.innerHTML=h;
  document.getElementById('cnt').textContent=hits.length;
  document.getElementById('none').classList.toggle('show',hits.length===0);
}
/* ---------------------------------------------------------------------
   THE SUGGESTION LIST.
   Sleven: the old page's search "allowed you to search for multiple
   different categories and also help predict what you're trying to type
   to help newer people out."  The old page did neither - it matched a
   substring of the name or role and showed a count.  So this is built,
   not copied.
   It indexes five kinds of thing and says which kind each hit is, so a
   new player typing "lor" learns Lorville is a place rather than
   wondering why a ship did not come up.
   --------------------------------------------------------------------- */
const IDX=(()=>{
  const add=(m,k,v)=>{ if(!k) return; const kk=k.trim(); if(!kk) return;
                       if(!m.has(kk)) m.set(kk,v); };
  const ship=new Map(), maker=new Map(), job=new Map(), shop=new Map(), place=new Map();
  for(const s of S){
    add(ship,s.n,s.n); add(maker,s.m,s.m); add(job,s.r,s.r); add(job,s.c,s.c);
    for(const d of (s.dl||[])) add(shop,d,d);
    for(const p of (s.pl||[])) add(place,p,p);
    for(const e of (s.ed||[])) add(ship,s.n+' '+e.name,s.n);
  }
  const kinds=[['ship',ship],['maker',maker],['job',job],['shop',shop],['place',place]];
  return kinds.map(([kind,m])=>({kind,items:[...m.keys()].sort()}));
})();

const sug=document.getElementById('sug');
/* Counted off S itself so a fact can never disagree with the cards below it. */
(function(){
  const uniq=(f)=>{const t=new Set(); for(const s of S){const v=f(s); if(Array.isArray(v)){for(const x of v) if(x) t.add(x);} else if(v) t.add(v);} return t.size;};
  const n=(x)=>x.toLocaleString('en-US');
  const rows=[
    ['ships tracked',      n(S.length), true],
    ['with a pledge price',n(S.filter(s=>s.u!=null).length), false],
    ['buyable in game',    n(S.filter(s=>s.a!=null||(s.dl&&s.dl.length)).length), false],
    ['manufacturers',      n(uniq(s=>s.m)), false],
    ['ship dealers',       n(uniq(s=>s.dl)), false],
    ['jobs covered',       n(uniq(s=>[s.c,s.r])), false],
  ];
  document.getElementById('facts').innerHTML = rows.map(([lab,val,hi])=>
    `<div class="fact${hi?' hi':''}"><b>${val}</b><span>${lab}</span></div>`).join('');
})();

let sugItems=[], sugAt=-1;

function buildSug(){
  const t=q.value.trim().toLowerCase();
  sugItems=[]; sugAt=-1;
  if(t.length<1){ sug.classList.remove('on'); sug.innerHTML=''; return; }
  for(const {kind,items} of IDX){
    /* a name that STARTS with what was typed is what the person meant;
       a name that merely contains it comes after. */
    const starts=[], has=[];
    for(const it of items){
      const l=it.toLowerCase();
      if(l.startsWith(t)) starts.push(it);
      else if(l.includes(t)) has.push(it);
    }
    for(const it of starts.concat(has).slice(0,6)) sugItems.push({kind,text:it});
  }
  sugItems=sugItems.slice(0,12);
  if(!sugItems.length){ sug.classList.remove('on'); sug.innerHTML=''; return; }
  sug.innerHTML=sugItems.map((s,i)=>
    `<div class="sg" data-i="${i}"><span class="sgk k-${s.kind}">${s.kind}</span>${esc(s.text)}</div>`).join('');
  sug.classList.add('on');
}
let ghostFull='';
function ghost(){
  const v=q.value, gt=document.getElementById('gtyped'), gr=document.getElementById('grest');
  gt.textContent=v; gr.textContent=''; ghostFull='';
  if(!v.trim()||!sugItems.length) return;
  /* only complete when the best hit actually STARTS with what was typed -
     completing "min" to "Starfarer Gemini" would be a lie about what the
     person is typing, even though it is a real hit. */
  const best=sugItems.find(s=>s.text.toLowerCase().startsWith(v.toLowerCase()));
  if(best && best.text.length>v.length){ gr.textContent=best.text.slice(v.length); ghostFull=best.text; }
}
function acceptGhost(){
  if(!ghostFull) return false;
  /* take the index's own spelling, not the person's - "star" + Tab is
     "Starfarer", not "starfarer". */
  q.value=ghostFull; filt.t=q.value.trim();
  sug.classList.remove('on');
  buildSug(); ghost(); render(); return true;
}
function pick(i){
  if(i<0||i>=sugItems.length) return;
  q.value=sugItems[i].text; filt.t=q.value; sug.classList.remove('on'); ghost(); render();
}
sug.addEventListener('mousedown',e=>{const d=e.target.closest('.sg'); if(d){e.preventDefault(); pick(+d.dataset.i);} });
q.addEventListener('input',()=>{filt.t=q.value.trim();buildSug();ghost();render();});
q.addEventListener('blur',()=>setTimeout(()=>sug.classList.remove('on'),120));
q.addEventListener('focus',buildSug);
q.addEventListener('keydown',e=>{
  if(e.key==='Escape'){q.value='';filt.t='';sug.classList.remove('on');ghost();render();return;}
  if(e.key==='Tab'||(e.key==='ArrowRight'&&q.selectionStart===q.value.length)){
    if(acceptGhost()){e.preventDefault();return;}
  }
  if(!sug.classList.contains('on')) return;
  if(e.key==='ArrowDown'||e.key==='ArrowUp'){
    e.preventDefault();
    sugAt=(sugAt+(e.key==='ArrowDown'?1:-1)+sugItems.length)%sugItems.length;
    [...sug.children].forEach((c,i)=>c.classList.toggle('at',i===sugAt));
    return;
  }
  if(e.key==='Enter'&&sugAt>=0){e.preventDefault(); pick(sugAt);}
});
document.querySelectorAll('.chip[data-career]').forEach(c=>c.onclick=()=>{
  const on=filt.career===c.dataset.career;
  document.querySelectorAll('.chip[data-career]').forEach(x=>x.classList.remove('on'));
  filt.career=on?null:c.dataset.career; if(!on)c.classList.add('on'); render();});
const b=document.getElementById('buy');
b.onclick=()=>{filt.buy=!filt.buy;b.classList.toggle('on',filt.buy);render();};
/* the card IS the link now - see card(). no click handler, so middle-click
   and open-in-new-tab work, which a JS handler quietly breaks. */

/* tabs */
document.querySelectorAll('.tab').forEach(t=>t.onclick=()=>{
  document.querySelectorAll('.tab').forEach(x=>x.classList.remove('on')); t.classList.add('on');
  document.querySelectorAll('.view').forEach(v=>v.classList.remove('on'));
  document.getElementById('v-'+t.dataset.v).classList.add('on');
  const shipOnly=t.dataset.v==='ships';
  document.getElementById('find').style.display=shipOnly?'':'none';
  document.getElementById('chips').style.display=shipOnly?'':'none';
});

/* currency - real rates on the live page, honest fallback offline */
const sel=document.getElementById('cur');
sel.onchange=()=>{cur=sel.value;render();};
fetch('https://open.er-api.com/v6/latest/USD').then(r=>r.json()).then(j=>{
  if(j&&j.rates){rates=Object.assign({USD:1},j.rates);document.getElementById('ratenote').textContent='live rates';}
}).catch(()=>{
  document.getElementById('ratenote').textContent='USD only — live rates need the internet';
  sel.disabled=true;
});

/* the two reference tabs, built from the current front page's own data */
document.getElementById('v-dev').innerHTML =
 `<div class="panel"><h2>Development Progress</h2>
  <div class="lead">CitizenCon (the big annual in-person fan event CIG normally holds in October/November) is NOT happening in 2026 &mdash; multiple community sources confirm it was called off for this year. This does not affect the Intergalactic Aerospace Expo (IAE), which is a separate in-game/sale event and is still expected in November 2026 per the community roadmap. CIG has not tied the Kraken's release to CitizenCon, so its absence this year does not change the Kraken estimate.</div>`
 + DATA.dev.map(r=>`<div class="item"><h3>${esc(r[0])}</h3>
     <div class="meta">${esc(r[1])} &middot; <b>${esc(r[2])}</b> &middot; ${esc(r[3])}</div>
     <p>${esc(r[4])}</p></div>`).join('') + `</div>`;

document.getElementById('v-cal').innerHTML =
 `<div class="panel"><h2>Sale Calendar</h2>
  <div class="lead">Recurring annual event pattern &mdash; general, not ship-specific.</div>`
 + DATA.cal.map(r=>`<div class="item"><h3>${esc(r[0])}</h3>
     <div class="meta"><b>${esc(r[1])}</b></div><p>${esc(r[2])}</p></div>`).join('') + `</div>`;

render(); q.focus();
"""

chips=''.join(f'<button class="chip" data-career="{html.escape(c)}">{html.escape(c)}</button>' for c in careers)
CURS=''.join(f'<option value="{c}">{c}</option>' for c in ['USD','EUR','GBP','CAD','AUD','JPY'])

doc=f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Citizen Compass &mdash; know where to buy, before you fly</title>
<style>{CSS}</style></head><body>
<section id="mast"><div class="wrap">
 <h1 id="brand">Citizen <em>Compass</em></h1>
 <p id="tag">Know where to buy, before you fly.</p>
 <div id="facts"></div>
</div></section>
<header><div class="wrap">
 <div id="top"><b>Citizen Compass</b><span>know where to buy, before you fly</span>
   <span id="ver">v0.4.0 &middot; <b id="cnt" style="color:#9fb3c8">0</b> ships</span></div>
 <div id="patch">
   <span class="dot"><i></i>Live <b class="mono" style="color:#9fb3c8">4.10.0</b> &ldquo;Siege of Orison&rdquo;</span>
   <span class="dot ptu"><i></i>PTU &mdash;</span>
   <span>Ship data compiled <b class="mono" style="color:#9fb3c8">2026-07-30</b></span>
   <span id="ratenote" style="margin-left:auto"></span>
 </div>
 <div id="tabs">
   <button class="tab on" data-v="ships">Ships</button>
   <button class="tab" data-v="dev">Development Progress</button>
   <button class="tab" data-v="cal">Sale Calendar</button>
   <button class="tab" data-v="legend">Legend &amp; Sources</button>
 </div>
 <div id="find"><div id="ghost" aria-hidden="true"><span id="gtyped"></span><span id="grest"></span></div><input id="q" placeholder="Search a ship, maker, job, shop or place &mdash; Vulture, Drake, mining, Lorville&hellip;" autocomplete="off" spellcheck="false"><div id="sug"></div></div>
 <div id="chips"><button class="chip buy" id="buy">Buyable in game</button>{chips}
   <select id="cur" title="pledge prices in">{CURS}</select></div>
</div></header>

<main><div class="wrap">
 <div class="view on" id="v-ships"><div id="list"></div><div id="none">nothing matches that</div></div>
 <div class="view" id="v-dev"></div>
 <div class="view" id="v-cal"></div>
 <div class="view" id="v-legend"><div class="panel">
   <h2>Legend &amp; Sources</h2>
   <div class="defs">
     <div class="def"><b>In game</b><span>Buyable now with aUEC at a listed dealer.</span></div>
     <div class="def"><b>Pledge only</b><span>Real money only, not yet buyable with aUEC.</span></div>
     <div class="def"><b>Flyable, no in-game dealer</b><span>Real and flyable now, just no aUEC dealer sells it yet.</span></div>
     <div class="def"><b>Not yet flyable</b><span>Still in development, concept or pledge-only for now.</span></div>
     <div class="def"><b>no image</b><span>We hold no picture of this ship. We would rather show a gap than the wrong hull.</span></div>
   </div>
   <h2 style="margin-top:22px">Where the numbers come from</h2>
   <div class="srcs">
     <a href="https://starcitizen.tools" target="_blank" rel="noopener">starcitizen.tools &mdash; ship and purchasing data</a>
     <a href="https://finder.cstone.space" target="_blank" rel="noopener">CStone &mdash; live in-game dealer verification</a>
     <a href="https://uexcorp.space" target="_blank" rel="noopener">UEX Corp &mdash; price cross-check</a>
     <a href="https://robertsspaceindustries.com/pledge/ships" target="_blank" rel="noopener">RSI Pledge Store &mdash; official buy links</a>
   </div>
   <h2 style="margin-top:22px">Better tools for other jobs</h2>
   <div class="srcs">
     <a href="https://www.erkul.games" target="_blank" rel="noopener">Erkul &mdash; loadouts and DPS</a>
     <a href="https://fleetyards.net" target="_blank" rel="noopener">Fleetyards &mdash; fleet tracking and images</a>
     <a href="https://www.spviewer.eu" target="_blank" rel="noopener">SPViewer &mdash; ship stat comparison</a>
   </div>
   <div class="warn" style="margin-top:20px">Known conflict, shown rather than resolved: the Aegis Idris-P reads $1,900 on the store today against $1,500 in an older snapshot. Both are recorded and neither is picked for you.</div>
 </div></div>
</div></main>

<footer><div class="wrap">
  <div>aUEC prices are community-reported and dated &mdash; <b>not verified in game</b>. Every figure carries the patch it was checked against, and a blank means we do not know rather than a guess.</div>
  <div style="margin-top:7px">Click any ship for the 3D model, its hardpoints in CIG's own positions, and the full loadout.</div>
  <div style="margin-top:7px">This is an unofficial Star Citizen fan site. Ship imagery &copy; Cloud Imperium Games. Star Citizen&reg;, Roberts Space Industries&reg; and Cloud Imperium&reg; are registered trademarks of Cloud Imperium Rights LLC.</div>
</div></footer>
<script>const DATA={payload};</script><script>{JS}</script></body></html>"""
open(OUT,'w',encoding='utf-8').write(doc)

# ---------------------------------------------------------------------------
# The same page, written as a build source so it can be published beside the
# current front page. Sleven, 2026-09-06: put it up beside, then rewire properly.
#
# The markers are emitted HERE rather than hand-added to the generated file,
# because a marker added by hand is lost the next time this script runs, and it
# would be lost silently. build_deploy.py injects the glossary at the marker and
# the trademark/contact strip on its own.
SRC_OUT=os.path.expanduser('~/mnt/citizen-compass/testing/_src/next.src.html')
IMG_DIR=os.path.expanduser('~/mnt/citizen-compass/testing/_src/images')

# ---------------------------------------------------------------------------
# THE BUILD SOURCE CARRIES ITS PICTURES AS FILES, NOT AS TEXT.
#
# Code measured it: 246 inlined data: URIs are 2,376,716 bytes, 95.6% of the
# page. A visitor waits for all of it before anything paints, and none of it can
# be cached between visits.
#
# This is done HERE rather than stripped out later in build_deploy.py, and that
# was Code's own question. If the generator kept emitting a 2.4 MB blob and the
# build quietly undid it every time, that is two transformations of one artifact
# by two owners - rule 14, and exactly the kind of thing that drifts. So the
# page is authored lean and nothing has to undo anything.
#
# `images/` is ALREADY an allowed directory in _deploy (check_deploy_clean.py
# DEFAULT_ALLOWED_DIRS), so no guard has to be widened to ship these.
#
# Files are named by the SHA-256 of their own bytes, so a picture used by two
# ships is written once and referenced twice, and a picture that has not changed
# keeps its name across rebuilds.
# ---------------------------------------------------------------------------
import base64, hashlib, shutil
_MIME_EXT = {'image/webp':'.webp','image/png':'.png','image/jpeg':'.jpg','image/gif':'.gif'}

# NOT wiped. Rule 1 - nothing is deleted. Files are named by the hash of their
# own bytes, so a rebuild rewrites the ones it still uses and simply leaves any
# it no longer references. Those are REPORTED at the end rather than removed,
# because a build that quietly deletes is a build that can quietly delete the
# wrong thing.
os.makedirs(IMG_DIR, exist_ok=True)
_pre = set(os.listdir(IMG_DIR))

_written = {}
def _extract(m):
    mime, b64 = m.group(1), m.group(2)
    ext = _MIME_EXT.get(mime)
    if ext is None:
        return m.group(0)           # unknown type stays inline rather than being guessed at
    try:
        raw = base64.b64decode(b64)
    except Exception:
        return m.group(0)           # refuse rather than write a corrupt file
    h = hashlib.sha256(raw).hexdigest()[:16]
    name = h + ext
    if name not in _written:
        with open(os.path.join(IMG_DIR, name), 'wb') as fh:
            fh.write(raw)
        _written[name] = len(raw)
    return 'images/' + name

_src = doc.replace('</head>', '<!-- CC_GLOSSARY -->\n</head>', 1)
if '<!-- CC_GLOSSARY -->' not in _src:
    raise SystemExit('the glossary marker was not placed. next.src.html not written.')

_before = len(_src)
_src = re.sub(r'data:(image/[a-z+]+);base64,([A-Za-z0-9+/=]+)', _extract, _src)

if 'data:image/' in _src:
    left = _src.count('data:image/')
    print('NOTE: %d image URI(s) left inline - unknown mime or undecodable' % left)

open(SRC_OUT,'w',encoding='utf-8',newline='').write(_src)
print('wrote build source %s' % SRC_OUT)
print('  page   %d -> %d bytes  (%.1f%% smaller)'
      % (_before, len(_src), 100.0*(_before-len(_src))/_before))
print('  images %d files, %d bytes, in %s' % (len(_written), sum(_written.values()), IMG_DIR))
_stale = sorted(_pre - set(_written))
if _stale:
    print('  %d image(s) no longer referenced, LEFT IN PLACE (rule 1): %s'
          % (len(_stale), ', '.join(_stale[:4]) + (' ...' if len(_stale) > 4 else '')))

print("wrote",os.path.getsize(OUT))
