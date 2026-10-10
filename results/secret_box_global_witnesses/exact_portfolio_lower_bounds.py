"""Exact accepted-opening lower bounds for all Secret Box output categories.

Each of three disjoint event families forces baseline failure and full-Box
success in the Aichi first-turn-core planner. Counts are combinatorial over
physical card identities; the outcome solver only consumes card names.

The Item family extends the previously exhausted 35-card filler family to
either physical Oddish and either physical Bunnelby (4x larger measure).
"""
from collections import Counter
from fractions import Fraction
from itertools import combinations
from math import comb
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from aichi_vileplume_als import BASICS, DECK_COUNTS
from aichi_vileplume_secret_box import (
    BASE_DECK, SECRET_BOX_DECK, _raw_state, _state_succeeds,
)
from aichi_secret_box_output_dependencies import _state_succeeds_with_mask
from stratified_item_payment_tail import (
    BANNED_GENERIC, FORCED_OPENING, PRIZES, pick_indices,
)

FILLERS = {
    "Guzma", "Cassius", "Karen", "Plumeria", "Gladion", "Faba",
    "Lusamine", "Peonia", "Team Yell's Cheer", "Bellelba & Brycen-Man",
}
SUPPORTER_PRIZES = ("Tag Call",) * 4 + ("Pidgeotto", "Gloom")
TOOL_STADIUM_PRIZES = ("Guzma & Hala",) * 4 + ("Pidgeotto", "Gloom")


def accepted_probability() -> Fraction:
    b = sum(DECK_COUNTS[name] for name in BASICS)
    assert b == 14 and sum(DECK_COUNTS.values()) == 60
    return 1 - Fraction(comb(60 - b, 7), comb(60, 7))


def physical_order(prizes, fixed_opening, filler_opening, draw):
    """Deterministically construct a complete real-card permutation."""
    available = set(range(60))
    prized_ids = pick_indices(tuple(prizes), available)
    fixed_ids = pick_indices(tuple(fixed_opening), available)
    assert all(i in available for i in (*filler_opening, draw))
    assert draw not in filler_opening
    for i in (*filler_opening, draw):
        available.remove(i)
    order = fixed_ids + list(filler_opening) + prized_ids + [draw] + sorted(available)
    assert len(order) == len(set(order)) == 60
    return order


def check_forced_family(label, prizes, fixed_opening, filler_count, forbidden_masks):
    """Exhaustively vary a conservative safe physical discard-filler class."""
    available = set(range(60))
    pick_indices(tuple(prizes), available)
    pick_indices(tuple(fixed_opening), available)
    generic = tuple(i for i in sorted(available) if BASE_DECK[i] in FILLERS)
    assert len(generic) == 11 and len(set(generic)) == 11
    assert not any(BASE_DECK[i] in BASICS for i in generic)
    cases = 0
    for filler in combinations(generic, filler_count):
        for draw in generic:
            if draw in filler:
                continue
            order = physical_order(prizes, fixed_opening, filler, draw)
            baseline = _raw_state(BASE_DECK, order)
            secret = _raw_state(SECRET_BOX_DECK, order)
            assert baseline is not None and secret is not None
            assert baseline[2] == secret[2] == "Oddish"
            outcomes = (
                _state_succeeds(baseline),
                _state_succeeds_with_mask(secret, 15),
                *(_state_succeeds_with_mask(secret, m) for m in forbidden_masks),
            )
            assert outcomes == (False, True) + (False,) * len(forbidden_masks), (
                label, filler, draw, outcomes
            )
            cases += 1
    expected = comb(11, filler_count) * (11 - filler_count)
    assert cases == expected
    print(label, "distinct physical filler/draw combinations:", cases)


def main():
    check_forced_family(
        "Supporter indispensable", SUPPORTER_PRIZES,
        ("Oddish", "Grand Tree"), 5, (11,),
    )
    check_forced_family(
        "Tool and Stadium each indispensable", TOOL_STADIUM_PRIZES,
        ("Oddish", "Grand Tree", "Jet Energy"), 4, (13, 7),
    )

    # The prior exhaustive test establishes the Item family's outcomes for
    # the 35 generic stock. Swapping either physically identical Basic
    # changes no named-card Counter, Active identity or lookup count.
    assert DECK_COUNTS["Oddish"] == DECK_COUNTS["Bunnelby"] == 2
    free = set(range(60))
    pick_indices(PRIZES, free)
    fixed = pick_indices(FORCED_OPENING, free)
    generic_item = tuple(i for i in free if BASE_DECK[i] not in BANNED_GENERIC)
    assert len(generic_item) == 35
    sample = tuple(sorted(generic_item)[:3])
    canonical = physical_order(PRIZES, FORCED_OPENING, sample[:2], sample[2])
    named = _raw_state(SECRET_BOX_DECK, canonical)
    assert named is not None
    assert not _state_succeeds(_raw_state(BASE_DECK, canonical))
    assert _state_succeeds_with_mask(named, 15)
    assert not _state_succeeds_with_mask(named, 14)

    # Event ordering: six Prize cards, seven starting cards, then one draw.
    # Opening validity is guaranteed for each constructed event.
    a = accepted_probability()
    prize_four_plus_two = Fraction(
        DECK_COUNTS["Pidgeotto"] * DECK_COUNTS["Gloom"], comb(60, 6)
    )
    supporter = (
        prize_four_plus_two
        * Fraction(DECK_COUNTS["Oddish"] * comb(11, 5), comb(54, 7))
        * Fraction(11 - 5, 47) / a
    )
    tool_stadium = (
        prize_four_plus_two
        * Fraction(DECK_COUNTS["Oddish"] * DECK_COUNTS["Jet Energy"]
                   * comb(11, 4), comb(54, 7))
        * Fraction(11 - 4, 47) / a
    )
    item = (
        Fraction(1, comb(60, 6))
        * Fraction(DECK_COUNTS["Oddish"] * DECK_COUNTS["Bunnelby"]
                   * comb(35, 2), comb(54, 7))
        * Fraction(33, 47) / a
    )
    assert supporter == Fraction(3, 48561235923200)
    assert tool_stadium == Fraction(1, 9712247184640)
    assert item == Fraction(1, 4570469263360)
    assert item == 4 * Fraction(1, 18281877053440)

    # The three event families have mutually incompatible fixed Prize sets.
    # If an output is disabled, its associated event contributes a distinct
    # strictly positive loss relative to the full-output model.
    for mask in range(15):
        guaranteed_loss = sum(
            p for necessary, p in ((4, supporter), (2, tool_stadium),
                                    (8, tool_stadium), (1, item))
            if necessary & mask != necessary
        )
        # Tool and Stadium rely on the *same* event, so count once.
        if mask & 10 != 10:
            guaranteed_loss -= (
                tool_stadium
                if mask & 2 == 0 and mask & 8 == 0 else 0
            )
        assert guaranteed_loss > 0, mask

    for name, p in (
        ("Supporter", supporter), ("Tool or Stadium", tool_stadium),
        ("Item", item),
    ):
        print(name, "exact accepted-opening lower bound:", p, float(p))
    print("All exact-output-family tests passed.")


if __name__ == "__main__":
    main()
