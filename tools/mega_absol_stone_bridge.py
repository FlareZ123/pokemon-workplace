"""Prize-aware Forest Seal Stone bridge for Aichi Mega Absol ex/Garbodor.

Restricts the first turn to a single independently payable named Item route,
or a Forest Seal Stone VSTAR Power mounted on Crobat V already held (or
recovered from Prizes by the same one Hisuian Heavy Ball). Adventure Bag
may find Forest Seal Stone if that Tool is still in the deck.

Assumes Tool slot, Bench, VSTAR Power, Abilities and Items are available.
No Crobat draw, action chains, opponent effects, or match outcomes are modeled.
"""
from __future__ import annotations

from collections import Counter
from fractions import Fraction
from itertools import combinations
from math import comb

from tools.mega_absol_named_item_access import (
    CATEGORIES as BASE_CATEGORIES,
    _hands,
    _route_flags,
    category_counts as base_category_counts,
)

CROBAT = "swsh3-104"
STONE = "swsh12-156"
BAG = "sm8-167"
CATEGORIES = (
    "mega", "other_basic", "crobat", "evolution", "quick_ball",
    "ultra_ball", "vip_pass", "communication", "heavy_ball",
    "energy", "stone", "bag", "filler",
)
POLICIES = (
    "named_paid", "stone_held_crobat", "stone_prize_crobat",
    "stone_any", "named_or_stone", "crobat_held", "stone_ready",
)


def category_counts(quantities: dict[str, int], records: dict) -> dict[str, int]:
    """Partition each exact physical card copy without double-counting."""
    old = base_category_counts(quantities, records)
    crobat = quantities.get(CROBAT, 0)
    stone = quantities.get(STONE, 0)
    bag = quantities.get(BAG, 0)
    assert records[CROBAT].is_basic_pokemon
    assert records[STONE].supertype == "Trainer"
    assert records[BAG].supertype == "Trainer"
    assert old["other_basic"] >= crobat
    assert old["filler"] >= stone + bag
    old["other_basic"] -= crobat
    old["filler"] -= stone + bag
    out = {
        name: (crobat if name == "crobat" else
               stone if name == "stone" else
               bag if name == "bag" else old[name])
        for name in CATEGORIES
    }
    assert sum(out.values()) == 60
    return out


def route_flags(
    full: dict[str, int],
    prized: dict[str, int],
    capacities: dict[str, int],
) -> dict[str, bool]:
    """Feasible independent routes under the stated strict payment policy."""
    original = {name: full[name] for name in BASE_CATEGORIES}
    original["other_basic"] += full["crobat"]
    original["_total_mega"] = capacities["mega"]
    named_paid = _route_flags(original, prized["mega"])["energy_paid"]

    # The Tool may already be held, or Adventure Bag can find it in deck.
    # Forest Seal Stone grants Star Alchemy only to a Pokémon V.
    stone_ready = full["stone"] > 0 or (
        full["bag"] > 0 and prized["stone"] == 0
    )
    mega_in_deck = full["mega"] + prized["mega"] < capacities["mega"]
    held = mega_in_deck and stone_ready and full["crobat"] > 0
    prize = (
        mega_in_deck and stone_ready and full["crobat"] == 0
        and prized["crobat"] > 0 and full["heavy_ball"] > 0
    )
    return {
        "named_paid": named_paid,
        "stone_held_crobat": held,
        "stone_prize_crobat": prize,
        "stone_any": held or prize,
        "named_or_stone": named_paid or held or prize,
        "crobat_held": full["crobat"] > 0,
        "stone_ready": stone_ready,
    }


def exact_access(
    capacities: dict[str, int], opening: int = 7, prizes: int = 6,
) -> dict[str, Fraction]:
    assert tuple(capacities) == CATEGORIES
    n = sum(capacities.values())
    assert 0 < opening < n - prizes
    assert capacities["mega"] > 0
    scores = Counter()
    accepted = 0
    prize_denominator = comb(n - opening - 1, prizes)

    # First draw before Prize enumeration is an exchangeable reordering of
    # the physical experiment hand -> Prizes -> first natural draw.
    for start, initial_weight in _hands(capacities, opening):
        if start["mega"] + start["other_basic"] + start["crobat"] == 0:
            continue
        for drawn in CATEGORIES:
            available = capacities[drawn] - start[drawn]
            if not available:
                continue
            full = start.copy()
            full[drawn] += 1
            weight = initial_weight * available
            accepted += weight
            rem = {name: capacities[name] - full[name] for name in CATEGORIES}
            other = n - opening - 1 - rem["mega"] - rem["crobat"] - rem["stone"]
            for pm in range(min(prizes, rem["mega"]) + 1):
                for pc in range(min(prizes - pm, rem["crobat"]) + 1):
                    for ps in range(min(prizes - pm - pc, rem["stone"]) + 1):
                        rest = prizes - pm - pc - ps
                        if rest > other:
                            continue
                        prize_weight = (
                            comb(rem["mega"], pm) * comb(rem["crobat"], pc)
                            * comb(rem["stone"], ps) * comb(other, rest)
                        )
                        flags = route_flags(
                            full, {"mega": pm, "crobat": pc, "stone": ps},
                            capacities,
                        )
                        for name in POLICIES:
                            scores[name] += weight * prize_weight * flags[name]
    denominator = accepted * prize_denominator
    assert denominator > 0
    return {name: Fraction(scores[name], denominator) for name in POLICIES}


def physical_oracle(
    capacities: dict[str, int], opening: int, prizes: int,
) -> dict[str, Fraction]:
    """Independent labeled-card enumeration in the actual deal order."""
    assert tuple(capacities) == CATEGORIES
    cards = [name for name in CATEGORIES for _ in range(capacities[name])]
    n = len(cards)
    scores = Counter()
    worlds = 0
    for opening_ids in combinations(range(n), opening):
        held = Counter(cards[i] for i in opening_ids)
        if held["mega"] + held["other_basic"] + held["crobat"] == 0:
            continue
        hand_ids = set(opening_ids)
        rest = [i for i in range(n) if i not in hand_ids]
        for prize_ids in combinations(rest, prizes):
            prize_set = set(prize_ids)
            prized = Counter(cards[i] for i in prize_ids)
            for draw_id in rest:
                if draw_id in prize_set:
                    continue
                full = {name: held[name] for name in CATEGORIES}
                full[cards[draw_id]] += 1
                flags = route_flags(full, prized, capacities)
                scores.update({name: int(flags[name]) for name in POLICIES})
                worlds += 1
    return {name: Fraction(scores[name], worlds) for name in POLICIES}
