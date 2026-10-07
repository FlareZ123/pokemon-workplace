"""Reproduce competing-connector policy results and validations."""

from __future__ import annotations

from functools import lru_cache
from itertools import combinations
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from competing_connector_policy import (  # noqa: E402
    competing_connector_success,
)


def pct(value: float) -> str:
    return f"{100 * value:.6f}%"


def exhaustive_small_case() -> tuple[float, dict[str, float]]:
    """Independent labeled-card recursion for a small validation deck."""

    cards = (
        ["C"] * 2
        + ["R"]
        + ["S"]
        + ["G"]
        + ["D"] * 2
        + ["T"] * 3
    )
    deck_size = len(cards)
    opening_hand_size = 3
    prize_count = 2
    turns = 2
    discard_cost = 1
    all_cards = tuple(range(deck_size))
    modes = ("none", "rescue", "setup", "flex")

    @lru_cache(maxsize=None)
    def future_success(
        mode: str,
        turns_remaining: int,
        critical_remaining: int,
        setup_acquired: bool,
        hand: tuple[int, ...],
        deck: tuple[int, ...],
    ) -> float:
        if critical_remaining == 0 and setup_acquired:
            return 1.0
        if turns_remaining == 0 or not deck:
            return 0.0

        probability = 0.0
        for drawn in deck:
            next_deck_list = list(deck)
            next_deck_list.remove(drawn)
            next_deck = tuple(sorted(next_deck_list))
            next_hand = tuple(sorted(hand + (drawn,)))
            acquired = setup_acquired or cards[drawn] == "S"

            action_states = [
                (
                    critical_remaining,
                    acquired,
                    next_hand,
                    next_deck,
                )
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

            connector_payable = (
                bool(connector_in_hand)
                and len(disposable_in_hand) >= discard_cost
            )

            if (
                connector_payable
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
                connector_payable
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

                    rescue_after_search = [
                        index
                        for index in hand_after
                        if cards[index] == "R"
                    ]
                    if critical_remaining > 0 and rescue_after_search:
                        hand_after_play = list(hand_after)
                        hand_after_play.remove(rescue_after_search[0])
                        action_states.append(
                            (
                                critical_remaining - 1,
                                True,
                                tuple(sorted(hand_after_play)),
                                tuple(sorted(deck_after)),
                            )
                        )

            best = max(
                future_success(
                    mode,
                    turns_remaining - 1,
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
            critical_prized = sum(
                cards[index] == "C" for index in prizes
            )
            if critical_prized == 0:
                continue

            critical_states += 1
            deck = tuple(
                sorted(index for index in after_hand if index not in prizes)
            )
            setup_acquired = any(
                cards[index] == "S" for index in hand
            )
            hand_state = tuple(sorted(hand))

            for mode in modes:
                success[mode] += future_success(
                    mode,
                    turns,
                    critical_prized,
                    setup_acquired,
                    hand_state,
                    deck,
                )

    return (
        critical_states / accepted,
        {
            mode: value / critical_states
            for mode, value in success.items()
        },
    )


def validate() -> None:
    exact = competing_connector_success(
        10,
        2,
        starter_cards=3,
        critical_nonstarter=2,
        rescue_supporters=1,
        setup_targets=1,
        disposable_nonstarters=2,
        discard_cost=1,
        opening_hand_size=3,
        turns=2,
    )
    brute_any, brute = exhaustive_small_case()

    if abs(exact.state_mass - 1.0) > 1e-14:
        raise AssertionError(exact.state_mass)
    if abs(exact.any_critical_prized - brute_any) > 1e-15:
        raise AssertionError((exact.any_critical_prized, brute_any))

    pairs = (
        (exact.conditional_no_connector_success, brute["none"]),
        (exact.conditional_rescue_only_success, brute["rescue"]),
        (exact.conditional_setup_only_success, brute["setup"]),
        (exact.conditional_flexible_success, brute["flex"]),
    )
    for exact_value, brute_value in pairs:
        if abs(exact_value - brute_value) > 1e-15:
            raise AssertionError((exact_value, brute_value))

    if (
        exact.conditional_flexible_success
        + 1e-15
        < max(
            exact.conditional_rescue_only_success,
            exact.conditional_setup_only_success,
        )
    ):
        raise AssertionError("flexible search cannot underperform a subset policy")


def main() -> None:
    validate()

    print("Competing connector policy")
    print(
        "60 cards, 6 Prizes, valid 7-card opener, 12 protected starters, "
        "4 critical non-starters, 2 rescue Supporters, 2 setup targets, "
        "1 universal cost-2 connector, 20 disposable non-starters"
    )
    print(
        "turn | no connector | rescue only | setup only | flexible | "
        "flex gain"
    )

    for turns in [1, 2, 3, 4]:
        result = competing_connector_success(
            60,
            6,
            starter_cards=12,
            critical_nonstarter=4,
            rescue_supporters=2,
            setup_targets=2,
            disposable_nonstarters=20,
            discard_cost=2,
            turns=turns,
        )
        print(
            f"{turns:4d} | "
            f"{pct(result.conditional_no_connector_success):>12} | "
            f"{pct(result.conditional_rescue_only_success):>11} | "
            f"{pct(result.conditional_setup_only_success):>10} | "
            f"{pct(result.conditional_flexible_success):>8} | "
            f"{pct(result.conditional_flexibility_gain):>9}"
        )

    print()
    print("Three-turn sensitivity to disposable-card density")
    print(
        "disposable | no connector | rescue only | setup only | "
        "flexible | flex gain"
    )
    for disposable in [5, 10, 15, 20, 25, 30]:
        result = competing_connector_success(
            60,
            6,
            starter_cards=12,
            critical_nonstarter=4,
            rescue_supporters=2,
            setup_targets=2,
            disposable_nonstarters=disposable,
            discard_cost=2,
            turns=3,
        )
        print(
            f"{disposable:10d} | "
            f"{pct(result.conditional_no_connector_success):>12} | "
            f"{pct(result.conditional_rescue_only_success):>11} | "
            f"{pct(result.conditional_setup_only_success):>10} | "
            f"{pct(result.conditional_flexible_success):>8} | "
            f"{pct(result.conditional_flexibility_gain):>9}"
        )

    print()
    print("Three-turn target-density comparison")
    print("setup copies | rescue-only | setup-only | flexible")
    for setup_targets in [1, 2, 3, 4]:
        result = competing_connector_success(
            60,
            6,
            starter_cards=12,
            critical_nonstarter=4,
            rescue_supporters=2,
            setup_targets=setup_targets,
            disposable_nonstarters=20,
            discard_cost=2,
            turns=3,
        )
        print(
            f"{setup_targets:12d} | "
            f"{pct(result.conditional_rescue_only_success):>11} | "
            f"{pct(result.conditional_setup_only_success):>10} | "
            f"{pct(result.conditional_flexible_success):>8}"
        )


if __name__ == "__main__":
    main()
