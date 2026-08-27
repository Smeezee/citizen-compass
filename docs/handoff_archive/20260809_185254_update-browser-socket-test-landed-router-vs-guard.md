# Update — the seam is in, the wiring is tested over a real socket, and the negative control found something

Picked up the item C1's ruling unblocked. Done, with one correction to myself and
one discovery the negative control produced.

## The seam

`serveBrowserUI` split into:

- **`startBrowserUI(calls, logf) (*browserUI, string, error)`** — builds the
  server, listens, returns the instance and URL. **Does not open a browser and
  does not block.**
- **`(*browserUI).wait(logf)`** — the watchdog loop, unchanged.
- **`serveBrowserUI`** — now a thin wrapper: start, log, `openInBrowser`, wait.
  **Behaviour is unchanged**; it just calls the other two.

That was the blocker. A selftest cannot pop a browser tab on somebody's machine,
so while starting the server also launched one, the routes were unreachable from
a test.

## `ui_browser_socket_selftest.go` — 13 checks, all passing

Real loopback socket, real `http.Client`, real routes. What it establishes that
nothing did before:

- the page is served to a correct token and **not** to a wrong one
- a refused request **did not run the action** — checked by observing whether the
  action fired, because a 404 that still ran `sendData` is not a refusal and a
  status code alone cannot tell you
- **NEGATIVE CONTROL:** the real token *does* reach `sendData` and it *does* run.
  Without this, every check above is satisfied by a server that refuses
  everything, including the page's own requests
- a cross-site POST is refused on the wire, and its action did not run
- `/leaving` refuses a wrong token and accepts a real one (204)
- an unknown action name 404s rather than returning an empty success
- the page is served `no-store` and `X-Frame-Options: DENY`

## The negative control found something I had assumed wrong

Deleting the guard from `/call/` and re-running showed **the two refusals do not
come from the same place**:

```
WRONG TOKEN  -> refused by the ROUTER. The token is part of the mux pattern, so a
                wrong one matches no route and 404s before any handler runs.
                STILL 404s with the guard deleted.
CROSS-SITE   -> refused by the GUARD, and only the guard. With it deleted this
                returned 200 and sendData ACTUALLY RAN.
```

So the wrong-token checks prove the **routing**, and only the cross-site pair
proves the **wiring**. I had been treating them as one claim. Both checks are
worth keeping, but they are no longer described as though they test the same
thing — the names now say which layer each exercises, and the reasoning is
recorded in the file's header so the next person does not have to re-derive it
by planting a defect.

**Proven able to fail, twice:** once before the rename and once after, since the
labels changed. Both times exactly two checks went red and named the cause.

## A correction to myself, repeated in three places

**There are three routes, not four.** `base+"/"`, `base+"/call/"`,
`base+"/leaving"`. I said "the four handlers" in my report to Sleven, in my
receipt of the ruling, and in the comments I had just written into
`ui_browser.go` and the new selftest. All four instances corrected. Nothing
functional turned on it, but a comment asserting a wrong count is exactly the
kind of thing that gets believed later.

## Suite state

**386 passing, 6 failing.** All 13 socket checks pass. The 6 failures are both
pre-existing and both already reported:

- **2 × `sent-rows`** — the other session's non-hermetic test, which mines the
  real machine's Star Citizen logs and so can only pass on a machine without the
  game installed. Still not mine to fix.
- **4 × staleness** — the ~1-in-5 flake, with my gate correctly reporting the two
  downstream checks as **NOT PERFORMED** rather than letting them pass on 0 == 0.
  Working as intended; the underlying race is still unfixed.

`gofmt` clean on everything I touched, `go vet` and `go build` clean.

## On the ruling itself

Recorded and followed. I did not re-file C1's ruling text into `docs/` — copying
it from here would make a second copy of one artifact, which is the failure the
ruling is about.

Worth noting the ruling's own honest caveat is right: this is a process
commitment, not a mechanical guard. Nothing structurally prevents a second writer
in `citizen-collector/` today. What did work, twice, was checking mtimes before
writing — which is how the collision was caught in the first place.

Nothing staged, nothing committed.
