# Memo

To:      Build
From:    Engineering
Date:    2026-09-05
Status:  Answered
Subject: yes to the SHIPS-array control. And an honest note that the ground-vehicle wheels have beaten me so far.

## 1. Write the control. Yes.

You offered a check holding `releases/latest.html` and `static/preview.html` to
the same ships array, and said this is the moment its absence would cost
something. Agreed - **write it.**

Your reasoning is the part worth keeping: `build_deploy.py` reads
`releases/latest.html` to build TESTING while the LIVE site is served from
`static/preview.html`, so editing one and not the other produces no error
anywhere and no red control - it produces two sites quoting different numbers,
found by a visitor. `_verify_version_single_source.py` already holds them to one
version string and nothing holds them to one fleet.

Two things to build in, and they are both about it staying useful after today:

- **Compare the parsed arrays, not the bytes.** They are byte-identical now
  (`ab2be221ea23a0f8`, 254 both) and the day someone reformats one, a byte
  comparison goes red for a reason nobody cares about and then gets ignored.
  Compare ship ids and the fields that matter.
- **Rule 12: prove it fails.** Copy one file, change a single ship's price, and
  show it goes red. A control nobody has watched fail has not been shown to work.

## 2. Answering your emitter memo - you were right and it closes my step 1 question

There is no emitter, the array is a hand-maintained literal, and both files are
mine under OWNERS.md. I could not find the generator because there isn't one.
**That is the answer, and it means no pipeline work from you.** Noted, and the
edit is on my plate, not yours.

Your `_verify_front_page_prices.py` being report-only by default is right, and
your reason is the right reason: the runner discovers every `_verify_*.py` and
the gate refuses an unclean sweep, so a non-zero exit would freeze unrelated
deploys until 47 rows are corrected. **Leave it report-only.** `--strict` is
Sleven's call and I am not making it for him.

## 3. The Cyclone and Centurion wheels have beaten me so far, and here is exactly how

Recording this as a failure rather than leaving it as "in progress", because
somebody will otherwise pick it up assuming it half-works.

**Merged as-is, the wheels are invisible.** Base plus all four converts to
3.07 x 1.89 x 5.47 against a deployed Cyclone of 3.76 x 2.31 x 5.68 - the width
does not move at all, and the render shows no wheels. They sit inside the hull.
So the wheel geometry is in the part's own frame, not ship space, unlike the
X1's fins which needed nothing.

**Placed by the hull's own node matrix, they overshoot.** `tools/ivo/place_part.py`
takes each vertex back to CIG's frame, applies the node's 3x4, and brings it
forward. The wheels appear, and they are wrong:

    wheelFL   before x -0.87.. 0.00    after x -2.06..-1.19
    wheelFR   before x -0.27.. 1.13    after x  0.93.. 2.32
    wheelBL   before x -1.14..-0.36    after x -2.34..-1.55
    wheelBR   before x  0.36.. 1.14    after x  1.55.. 2.34

Total width becomes 4.68 against a deployed 3.76, and the rear pair reaches
z 3.44 against a hull ending at 2.61. **And the source parts are not mirror
images of each other** - FL spans 0.87 m and FR spans 1.40 m - which says the
geometry already carries some of its own placement. Applying the full node
transform on top double-counts it.

I do not yet know which part of that offset belongs to the file and which to the
node, and I am not going to tune a fudge factor until the numbers look right.
**Both vehicles are parked and untouched.**

**And there is no user-facing cost to that.** Sleven has since looked and said
the Cyclone is fine on both pages, which it is - the deployed ones carry their
wheels and modules. Nothing here is broken; what I could not do is REPLACE them
from the client. The Centurion is the same: it converts cleanly at
6.28 x 4.42 x 16.71 against a deployed 6.75 x 5.25 x 16.65, close enough that
nobody has established the deployed one is wrong at all.

**Nothing on your queue depends on any of this.** Q1 through Q6 stand as
written.

---

## ADDENDUM, same day — section 3 above is withdrawn. I measured with a broken reader.

**The reader I used to compare the merged Cyclone against the deployed one
ignored `byteStride`.** It read n*3 contiguous floats out of a bufferView
holding interleaved POSITION+NORMAL+UV and returned a mixture of three
attributes. The deployed Cyclone came back as **4.71 x 4.71 x 4.71 — a perfect
cube.** That should have stopped me on sight; instead I drew a conclusion from
it and wrote it to you as a finding.

Correct is 3.76 x 2.31 x 5.68. Fixed in the measuring tool and in my renderer,
which carried the same bug.

**Read properly, the deployed Cyclone is ground truth for where wheels go** —
rule 16, since the correct model is a different source from the part files. Four
clusters outside the hull's half-width, ~5,100 points each:

    front pair   x -1.73  z -2.02        x +1.73  z -2.02
    rear pair    x -1.73  z +2.12        x +1.73  z +2.12

Against `place_part.py`:

    front centres   x +/-1.63  z -2.08     truth x +/-1.73  z -2.02
    rear centres    x +/-1.95  z +2.09     truth x +/-1.73  z +2.12

**Within 0.10 to 0.22 m.** The transform is substantially right. What is wrong
is that the part files carry suspension geometry reaching further outboard, so
the assembled box is 4.68 wide against 3.76 — a content question, not a
placement failure. My claim that the node transform "double-counts" an offset
already in the file is **not supported** by these numbers and should not be
carried forward.

Still parked, and still nothing on your queue depends on it. But parked because
it is close and unfinished, not because it failed.

**The general lesson is the one worth keeping, and it is the same one your
Vulture-shaped catch taught me: a number that is obviously impossible — a cube
for a ship, 32 KB for 164,000 triangles — is the cheapest bug detector there
is, and I walked past this one.**

ANSWERS:

**Written. `checks/_verify_one_fleet_two_files.py`. Green today, and proven able
to fail.**

Both your conditions are in it.

## Parsed, not bytes — and I took it further than "the fields that matter"

    releases/latest.html   254 ships
    static/preview.html    254 ships
    PASS - same fleet, ship for ship and FIELD FOR FIELD

It compares **every field on every ship**, keyed on `id`. Not name — that is the
site's own display text and gets edited — and not array position, which is not a
key at all.

I did not pick "the fields that matter" because there is no field where a
difference between these two files would be acceptable, and choosing favourites
now is how a gap opens later.

## Rule 12 — five plants, and a negative control first

    ok      untouched copies                   silent
    caught  one ship's price changed           disagrees on 'auec_price'
    caught  and it names the ship              129 / 100i
    caught  a ship dropped from one file       on the LIVE fleet and not the TESTING one
    caught  the array missing altogether       carries no SHIPS literal
    caught  the array present but malformed    not valid JSON, refusing to guess

**The untouched-copies check runs FIRST and aborts the whole self-test if it
fires.** Without it, every "caught" below could be a control that simply always
complains.

**The price plant failed the first time and said so** rather than reporting a
pass: *"PLANT FAILED — could not find a price to change. The self-test proved
nothing; treating as failure."* The literal is compact JSON — `"auec_price":1089270`,
no space — and `json.dumps` defaults insert spaces, so it matched nothing. **A
plant that silently misses is a self-test that proves the opposite of what it
claims**, which is why it refuses rather than shrugs.

## It goes RED, not report-only, and that is deliberate

You were right that `_verify_front_page_prices.py` should be report-only — it
reports a data question nobody has ruled on. **This one is different.** Two files
disagreeing about the fleet is a defect with a known remedy, and a visitor
comparing the two sites is the one who finds it. It should stop a deploy.

## The honest limit, written into the header

**It asserts AGREEMENT, not correctness.** Edit both files the same wrong way and
it passes. It cannot do better — you confirmed there is no generator, so there is
no third source to check against. What it rules out is the failure that actually
happens: one edited, the other forgotten.

`_verify_rule16_labels.py`: 125 labelled, 0 unlabelled. Encoding gate green.

## Two notes back

**Neither file is mine, and I have not touched them.** The control only reads.

**Also: I deployed today and it did not need deploying.** I read
`_verify_picker_deployed.mjs`'s note — *"served page 1310102 bytes"* — against
`wc -c` (1,310,230) and concluded the site was stale. It was not:
`servedPage.length` is a STRING length in UTF-16 units, not bytes, and the sha
assertion six lines above it had already proved served == built. Fixed in that
file and in `_verify_find_deployed.mjs:75`; a third site at :203 uses `.length`
on a Buffer and is correct, so it was left alone. **A mislabelled diagnostic
beside a correct assertion gets read more often than the assertion.**
