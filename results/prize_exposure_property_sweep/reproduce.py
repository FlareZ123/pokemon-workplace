"""Seeded adversarial physical-oracle sweep across the Prize deck draw kernels.

Every case constructs an explicit five-card physical deck with unique instance
IDs, enumerates all 5!=120 permutations independently, conditions on a
randomly selected set of observed prefix positions, and cross-validates the
grouped dynamic programs against direct labeled-card enumeration.
"""

from collections import Counter
from itertools import permutations
from math import isclose
from pathlib import Path
from random import Random
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from prize_position_top_swap import PrizePositionTopBelief
from prize_top_draw_pool import PrizePoolBelief
from prize_deck_prefix import PrizeDeckPrefixBelief
from prize_prefix_draw_exposure import probability_target_exposure
from prize_joint_draw_requirements import probability_joint_draw_requirements
from prize_resource_allocation_exposure import probability_allocatable_draws


def close(actual, expected, case):
    assert isclose(actual, expected, abs_tol=1e-12), (
        f"case {case}: {actual} != {expected}"
    )


def brute_allocatable(cards, profiles, required):
    states = {(0,) * len(required)}
    for card in cards:
        options = profiles.get(card, ()) + ((0,) * len(required),)
        next_states = set()
        for state in states:
            for option in options:
                next_states.add(tuple(
                    min(required[i], state[i] + option[i])
                    for i in range(len(required))
                ))
        states = next_states
    return required in states


def main():
    rng = Random(20261010)
    group_order = ("P", "E", "FLEX", "X")
    roles = {
        "P": ((1, 0),),
        "E": ((0, 1),),
    }
    cases = 220

    for number in range(cases):
        card_groups = [
            "P", "E",
            *(rng.choice(group_order) for _ in range(3)),
        ]
        counts = {
            group: card_groups.count(group)
            for group in group_order if group in card_groups
        }
        labels = tuple(permutations(range(5)))
        physical_deals = tuple(
            tuple(card_groups[i] for i in order) for order in labels
        )
        true_order = rng.choice(physical_deals)

        depth = rng.randrange(4)
        observed_positions = [
            pos for pos in range(depth + 1)
            if rng.randrange(2)
        ]
        conditioned = [
            row for row in physical_deals
            if all(row[pos] == true_order[pos] for pos in observed_positions)
        ]
        assert conditioned

        prior = PrizePositionTopBelief.from_pool(
            counts, pool_size=5, prize_count=0
        )
        base = PrizePoolBelief.from_joint_prior(
            prior, counts, pool_size=5
        )
        belief = PrizeDeckPrefixBelief.from_exchangeable_pool(
            base, depth=depth
        )
        for pos in observed_positions:
            belief = belief.observe_deck_position(pos, true_order[pos])

        draw_count = rng.randrange(6)
        required_p = rng.choice((1, 2))
        required_e = rng.choice((1, 2))
        conditions = {"P": required_p, "E": required_e}
        flex_profile = (
            ((1, 1),) if rng.randrange(2)
            else ((1, 0), (0, 1))
        )
        profiles = {
            group: profile for group, profile in {
                **roles, "FLEX": flex_profile
            }.items() if group in counts
        }

        for shuffled in (False, True):
            oracle_orders = physical_deals if shuffled else conditioned
            denominator = len(oracle_orders)

            univariate = sum(
                row[:draw_count].count("P") >= required_p
                for row in oracle_orders
            ) / denominator
            joint = sum(
                row[:draw_count].count("P") >= required_p
                and row[:draw_count].count("E") >= required_e
                for row in oracle_orders
            ) / denominator
            alloc = sum(
                brute_allocatable(row[:draw_count], profiles, (1, 1))
                for row in oracle_orders
            ) / denominator

            close(probability_target_exposure(
                belief,
                targets=("P",),
                draw_count=draw_count,
                at_least=required_p,
                shuffle_first=shuffled,
            ), univariate, number)
            close(probability_joint_draw_requirements(
                belief,
                requirements=conditions,
                draw_count=draw_count,
                shuffle_first=shuffled,
            ), joint, number)
            close(probability_allocatable_draws(
                belief,
                requirements=(1, 1),
                profiles_by_group=profiles,
                draw_count=draw_count,
                shuffle_first=shuffled,
            ), alloc, number)

        # Draw one card while retaining current posterior. The newly exposed
        # top must have exactly the old physical position-one distribution.
        next_state = belief.draw_top_and_advance()
        for group in counts:
            physical_probability = sum(
                row[1] == group for row in conditioned
            ) / len(conditioned)
            close(
                next_state.probability_at_deck_position(0, group),
                physical_probability,
                number,
            )

    print(
        f"PASS: {cases} deterministic randomized cases x 120 physical orders"
    )
    print(
        "Three exposure kernels each checked shuffled/unshuffled; "
        "next-top transition checked per group"
    )


if __name__ == "__main__":
    main()
