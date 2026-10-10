"""Exact all-six-Prize Jirachi -> Box Item-output dominance certificate.

For every valid grouped opening where Jirachi starts Active, Box is absent
from opener and first draw, and Stellar Wish reveals Box among top five,
check that the Aichi first-turn-core succeeds with full Box iff it succeeds
with Item output disabled. This checks beyond the earlier incremental-only
filter and carries exact labeled physical-state multiplicities.
"""
from fractions import Fraction
from math import comb
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))

from exact_six_prize_item_necessity import (
    ACE, JIR, COUNTS, STELLAR,
    composition, physical_combinations, top_masks,
    state, picked_state, possible, UNSEEN_TOP,
)


def can_succeed(opening, draw, top_mask, box_outputs):
    raw = state(opening, draw, "Jirachi", True)
    assert not raw[0][5]  # Secret Box absent initially.
    # Jirachi may pick no card or one of the present Stellar Trainers.
    picks = [None] + [
        category for bit, category in enumerate(STELLAR)
        if top_mask & (1 << bit)
    ]
    return any(
        possible(raw if pick is None else picked_state(raw, pick), box_outputs)
        for pick in picks
    )


def main():
    full_mass = 0
    no_item_mass = 0
    attainable_states = 0
    discordant_states = 0
    observation_groups = 0
    for opening in composition(7):
        if not opening[JIR] or opening[ACE]:
            continue
        hand_ways = physical_combinations(opening)
        for draw, count in enumerate(COUNTS):
            available = count - opening[draw]
            if draw == ACE or available <= 0:
                continue
            leftover = tuple(
                count - opening[i] - int(draw == i)
                for i, count in enumerate(COUNTS)
            )
            assert leftover[ACE] == 1
            for top_mask, presence_ways in top_masks(
                tuple(leftover[i] for i in STELLAR)
            ):
                if not top_mask & 8:
                    continue
                w = hand_ways * available * presence_ways
                full = can_succeed(opening, draw, top_mask, 15)
                no_item = can_succeed(opening, draw, top_mask, 14)
                full_mass += w * int(full)
                no_item_mass += w * int(no_item)
                attainable_states += w
                discordant_states += w * int(full != no_item)
                observation_groups += 1

    assert observation_groups > 0
    assert attainable_states > 0 and full_mass > 0
    assert discordant_states == 0
    assert full_mass == no_item_mass
    denominator = (comb(54, 7) - comb(40, 7)) * 47 * UNSEEN_TOP
    print("Distinct grouped Stellar observations:", observation_groups)
    print("Stellar-only Box-access probability conditional on six Prizes",
          "and valid opener:", Fraction(attainable_states, denominator))
    print("Full-output success given that access:",
          Fraction(full_mass, attainable_states))
    print("No-Item output success given that access:",
          Fraction(no_item_mass, attainable_states))
    print("Distinct disagreements:", discordant_states)
    print("Exact Jirachi-only Item-output dominance passed.")


if __name__ == "__main__":
    main()
