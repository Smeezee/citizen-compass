# -*- coding: utf-8 -*-
"""attribution.py - the trademark notice and the source/contact notice.

ONE DEFINITION. EVERY PAGE TAKES IT FROM HERE.
==============================================
Before this file there were THREE different wordings of CIG's trademark notice
across the site and two pages carrying none at all:

    x4  Star Citizen(R), Roberts Space Industries(R) and Cloud Imperium(R) are
        registered trademarks of Cloud Imperium Rights LLC.
    x1  Star Citizen(R) and related marks are the property of Cloud Imperium
        Rights LLC.                                  <- download.html, not CIG's
    x1  Star Citizen(R), Squadron 42(R), Roberts Space Industries(R), and Cloud
        Imperium(R) ...                              <- static/preview.html
    x0  holo.html, stick-test.html

That is the failure the order predicted in advance: "six hand-copied instances
is six chances at one". A required legal notice with a typo in it is a defect,
and there is no way to notice one by reading six copies.

THE TEXT BELOW IS VERBATIM AND IS NOT TO BE EDITED. It is quoted from
claude/FINDING_fankit-inventory-2026-08-08.md, which read CIG's Fan Kit
Guidelines PDF itself. Three registered-trademark symbols and one specific legal
entity name.

CIG'S TWO STATED REQUIREMENTS, both enforced by checks/_verify_attribution.mjs:
  * minimum 10-point font
  * on a website, "displayed on the home page, on a navigation area that is
    always visible regardless of scrolling, or both"

`10pt` is written literally in the CSS rather than as its pixel equivalent. The
site's existing bar uses `13.333px`, which is the same size - 10pt x 96/72 - but
a checker asserting "at least 10 point" should not have to perform a unit
conversion to believe the answer, and neither should a person reading it.

Rule 15: this module opens no file, so it states no encoding. If that changes,
state one.
"""

# ---------------------------------------------------------------------------
# A1. VERBATIM. DO NOT EDIT, DO NOT REFLOW, DO NOT RETYPE.
# ---------------------------------------------------------------------------
TRADEMARK = (
    "Star Citizen®, Roberts Space Industries® and Cloud Imperium® "
    "are registered trademarks of Cloud Imperium Rights LLC."
)

# The same sentence with the registered marks as HTML entities, for pages that
# are written 7-bit. Generated FROM the constant above rather than typed again,
# so the two cannot drift.
TRADEMARK_HTML = TRADEMARK.replace("®", "&reg;")

# The always-visible strip. `position:sticky; bottom:0` keeps it on screen
# regardless of scrolling, which is the second of CIG's two requirements.
TRADEMARK_CSS = """<style>
.cc-tm-bar{position:sticky;bottom:0;z-index:2147483000;
 background:#0B1626;border-top:1px solid rgba(0,201,167,.3);
 color:#C8D6E2;text-align:center;font-size:10pt;line-height:1.4;
 padding:7px 14px;margin:0}
</style>"""

TRADEMARK_BAR = '<div class="cc-tm-bar">%s</div>' % TRADEMARK_HTML


def trademark_block():
    """The strip and the style that makes it always visible, as one string."""
    return TRADEMARK_CSS + "\n" + TRADEMARK_BAR


# ---------------------------------------------------------------------------
# A3. THE SOURCE AND CONTACT NOTICE.
#
# What it is, who owns it, and how to complain - in the plain register the ship
# page already uses, because somebody has to understand what they are looking
# at and that applies to a legal notice more than to a stat tile, not less.
#
# THE CONTACT ADDRESS IS NOT WRITTEN HERE. It is read from configuration by
# build_deploy.py, and a build with no configured address FAILS. A page that
# promises a way to complain and does not have one is worse than a page that
# promises nothing.
# ---------------------------------------------------------------------------
SOURCE_NOTICE_CSS = """<style>
.cc-src-note{margin:10px 0 0;padding:10px 13px;background:#0E1B2E;
 border:1px solid #22364F;border-radius:9px;
 font:400 12.5px/1.55 "Segoe UI",system-ui,sans-serif;color:#93A7B6}
.cc-src-note b{color:#EDE3D8}
.cc-src-note a{color:#FF6B00}
</style>"""


def source_notice(contact):
    """The block for any page that shows ship content.

    `contact` is required. Passing a falsy value is a programming error rather
    than a state to render around, and it raises here so it cannot become a
    page that says "contact:" and then stops.
    """
    if not contact or not str(contact).strip():
        raise ValueError(
            "No contact address was supplied for the source notice. This page "
            "would promise a way to reach us about the ship content and then "
            "not provide one. Refusing to build it.")
    contact = str(contact).strip()
    href = contact if "://" in contact or contact.startswith("mailto:") \
        else "mailto:" + contact
    shown = contact.replace("mailto:", "")
    return SOURCE_NOTICE_CSS + "\n" + (
        '<div class="cc-src-note">'
        '<b>Where the ship models and images come from.</b> '
        'They are Cloud Imperium Games’ own, taken from the holoviewer on '
        'robertsspaceindustries.com. Cloud Imperium Games owns them. '
        '<b>This is an unofficial fan site.</b> It is not affiliated with, '
        'endorsed by, or connected to Cloud Imperium Games in any way, and '
        'nothing here is official.'
        '<br><br>'
        '<b>If Cloud Imperium Games would like any of this taken down</b>, '
        'write to <a href="%s">%s</a> and it will be removed. '
        'No argument and no delay — just say which ship or which image '
        'and it comes off the site.'
        '</div>' % (href, shown))
