/* test_sc_export.js - every assertion has a negative control.
   A check that cannot fail is not a check. Rule 12. */
var SCX = require('./sc_export.js');
var fs = require('fs');
var cats = JSON.parse(fs.readFileSync(
  '../../data-layer/processed/actionmap_categories.json','utf8'));

var pass=0, fail=[];
function ck(c,m){ if(c) pass++; else fail.push(m); }

/* ---- 1. a plain keyboard export matches the proven shape ---- */
var r = SCX.build([
  {map:"spaceship_movement", action:"v_roll_left",  input:"kb1_z"},
  {map:"spaceship_movement", action:"v_roll_right", input:"kb1_c"},
  {map:"player",             action:"toggleAttachHelmet", input:"kb1_mouse4"}
], {profileName:"Citizen Compass Test", categories:cats});

ck(/^<ActionMaps version="1" optionsVersion="2" rebindVersion="2" profileName="Citizen Compass Test">/.test(r.xml),
   "root element does not match the proven header");
ck(r.xml.indexOf('<options type="keyboard" instance="1" Product="Keyboard  {6F1D2B61-D5A0-11CF-BFC7-444553540000}"/>')>-1,
   "keyboard options line missing or altered");
ck(r.xml.indexOf('<modifiers />')>-1, "modifiers element missing");
ck(r.xml.indexOf('</ActionMaps>')>-1, "root never closed");
ck(r.written===3, "expected 3 bindings written, got "+r.written);
ck(r.refused.length===0, "a valid binding was refused: "+JSON.stringify(r.refused));
ck(r.verified===true, "keyboard-only output should be marked verified");

/* actionmaps grouped, not repeated */
ck((r.xml.match(/<actionmap name="spaceship_movement">/g)||[]).length===1,
   "spaceship_movement emitted more than once - bindings not grouped");
ck(r.xml.indexOf('<category label="@ui_CCSpaceFlight"/>')>-1,
   "category not derived from the actionmap");
ck(r.xml.indexOf('<mouse instance="1"/>')>-1,
   "mouse device missing though a kb1_mouse binding is present");

/* ---- 2. the refusals actually refuse ---- */
ck(SCX.reject({map:"m",action:"a",input:"kb1_lctrl+kb1_k"})!==null,
   "a modifier combo was accepted - notation is unverified");
ck(SCX.reject({map:"m",action:"a",input:"ms1_mouse4"})!==null,
   "ms1_ prefix accepted - mouse must ride the keyboard prefix");
ck(SCX.reject({map:"m",action:"a",input:"wat_1"})!==null,
   "unknown device prefix accepted");
ck(SCX.reject({map:"m",action:"a",input:""})!==null, "empty input accepted");

var r2 = SCX.build([{map:"m",action:"a",input:"kb1_lctrl+kb1_k"}],{categories:cats});
ck(r2.written===0 && r2.refused.length===1,
   "a refused binding still reached the file");
ck(r2.xml.indexOf("lctrl+")===-1, "refused binding text leaked into the XML");

/* ---- 3. joystick output is emitted but never called verified ---- */
var r3 = SCX.build([{map:"spaceship_movement",action:"v_roll_left",input:"js1_button3"}],
                   {categories:cats});
ck(r3.written===1, "joystick binding was dropped");
ck(r3.verified===false, "joystick output must not be marked verified");
ck(r3.warnings.join(" ").indexOf("never been confirmed")>-1,
   "joystick file carries no honesty warning");
ck(r3.xml.indexOf('type="joystick"')===-1,
   "a joystick options line was invented");
ck(r3.xml.indexOf('<joystick instance="1"/>')>-1, "joystick device not declared");

/* ---- 4. injection and naming ---- */
var r4 = SCX.build([{map:'a"><evil/>',action:"a",input:"kb1_k"}],{profileName:'../../evil <x>'});
ck(r4.xml.indexOf("<evil/>")===-1, "XML injection through the actionmap name");
ck(r4.filename.indexOf("..")===-1 && r4.filename.indexOf("/")===-1,
   "profile name escaped into a path: "+r4.filename);

/* ---- NEGATIVE CONTROLS: these must NOT hold ---- */
var neg=[];
if(SCX.reject({map:"m",action:"a",input:"kb1_k"})!==null)
  neg.push("a plainly valid binding was refused - checker is broken");
if(r.xml.indexOf("<actionmap name=\"never_exists\">")>-1)
  neg.push("negative control passed - checker is asleep");
if(SCX.build([],{}).written!==0) neg.push("empty input produced bindings");

console.log("passed: "+pass+"   failed: "+fail.length);
fail.forEach(function(f){ console.log("  FAIL  "+f); });
neg.forEach(function(n){ console.log("  BROKEN CHECKER  "+n); });
process.exit(fail.length||neg.length ? 1 : 0);
