"""Reproduce distinct-deadline connector allocation results and validations."""

from __future__ import annotations

from functools import lru_cache
from itertools import combinations
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from competing_connector_deadlines import (  # noqa: E402
    competing_connector_deadline_success,
)
from competing_connector_policy import competing_connector_success  # noqa: E402


def pct(value: float) -> str:
    return f"{100 * value:.6f}%"


def exhaustive_small_case(
    *, rescue_turns: int, setup_deadline: int
) -> tuple[float, dict[str, float]]:
    """Independent labeled-card recursion for separate deadlines."""

    cards = (
        ["C"] * 2
        + ["R"]
        + ["S"]
        + ["G"]
        + ["D"] * 2
        + ["T"] * 3
    )
    opening_hand_size = 3
    prize_count = 2
    discard_cost = 1
    all_cards = tuple(range(len(cards)))
    modes = ("none", "rescue", "setup", "flex")

    @lru_cache(maxsize=None)
    def future_success(
        mode: str,
        turns_remaining: int,
        setup_turns_remaining: int,
        critical_remaining: int,
        setup_acquired: bool,
        hand: tuple[int, ...],
        deck: tuple[int, ...],
    ) -> float:
        if not setup_acquired and setup_turns_remaining == 0:
            return 0.0
        if critical_remaining == 0 and setup_acquired:
            return 1.0
        if turns_remaining == 0 or not deck:
            return 0.0

        probability = 0.0
        for drawn in deck:
            deck_after_draw = list(deck)
            deck_after_draw.remove(drawn)
            next_deck = tuple(sorted(deck_after_draw))
            next_hand = tuple(sorted(hand + (drawn,)))
            acquired = setup_acquired or cards[drawn] == "S"

            action_states = [
                (critical_remaining, acquired, next_hand, next_deck)
            ]

            rescue_in_hand = [
                index for index in next_hand if cards[index] == "R"
            ]
            connector_in_hand = [
                index for index in next_hand if cards[index] == "G"
            ]
            disposable_in_hand = [
                index for index in next_hand if cards[index] == "D"
            ]

            if critical_remaining > 0 and rescue_in_hand:
                hand_after = list(next_hand)
                hand_after.remove(rescue_in_hand[0])
                action_states.append(
                    (
                        critical_remaining - 1,
                        acquired,
                        tuple(sorted(hand_after)),
                        next_deck,
                    )
                )

            payable = (
                bool(connector_in_hand)
                and len(disposable_in_hand) >= discard_cost
            )

            if (
                payable
                and mode in {"rescue", "flex"}
                and critical_remaining > 0
            ):
                rescue_in_deck = [
                    index for index in next_deck if cards[index] == "R"
                ]
                if rescue_in_deck:
                    hand_after = list(next_hand)
                    deck_after = list(next_deck)
                    hand_after.remove(connector_in_hand[0])
                    for index in disposable_in_hand[:discard_cost]:
                        hand_after.remove(index)
                    deck_after.remove(rescue_in_deck[0])
                    hand_after.append(rescue_in_deck[0])

                    action_states.append(
                        (
                            critical_remaining,
                            acquired,
                            tuple(sorted(hand_after)),
                            tuple(sorted(deck_after)),
                        )
                    )

                    hand_after_play = list(hand_after)
                    hand_after_play.remove(rescue_in_deck[0])
                    action_states.append(
                        (
                            critical_remaining - 1,
                            acquired,
                            tuple(sorted(hand_after_play)),
                            tuple(sorted(deck_after)),
                        )
                    )

            if (
                payable
                and mode in {"setup", "flex"}
                and not acquired
            ):
                setup_in_deck = [
                    index for index in next_deck if cards[index] == "S"
                ]
                if setup_in_deck:
                    hand_after = list(next_hand)
                    deck_after = list(next_deck)
                    hand_after.remove(connector_in_hand[0])
                    for index in disposable_in_hand[:discard_cost]:
                        hand_after.remove(index)
                    deck_after.remove(setup_in_deck[0])
                    hand_after.append(setup_in_deck[0])

                    action_states.append(
                        (
                            critical_remaining,
                            True,
                            tuple(sorted(hand_after)),
                            tuple(sorted(deck_after)),
                        )
                    )

                    rescue_after = [
                        index for index in hand_after if cards[index] == "R"
                    ]
                    if critical_remaining > 0 and rescue_after:
                        hand_after_play = list(hand_after)
                        hand_after_play.remove(rescue_after[0])
                        action_states.append(
                            (
                                critical_remaining - 1,
                                True,
                                tuple(sorted(hand_after_play)),
                                tuple(sorted(deck_after)),
                            )
                        )

            next_setup_turns = max(0, setup_turns_remaining - 1)
            best = max(
                future_success(
                    mode,
                    turns_remaining - 1,
                    next_setup_turns,
                    action_critical,
                    action_setup,
                    action_hand,
                    action_deck,
                )
                for (
                    action_critical,
                    action_setup,
                    action_hand,
                    action_deck,
                ) in action_states
            )
            probability += best

        return probability / len(deck)

    accepted = 0
    critical_states = 0
    success = {mode: 0.0 for mode in modes}

    for hand in combinations(all_cards, opening_hand_size):
        if not any(cards[index] == "T" for index in hand):
            continue
        after_hand = tuple(index for index in all_cards if index not in hand)

        for prizes in combinations(after_hand, prize_count):
            accepted += 1
            critical_prized = sum(cards[index] == "C" for index in prizes)
            if critical_prized == 0:
                continue

            critical_states += 1
            deck = tuple(
                sorted(index for index in after_hand if index not in prizes)
            )
            setup_acquired = any(cards[index] == "S" for index in hand)
            hand_state = tuple(sorted(hand))

            for mode in modes:
                success[mode] += future_success(
                    mode,
                    rescue_turns,
                    setup_deadline,
                    critical_prized,
                    setup_acquired,
                    hand_state,
                    deck,
                )

    return (
        critical_states / accepted,
        {mode: value / critical_states for mode, value in success.items()},
    )


def validate() -> None:
    for deadline in (1, 2):
        exact = competing_connector_deadline_success(
            10,
            2,
            starter_cards=3,
            critical_nonstarter=2,
            rescue_supporters=1,
            setup_targets=1,
            disposable_nonstarters=2,
            discard_cost=1,
            opening_hand_size=3,
            rescue_turns=2,
            setup_deadline=deadline,
        )
        brute_any, brute = exhaustive_small_case(
            rescue_turns=2,
            setup_deadline=deadline,
        )
        if abs(exact.state_mass - 1.0) > 1e-14:
            raise AssertionError(exact.state_mass)
        if abs(exact.any_critical_prized - brute_any) > 5e-15:
            raise AssertionError((exact.any_critical_prized, brute_any))

        exact_values = (
            exact.conditional_no_connector_success,
            exact.conditional_rescue_only_success,
            exact.conditional_setup_only_success,
            exact.conditional_flexible_success,
        )
        brute_values = (
            brute["none"],
            brute["rescue"],
            brute["setup"],
            brute["flex"],
        )
        for exact_value, brute_value in zip(exact_values, brute_values):
            if abs(exact_value - brute_value) > 5e-15:
                raise AssertionError((deadline, exact_value, brute_value))

    equal_deadline = competing_connector_deadline_success(
        60,
        6,
        starter_cards=12,
        critical_nonstarter=4,
        rescue_supporters=2,
        setup_targets=2,
        disposable_nonstarters=20,
        discard_cost=2,
        rescue_turns=3,
        setup_deadline=3,
    )
    prior = competing_connector_success(
        60,
        6,
        starter_cards=12,
        critical_nonstarter=4,
        rescue_supporters=2,
        setup_targets=2,
        disposable_nonstarters=20,
        discard_cost=2,
        turns=3,
    )
    pairs = (
        (
            equal_deadline.conditional_no_connector_success,
            prior.conditional_no_connector_success,
        ),
        (
            equal_deadline.conditional_rescue_only_success,
            prior.conditional_rescue_only_success,
        ),
        (
            equal_deadline.conditional_setup_only_success,
            prior.conditional_setup_only_success,
        ),
        (
            equal_deadline.conditional_flexible_success,
            prior.conditional_flexible_success,
        ),
    )
    for deadline_value, prior_value in pairs:
        if abs(deadline_value - prior_value) > 5e-15:
            raise AssertionError((deadline_value, prior_value))


def main() -> None:
    validate()

    print("Distinct setup deadline with rescue due by turn 4")
    print(
        "60 cards, 6 Prizes, valid 7-card opener, 12 protected starters, "
        "4 critical non-starters, 2 rescue Supporters, 2 setup targets, "
        "1 universal cost-2 connector, 20 disposable non-starters"
    )
    print(
        "setup deadline | no connector | rescue only | setup only | "
        "flexible | flex gain"
    )

    for deadline in (1, 2, 3, 4):
        result = competing_connector_deadline_success(
            60,
            6,
            starter_cards=12,
            critical_nonstarter=4,
            rescue_supporters=2,
            setup_targets=2,
            disposable_nonstarters=20,
            discard_cost=2,
            rescue_turns=4,
            setup_deadline=deadline,
        )
        print(
            f"{deadline:14d} | "
            f"{pct(result.conditional_no_connector_success):>12} | "
            f"{pct(result.conditional_rescue_only_success):>11} | "
            f"{pct(result.conditional_setup_only_success):>10} | "
            f"{pct(result.conditional_flexible_success):>8} | "
            f"{pct(result.conditional_flexibility_gain):>9}"
        )

    print()
    print("One setup copy, rescue still due by turn 4")
    print("setup deadline | rescue only | setup only | flexible")
    for deadline in (1, 2, 3, 4):
        result = competing_connector_deadline_success(
            60,
            6,
            starter_cards=12,
            critical_nonstarter=4,
            rescue_supporters=2,
            setup_targets=1,
            disposable_nonstarters=20,
            discard_cost=2,
            rescue_turns=4,
            setup_deadline=deadline,
        )
        print(
            f"{deadline:14d} | "
            f"{pct(result.conditional_rescue_only_success):>11} | "
            f"{pct(result.conditional_setup_only_success):>10} | "
            f"{pct(result.conditional_flexible_success):>8}"
        )


if __name__ == "__main__":
    main()
