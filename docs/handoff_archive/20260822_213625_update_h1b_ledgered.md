# Update - H1b closed out. Ledger `d10bb75`, deployed `0c3b086c`.

H1b was committed (`4e9d016`) and deployed in the previous context and then
**neither ledgered nor reported** - the context cleared in the gap. Closed now
before starting anything new.

Verified rather than assumed, in this order:

- The **served** `loadout.html` carries `layoutLabels`, so the deploy is real.
- `wrangler deployments list` names the deploy after H1f's `4f397e10` as
  **`0c3b086c-fadc-4f01-98cb-416387a9234d`**, 2026-08-23 02:23:42Z.
- `checks/_verify_labels.mjs` re-run from scratch: **23 ok, exit 0**.
  `--mutate-nodeconflict`: **exit 1**, Sabre 8 overlaps, Polaris 75,
  Perseus 213.

**One thing worth keeping.** I checked those exit codes through `| tail`, which
reports **tail's** status, not node's - the mutate run printed "a non-zero exit
is the correct outcome" beside `EXIT=0`. Re-run with the pipe removed. A
pipeline hides the exit code of every command but the last, so a `--mutate`
proof read through `head` or `tail` proves nothing.

Starting H1g now.
