/* ================================================================
   sc_export2.js — build AND read a Star Citizen mapping file.

   This replaces the first exporter. Everything here was measured
   against two real exports produced by the game itself
   (test1CR.xml, test3cr.xml — same machine, two VKB sticks),
   not reconstructed from memory.

   WHAT THE REAL FILES PROVED, and what this does about it
   -------------------------------------------------------
   1. A joystick needs its own <options> line carrying a DirectInput
      Product GUID. The old exporter omitted it. Emitted here.
   2. The GUID is {<PID><VID>-0000-0000-0000-504944564944}, upper
      case, 4 hex digits each; the tail is ASCII "PIDVID". Chrome's
      Gamepad id string carries the same VID and PID, so the page can
      build it with no user input. Reconstructed both sticks' GUIDs
      from the browser strings and they matched the file exactly.
   3. "prefix_" followed by a SPACE is an explicit unbind. 202 of 247
      rebinds in the first real file are that shape. A tool that only
      writes positive bindings cannot clear a game default.
   4. mo1_ is a real device prefix (mouse axes). famOf() must know it
      or those inputs are silently refused.
   5. One action may carry several <rebind> children, one per device.
   6. activationMode is a real attribute on a rebind.
   7. Buttons reach at least 29. No ceiling is imposed.
   8. One input may legitimately drive several actions (js1_x is both
      roll and lateral strafe on a HOSAS). Allowed; the caller is told
      so it can warn rather than block.

   ORDERING, measured — this is what makes byte-exact output possible
   -------------------------------------------------------
   - actionmaps appear in the GAME's canonical order, which is the
     first-seen order of keybinds_site.json, filtered to the maps
     present. Verified against both files: exact.
   - actions inside an actionmap are sorted ASCII-ascending by name.
     Verified: all 57 actionmaps across both files, exact.
   - rebinds inside an action follow device order
     keyboard, mouse, joystick, gamepad. Verified on all 39
     multi-rebind actions across both files.
   - categories are first-seen in emitted actionmap order, looked up
     from actionmap_categories.json. Verified: both files, exact.
   - CRLF line endings, one space of indent per level, no XML
     declaration, <modifiers /> with a space.

   STILL NOT PROVEN, and treated as such
   -------------------------------------------------------
   - Modifier combinations. Zero inputs in either file contain "+".
     Still REFUSED.
   - Whether the Product NAME text matters or only the GUID. The file
     says " VKBsim Gladiator EVO L    " with irregular padding;
     Chrome says "VKB Gladiator NXT EVO L". Different strings, same
     device. When we synthesise a name we cannot match the padding,
     so build() reports nameSynthesised so the UI can say so.
   - No file WE generated has ever been loaded by the game. That test
     is still the only one that settles it.

   ES5, no dependencies, works in a browser or in node.
   ================================================================ */
var SCX = (function(){

  var KB_GUID = "Keyboard  {6F1D2B61-D5A0-11CF-BFC7-444553540000}";
  var GUID_TAIL = "0000-0000-0000-504944564944";   /* ASCII "PIDVID" */

  /* Device families in the order the game writes them. Used for the
     <devices> block, the <options> lines, and rebind order inside an
     action. All three were measured, not assumed. */
  var FAM_ORDER = ["keyboard","mouse","joystick","gamepad"];
  var PREFIX = {kb:"keyboard", mo:"mouse", js:"joystick", gp:"gamepad"};
  var FAMPREFIX = {keyboard:"kb", mouse:"mo", joystick:"js", gamepad:"gp"};

  function esc(s){
    return String(s).replace(/&/g,"&amp;").replace(/</g,"&lt;")
                    .replace(/>/g,"&gt;").replace(/"/g,"&quot;");
  }

  function safeName(n){
    n = String(n||"").replace(/[^A-Za-z0-9 _-]/g,"").replace(/\s+/g," ").trim();
    return n.slice(0,48) || "custom";
  }

  /* ---- device identity ---------------------------------------- */

  /* {<PID><VID>-0000-0000-0000-504944564944}. Both halves are the
     4-hex-digit values Chrome reports, upper case. */
  function guidFromVidPid(vid, pid){
    var v = String(vid||"").replace(/[^0-9a-fA-F]/g,"").toUpperCase();
    var p = String(pid||"").replace(/[^0-9a-fA-F]/g,"").toUpperCase();
    if(v.length!==4 || p.length!==4) return null;
    return "{" + p + v + "-" + GUID_TAIL + "}";
  }

  /* Chrome: "VKB Gladiator NXT EVO L (Vendor: 231d Product: 0201)".
     Firefox uses "231d-0201-Name". Both handled; anything else
     returns null rather than a guess. */
  function parseGamepadId(id){
    id = String(id||"");
    var m = /\(?\s*Vendor:?\s*([0-9a-fA-F]{4})\s+Product:?\s*([0-9a-fA-F]{4})\s*\)?/.exec(id);
    if(m) return {vid:m[1], pid:m[2], name:id.slice(0, m.index).trim()};
    m = /^([0-9a-fA-F]{4})-([0-9a-fA-F]{4})-(.*)$/.exec(id);
    if(m) return {vid:m[1], pid:m[2], name:m[3].trim()};
    return null;
  }

  /* The Product attribute for a stick. The GUID half is proven. The
     name half is the device's own DirectInput string, which the
     browser does not expose — what we have is a different string for
     the same device. We mimic the observed shape and say so. */
  function productString(name, guid){
    return " " + String(name||"Joystick").replace(/[<>"&]/g,"") + "    " + guid;
  }

  /* ---- inputs -------------------------------------------------- */

  function famOf(input){
    var m = /^([a-z]+)([0-9]+)_/.exec(String(input));
    if(!m || !PREFIX[m[1]]) return null;
    return {fam:PREFIX[m[1]], prefix:m[1], inst:parseInt(m[2],10)};
  }

  /* An explicit unbind is the prefix, an underscore and a single
     space: "kb1_ ". It means "clear the game default", and without
     it the default silently stays. */
  function isUnbind(input){ return /^[a-z]+[0-9]+_ $/.test(String(input)); }

  function unbindFor(prefix, inst){ return prefix + (inst||1) + "_ "; }

  function reject(b){
    if(!b || !b.map || !b.action || typeof b.input !== "string" || b.input === "")
      return "missing actionmap, action or input";
    if(/[+]/.test(b.input))
      return "modifier combinations are not verified — neither real export "+
             "contains one, so the notation would be a guess";
    if(/^ms[0-9]+_/.test(b.input))
      return "mouse buttons use the keyboard prefix (kb1_mouse4); mouse AXES "+
             "use mo1_. ms1_ appears in no real file";
    if(!famOf(b.input))
      return "input '"+b.input+"' has no recognised device prefix "+
             "(expected kb1_, mo1_, js1_, gp1_)";
    if(b.activationMode!=null && !/^[a-z_]+$/.test(String(b.activationMode)))
      return "activationMode '"+b.activationMode+"' is not a plain name";
    return null;
  }

  /* ---- reading a file the game wrote --------------------------- */

  /* Returns the whole profile, including the things the first
     importer threw away: every rebind (not just the first), the
     device declarations, and activationMode. */
  function parse(xmlText, DOMParserImpl){
    var DP = DOMParserImpl || (typeof DOMParser!=="undefined" ? DOMParser : null);
    if(!DP) throw new Error("no DOMParser available");
    var doc = new DP().parseFromString(String(xmlText), "application/xml");
    if(doc.getElementsByTagName("parsererror").length) throw new Error("not valid XML");
    var root = doc.documentElement;
    if(!root || root.nodeName!=="ActionMaps") throw new Error("not a Star Citizen mapping file (root is not <ActionMaps>)");

    var out = {
      profileName: root.getAttribute("profileName") || "",
      version: root.getAttribute("version"),
      optionsVersion: root.getAttribute("optionsVersion"),
      rebindVersion: root.getAttribute("rebindVersion"),
      devices: [],       /* [{type,instance,product}] from <options> */
      declared: [],      /* [{type,instance}] from <devices> */
      binds: []          /* [{map,action,input,activationMode}] in file order */
    };

    var hdr = root.getElementsByTagName("CustomisationUIHeader")[0];
    if(hdr){
      var dv = hdr.getElementsByTagName("devices")[0];
      if(dv) for(var i=0;i<dv.childNodes.length;i++){
        var c = dv.childNodes[i];
        if(c.nodeType===1) out.declared.push({type:c.nodeName, instance:parseInt(c.getAttribute("instance")||"1",10)});
      }
    }
    var opts = root.getElementsByTagName("options");
    for(var o=0;o<opts.length;o++){
      if(opts[o].parentNode!==root) continue;
      out.devices.push({
        type: opts[o].getAttribute("type"),
        instance: parseInt(opts[o].getAttribute("instance")||"1",10),
        product: opts[o].getAttribute("Product") || ""
      });
    }
    var ams = root.getElementsByTagName("actionmap");
    for(var a=0;a<ams.length;a++){
      var mname = ams[a].getAttribute("name");
      var acts = ams[a].getElementsByTagName("action");
      for(var b=0;b<acts.length;b++){
        var aname = acts[b].getAttribute("name");
        var rbs = acts[b].getElementsByTagName("rebind");
        for(var r=0;r<rbs.length;r++){
          out.binds.push({
            map: mname, action: aname,
            input: rbs[r].getAttribute("input"),
            activationMode: rbs[r].getAttribute("activationMode") || null
          });
        }
      }
    }
    return out;
  }

  /* ---- duplicate detection ------------------------------------- */

  /* One input on several actions is legal and sometimes the point.
     We report it; the caller warns, never blocks. Unbinds are
     excluded — every device shares the same unbind token. */
  function duplicates(bindings){
    var byInput = {}, out = [];
    bindings.forEach(function(b){
      if(!b || typeof b.input!=="string" || isUnbind(b.input)) return;
      (byInput[b.input] = byInput[b.input] || []).push(b);
    });
    Object.keys(byInput).forEach(function(k){
      if(byInput[k].length>1) out.push({input:k, on:byInput[k]});
    });
    return out;
  }

  /* ---- writing ------------------------------------------------- */

  /* opts:
       profileName    string
       categories     {actionmap: "@ui_..."}   from actionmap_categories.json
       mapOrder       [actionmap]              the game's canonical order
       devices        [{type,instance,product}]  verbatim, when round-tripping
       joysticks      [{instance,vid,pid,name}]  when building from live pads
       eol            "\r\n" (default) or "\n"
  */
  function build(bindings, opts){
    opts = opts || {};
    var name  = safeName(opts.profileName || "citizen-compass");
    var cats  = opts.categories || {};
    var order0 = opts.mapOrder || [];
    var EOL   = opts.eol || "\r\n";

    var good=[], bad=[], i, r;
    for(i=0;i<bindings.length;i++){
      r = reject(bindings[i]);
      if(r) bad.push({binding:bindings[i], why:r}); else good.push(bindings[i]);
    }

    /* group: map -> action -> [rebind] */
    var byMap = {}, mapsSeen = [];
    good.forEach(function(b){
      if(!byMap[b.map]){ byMap[b.map] = {}; mapsSeen.push(b.map); }
      (byMap[b.map][b.action] = byMap[b.map][b.action] || []).push(b);
    });

    /* actionmap order: canonical first, then anything the canonical
       list does not know about, appended in first-seen order rather
       than dropped. An unknown map is still the player's binding. */
    var emitted = [], unknown = [];
    order0.forEach(function(m){ if(byMap[m]) emitted.push(m); });
    mapsSeen.forEach(function(m){ if(emitted.indexOf(m)<0){ emitted.push(m); unknown.push(m); } });

    /* devices referenced */
    var fams={}, inst={};
    good.forEach(function(b){
      var f = famOf(b.input);
      fams[f.fam]=true;
      inst[f.fam] = Math.max(inst[f.fam]||1, f.inst);
    });
    if(fams.keyboard) fams.mouse = true;   /* the game declares both together */

    /* <options> lines. Round-tripping supplies them verbatim; building
       from live pads synthesises them from VID/PID. */
    var optLines = [], nameSynthesised = false, missingGuid = [];
    if(opts.devices && opts.devices.length){
      opts.devices.forEach(function(d){
        optLines.push({type:d.type, instance:d.instance, product:d.product});
      });
    } else {
      if(fams.keyboard) optLines.push({type:"keyboard", instance:1, product:KB_GUID});
      if(fams.joystick){
        var js = opts.joysticks || [];
        for(var n=1;n<=(inst.joystick||1);n++){
          var d = null;
          for(var k=0;k<js.length;k++) if(js[k].instance===n) d = js[k];
          var guid = d ? guidFromVidPid(d.vid, d.pid) : null;
          if(!guid){ missingGuid.push(n); continue; }
          nameSynthesised = true;
          optLines.push({type:"joystick", instance:n, product:productString(d.name, guid)});
        }
      }
    }

    /* categories, first-seen across the emitted maps */
    var seen={}, catList=[];
    emitted.forEach(function(m){
      var c = cats[m];
      if(c && !seen[c]){ seen[c]=true; catList.push(c); }
    });

    var x = [];
    x.push('<ActionMaps version="1" optionsVersion="2" rebindVersion="2" profileName="'+esc(name)+'">');
    x.push(' <CustomisationUIHeader label="'+esc(name)+'" description="" image="">');
    x.push('  <devices>');
    FAM_ORDER.forEach(function(f){
      if(!fams[f]) return;
      for(var n=1;n<=(inst[f]||1);n++) x.push('   <'+f+' instance="'+n+'"/>');
    });
    x.push('  </devices>');
    x.push('  <categories>');
    catList.forEach(function(c){ x.push('   <category label="'+esc(c)+'"/>'); });
    x.push('  </categories>');
    x.push(' </CustomisationUIHeader>');
    optLines.forEach(function(d){
      x.push(' <options type="'+esc(d.type)+'" instance="'+d.instance+'" Product="'+esc(d.product)+'"/>');
    });
    x.push(' <modifiers />');

    emitted.forEach(function(m){
      x.push(' <actionmap name="'+esc(m)+'">');
      var actions = Object.keys(byMap[m]).sort();      /* ASCII, as the game writes them */
      actions.forEach(function(a){
        var rbs = byMap[m][a].slice().sort(function(p,q){
          return FAM_ORDER.indexOf(famOf(p.input).fam) - FAM_ORDER.indexOf(famOf(q.input).fam);
        });
        x.push('  <action name="'+esc(a)+'">');
        rbs.forEach(function(b){
          x.push('   <rebind input="'+esc(b.input)+'"'+
                 (b.activationMode ? ' activationMode="'+esc(b.activationMode)+'"' : '')+'/>');
        });
        x.push('  </action>');
      });
      x.push(' </actionmap>');
    });
    x.push('</ActionMaps>');

    var dup = duplicates(good);
    var warn = [];
    if(missingGuid.length)
      warn.push("Joystick instance "+missingGuid.join(", ")+" has no VID/PID, so no "+
                "<options> line could be written for it and the game will not know "+
                "which stick those bindings belong to.");
    if(nameSynthesised)
      warn.push("The joystick Product NAME is synthesised from what the browser reports, "+
                "which is not the same string DirectInput gives the game. The GUID is exact. "+
                "Whether the name matters is untested.");
    if(dup.length)
      warn.push(dup.length+" input(s) drive more than one action. That is legal — a HOSAS "+
                "puts roll and lateral strafe on the same axis — but check it is deliberate.");
    if(bad.length)
      warn.push(bad.length+" binding(s) were refused and are NOT in this file.");
    warn.push("No file generated by this tool has ever been loaded by Star Citizen. "+
              "The format matches two real exports exactly; that is not the same as working.");

    return {
      xml: x.join(EOL)+EOL,
      filename: name.replace(/ /g,"_")+".xml",
      written: good.length,
      actions: emitted.reduce(function(n,m){ return n+Object.keys(byMap[m]).length; },0),
      maps: emitted.length,
      unknownMaps: unknown,
      refused: bad,
      duplicates: dup,
      warnings: warn,
      verified: false
    };
  }

  return {
    build:build, parse:parse, reject:reject, safeName:safeName,
    famOf:famOf, isUnbind:isUnbind, unbindFor:unbindFor,
    duplicates:duplicates, guidFromVidPid:guidFromVidPid,
    parseGamepadId:parseGamepadId, productString:productString,
    KB_GUID:KB_GUID, FAM_ORDER:FAM_ORDER, FAMPREFIX:FAMPREFIX
  };
})();

if(typeof module!=="undefined") module.exports = SCX;
