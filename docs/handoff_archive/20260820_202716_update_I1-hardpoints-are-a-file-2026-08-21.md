# UPDATE — I1 DONE: the public site needs no server at all

    from  Code, 2026-08-21
    item  I1 of the 2026-08-21 order
    sha   a05a021 (code), 39e7616 (ledger)

The ship page's Loadout panel was the last thing on this site calling a live
server. It now reads a generated file.

- build_hardpoint_data.py -> testing/_src/hardpoint_data.gen.js
  235 models, 2,195 slots. 149.0 KB raw, **14.2 KB gzipped** (H1's price file
  was 188 KB; the 60 KB ceiling was not approached, so no shape change to
  explain).
- Acceptance asserted, not eyeballed: slots in file == slots in database,
  counted out of the emitted structure.
- THE CONTROL: with fetch/XHR/WebSocket/EventSource/sendBeacon all replaced by
  throwers - and the poison proven live - the panel fills. 600i Explorer
  renders all 15 mounts grouped. 35 assertions.
- The API path is KEPT as the fallback with every failure sentence intact, and
  the suite that covers it now ASSERTS it is on the fallback (no HP_DATA in
  context, fetch calls counted). Proven by planting HP_DATA into a copy: it
  failed, exit 1.

Found and fixed while doing it, already live on the API path since G8: 8 mounts
state size 0 and 167 state '<= PLACEHOLDER =>' as their fitted item. The panel
was showing both to visitors as if they were a size and a component. The mount
is still listed; the non-value is no longer displayed as a value.

Next: I2, scripts/deploy_live.ps1 and a live wrangler config. Dry run only -
the live site is NOT deployed in this run.
