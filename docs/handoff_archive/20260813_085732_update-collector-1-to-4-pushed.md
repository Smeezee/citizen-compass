# Update — §1-§4 committed and pushed. Three commits, verified by re-fetching.

Sleven gave the go-ahead in session: "commit and push §1-§4".

```
ce984a6..6dde2bd  main -> main
local and origin both at 6dde2bdb861284152bc8c37f9aaaae122349dfb4
```

```
7d12ace  location_inventory_name is a measured zero, not a stale pattern
b75a94a  The collector stops photographing the main menu, and the interval is 120s
6dde2bd  One press of the hotkey is a burst, and a press still always yields a frame
```

`git add` by path, never `-A`, per §7. `git status` on `citizen-collector/` is
clean afterwards, so nothing was left half-staged.

**§4 rode with the second commit** rather than getting its own, because its only
artefact is a comment in `auto.go` and that file already carried §2. The commit
message says so, including the correction: there is no startup mine, and the
reason a startup mine would be a no-op.

## NOT deployed, and nothing published

The collector is a desktop program, not the website. **No release was built and
nothing was published** - §7 forbids it and no part of this touched it. What is
pushed is source.

## State

```
§1 ANSWERED   §2 BUILT   §3 BUILT   §4 NOTHING BUILT, premise corrected
§5 HELD for C1's correction        §6 HELD - it is defined by §5
```

Verified at the commit: 414 ok, 2 FAIL, `EXITCODE=1`, both failures the
pre-existing `sent-rows` pair that only fails on a machine with Star Citizen
installed. `go build`, `go vet`, `gofmt` clean.

## Still open, unchanged

- **§5 and §6** wait on the correction. §6 cannot be built first; its job is
  refusing what §5 defines as unsafe.
- **The `sent-rows` failure** belongs with §6 - it is export-path, and fixing it
  now would mean touching `export.go` twice, the second time against a
  definition that has not arrived.
- **The 818 MB baseline** needs a real session to re-measure. §2's effect is
  directional and mechanical; the number is not mine to estimate.
- **`_to_delete/`** holds two things for Sleven: the stale `.git/index.lock`
  moved aside earlier, and the eleven-line `go test` entry point that runs §3's
  checks in 0.2s instead of eight minutes.
