"""Adversarially sample the all-six-Prized Item-payment witness family.

Force exactly these six Prizes: 3 Stealthy Hood, Counter Gain, 2 Artazon.
Force both TM Evolution, one Bunnelby, one Oddish, and the ACE slot into
the opening seven. Restrict two filler draws and the first turn draw to
cards compressed as generic disposable material by the Aichi core planner.

This is a *stratified counterexample family*, not an unconditional Monte
Carlo estimate. Exact combinatorial probability of the stratum is provided.
"""

from collections import Counter
from fractions import Fraction
from math import comb
from pathlib import Path
import random
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))

from accepted_opening_prize_probabilities import (
    fixed_nonbasic_prized_given_valid_opener,
)
from aichi_vileplume_als import BASICS
from aichi_secret_box_output_dependencies import _state_succeeds_with_mask
from aichi_vileplume_secret_box import (
    BASE_DECK, SECRET_BOX_DECK, _raw_state, _state_succeeds,
)


PRIZES = (
    "Stealthy Hood", "Stealthy Hood", "Stealthy Hood",
    "Counter Gain", "Artazon", "Artazon",
)
FORCED_OPENING = (
    "Oddish", "Grand Tree", "Bunnelby",
    "Technical Machine: Evolution", "Technical Machine: Evolution",
)
BANNED_GENERIC = {
    "Jet Energy", "Tag Call", "Guzma & Hala", "Jirachi",
    "Bunnelby", "Fan Rotom", "Bellelba & Brycen-Man",
}


def pick_indices(names: tuple[str, ...], available: set[int]) -> list[int]:
    result = []
    for name in names:
        index = next(
            (i for i in sorted(available) if BASE_DECK[i] == name),
            None,
        )
        if index is None:
            raise AssertionError(f"Missing named card: {name}")
        result.append(index)
        available.remove(index)
    return result


def main(trials: int = 5_000) -> None:
    free = set(range(60))
    prized = pick_indices(PRIZES, free)
    opening_forced = pick_indices(FORCED_OPENING, free)
    generic = [
        i for i in sorted(free)
        if BASE_DECK[i] not in BANNED_GENERIC
    ]
    assert len(prized) == 6 and len(opening_forced) == 5
    assert set(prized).isdisjoint(opening_forced)

    # Given all six nonBasic Prizes, the opening is a uniform 7-subset
    # of the remaining 54; its first draw is uniform from the other 47.
    m = len(generic)
    valid_given_prizes = 1 - Fraction(comb(40, 7), comb(54, 7))
    stratum_conditional = (
        Fraction(comb(m, 2), comb(54, 7))
        * Fraction(m - 2, 47) / valid_given_prizes
    )
    prize_probability = fixed_nonbasic_prized_given_valid_opener(
        cards=60, basics=14, opening=7, prizes=6,
        forced_nonbasic=6,
    )
    full_joint_probability = prize_probability * stratum_conditional

    rng = random.Random(20261010)
    outcomes = Counter()
    for _ in range(trials):
        extras = rng.sample(generic, 3)
        opener = opening_forced + extras[:2]
        rng.shuffle(opener)
        draw = extras[2]
        rest = list(free.difference(extras))
        rng.shuffle(rest)
        shuffled_prizes = prized.copy()
        rng.shuffle(shuffled_prizes)
        order = opener + shuffled_prizes + [draw] + rest

        assert len(order) == len(set(order)) == 60
        base = _raw_state(BASE_DECK, order)
        secret = _raw_state(SECRET_BOX_DECK, order)
        assert base is not None and secret is not None
        baseline = _state_succeeds(base)
        full = _state_succeeds_with_mask(secret, 15)
        without_item = _state_succeeds_with_mask(secret, 14)
        with_item_only = _state_succeeds_with_mask(secret, 1)
        outcomes[(baseline, full, without_item, with_item_only)] += 1

    print("Generic physical card stock:", m)
    print("Accepted-opening conditional family probability given Prizes:",
          stratum_conditional, float(stratum_conditional))
    print("Exact joint accepted-opening family probability:",
          full_joint_probability, float(full_joint_probability))
    print("Outcome (baseline,full,no-item,item-only) counts:",
          dict(outcomes))
    assert sum(outcomes.values()) == trials
    assert outcomes[(False, True, False, True)] == trials, outcomes
    print("Stratified Item-payment family stress test passed.")


if __name__ == "__main__":
    main()
