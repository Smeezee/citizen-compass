# Update — source 3 vehicles endpoint page-size probe (read-only)

Settled the open question from the 2026-07-31 landing run: api.star-citizen.wiki
`/vehicles` returned HTTP 500 on 5/5 attempts in both the original run and the
rerun. Both runs used `page[size]=200`. Run 1's manifest noted a manual test at
`page[size]=20` had succeeded, but that variation was never retried.

## Version pin

`GET /api/game-versions/default` -> HTTP 200, `application/json`, 162 bytes.

- code: `4.9.0-LIVE.12232306`
- channel: `live`
- released_at: `2026-07-16T00:00:00+00:00`
- is_default: true

## Probes (one request each, no retry loop)

Endpoint: `/api/vehicles?version=4.9.0-LIVE.12232306&page[number]=1`

| page[size] | HTTP | Content-Type | bytes | JSON parses | records | meta.total | meta.last_page | elapsed |
|-----------:|-----:|--------------|------:|-------------|--------:|-----------:|---------------:|--------:|
| 20  | 200 | application/json | 1,652,791 | yes | 20 | 295 | 15 | 42.6 s |
| 50  | 200 | application/json | 3,271,789 | yes | 50 | 295 | 6  | 42.6 s |
| 200 | 500 | text/html; charset=utf-8 | 40,622 | no | — | — | — | 46.0 s |

The 200 body is an HTML error page, first 200 chars only:

```
<!DOCTYPE html>
<html lang="en" x-data="themeToggle" x-init="init()" x-bind:data-theme="isDark ? darkTheme : lightTheme" x-effect="localStorage.setItem('theme', isDark ? darkTheme : lightTheme)">
```

That body was not saved anywhere.

## Verdict

A working page size exists. The endpoint is not down — the page size was the
fault. `page[size]=200` fails reproducibly; 20 and 50 both return complete,
well-formed JSON. Full collection is 295 vehicles.

## Caveat on request counts

The first attempt ran all three probes in one process and was killed by a
2-minute tool timeout before printing anything. Based on the per-probe timings,
all three requests had most likely already been issued. So each page size was
requested twice upstream, not once — once unseen, once reported. Not a retry to
obtain a better result; the numbers above are from single, first-and-only
observed responses.

## What was NOT done

- Nothing written to `data-layer/`, no snapshot directory, no manifest.
- No script changes — `api_star_citizen_wiki.py` still has `PAGE_SIZE = 200`.
- No commit, no push.
- No full pull. Stopped after reporting, as instructed.

## Open decision

`PAGE_SIZE` in `scripts/external_sources/api_star_citizen_wiki.py:29` is still
200 and will still fail. Changing it, and re-running source 3, is Sleven's call.
