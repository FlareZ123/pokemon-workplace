"""Exhaustive grouped proof for the two relaxed Aichi Secret Box families.

Instead of multiplying millions of physical opening-filler, variable-Prize,
and draw combinations, enumerate their exact compressed hand/deck states.
Each group state's integer multiplicity is the number of physical layouts
it represents. This is exhaustive for the source planner: only these grouped
hand/deck counters and the fixed Active choice influence its decision.
"""
from collections import Counter
from fractions import Fraction
from itertools import combinations_with_replacement
from math import comb
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
from aichi_vileplume_als import DECK_COUNTS
from aichi_vileplume_secret_box import (
    BASE_DECK, DECK_NAMES, DECK_INDEX,
    _compress_hand, _compress_deck, _core_possible,
)

UNUSED = len(DECK_NAMES)
OTHER_SUPPORTER = DECK_INDEX["supporter_other"]
OTHER_TAG_TEAM = DECK_INDEX["tag_team_other"]
FILLER_OUTPUTS = (OTHER_SUPPORTER, OTHER_TAG_TEAM)


def physical_group_stocks(fixed_opening, forced_name, k, bellelba_held):
    """Stock after opener and four forced Prizes, before the last two."""
    stock = list(_compress_deck(BASE_DECK))
    assert len(stock) == UNUSED
    for name in (*fixed_opening, *((forced_name,) * 4)):
        remove = _compress_deck([name])
        stock = [a - b for a, b in zip(stock, remove)]
    # All ten other Supporter cards are a single compressed deck category;
    # the sole Bellelba is its own TAG TEAM category.
    stock[OTHER_TAG_TEAM] -= bellelba_held
    stock[OTHER_SUPPORTER] -= k - bellelba_held
    assert min(stock) >= 0
    unused_cards = 49 - sum(stock)
    assert unused_cards >= 0
    return tuple((*stock, unused_cards))


def compressed_hand(fixed_opening, k, secret_box):
    """Remove Active Oddish; all k+1 discarded filler sources compress as other."""
    assert fixed_opening[0] == "Oddish"
    names = list(fixed_opening[1:])
    if secret_box:
        names[names.index("Grand Tree")] = "Secret Box"
    return _compress_hand((*names, *(("Guzma",) * (k + 1))))


def count_exact_grouped_family(label, fixed_opening, forced_name, k,
                               needed, missing_masks, expected_weight,
                               fixed_copy_ways, expected_probability):
    h_base = compressed_hand(fixed_opening, k, False)
    h_box = compressed_hand(fixed_opening, k, True)
    cases = 0
    total_weight = 0
    pair_weight = 0
    unique_signatures = set()
    source_categories = tuple(range(UNUSED + 1))

    for b in (0, 1):
        if b > k:
            continue
        opener_ways = comb(1, b) * comb(10, k - b)
        if not opener_ways:
            continue
        stock = physical_group_stocks(fixed_opening, forced_name, k, b)
        assert len(stock) == UNUSED + 1
        for x, y in combinations_with_replacement(source_categories, 2):
            copies = comb(stock[x], 2) if x == y else stock[x] * stock[y]
            if copies == 0:
                continue
            after_prizes = list(stock)
            after_prizes[x] -= 1
            after_prizes[y] -= 1
            if any(after_prizes[DECK_INDEX[name]] == 0 for name in needed):
                continue
            pair_weight += opener_ways * copies
            for draw_group in FILLER_OUTPUTS:
                draw_ways = after_prizes[draw_group]
                if draw_ways == 0:
                    continue
                after_draw = after_prizes.copy()
                after_draw[draw_group] -= 1
                d = tuple(after_draw[:UNUSED])
                signature = (h_base, h_box, d)
                unique_signatures.add(signature)
                base = (h_base, d, False, False, False, False, False)
                box = (h_box, d, False, False, False, False, False)
                outcomes = (
                    _core_possible(base),
                    _core_possible(box, 15),
                    *(_core_possible(box, m) for m in missing_masks),
                )
                assert outcomes == (False, True) + (False,) * len(missing_masks), (
                    label, b, x, y, draw_group, outcomes
                )
                total_weight += opener_ways * copies * draw_ways
                cases += 1

    assert total_weight == comb(11, k) * expected_weight, (
        label, total_weight, expected_weight
    )
    assert pair_weight == comb(11, k) * (comb(49, 2) - len(needed)), (
        label, pair_weight
    )
    acceptance = 1 - Fraction(comb(46, 7), comb(60, 7))
    probability = (
        Fraction(fixed_copy_ways * total_weight,
                 comb(60, 7) * comb(53, 6) * 47) / acceptance
    )
    assert probability == expected_probability, (label, probability)
    print(label)
    print("  grouped branches checked:", cases)
    print("  distinct compressed states checked:", len(unique_signatures))
    print("  weighted physical filler/prize/draw configurations:", total_weight)
    print("  probability conditional on accepted opening:", probability)
    return probability


def main():
    s = count_exact_grouped_family(
        "Supporter-required",
        ("Oddish", "Grand Tree"),
        "Tag Call", 5,
        ("tm_evolution", "jet_energy", "artazon", "bunnelby"),
        (11,), 6744, DECK_COUNTS["Oddish"],
        Fraction(843, 48561235923200),
    )
    t = count_exact_grouped_family(
        "Tool-and-Stadium-required",
        ("Oddish", "Grand Tree", "Jet Energy"),
        "Guzma & Hala", 4,
        ("tm_evolution", "artazon", "bunnelby"),
        (13, 7), 7875,
        DECK_COUNTS["Oddish"] * DECK_COUNTS["Jet Energy"],
        Fraction(225, 7769797747712),
    )
    assert 0 < s < t
    print("Complete compressed cross-product certificate passed.")


if __name__ == "__main__":
    main()
