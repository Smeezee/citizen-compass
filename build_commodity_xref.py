"""
G5 / R1 - link the item-side "Commodities" category to the commodity import.

WHAT THIS IS FOR
================

UEX describes the same tradeable substance twice, in two id spaces that do not
reference each other:

    as an ITEM       category 36 "Commodities", 158 rows, ZERO of them priced
    as a COMMODITY   the commodities endpoint, 204 rows, 147 priced (72%)

Sleven ruled that the SITE shows the commodity import, because a price site
showing a commodity with no price is worse than not showing it. He also ruled
that BOTH STAY STORED - standing preservation rule, nothing is deleted - and
that the category-36 rows become a CROSS-REFERENCE rather than a tombstone.

So this writes links. It does not merge the two rows and it does not delete
either of them, because collapsing them would destroy the evidence that they
differ: the item side calls it "Aslarite (Raw)" and the commodity side calls it
"Aslarite (Ore)", the item side has no prices and the commodity side does. Those
disagreements are data about the source and are worth more than a tidy table.

WHAT IT MATCHES ON, AND WHY NOT UUID
=====================================

Name. There is nothing else. Not one of the 204 commodities carries a uuid, and
the two id spaces collide rather than correspond - id 1 is the "Omnisky III
Cannon" as an item and "Agricium" as a commodity. That is the same finding that
overturned the order's original "join on UUID, never on display name" ruling,
and it applies here with no ambiguity at all: measured on today's data, no name
on either side maps to two rows on the other.

TWO TIERS, RECORDED SEPARATELY
==============================

    exact_name   the names are identical once case and punctuation are
                 normalised. 156 of the 158.
    token_set    the same words in a different order - "Raw Ice" against
                 "Ice (Raw)". Exactly one row.

The weaker tier is stored in `match_method` rather than folded in with the
others, so that dropping it later is one WHERE clause instead of an argument
about which links were guesses. A reader who cannot tell the two apart cannot
judge either.

Nothing beyond those two rules. No fuzzy matching, no edit distance, no
"probably the same" - a wrong link here would put one substance's prices under
another substance's name, which is the same class of error as putting a
Hammerhead's hardpoints on a Gladius.

IDEMPOTENT. Re-running inserts nothing new. The 1:1 unique constraints on both
sides mean the database refuses a second link rather than quietly recording two.

Usage:
    venv/Scripts/python.exe build_commodity_xref.py --dry-run
    venv/Scripts/python.exe build_commodity_xref.py

Rule 15: encodings stated (no file reads here - this is database to database).
"""

import argparse
import re
import sys
from collections import defaultdict
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent
load_dotenv(PROJECT_ROOT / ".env")

from sqlalchemy import select  # noqa: E402

from app.database import SessionLocal  # noqa: E402
from app.models import (  # noqa: E402
    ItemCategory,
    ItemPrice,
    ShopItem,
    ShopItemCommodityXref,
)

# UEX's own id for the "Commodities" item category. Not the primary key - the
# primary key is whatever this database happened to assign on import.
COMMODITY_CATEGORY_UEX_ID = 36


def log(message):
    print(message, flush=True)


def normalise(name):
    """Case and punctuation folded away. Nothing else."""
    return re.sub(r"[^a-z0-9]+", " ", (name or "").lower()).strip()


def token_key(name):
    """The same words in any order. The weaker of the two tiers."""
    return " ".join(sorted(normalise(name).split()))


def build_links(session, dry_run):
    category = session.execute(
        select(ItemCategory).where(
            ItemCategory.uex_id == COMMODITY_CATEGORY_UEX_ID
        )
    ).scalar_one_or_none()
    if category is None:
        log(f"FAILED: no item category with uex_id "
            f"{COMMODITY_CATEGORY_UEX_ID}. Nothing was written.")
        return None

    items = list(session.execute(
        select(ShopItem).where(
            ShopItem.category_id == category.id,
            ShopItem.source_kind == "item",
        )
    ).scalars())
    commodities = list(session.execute(
        select(ShopItem).where(ShopItem.source_kind == "commodity")
    ).scalars())

    log(f"category {COMMODITY_CATEGORY_UEX_ID} ({category.name!r}): "
        f"{len(items)} item-side rows")
    log(f"commodity import:                {len(commodities)} rows")

    by_exact = defaultdict(list)
    by_token = defaultdict(list)
    for commodity in commodities:
        by_exact[normalise(commodity.name)].append(commodity)
        by_token[token_key(commodity.name)].append(commodity)

    existing = {
        row.item_shop_item_id
        for row in session.execute(select(ShopItemCommodityXref)).scalars()
    }

    linked, unmatched, ambiguous, already = [], [], [], 0
    for item in sorted(items, key=lambda r: r.name or ""):
        candidates = by_exact.get(normalise(item.name))
        method = "exact_name"
        if not candidates:
            candidates = by_token.get(token_key(item.name))
            method = "token_set"

        if not candidates:
            unmatched.append(item)
            continue
        if len(candidates) > 1:
            # AMBIGUITY IS NOT RESOLVED, IT IS REPORTED. Picking one would be
            # the silent version of the problem - see the D2 409 ruling, same
            # reasoning: returning the first match hides an upstream defect.
            ambiguous.append((item, candidates))
            continue

        if item.id in existing:
            already += 1
            continue

        linked.append((item, candidates[0], method))
        if not dry_run:
            session.add(ShopItemCommodityXref(
                item_shop_item_id=item.id,
                commodity_shop_item_id=candidates[0].id,
                match_method=method,
            ))

    return {
        "items": items,
        "commodities": commodities,
        "linked": linked,
        "unmatched": unmatched,
        "ambiguous": ambiguous,
        "already": already,
    }


def report(session, result):
    """The numbers R1 asked for. The unmatched ones are the interesting half."""
    linked = result["linked"]
    by_method = defaultdict(int)
    for _, _, method in linked:
        by_method[method] += 1

    log("")
    log("LINKS")
    for method in sorted(by_method):
        log(f"  {method:<12} {by_method[method]:>4}")
    if result["already"]:
        log(f"  {'already held':<12} {result['already']:>4}  "
            f"(re-run, nothing inserted)")

    total_linked = len(linked) + result["already"]
    log(f"  {'TOTAL':<12} {total_linked:>4} of {len(result['items'])} "
        f"category-36 items")

    log("")
    log(f"NO COMMODITY COUNTERPART: {len(result['unmatched'])}")
    for item in result["unmatched"]:
        log(f"  {item.name}")
    if not result["unmatched"]:
        log("  (none)")

    if result["ambiguous"]:
        log("")
        log(f"AMBIGUOUS - reported, NOT linked: {len(result['ambiguous'])}")
        for item, candidates in result["ambiguous"]:
            log(f"  {item.name!r} -> {[c.name for c in candidates]}")

    # The other direction, because "which commodities nothing points at" is a
    # different question from "which items found nothing" and neither answers
    # the other.
    pointed_at = {c.id for _, c, _ in linked}
    if result["already"]:
        pointed_at |= {
            row.commodity_shop_item_id
            for row in session.execute(select(ShopItemCommodityXref)).scalars()
        }
    orphan_commodities = [c for c in result["commodities"]
                          if c.id not in pointed_at]
    log("")
    log(f"COMMODITIES WITH NO ITEM-SIDE COUNTERPART: "
        f"{len(orphan_commodities)} of {len(result['commodities'])}")
    for commodity in sorted(orphan_commodities, key=lambda r: r.name or "")[:60]:
        log(f"  {commodity.name}")
    if len(orphan_commodities) > 60:
        log(f"  ... and {len(orphan_commodities) - 60} more")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    log("G5 / R1 - commodity cross-reference"
        f"{' (DRY RUN - nothing will be written)' if args.dry_run else ''}")

    with SessionLocal() as session:
        result = build_links(session, args.dry_run)
        if result is None:
            return 1
        report(session, result)

        if args.dry_run:
            session.rollback()
            log("")
            log("DRY RUN - rolled back. Nothing was written.")
            return 0

        session.commit()

        held = session.query(ShopItemCommodityXref).count()
        log("")
        log(f"shop_item_commodity_xref holds {held} link(s)")

        # THE POINT OF THE WHOLE EXERCISE, stated as a number rather than
        # assumed: how many prices does following a link actually reach?
        priced = session.execute(
            select(ShopItemCommodityXref.id)
            .join(ItemPrice,
                  ItemPrice.shop_item_id
                  == ShopItemCommodityXref.commodity_shop_item_id)
            .distinct()
        ).all()
        log(f"{len(priced)} of those links reach at least one price row - "
            f"which is what a category-36 item gains by being linked, since "
            f"not one of them carries a price of its own.")

        expected = len(result["items"]) - len(result["unmatched"]) \
            - len(result["ambiguous"])
        if held != expected:
            log(f"FAILED: expected {expected} links, hold {held}")
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
