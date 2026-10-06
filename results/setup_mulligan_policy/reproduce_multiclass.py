"""Reproduce and validate identity-specific optional-starter setup policies."""

from __future__ import annotations

from itertools import combinations
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools.setup_multiclass_policy import (  # noqa: E402
    conditioned_prize_multiclass_distribution,
    expected_mulligans_multiclass,
    opening_acceptance_multiclass,
    specific_class_card_prize_probability,
)


def pct(value: float) -> str:
    return f"{100 * value:.6f}%"


def exhaustive_distribution(
    deck_size: int,
    prize_count: int,
    hand_size: int,
    forced: int,
    groups: tuple[int, ...],
    policy,
) -> dict[tuple[int, ...], float]:
    classes = [0] * forced
    for group_index, size in enumerate(groups, start=1):
        classes.extend([group_index] * size)
    other_index = len(groups) + 1
    classes.extend([other_index] * (deck_size - forced - sum(groups)))

    all_cards = set(range(deck_size))
    weights: dict[tuple[int, ...], float] = {}
    total_weight = 0.0
    for hand_tuple in combinations(range(deck_size), hand_size):
        hand = set(hand_tuple)
        forced_in_hand = sum(classes[i] == 0 for i in hand)
        optional_counts = tuple(
            sum(classes[i] == group_index for i in hand)
            for group_index in range(1, len(groups) + 1)
        )
        keep_probability = 1.0 if forced_in_hand else float(policy(optional_counts))
        if keep_probability == 0.0:
            continue

        remaining = all_cards - hand
        for prize_tuple in combinations(sorted(remaining), prize_count):
            counts = [0] * (len(groups) + 2)
            for i in prize_tuple:
                counts[classes[i]] += 1
            key = tuple(counts)
            weights[key] = weights.get(key, 0.0) + keep_probability
            total_weight += keep_probability
    return {key: value / total_weight for key, value in weights.items()}


def validate() -> None:
    policies = [
        lambda counts: float(counts[1] > 0),
        lambda counts: float(sum(counts) >= 2),
        lambda counts: 0.75 if counts[0] > 0 else 0.25 if counts[1] > 0 else 0.0,
    ]
    cases = [
        (10, 2, 3, 2, (2, 1)),
        (11, 3, 3, 3, (1, 2)),
        (12, 3, 4, 2, (2, 2)),
    ]
    for args, policy in zip(cases, policies):
        deck, prizes, hand, forced, groups = args
        exact = dict(
            conditioned_prize_multiclass_distribution(
                deck,
                prizes,
                forced_starters=forced,
                optional_group_sizes=groups,
                optional_policy=policy,
                opening_hand_size=hand,
            )
        )
        brute = exhaustive_distribution(deck, prizes, hand, forced, groups, policy)
        if set(exact) != set(brute):
            raise AssertionError((args, set(exact), set(brute)))
        for key in exact:
            if abs(exact[key] - brute[key]) > 1e-14:
                raise AssertionError((args, key, exact[key], brute[key]))
        if abs(sum(exact.values()) - 1.0) > 1e-14:
            raise AssertionError((args, sum(exact.values())))


def main() -> None:
    validate()

    # Example: four ordinary Basics, two Manectric, two Snorlax Doll. Going
    # second makes Manectric available. The selective policy keeps an
    # optional-only hand exactly when at least one Snorlax Doll is present.
    accept_any = lambda counts: float(sum(counts) > 0)
    accept_snorlax = lambda counts: float(counts[1] > 0)
    decline_all = lambda counts: 0.0

    print("4 forced Basics + 2 Manectric + 2 Snorlax Doll")
    print("policy | accept/attempt | expected mulligans | forced Prize | Manectric Prize | Doll Prize | other Prize")
    for name, policy in [
        ("decline all optional-only", decline_all),
        ("accept Doll optional-only", accept_snorlax),
        ("accept any optional-only", accept_any),
    ]:
        accepted = opening_acceptance_multiclass(60, 4, (2, 2), policy)
        mulligans = expected_mulligans_multiclass(60, 4, (2, 2), policy)
        probabilities = [
            specific_class_card_prize_probability(
                60,
                6,
                forced_starters=4,
                optional_group_sizes=(2, 2),
                optional_policy=policy,
                class_index=index,
            )
            for index in range(4)
        ]
        print(
            f"{name:26s} | {pct(accepted):>14} | {mulligans:18.6f} | "
            + " | ".join(f"{pct(value):>15}" for value in probabilities)
        )

    # Nonlinear policy example: accept a Basic-less optional hand only when at
    # least two optional cards are present, regardless of their identities.
    accept_two_optional = lambda counts: float(sum(counts) >= 2)
    accepted = opening_acceptance_multiclass(60, 4, (2, 2), accept_two_optional)
    probs = [
        specific_class_card_prize_probability(
            60,
            6,
            forced_starters=4,
            optional_group_sizes=(2, 2),
            optional_policy=accept_two_optional,
            class_index=index,
        )
        for index in range(4)
    ]
    print("\naccept only if at least 2 optional cards are present")
    print("accept/attempt", pct(accepted))
    print("forced, Manectric, Doll, other Prize", *(pct(value) for value in probs))


if __name__ == "__main__":
    main()
