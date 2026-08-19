"""
Auditors for the shop and price layer. FLAG ONLY - nothing here ever writes to
project data.

Phase C of docs/ORDER_shop-and-price-layer-RUN-CONTINUOUSLY-2026-08-19.md:

    C1  price outliers          prices absurd against their category
    C2  orphans                 price rows whose item or terminal is missing
    C3  name collisions         display names mapping to more than one record
    C4  category price coverage how many items per category carry a price
    C5  staleness               age of each row's source date_modified

Each takes a SQLAlchemy Session and returns list[Finding], matching
checks/db_checks.py. Registered in CHECKERS at the bottom.

Every one of them is proven in BOTH directions by
checks/_verify_shop_checks.py: fed a row that must trip it and observed
firing, then fed clean data and observed staying silent. That is C6, and it is
not optional - an auditor never observed firing is not an auditor.

WHY SO MANY OF THESE REPORT WARNING RATHER THAN DEFECT
------------------------------------------------------
DEFECT means "a confirmed real problem". A price that is 400x its category
median is not confirmed wrong - Star Citizen genuinely sells a 3-million-aUEC
gun next to a 200-aUEC one. Calling that a DEFECT would train whoever reads
these to ignore the word. So the outlier and staleness checkers report
WARNING, the coverage checker reports LIMITATION where data is simply absent,
and DEFECT is reserved for things that cannot be right under any reading -
a price row pointing at an item that does not exist, for instance.
"""

import datetime
import statistics
from collections import defaultdict

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import ItemCategory, ItemPrice, ShopItem, Terminal
from checks.framework import Finding

# ---------------------------------------------------------------------------
# C1 tuning. These are thresholds, and a threshold nobody wrote a reason for
# is a magic number, so:
#
# MIN_SAMPLE - below this, a "distribution" is not one. With 4 priced items in
#   a category, every one of them is 25% of the sample and the median moves if
#   any single one is wrong. Categories under this report LIMITATION (a known
#   gap) rather than a silent PASS, because "we could not judge" and "we
#   judged it fine" are different answers.
#
# IQR_MULTIPLIER - Tukey's fence is 1.5 for "outlier" and 3.0 for "far out".
#   3.0 is used because game prices are genuinely wide and 1.5 would flag a
#   large share of every category, which is the same as flagging nothing.
#
# RATIO_FLOOR - a second, independent gate. A category where everything costs
#   between 100 and 120 aUEC has a tiny IQR, so an item at 400 clears the
#   fence while being perfectly ordinary. A row must ALSO be at least this
#   many times the median (or this fraction of it) before it is reported.
# ---------------------------------------------------------------------------
MIN_SAMPLE = 8
IQR_MULTIPLIER = 3.0
RATIO_FLOOR = 10.0

# Outliers are judged on log(price), not price. This was changed after the
# first real run, which is the only way it could have been got right:
#
#   Run 1, linear space, flagged 590 of 26,657 rows - 2.2% of everything, and
#   reading them showed the detector was not wrong so much as asking the wrong
#   question. "Scourge Railgun Magazine, 5,888 aUEC, 16.8x the Attachments
#   median of 350" is a perfectly ordinary expensive magazine. A detector that
#   flags 590 ordinary rows is one nobody will read, which makes it worse than
#   no detector at all.
#
# Game prices are MULTIPLICATIVE. A category spans 200 aUEC to 3,000,000 aUEC
# because that is what the game sells, and on a linear scale the whole upper
# half of any such category sits outside a Tukey fence built from its lower
# half. In log space the same distribution is roughly symmetric, and the fence
# then means what it is supposed to mean: "far from the others, in the terms
# this data is actually spread in".
#
# Kept as an explicit switch rather than silently changed, because the linear
# number is the evidence for the log one.
USE_LOG_SCALE = True

# C5 buckets, in days.
STALENESS_BUCKETS = [
    ("0-30 days", 0, 30),
    ("31-90 days", 31, 90),
    ("91-180 days", 91, 180),
    ("181-365 days", 181, 365),
    ("over a year", 366, None),
]


def _scale(value):
    """Map a price into the space outliers are judged in.

    log1p rather than log: a price of 0 never reaches here (0 is stored as
    NULL, see A5), but a price of 1 would give log(1) = 0 and sit oddly, and
    log1p keeps the low end well-behaved without a special case.
    """
    if not USE_LOG_SCALE:
        return float(value)
    import math
    return math.log1p(max(value, 0))


def _quartiles(values):
    """(q1, median, q3) for a sorted-able sequence. Plain statistics module,
    no numpy - this project does not carry it and one dependency for three
    percentiles is a bad trade."""
    ordered = sorted(values)
    n = len(ordered)
    median = statistics.median(ordered)
    lower = ordered[: n // 2]
    upper = ordered[(n + 1) // 2:]
    return statistics.median(lower), median, statistics.median(upper)


# ---------------------------------------------------------------------------
# C1 - price outliers
# ---------------------------------------------------------------------------

def price_outlier_check(session: Session, repo_root=None) -> list[Finding]:
    """Prices that sit absurdly far from the rest of their category.

    Judged per category and per side. Buy and sell are NOT pooled: §3.1 keeps
    them apart everywhere else, and a category where things are bought at 100
    and sold at 20,000 would produce a bimodal blob that flags nothing.
    """
    findings = []

    rows = session.execute(
        select(
            ShopItem.category_name,
            ShopItem.name,
            ShopItem.uex_id,
            ItemPrice.price_buy,
            ItemPrice.price_sell,
            Terminal.name,
        )
        .join(ShopItem, ItemPrice.shop_item_id == ShopItem.id)
        .join(Terminal, ItemPrice.terminal_id == Terminal.id)
    ).all()

    if not rows:
        return [Finding(
            "shop_price_outlier", None, "LIMITATION",
            "no price rows are stored, so no distribution could be built. "
            "Reported as not-performed rather than as a pass.",
        )]

    by_category = defaultdict(lambda: {"buy": [], "sell": []})
    for category, item_name, uex_id, buy, sell, terminal in rows:
        key = category or "(no category)"
        if buy is not None:
            by_category[key]["buy"].append((buy, item_name, uex_id, terminal))
        if sell is not None:
            by_category[key]["sell"].append((sell, item_name, uex_id, terminal))

    judged = flagged = 0
    for category, sides in sorted(by_category.items()):
        for side, entries in sides.items():
            if len(entries) < MIN_SAMPLE:
                if entries:
                    findings.append(Finding(
                        "shop_price_outlier", f"{category} / {side}",
                        "LIMITATION",
                        f"only {len(entries)} priced row(s) - below the "
                        f"minimum sample of {MIN_SAMPLE}, so no distribution "
                        f"was judged. NOT a pass: this category was not "
                        f"checked for outliers.",
                    ))
                continue

            judged += 1
            scaled = [_scale(e[0]) for e in entries]
            q1, med_scaled, q3 = _quartiles(scaled)
            iqr = q3 - q1
            high = q3 + IQR_MULTIPLIER * iqr
            low = q1 - IQR_MULTIPLIER * iqr
            median = statistics.median([e[0] for e in entries])

            hits = []
            for price, item_name, uex_id, terminal in entries:
                point = _scale(price)
                if point > high and median > 0 and price >= median * RATIO_FLOOR:
                    hits.append((price / median, price, item_name, uex_id,
                                 terminal, "above"))
                elif (point < low and price > 0 and median > 0
                      and price * RATIO_FLOOR <= median):
                    hits.append((price / median, price, item_name, uex_id,
                                 terminal, "below"))

            if not hits:
                continue
            flagged += len(hits)

            # One summary finding per category/side, then the most extreme
            # few individually. 590 individual findings in the first run was
            # a wall nobody would read; the count is what matters, and the
            # worst offenders are what a human would go and look at.
            hits.sort(key=lambda h: abs(1 - h[0]), reverse=True)
            findings.append(Finding(
                "shop_price_outlier", f"{category} / {side}", "WARNING",
                f"{len(hits)} of {len(entries)} priced rows sit outside a "
                f"{IQR_MULTIPLIER}x IQR fence in log space AND at least "
                f"{RATIO_FLOOR}x from the median of {median:,.0f} aUEC. "
                f"FLAG ONLY - the {min(3, len(hits))} most extreme are listed "
                f"separately.",
            ))
            for ratio, price, item_name, uex_id, terminal, direction in hits[:3]:
                described = (f"{ratio:,.1f}x" if direction == "above"
                             else f"1/{1 / ratio:,.1f} of")
                findings.append(Finding(
                    "shop_price_outlier",
                    f"{item_name} (uex_id {uex_id}) @ {terminal}",
                    "WARNING",
                    f"{side} price {price:,} aUEC is {described} the "
                    f"{category} median of {median:,.0f}, and outside the "
                    f"log-space fence. FLAG ONLY - Star Citizen genuinely "
                    f"sells very expensive things, so this is a prompt to "
                    f"look, not a confirmed error.",
                ))

    findings.append(Finding(
        "shop_price_outlier", "SUMMARY",
        "PASS" if not flagged else "WARNING",
        f"judged {judged} category/side distribution(s) over {len(rows):,} "
        f"price rows in "
        f"{'log' if USE_LOG_SCALE else 'linear'} space; {flagged:,} row(s) "
        f"({flagged / len(rows):.2%}) fell outside a {IQR_MULTIPLIER}x IQR "
        f"fence AND {RATIO_FLOOR}x from their category median.",
    ))
    return findings


# ---------------------------------------------------------------------------
# C2 - orphans
# ---------------------------------------------------------------------------

def orphan_check(session: Session, repo_root=None) -> list[Finding]:
    """Price rows whose item or terminal does not resolve, and the softer
    orphans the foreign keys cannot catch.

    THE HARD ORPHANS SHOULD ALWAYS BE ZERO, because A7 put foreign keys on all
    three columns. This checker exists anyway, for the same reason
    db_checks.referential_integrity_check does: a raw INSERT in a one-off
    migration, or a constraint dropped and not restored, would produce exactly
    this and nothing else would notice. checks/_verify_shop_checks.py proves
    it can still fire by removing a foreign key inside a rolled-back
    transaction and watching it catch the orphan.

    THE SOFT ORPHANS ARE THE ONES THAT ACTUALLY OCCUR: a terminal with no
    location, an item with no category. Those columns are nullable by design -
    §3.6, absence is data - so no constraint refuses them and only a checker
    will ever mention them.
    """
    findings = []

    orphan_items = session.execute(
        select(func.count())
        .select_from(ItemPrice)
        .outerjoin(ShopItem, ItemPrice.shop_item_id == ShopItem.id)
        .where(ShopItem.id.is_(None))
    ).scalar()
    orphan_terminals = session.execute(
        select(func.count())
        .select_from(ItemPrice)
        .outerjoin(Terminal, ItemPrice.terminal_id == Terminal.id)
        .where(Terminal.id.is_(None))
    ).scalar()

    if orphan_items:
        findings.append(Finding(
            "shop_orphan", "item_prices.shop_item_id", "DEFECT",
            f"{orphan_items:,} price row(s) point at a shop_items row that "
            f"does not exist. A foreign key should make this impossible, so "
            f"either the constraint is gone or something wrote around it.",
        ))
    if orphan_terminals:
        findings.append(Finding(
            "shop_orphan", "item_prices.terminal_id", "DEFECT",
            f"{orphan_terminals:,} price row(s) point at a terminals row that "
            f"does not exist. As above - the foreign key should prevent this.",
        ))

    # -- the soft ones ------------------------------------------------------
    unplaced = session.execute(
        select(func.count()).select_from(Terminal)
        .where(Terminal.location_id.is_(None))
    ).scalar()
    if unplaced:
        findings.append(Finding(
            "shop_orphan", "terminals.location_id", "WARNING",
            f"{unplaced:,} terminal(s) resolve to no location. They will "
            f"appear on the site with no place attached. Not a defect - the "
            f"column is nullable on purpose, because a terminal we cannot "
            f"place is better stored unplaced than given a guessed location.",
        ))

    uncategorised = session.execute(
        select(func.count()).select_from(ShopItem)
        .where(ShopItem.category_id.is_(None),
               ShopItem.source_kind == "item")
    ).scalar()
    if uncategorised:
        findings.append(Finding(
            "shop_orphan", "shop_items.category_id", "WARNING",
            f"{uncategorised:,} item(s) have no category FK. Commodities are "
            f"excluded from this count - they legitimately have none, because "
            f"UEX gives them a `kind` string and no category id.",
        ))

    if not findings:
        findings.append(Finding(
            "shop_orphan", None, "PASS",
            "every price row resolves to a real item and a real terminal; "
            "every terminal has a location; every item has a category.",
        ))
    return findings


# ---------------------------------------------------------------------------
# C3 - name collisions
# ---------------------------------------------------------------------------

def name_collision_check(session: Session, repo_root=None) -> list[Finding]:
    """How badly display names collide - the numbers §3.2 rests on.

    Reports three separate populations, because they collide at very different
    rates and averaging them would hide it:
      * item display name -> more than one shop_items row
      * item uuid         -> more than one shop_items row  (the A4 finding)
      * terminal name     -> more than one terminals row
    """
    findings = []

    # Split by source_kind FIRST. Pooling them inflates the number badly and
    # in a misleading direction: an item and a commodity sharing a name (a
    # "Gasping Weevil Eggs" item and a "Gasping Weevil Eggs" commodity) is
    # UEX describing the same real thing through two endpoints, which is a
    # completely different problem from two distinct guns sharing a name.
    for kind in ("item", "commodity"):
        rows_k = session.execute(
            select(ShopItem.name, func.count(ShopItem.id))
            .where(ShopItem.source_kind == kind)
            .group_by(ShopItem.name)
            .having(func.count(ShopItem.id) > 1)
            .order_by(func.count(ShopItem.id).desc())
        ).all()
        distinct_k = session.execute(
            select(func.count(func.distinct(ShopItem.name)))
            .where(ShopItem.source_kind == kind)
        ).scalar()
        if rows_k:
            worst_k, worst_kc = rows_k[0]
            # Examples, not just the worst case. C6 caught this: reporting
            # only "worst case 2 share X" means a NEW collision is invisible
            # unless it happens to become the worst one, and a reader is
            # given a number they cannot act on. The names are what someone
            # would go and look at.
            examples = ", ".join(f"{n!r} x{c}" for n, c in rows_k[:8])
            more = ("" if len(rows_k) <= 8
                    else f", and {len(rows_k) - 8:,} more")
            findings.append(Finding(
                "shop_name_collision", f"shop_items.name [{kind} only]",
                "WARNING",
                f"{len(rows_k):,} name(s) of {distinct_k:,} map to more than "
                f"one {kind}. Worst case {worst_kc} share {worst_k!r}. "
                f"All of them: {examples}{more}.",
            ))
        else:
            findings.append(Finding(
                "shop_name_collision", f"shop_items.name [{kind} only]",
                "PASS",
                f"all {distinct_k:,} {kind} display names are unique within "
                f"their own kind.",
            ))

    cross = session.execute(
        select(ShopItem.name)
        .group_by(ShopItem.name)
        .having(func.count(func.distinct(ShopItem.source_kind)) > 1)
    ).scalars().all()
    if cross:
        findings.append(Finding(
            "shop_name_collision", "shop_items.name [item vs commodity]",
            "LIMITATION",
            f"{len(cross):,} name(s) exist as BOTH an item and a commodity, "
            f"e.g. {', '.join(repr(c) for c in cross[:4])}. That is UEX "
            f"describing one real thing through two endpoints, not a data "
            f"defect - but anything joining on name across both kinds will "
            f"merge them.",
        ))

    name_rows = session.execute(
        select(ShopItem.name, func.count(ShopItem.id))
        .group_by(ShopItem.name)
        .having(func.count(ShopItem.id) > 1)
        .order_by(func.count(ShopItem.id).desc())
    ).all()
    total_names = session.execute(
        select(func.count(func.distinct(ShopItem.name)))
    ).scalar()

    if name_rows:
        worst_name, worst_count = name_rows[0]
        examples = ", ".join(f"{n!r} x{c}" for n, c in name_rows[:5])
        findings.append(Finding(
            "shop_name_collision", "shop_items.name", "WARNING",
            f"POOLED ACROSS BOTH KINDS: {len(name_rows):,} display name(s) "
            f"of {total_names:,} map to more than one row. Worst case "
            f"{worst_count} records share "
            f"{worst_name!r}. Examples: {examples}. This is why the UI must "
            f"disambiguate on size, then grade, then manufacturer (§3.2).",
        ))
    else:
        findings.append(Finding(
            "shop_name_collision", "shop_items.name", "PASS",
            f"all {total_names:,} item display names are unique.",
        ))

    uuid_rows = session.execute(
        select(ShopItem.uuid, func.count(ShopItem.id))
        .where(ShopItem.uuid.isnot(None))
        .group_by(ShopItem.uuid)
        .having(func.count(ShopItem.id) > 1)
        .order_by(func.count(ShopItem.id).desc())
    ).all()
    with_uuid = session.execute(
        select(func.count()).select_from(ShopItem)
        .where(ShopItem.uuid.isnot(None))
    ).scalar()
    without_uuid = session.execute(
        select(func.count()).select_from(ShopItem)
        .where(ShopItem.uuid.is_(None))
    ).scalar()

    if uuid_rows:
        worst_uuid, worst_count = uuid_rows[0]
        shared = session.execute(
            select(ShopItem.name).where(ShopItem.uuid == worst_uuid).limit(4)
        ).scalars().all()
        findings.append(Finding(
            "shop_name_collision", "shop_items.uuid", "DEFECT",
            f"{len(uuid_rows):,} uuid(s) are shared by more than one item. "
            f"Worst case {worst_count} items share {worst_uuid} - "
            f"{', '.join(repr(s) for s in shared)}. A further {without_uuid:,} "
            f"items carry no uuid at all, out of {with_uuid + without_uuid:,}. "
            f"THIS IS WHY uex_id AND NOT uuid IS THE JOIN KEY (see A4). "
            f"Recorded as a DEFECT in the SOURCE DATA, not in this database - "
            f"nothing here is broken by it, and nothing should be auto-fixed.",
        ))
    else:
        findings.append(Finding(
            "shop_name_collision", "shop_items.uuid", "PASS",
            f"every one of the {with_uuid:,} uuids present is unique "
            f"({without_uuid:,} items carry none).",
        ))

    terminal_rows = session.execute(
        select(Terminal.name, func.count(Terminal.id))
        .group_by(Terminal.name)
        .having(func.count(Terminal.id) > 1)
        .order_by(func.count(Terminal.id).desc())
    ).all()
    total_terminals = session.execute(
        select(func.count(func.distinct(Terminal.name)))
    ).scalar()
    if terminal_rows:
        worst_name, worst_count = terminal_rows[0]
        findings.append(Finding(
            "shop_name_collision", "terminals.name", "WARNING",
            f"{len(terminal_rows):,} terminal name(s) of {total_terminals:,} "
            f"are used by more than one terminal. Worst case {worst_count} "
            f"share {worst_name!r}. Terminals must be disambiguated by their "
            f"resolved location, not their name.",
        ))
    else:
        findings.append(Finding(
            "shop_name_collision", "terminals.name", "PASS",
            f"all {total_terminals:,} terminal names are unique.",
        ))

    return findings


# ---------------------------------------------------------------------------
# C4 - category price coverage
# ---------------------------------------------------------------------------

def category_coverage_check(session: Session, repo_root=None) -> list[Finding]:
    """For each category, how many of its items carry at least one price row.

    THIS IS THE ITEM THAT ANSWERS THE THRUSTER / ARMOUR / FUEL-TANK QUESTION
    WITH A NUMBER (§3.3). It is not a pass/fail check - it is a measurement
    that happens to live in the findings store, and every category gets a row
    whether its coverage is 100% or 0%.

    A category at 0% is reported as LIMITATION, not DEFECT: "nobody sells
    this" is a legitimate fact about Star Citizen, and §3.6 says the site must
    be able to say it.
    """
    findings = []

    priced = (
        select(ItemPrice.shop_item_id)
        .distinct()
        .subquery()
    )

    # DRIVEN FROM item_categories, NOT from shop_items. The order asks for
    # "each of the 100 categories", and grouping the items would silently
    # omit the 44 categories that hold no items at all - which are precisely
    # the rows a reader most needs to see, because their absence from a table
    # of 56 looks like an oversight rather than a fact.
    rows = session.execute(
        select(
            ItemCategory.uex_id,
            ItemCategory.section,
            ItemCategory.name,
            ItemCategory.is_game_related,
            func.count(func.distinct(ShopItem.id)),
            func.count(func.distinct(priced.c.shop_item_id)),
        )
        .outerjoin(ShopItem, ShopItem.category_id == ItemCategory.id)
        .outerjoin(priced, priced.c.shop_item_id == ShopItem.id)
        .group_by(ItemCategory.uex_id, ItemCategory.section,
                  ItemCategory.name, ItemCategory.is_game_related)
        .order_by(func.count(func.distinct(ShopItem.id)).desc(),
                  ItemCategory.name)
    ).all()

    # Commodities carry no category FK by design, so they would vanish from a
    # categories-driven query. Counted separately rather than dropped.
    commodity_total = session.execute(
        select(func.count()).select_from(ShopItem)
        .where(ShopItem.source_kind == "commodity")
    ).scalar()
    commodity_priced = session.execute(
        select(func.count(func.distinct(ShopItem.id)))
        .select_from(ShopItem)
        .join(priced, priced.c.shop_item_id == ShopItem.id)
        .where(ShopItem.source_kind == "commodity")
    ).scalar()

    if not rows:
        return [Finding(
            "shop_category_coverage", None, "LIMITATION",
            "no shop_items rows are stored, so coverage could not be "
            "measured. Reported as not-performed, not as a pass.",
        )]

    total_items = sum(r[4] for r in rows) + commodity_total
    total_priced = sum(r[5] for r in rows) + commodity_priced

    for uex_id, section, name, is_game, item_count, priced_count in rows:
        share = (priced_count / item_count) if item_count else 0
        subject = f"{section} / {name} (cat {uex_id})"
        game_note = "" if is_game else " NOT is_game_related."
        if item_count == 0:
            result = "LIMITATION"
            note = ("this category holds NO ITEMS in the snapshot at all - "
                    "UEX returned HTTP 200 with an empty body for it. "
                    "Coverage is undefined, not zero.")
        elif priced_count == 0:
            result = "LIMITATION"
            note = ("NOT ONE item in this category carries a price row. "
                    "That is a legitimate fact - it means nobody sells them - "
                    "and the site must be able to say so rather than showing "
                    "an empty table.")
        elif share < 0.10:
            result = "WARNING"
            note = ("under 10% coverage. Worth knowing before this category "
                    "is shown as though it had prices.")
        else:
            result = "PASS"
            note = "coverage measured."
        findings.append(Finding(
            "shop_category_coverage", subject, result,
            f"{priced_count:,} of {item_count:,} items priced "
            f"({share:.1%}).{game_note} {note}",
        ))

    findings.append(Finding(
        "shop_category_coverage", "Commodities [no category FK]",
        "PASS" if commodity_priced else "LIMITATION",
        f"{commodity_priced:,} of {commodity_total:,} commodities priced "
        f"({commodity_priced / commodity_total:.1%} ). Commodities carry no "
        f"category FK - UEX gives them a `kind` string and no category id - "
        f"so they are counted here rather than dropped from the table."
        if commodity_total else "no commodities stored.",
    ))

    findings.append(Finding(
        "shop_category_coverage", "ALL CATEGORIES", "PASS",
        f"{total_priced:,} of {total_items:,} items across {len(rows)} "
        f"declared categories plus {commodity_total:,} commodities carry at "
        f"least one price row ({total_priced / total_items:.1%} overall).",
    ))
    return findings


# ---------------------------------------------------------------------------
# C5 - staleness
# ---------------------------------------------------------------------------

def price_staleness_check(session: Session, repo_root=None) -> list[Finding]:
    """How old each price row's own source date_modified is, bucketed.

    Measured against UEX's date_modified, NOT against the snapshot capture
    time. Those are different questions: the snapshot says when we pulled, and
    date_modified says when a human last confirmed the price in game. A price
    pulled yesterday can be two years old, and it is the second number that
    tells a player whether to trust it.
    """
    findings = []
    now = datetime.datetime.now()

    total = session.execute(select(func.count()).select_from(ItemPrice)).scalar()
    if not total:
        return [Finding(
            "shop_price_staleness", None, "LIMITATION",
            "no price rows stored, so staleness could not be measured.",
        )]

    undated = session.execute(
        select(func.count()).select_from(ItemPrice)
        .where(ItemPrice.source_date_modified.is_(None))
    ).scalar()
    if undated:
        findings.append(Finding(
            "shop_price_staleness", "no source date", "WARNING",
            f"{undated:,} of {total:,} price row(s) carry no "
            f"source_date_modified at all. Their age is UNKNOWN - which is "
            f"not the same as fresh, and the front end must not present them "
            f"as either.",
        ))

    for label, low, high in STALENESS_BUCKETS:
        newest = now - datetime.timedelta(days=low)
        clause = [ItemPrice.source_date_modified <= newest]
        if high is not None:
            clause.append(
                ItemPrice.source_date_modified > now - datetime.timedelta(days=high)
            )
        count = session.execute(
            select(func.count()).select_from(ItemPrice).where(*clause)
        ).scalar()

        share = count / total
        if high is None and count:
            result = "WARNING"
            note = ("over a year old. These should be visibly flagged as "
                    "unverified wherever they are shown.")
        elif label == "181-365 days" and share > 0.25:
            result = "WARNING"
            note = f"{share:.0%} of all prices sit in this bucket."
        else:
            result = "PASS"
            note = "bucket measured."
        findings.append(Finding(
            "shop_price_staleness", label, result,
            f"{count:,} of {total:,} price rows ({share:.1%}). {note}",
        ))

    # A future date is not staleness, it is a broken date, and it would make
    # every bucket above lie by omission.
    future = session.execute(
        select(func.count()).select_from(ItemPrice)
        .where(ItemPrice.source_date_modified > now)
    ).scalar()
    if future:
        findings.append(Finding(
            "shop_price_staleness", "dated in the future", "DEFECT",
            f"{future:,} price row(s) carry a source_date_modified later than "
            f"now. That is not a stale price, it is a wrong one, and it makes "
            f"every bucket above understate the real age of the data.",
        ))

    return findings


CHECKERS = [
    ("shop_price_outlier", price_outlier_check),
    ("shop_orphan", orphan_check),
    ("shop_name_collision", name_collision_check),
    ("shop_category_coverage", category_coverage_check),
    ("shop_price_staleness", price_staleness_check),
]
