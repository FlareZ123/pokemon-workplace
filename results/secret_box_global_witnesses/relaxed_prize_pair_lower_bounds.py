"""Relax the last two forced Prizes in the Aichi Secret Box witnesses.

Supporter is forced by Tag Call x4 in Prizes; Tool and Stadium are
forced by Guzma & Hala x4 in Prizes. The other two Prize identities
are arbitrary provided they do not exhaust a required two-copy payload.

This is a mathematically certified sufficient family for the existing
compressed first-turn-core planner. It is not a probability of match wins.
"""
from collections import Counter
from fractions import Fraction
from itertools import combinations
from math import comb
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
from aichi_vileplume_als import DECK_COUNTS
from aichi_vileplume_secret_box import (
    BASE_DECK, SECRET_BOX_DECK, _raw_state, _state_succeeds,
)
from aichi_secret_box_output_dependencies import _state_succeeds_with_mask

FILLERS = {
    "Guzma", "Cassius", "Karen", "Plumeria", "Gladion", "Faba",
    "Lusamine", "Peonia", "Team Yell's Cheer", "Bellelba & Brycen-Man",
}
SUPPORTER_REQUIRED = (
    ("Oddish", "Grand Tree"),
    "Tag Call",
    5,
    frozenset({"Technical Machine: Evolution", "Jet Energy",
               "Artazon", "Bunnelby"}),
    (11,),
)
TOOL_STADIUM_REQUIRED = (
    ("Oddish", "Grand Tree", "Jet Energy"),
    "Guzma & Hala",
    4,
    frozenset({"Technical Machine: Evolution", "Artazon", "Bunnelby"}),
    (13, 7),
)


def take(names, available):
    result = []
    for name in names:
        i = next((i for i in sorted(available) if BASE_DECK[i] == name), None)
        assert i is not None, name
        result.append(i)
        available.remove(i)
    return result


def family_configuration(spec):
    fixed, forced_prize_name, fillers, targets, masks = spec
    available = set(range(60))
    opening = take(fixed, available)
    chosen_filler = [
        i for i in sorted(available) if BASE_DECK[i] in FILLERS
    ][:fillers]
    assert len(chosen_filler) == fillers
    for i in chosen_filler:
        available.remove(i)
    opening.extend(chosen_filler)
    forced_prizes = take((forced_prize_name,) * 4, available)
    assert len(available) == 49
    return opening, forced_prizes, available


def valid_extra_prizes(pair, excluded_targets):
    identities = Counter(BASE_DECK[i] for i in pair)
    return all(identities[target] < 2 for target in excluded_targets)


def replay(opening, forced_prizes, extras, draw, excluded_masks):
    used = set((*opening, *forced_prizes, *extras, draw))
    order = (
        list(opening) + list(forced_prizes) + list(extras) + [draw]
        + sorted(set(range(60)) - used)
    )
    assert len(order) == len(set(order)) == 60
    baseline = _raw_state(BASE_DECK, order)
    secret = _raw_state(SECRET_BOX_DECK, order)
    assert baseline is not None and secret is not None
    assert baseline[2] == secret[2] == "Oddish"
    assert not _state_succeeds(baseline)
    assert _state_succeeds_with_mask(secret, 15)
    for mask in excluded_masks:
        assert not _state_succeeds_with_mask(secret, mask), (extras, draw, mask)


def count_pair_weight(spec):
    """Enumerate each physical Prize pair and count available filler draws."""
    fixed, forced_name, k, target_names, masks = spec
    opening, forced_prizes, free = family_configuration(spec)
    fillers_left = {i for i in free if BASE_DECK[i] in FILLERS}
    assert len(fillers_left) == 11 - k
    pairs = 0
    draw_weight = 0
    for pair in combinations(sorted(free), 2):
        if not valid_extra_prizes(pair, target_names):
            continue
        eligible = sorted(fillers_left.difference(pair))
        assert eligible
        replay(opening, forced_prizes, pair, eligible[0], masks)
        pairs += 1
        draw_weight += len(eligible)
    expected_pairs = comb(49, 2) - len(target_names)
    expected_weight = (
        (11 - k) * comb(49, 2)
        - (11 - k) * 48
        - (11 - k) * len(target_names)
    )
    assert pairs == expected_pairs
    assert draw_weight == expected_weight, (draw_weight, expected_weight)
    return pairs, draw_weight


def main():
    n_s, w_s = count_pair_weight(SUPPORTER_REQUIRED)
    n_t, w_t = count_pair_weight(TOOL_STADIUM_REQUIRED)
    assert (n_s, w_s) == (1172, 6744)
    assert (n_t, w_t) == (1173, 7875)
    acceptance = 1 - Fraction(comb(46, 7), comb(60, 7))
    s = (
        Fraction(DECK_COUNTS["Oddish"] * comb(11, 5), comb(60, 7))
        * Fraction(w_s, comb(53, 6) * 47) / acceptance
    )
    t = (
        Fraction(DECK_COUNTS["Oddish"] * DECK_COUNTS["Jet Energy"]
                 * comb(11, 4), comb(60, 7))
        * Fraction(w_t, comb(53, 6) * 47) / acceptance
    )
    assert s == Fraction(843, 48561235923200)
    assert t == Fraction(225, 7769797747712)
    # The previous fixed Pidgeotto/Gloom Prize families are strict subsets.
    assert s / Fraction(3, 48561235923200) == 281
    assert t / Fraction(1, 9712247184640) == Fraction(1125, 4)
    print("Supporter required; checked Prize-pairs:", n_s,
          "weighted first draws:", w_s, "exact lower bound:", s, float(s))
    print("Tool and Stadium required; checked Prize-pairs:", n_t,
          "weighted first draws:", w_t, "exact lower bound:", t, float(t))
    print("All relaxed-Prize-pair lower-bound checks passed.")


if __name__ == "__main__":
    main()
