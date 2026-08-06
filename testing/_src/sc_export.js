/* ================================================================
   sc_export.js - build a Star Citizen mapping file the game will load.

   The schema below was read from Sleven's own two exports and his live
   profile. It is not reconstructed from memory. Anything NOT present in
   those exports is treated as unproven and is refused or flagged rather
   than invented, because a mapping file the game silently declines to
   load is worse than no file: nothing errors, the bindings just are not
   there and the player hunts for a reason.

   PROVEN, from real exports:
     - root <ActionMaps version="1" optionsVersion="2" rebindVersion="2">
     - a CustomisationUIHeader carrying devices and categories
     - <options type="keyboard" .../> with the standard Windows GUID
     - an export contains ONLY what changed, never the full 1,103 actions
     - mouse uses the KEYBOARD prefix: kb1_mouse4, never ms1_

   NOT PROVEN, and handled as such:
     - how a modifier combination is written. No export of his contains
       one. combos are REFUSED outright.
     - whether a joystick needs its DirectInput Product GUID in <options>
       or binds by instance order. Joystick output is EMITTED but reported
       as unverified, because refusing would block the entire feature on a
       test he cannot run right now. It is never described as working.

   ES5. Rule 15 does not apply - no file is opened here.
   ================================================================ */
var SCX = (function(){

  var KB_GUID = "Keyboard  {6F1D2B61-D5A0-11CF-BFC7-444553540000}";

  function esc(s){
    return String(s).replace(/&/g,"&amp;").replace(/</g,"&lt;")
                    .replace(/>/g,"&gt;").replace(/"/g,"&quot;");
  }

  /* A profile name goes into a filename and into XML. Anything that is not
     plainly safe in both is removed rather than escaped. */
  function safeName(n){
    n = String(n||"").replace(/[^A-Za-z0-9 _-]/g,"").replace(/\s+/g," ").trim();
    return n.slice(0,48) || "custom";
  }

  /* Which device family a binding belongs to, read from its prefix. */
  function famOf(input){
    var m = /^([a-z]+)([0-9]+)_/.exec(String(input));
    if(!m) return null;
    if(m[1]==="kb") return {fam:"keyboard", inst:parseInt(m[2],10)};
    if(m[1]==="js") return {fam:"joystick", inst:parseInt(m[2],10)};
    if(m[1]==="gp") return {fam:"gamepad",  inst:parseInt(m[2],10)};
    return null;
  }

  /* The refusals. Each returns a reason string, or null when the binding
     is acceptable. A binding that cannot be proven is not written. */
  function reject(b){
    if(!b || !b.map || !b.action || !b.input)
      return "missing actionmap, action or input";
    if(/[+]/.test(b.input))
      return "modifier combinations are not verified - no known export "+
             "contains one, so the notation would be a guess";
    if(/^ms[0-9]+_/.test(b.input))
      return "mouse uses the keyboard prefix (kb1_mouse4), not ms1_";
    if(!famOf(b.input))
      return "input '"+b.input+"' has no recognised device prefix "+
             "(expected kb1_, js1_, gp1_)";
    return null;
  }

  /* categories: map -> UICategory, supplied by the caller from
     actionmap_categories.json. Missing is normal - 12 of 50 have none. */
  function build(bindings, opts){
    opts = opts || {};
    var name = safeName(opts.profileName || "citizen-compass");
    var cats = opts.categories || {};

    var good = [], bad = [], i, r;
    for(i=0;i<bindings.length;i++){
      r = reject(bindings[i]);
      if(r) bad.push({binding:bindings[i], why:r});
      else  good.push(bindings[i]);
    }

    /* group by actionmap, preserving first-seen order */
    var order = [], byMap = {};
    good.forEach(function(b){
      if(!byMap[b.map]){ byMap[b.map]=[]; order.push(b.map); }
      byMap[b.map].push(b);
    });

    /* devices actually referenced */
    var fams = {}, instances = {};
    good.forEach(function(b){
      var f = famOf(b.input);
      fams[f.fam] = true;
      instances[f.fam] = Math.max(instances[f.fam]||1, f.inst);
    });
    if(fams.keyboard) fams.mouse = true;   /* mouse rides the keyboard device */

    var devLine = "";
    ["keyboard","mouse","joystick","gamepad"].forEach(function(f){
      if(fams[f]) devLine += '<'+f+' instance="'+(instances[f]||1)+'"/>';
    });

    var catSet = {}, catList = [];
    order.forEach(function(m){
      var c = cats[m];
      if(c && !catSet[c]){ catSet[c]=true; catList.push(c); }
    });

    var x = [];
    x.push('<ActionMaps version="1" optionsVersion="2" rebindVersion="2" profileName="'+esc(name)+'">');
    x.push(' <CustomisationUIHeader label="'+esc(name)+'" description="" image="">');
    x.push('  <devices>'+devLine+'</devices>');
    x.push('  <categories>'+catList.map(function(c){
              return '<category label="'+esc(c)+'"/>'; }).join('')+'</categories>');
    x.push(' </CustomisationUIHeader>');
    if(fams.keyboard)
      x.push(' <options type="keyboard" instance="1" Product="'+esc(KB_GUID)+'"/>');
    x.push(' <modifiers />');
    order.forEach(function(m){
      x.push(' <actionmap name="'+esc(m)+'">');
      byMap[m].forEach(function(b){
        x.push('  <action name="'+esc(b.action)+'"><rebind input="'+esc(b.input)+'"/></action>');
      });
      x.push(' </actionmap>');
    });
    x.push('</ActionMaps>');

    /* Everything the caller needs to tell the truth about this file. */
    var warn = [];
    if(fams.joystick)
      warn.push("Joystick bindings are included but the <options type=\"joystick\"> "+
                "line is omitted - it is not known whether Star Citizen needs the "+
                "stick's DirectInput Product GUID there or binds by instance order. "+
                "This file has never been confirmed to load with joystick bindings. "+
                "Load it once and say whether the bindings took.");
    if(bad.length)
      warn.push(bad.length+" binding(s) were refused and are NOT in this file.");

    return {
      xml: x.join("\n")+"\n",
      filename: name.replace(/ /g,"_")+".xml",
      written: good.length,
      refused: bad,
      warnings: warn,
      verified: !fams.joystick    /* keyboard-only output matches proven exports */
    };
  }

  return {build:build, reject:reject, safeName:safeName, KB_GUID:KB_GUID};
})();

if(typeof module!=="undefined") module.exports = SCX;
