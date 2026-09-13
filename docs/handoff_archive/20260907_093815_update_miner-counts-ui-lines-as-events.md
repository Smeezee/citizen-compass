# Update - the log miner counts UI lines as events. Payouts are 8x too high. Fix, re-mine, prove.

To: Code
From: C1
Date: 2026-09-07
Reads: `claude/FINDING_the-payout-numbers-are-eight-times-too-high-and-i-can-prove-it-2026-09-07.md`
       `claude/AUDIT_the-foundation-is-two-thirds-built-and-three-things-are-quietly-wrong-2026-09-07.md`
       `claude/DESIGN_seven-things-that-must-be-decided-before-the-first-row-2026-09-07.md`

Sleven has approved the direction. This is work, not a proposal.

## The defect

`collector2`'s game-log miner treats every matching line as an event. The game
writes many lines per event, so the store is inflated.

One award of 50,250 aUEC in the archive:

    SHUDEvent_OnNotification   Added notification "Awarded 50250 aUEC: " [46] to queue   <- THE EVENT
                               "Awarded 50250 aUEC: " [46]                               <- echo
    UpdateNotificationItem     ... [46], Action: Next                                    <- UI
    UpdateNotificationItem     ... [46], Action: StartFade                               <- UI
    UpdateNotificationItem     ... [46], Action: Remove                                  <- UI

Counted across all 243 archived logs:

    echo line                            413
    REAL: Added notification             104
    UI: UpdateNotificationItem Next      104
    UI: UpdateNotificationItem StartFade 104
    UI: UpdateNotificationItem Remove    104
    -----------------------------------------
    total award lines                    829
    actual payouts                       104        7.97x

The 104/104/104/104 is the notification lifecycle - exactly four states, every
time. That regularity is why this is a rule and not a heuristic.

**Any earnings figure the store has produced is wrong by up to 8x.** Treat
anything already concluded from `facts.json` about run payouts as void.

## Two explanations of mine that were WRONG - do not build on them

Both are in the audit and both are now disproven. Flagging so you do not inherit
them:

- **"The archived logs overlap each other."** Tested: 932,745 lines, 846,823
  distinct, **129 lines appear in more than one file (0.0%)**, and those are
  boilerplate headers. The logs do not overlap.
- **"The miner was re-run over the same archive."** Mostly not. The repetition is
  in the log itself.

## Shop transactions - same shape, not yet measured cleanly

Of 1,091 commodity/shop lines in the archive, only ~298 are actual transaction
requests:

    SendShopBuyRequest           250
    SendStandardItemBuyRequest    29
    SendShopSellRequest           10
    SendCommoditySellRequest       9

The rest - `AddInventoryEntities`, `AddPlayerCommodityItem`,
`ClSetSelectedPlayerLocation`, `LoadSelectedShipBinding` - are the shop UI
loading itself. The store holds 1,156 `shop_transaction` rows. **Those two
numbers are not directly comparable** (the store was built from a subset of these
logs) so treat this as a lead, measure it properly, and report the real ratio
rather than assuming 8x here too.

## The work

**1. Whitelist the event-producing line types.**
For payouts, exactly one: `SHUDEvent_OnNotification` AND `Added notification`.
**Whitelist, not blacklist** - a UI line type CIG adds next patch must be
ignored by default rather than counted by default.

**2. Natural key on every observation.**
For payouts, `(timestamp, notification id)` - the `[46]`. Verified exact against
the archive: 104 distinct keys, 104 events, no collisions. It comes out of the
log rather than being invented, which is the property the seven asked for.

Find the equivalent request identity for shop lines and state what you chose.

**3. `occurred` becomes required. Rename `at` to what it is.**
`at` currently holds **ingest time** and is present on all 2,500 rows; `occurred`
holds real event time and is on **633**. One row says `at` 2026-08-31 for an
event from 2025-11-23. Nine months. Anything that trusted `at` has already drawn
a wrong conclusion.

**4. Then re-mine all 243 logs as `gamelog@3`.**

**5. Do NOT delete or de-duplicate the existing rows.**
Leave them as `gamelog@1`/`@2`. The new reader writes beside them. The
old-vs-new comparison is the proof the fix worked, and rule 1 covers the rest.

## Why 4 is worth more than it looks

`gamelog@1` and `gamelog@2` **overlap on zero payloads** - the newer reader has
never re-read anything the older one read. The entire argument for keeping raw
logs is *"a better reader re-reads old nights"*, and that capability is built and
has never once been exercised. Rule 12: a check that cannot fail is not a check,
and a capability never run is the same category.

This is its first real test. If re-mining does not reproduce and correct the old
rows, the problem is bigger than the miner.

## Acceptance

    payout events from the full archive          104
    distinct natural keys                        104
    every new row carries occurred               yes
    every new row carries a natural key          yes
    gamelog@1/@2 rows still present, untouched   yes
    shop transaction ratio measured and reported yes
    a control that FAILS if UI lines are counted again

That last one matters most. This defect was invisible for weeks because every
individual row looked correct and nothing counted them against the source. Fix
without a control and it comes back.

## Not in scope

The place chain, units on payout rows, and `session_id` are on the seven and are
real, but they do not block this and mixing them in makes the re-mine harder to
judge. Separate pass.
