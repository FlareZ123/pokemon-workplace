"""Joint physical Mega Absol / Crobat V / Forest Seal Stone route model.

A source-verified Crobat V may use Star Alchemy from Forest Seal Stone
held directly or acquired with Adventure Bag. All routes are prelock,
one-turn, unlocked, and conditional on Basic-valid openings.
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
)

CATEGORIES = (
    "mega", "other_basic", "crobat", "evolution", "quick_ball",
    "ultra_ball", "vip_pass", "communication", "heavy_ball",
    "energy", "forest_seal_stone", "adventure_bag", "filler",
)
EXACT_IDS = {
    "mega": "me1-86",
    "crobat": "swsh3-104",
    "quick_ball": "swsh1-179",
    "ultra_ball": "swsh9-150",
    "vip_pass": "swsh8-225",
    "communication": "sm9-152",
    "heavy_ball": "swsh10-146",
    "forest_seal_stone": "swsh12-156",
    "adventure_bag": "sm8-167",
}
OUTPUTS = (
    "direct", "paid_item", "seal_route",
    "seal_increment", "paid_plus_seal",
)


def category_counts(quantities: dict[str, int], records: dict) -> dict[str, int]:
    by_id = {card_id: kind for kind, card_id in EXACT_IDS.items()}
    result = Counter({kind: 0 for kind in CATEGORIES})
    for card_id, count in quantities.items():
        if card_id in by_id:
            kind = by_id[card_id]
        elif records[card_id].is_basic_pokemon:
            kind = "other_basic"
        elif records[card_id].supertype == "Pokémon":
            kind = "evolution"
        elif records[card_id].supertype == "Energy":
            kind = "energy"
        else:
            kind = "filler"
        result[kind] += count
    assert sum(result.values()) == 60
    return dict(result)


def project_named_categories(cap: dict[str, int]) -> dict[str, int]:
    projected = {name: cap[name] for name in BASE_CATEGORIES}
    projected["other_basic"] += cap["crobat"]
    projected["filler"] += cap["forest_seal_stone"] + cap["adventure_bag"]
    return projected


def _flags(
    visible: dict[str, int],
    mega_prized: int,
    stone_prized: int,
    mega_total: int,
    stone_total: int,
) -> dict[str, bool]:
    named = project_named_categories(visible)
    named["_total_mega"] = mega_total
    routes = _route_flags(named, mega_prized)
    paid = routes["energy_paid"]
    target_in_deck = mega_total - visible["mega"] - mega_prized > 0
    stone_in_deck = stone_total - visible["forest_seal_stone"] - stone_prized > 0
    stone_available = (
        visible["forest_seal_stone"] > 0
        or visible["adventure_bag"] > 0 and stone_in_deck
    )
    # The only Pokémon V in the original list is Crobat V.
    seal = visible["crobat"] > 0 and stone_available and target_in_deck
    return {
        "direct": routes["direct"],
        "paid_item": paid,
        "seal_route": seal,
        "seal_increment": seal and not paid,
        "paid_plus_seal": seal or paid,
    }


def exact_access(
    capacities: dict[str, int], opening: int = 7, prizes: int = 6
) -> dict[str, Fraction]:
    assert set(capacities) == set(CATEGORIES)
    n = sum(capacities.values())
    assert 0 < opening < n - prizes
    mega_total = capacities["mega"]
    stone_total = capacities["forest_seal_stone"]
    assert mega_total > 0
    accepted_weight = 0
    scores = Counter({name: 0 for name in OUTPUTS})
    prize_denominator = comb(n - opening - 1, prizes)

    for hand, ways in _hands(capacities, opening):
        if hand["mega"] + hand["other_basic"] + hand["crobat"] == 0:
            continue
        for draw_type in CATEGORIES:
            if hand[draw_type] >= capacities[draw_type]:
                continue
            shown = hand.copy()
            shown[draw_type] += 1
            weight = ways * (capacities[draw_type] - hand[draw_type])
            accepted_weight += weight
            m_remaining = mega_total - shown["mega"]
            s_remaining = stone_total - shown["forest_seal_stone"]
            other_remaining = n - opening - 1 - m_remaining - s_remaining
            for k_m in range(min(m_remaining, prizes) + 1):
                for k_s in range(min(s_remaining, prizes - k_m) + 1):
                    prize_weight = (
                        comb(m_remaining, k_m)
                        * comb(s_remaining, k_s)
                        * comb(other_remaining, prizes - k_m - k_s)
                    )
                    flags = _flags(shown, k_m, k_s, mega_total, stone_total)
                    scores.update({
                        name: weight * prize_weight * int(flags[name])
                        for name in OUTPUTS
                    })

    denominator = accepted_weight * prize_denominator
    return {
        "valid_opening": Fraction(
            accepted_weight, comb(n, opening) * (n - opening)
        ),
        **{name: Fraction(scores[name], denominator) for name in OUTPUTS},
    }


def physical_oracle(
    capacities: dict[str, int], opening: int, prizes: int
) -> dict[str, Fraction]:
    # Exhaustive independent physically labeled deal order: hand, Prizes, draw.
    card_kinds = [
        name for name in CATEGORIES for _ in range(capacities[name])
    ]
    n = len(card_kinds)
    accepted_hands = 0
    accepted_worlds = 0
    hits = Counter({name: 0 for name in OUTPUTS})
    for hand in combinations(range(n), opening):
        observed = Counter(card_kinds[i] for i in hand)
        if observed["mega"] + observed["other_basic"] + observed["crobat"] == 0:
            continue
        accepted_hands += 1
        hand_ids = set(hand)
        remaining = [i for i in range(n) if i not in hand_ids]
        for prizes_tuple in combinations(remaining, prizes):
            prize_set = set(prizes_tuple)
            prize_count = Counter(card_kinds[i] for i in prizes_tuple)
            for next_draw in remaining:
                if next_draw in prize_set:
                    continue
                full = Counter(observed)
                full[card_kinds[next_draw]] += 1
                flags = _flags(
                    {name: full[name] for name in CATEGORIES},
                    prize_count["mega"], prize_count["forest_seal_stone"],
                    capacities["mega"], capacities["forest_seal_stone"],
                )
                hits.update(name for name in OUTPUTS if flags[name])
                accepted_worlds += 1

    return {
        "valid_opening": Fraction(accepted_hands, comb(n, opening)),
        **{name: Fraction(hits[name], accepted_worlds) for name in OUTPUTS},
    }
