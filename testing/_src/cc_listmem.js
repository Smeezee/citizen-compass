/* cc_listmem.js - GOING BACK GOES BACK.

   Sleven, 2026-08-23: "If I'm sitting at the very bottom of the page and I
   click the Cyclone TR, it takes me to the page. I wanna look at the other
   Cyclone - bam, right back to Avenger Stalker at the very top. Fix it."

   WHAT THIS REMEMBERS, AND WHY IT IS NOT JUST A SCROLL OFFSET. A person
   comparing four Cyclones has a search typed, a role picked, a column sorted
   and a row they were looking at. Restoring the offset alone drops them at
   pixel 4,300 of a list that is no longer filtered the way it was, which is a
   different wrong place rather than the right one. So the whole state travels
   together or none of it does.

   WHY sessionStorage. "A list you have never visited THIS SESSION opens at the
   top" is the order's own wording, and it is also the right lifetime: a scroll
   offset is about what somebody is doing now. Settings persist indefinitely
   (H1f-2); a position does not.

   WHY EVERY LIST DECLARES ITS OWN CAPTURE AND APPLY. The ship matrix, FIND's
   results and the keybind list keep their state in completely different
   places - a site-wide module that reached into each of them would be one file
   that has to know three pages, and would break whenever any of them moved.
   Each page hands over two functions and this file never learns what a role
   filter is.

   ONE KEY PER LIST, AND THAT IS THE LOAD-BEARING PART. The order's negative
   control is a list never visited this session, which must open at the top -
   and it can only fail if a stale offset from a DIFFERENT list can reach it.
   Keys are namespaced per list and a miss returns null rather than a default.
*/
'use strict';

var CCListMem = (function () {

  var PREFIX = 'ccList:';

  /* Read through a guard, for the reason every other store on this site is:
     storage THROWS outright where it is disabled, and a page must not fall
     over because it could not remember where somebody was scrolled to. */
  function store() {
    try {
      return (typeof sessionStorage !== 'undefined') ? sessionStorage : null;
    } catch (e) { return null; }
  }
  function read(key) {
    var s = store();
    if (!s) return null;
    try {
      var raw = s.getItem(PREFIX + key);
      return raw ? JSON.parse(raw) : null;
    } catch (e) { return null; }
  }
  function write(key, v) {
    var s = store();
    if (!s) return false;
    try { s.setItem(PREFIX + key, JSON.stringify(v)); return true; }
    catch (e) { return false; }
  }
  function forget(key) {
    var s = store();
    if (!s) return;
    try { s.removeItem(PREFIX + key); } catch (e) {}
  }

  /* A list may scroll in its own box or in the window. Both are real on this
     site - the ship matrix scrolls the window, a picker pane scrolls itself -
     and getting the wrong one restores a number nobody can see. */
  function scrollerOf(spec) {
    var sc = spec.scroller ? spec.scroller() : null;
    return (sc && sc !== document.documentElement && sc !== document.body)
      ? sc : null;
  }
  function readScroll(spec) {
    var sc = scrollerOf(spec);
    if (sc) return sc.scrollTop || 0;
    if (typeof window === 'undefined') return 0;
    return window.scrollY
      || (document.documentElement && document.documentElement.scrollTop)
      || (document.body && document.body.scrollTop) || 0;
  }
  function writeScroll(spec, y) {
    var sc = scrollerOf(spec);
    if (sc) { sc.scrollTop = y; return sc.scrollTop; }
    if (typeof window === 'undefined' || !window.scrollTo) return 0;
    window.scrollTo(0, y);
    return readScroll(spec);
  }

  var specs = {};

  /* THE BROWSER'S OWN RESTORE IS TURNED OFF, and it has to be. Left on, it
     restores its own idea of the offset on Back at a moment when the table
     still says "Loading ships" and is 200px tall - so it lands at the top,
     and then our restore lands somewhere else a moment later. Two restores
     fighting is worse than one that is late. */
  function manualScroll() {
    try {
      if (typeof history !== 'undefined' && 'scrollRestoration' in history) {
        history.scrollRestoration = 'manual';
      }
    } catch (e) {}
  }

  function attach(spec) {
    if (!spec || !spec.key) return null;
    specs[spec.key] = spec;
    manualScroll();

    /* CAPTURED ON THE WAY OUT, BY WHATEVER ROUTE. A click handler on the
       detail links alone would miss a keyboard activation, a middle-click
       promoted to a navigation, a reload, and the browser's own Back out of
       the list - and "the list state survives a reload" is in the order. */
    if (typeof window !== 'undefined' && window.addEventListener) {
      window.addEventListener('pagehide', function () { save(spec.key); });
      /* pagehide does not fire on every browser for every navigation; this is
         belt and braces rather than a second mechanism, and both write the
         same record through the same function. */
      window.addEventListener('beforeunload', function () { save(spec.key); });
    }

    /* AND ON THE CLICK ITSELF, so the row somebody opened is the row that is
       marked when they come back. By the time pagehide runs the click target
       is gone. Capture phase, because a link's own handler may navigate. */
    if (spec.linkSel && typeof document !== 'undefined'
        && document.addEventListener) {
      document.addEventListener('click', function (e) {
        var t = e && e.target;
        var a = (t && t.closest) ? t.closest(spec.linkSel) : null;
        if (!a) return;
        save(spec.key, spec.idOf ? spec.idOf(a) : null);
      }, true);
    }
    return spec;
  }

  function save(key, hi) {
    var spec = specs[key];
    if (!spec) return null;
    if (hi !== undefined && hi !== null) spec._hi = hi;
    var v = {
      y: readScroll(spec),
      s: spec.capture ? spec.capture() : null,
      hi: spec._hi || null,
      /* Stamped so a reader can tell a record apart from a default. */
      k: key
    };
    write(key, v);
    return v;
  }

  /* RESTORE IS CALLED BY THE PAGE, WHEN ITS ROWS EXIST - not on DOMContentLoaded
     and not on a timer. A list whose rows are built by script has no height
     until they are, and scrolling a 200px document to 4,300 lands at the
     bottom of nothing. The page knows when it is ready; this file cannot. */
  function restore(key) {
    var spec = specs[key];
    if (!spec) return false;
    var v = read(key);
    /* NO RECORD MEANS THE TOP, and it means it by doing nothing at all rather
       than by scrolling to 0. A list arrived at fresh should keep whatever
       position the browser or an anchor gave it. */
    if (!v || v.k !== key) return false;
    if (spec.apply && v.s) {
      try { spec.apply(v.s); } catch (e) {}
    }
    if (v.hi && spec.highlight) {
      try { spec.highlight(v.hi); } catch (e) {}
    }
    var want = Math.max(0, Number(v.y) || 0);
    var got = writeScroll(spec, want);
    /* THE ROWS MAY STILL BE ARRIVING. A filter re-run, an image, a font - any
       of them can change the document's height after this returns, and a
       restore that lands short is the defect wearing a smaller number. Bounded
       and observable: it retries a few frames and stops, rather than fighting
       the page forever. */
    if (Math.abs(got - want) > 2) {
      var tries = 0;
      var again = function () {
        if (tries++ > 8) return;
        var now = writeScroll(spec, want);
        if (Math.abs(now - want) > 2) {
          if (typeof requestAnimationFrame === 'function') {
            requestAnimationFrame(again);
          }
        }
      };
      if (typeof requestAnimationFrame === 'function') {
        requestAnimationFrame(again);
      }
    }
    return true;
  }

  return {
    attach: attach,
    save: save,
    restore: restore,
    peek: read,
    forget: forget,
    /* Named so a control can drive the storage directly without reaching into
       a closure, and so two lists can be shown to use different keys. */
    PREFIX: PREFIX,
    _specs: specs
  };
})();

if (typeof module !== 'undefined' && module.exports) {
  module.exports = CCListMem;
}
