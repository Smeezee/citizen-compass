#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""community_mark.py - CIG's "Made By The Community" mark, applied and detected.

A2. WHAT CIG REQUIRES
=====================
    * in the CORNER of any images
    * NO LESS THAN 50% OPACITY
    * a reasonably legible size - CIG names legibility, not a pixel figure

And the prohibitions, which CIG applies to all its images and assets:
NO recolouring, NO flipping or reversing, NO distorting, NO outlines or drop
shadows, NO patterns, textures or effects applied on top.

THE PRECEDENT IS FOLLOWED, NOT REINVENTED. docs/FINDING_hologram-display-
concept-2026-08-08.md did this once correctly on a real render at 70% opacity,
logo in the corner, legible size. 70% is what this uses.

WHY THERE IS A DETECTOR AND NOT JUST AN APPLIER
===============================================
The order is explicit that the negative control is the load-bearing one:
"assert that an image composited WITHOUT the mark is REFUSED by the build.
Without that, 'the mark is applied' also passes on a build that applies
nothing."

A flag in a register saying `marked: true` is a CLAIM, not a check - it stays
true when the compositing step silently stops running. So `mark_score()` looks
at the pixels.

HOW THE DETECTION WORKS, and the first version of it that was WRONG.
The obvious statistic is "is the corner brighter where the mark is opaque". It
was measured and it does not work, so it is not what this uses. The mark is not
a flat silhouette: 72% of it is opaque, and that opaque region runs the whole
luminance range 9..255 with a MEAN OF 113 - mid grey. Composited onto a mid-grey
render it therefore shifts the average by almost nothing. Measured: a mid-grey
fixture scored 5.36 where dark and light fixtures scored 57 and 68. That
detector would have passed the mark as missing on exactly the mid-tone images a
ship render actually produces.

What this uses instead is the CORRELATION between the corner's luminance and the
mark's own luminance, over the mark's opaque pixels. Alpha compositing is
linear: a marked corner is (opacity * mark) + ((1 - opacity) * background), so
its pixels track the mark's internal structure almost perfectly whatever the
background is. Correlation is invariant to both the background's brightness and
the opacity, which is precisely the property the mean-difference version lacked.
Score is Pearson's r in 0..1.

IT IS A CORRELATION, NOT A CRYPTOGRAPHIC PROOF. An image that happened to
contain the mark's own structure exactly where the mark goes would score high.
That is a tolerable false-positive: the failure this guards against is the
compositing step not running at all, which produces a score near zero on every
image at once.

THE MARK FILE IS NOT COMMITTED TO THIS REPOSITORY. It is read from the Fan Kit
on disk, or from CC_FANKIT_DIR. Copying a CIG asset into a public git repo is a
separate decision from the one Sleven has taken, and is not mine to make.

Rule 15: every open states its encoding. Images are opened in binary by PIL,
which takes none.
"""

import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)

# Where the Fan Kit lives. Overridable, because a path under one person's
# Downloads folder is not a build input anybody else has.
DEFAULT_FANKIT = os.path.join(
    os.path.expanduser("~"), "Downloads", "Fankit_2025_11_19",
    "Fankit_2025_11_19")

MARK_BLACK = os.path.join("03_LOGOS", "MadeByTheCommunity_Black.png")
MARK_WHITE = os.path.join("03_LOGOS", "MadeByTheCommunity_White.png")

# The precedent's figure. CIG's floor is 50%; this is above it deliberately,
# and the applier refuses anything below the floor rather than trusting a
# caller to pass a legal value.
OPACITY = 0.70
MIN_OPACITY = 0.50

# "A reasonably legible size" - CIG names legibility, not pixels. Expressed as a
# fraction of the image's shorter side, with a floor in pixels so it stays
# legible on a small thumbnail rather than shrinking with it.
MARK_FRACTION = 0.22
MARK_MIN_PX = 64
MARGIN_FRACTION = 0.025

# Pearson r above which the corner counts as carrying the mark. Set from
# measuring both cases on real fixtures rather than picked. Across dark, mid,
# light, a gradient with a deliberately bright corner blob, and a 320px image,
# both variants, at 70% AND at CIG's 50% floor: marked scored 0.9683..0.9994,
# unmarked scored at most 0.0212. 0.50 sits in the middle of that 0.947 gap.
# checks/_verify_community_mark.py re-measures both ends every run, so this
# number cannot quietly stop separating the two cases.
MARK_THRESHOLD = 0.50


def fankit_dir():
    return os.environ.get("CC_FANKIT_DIR") or DEFAULT_FANKIT


def mark_path(variant="white"):
    """The mark file. Raises rather than returning a path that is not there,
    because a missing mark must stop a build and not produce an unmarked
    image."""
    rel = MARK_WHITE if variant == "white" else MARK_BLACK
    p = os.path.join(fankit_dir(), rel)
    if not os.path.exists(p):
        raise FileNotFoundError(
            "The 'Made By The Community' mark is not at %s.\n"
            "CIG requires it in the corner of any image built from their "
            "assets, so an image cannot be produced without it.\n"
            "Set CC_FANKIT_DIR to the Fan Kit directory." % p)
    return p


def _load(path):
    from PIL import Image
    return Image.open(path).convert("RGBA")


def apply_mark(src, dst, variant="white", opacity=OPACITY):
    """Composite the mark into the bottom-right corner and write `dst`.

    THE PROHIBITIONS ARE STRUCTURAL HERE, not a comment. The mark is scaled on
    BOTH axes by the same factor, so it cannot be distorted; it is never
    transposed, so it cannot be flipped; its own pixels are copied unchanged,
    so it cannot be recoloured; and nothing is drawn on top of it, so it gets
    no outline, shadow, pattern or effect. The ONLY thing varied is overall
    alpha, which CIG permits down to 50%.
    """
    from PIL import Image
    if opacity < MIN_OPACITY:
        raise ValueError(
            "opacity %.2f is below CIG's 50%% floor for the 'Made By The "
            "Community' mark. Refusing to write an image that breaches it."
            % opacity)
    base = _load(src)
    mark = _load(mark_path(variant))

    short = min(base.size)
    target_w = max(MARK_MIN_PX, int(round(short * MARK_FRACTION)))
    # ONE scale factor for both axes. Aspect ratio is preserved by
    # construction rather than by remembering to.
    scale = target_w / mark.width
    new = (max(1, int(round(mark.width * scale))),
           max(1, int(round(mark.height * scale))))
    mark = mark.resize(new, Image.LANCZOS)

    if opacity < 1.0:
        a = mark.getchannel("A").point(lambda v: int(v * opacity))
        mark.putalpha(a)

    margin = max(6, int(round(short * MARGIN_FRACTION)))
    pos = (base.width - mark.width - margin, base.height - mark.height - margin)

    out = base.copy()
    out.alpha_composite(mark, pos)
    os.makedirs(os.path.dirname(os.path.abspath(dst)) or ".", exist_ok=True)
    out.convert("RGB").save(dst, quality=92)
    return {"file": dst, "opacity": opacity, "mark_size": new, "pos": pos}


def mark_score(path, variant="white"):
    """Pearson correlation between this image's corner and the mark's own
    luminance, over the mark's opaque pixels.

    Near zero means the corner has no relationship to the mark's structure,
    which is what an image the compositing step never touched looks like.
    Near one means the mark is there, at whatever opacity, on whatever
    background.
    """
    from PIL import Image
    img = _load(path)
    mark = _load(mark_path(variant))

    short = min(img.size)
    target_w = max(MARK_MIN_PX, int(round(short * MARK_FRACTION)))
    scale = target_w / mark.width
    new = (max(1, int(round(mark.width * scale))),
           max(1, int(round(mark.height * scale))))
    mark = mark.resize(new, Image.LANCZOS)
    margin = max(6, int(round(short * MARGIN_FRACTION)))
    box = (img.width - mark.width - margin, img.height - mark.height - margin,
           img.width - margin, img.height - margin)
    if box[0] < 0 or box[1] < 0:
        return 0.0

    corner = list(img.crop(box).convert("L").getdata())
    ml = list(mark.convert("L").getdata())
    ma = list(mark.getchannel("A").getdata())

    xs = [c for c, a in zip(corner, ma) if a > 200]
    ys = [m for m, a in zip(ml, ma) if a > 200]
    n = len(xs)
    if n < 64:
        return 0.0

    mx, my = sum(xs) / n, sum(ys) / n
    sxy = sxx = syy = 0.0
    for x, y in zip(xs, ys):
        dx, dy = x - mx, y - my
        sxy += dx * dy
        sxx += dx * dx
        syy += dy * dy
    # A corner of literally uniform colour correlates with nothing. Report 0
    # rather than dividing by zero - "cannot tell" fails closed as "not marked".
    if sxx <= 1e-9 or syy <= 1e-9:
        return 0.0
    return max(0.0, sxy / ((sxx ** 0.5) * (syy ** 0.5)))


def has_mark(path, variant="white"):
    return mark_score(path, variant) >= MARK_THRESHOLD
