"""Reproduce and validate the competing connector policy result."""

from __future__ import annotations

from functools import lru_cache
from itertools import combinations
from math import isclose
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from connector_competing_policy import competing_connector_success


def _assert_close(actual: float, expected: float) -> None:
    if not isclose(actual, expected, rel_tol=0.0, abs_tol=1e-12):
        raise AssertionError(f"{actual!r} != {expected!r}")


@lru_cache(maxsize=None)
def _labeled_optimal(
    turns_remaining: int,
    critical_remaining: int,
    setup_secured: bool,
    rescue_in_hand: int,
    connector_in_hand: int,
    disposable_in_hand: int,
    deck: tuple[str, ...],
    discard_cost: int,
) -> float:
    if setup_secured and critical_remaining == 0:
        return 1.0
    if turns_remaining == 0 or not deck:
        return 0.0

    probability = 0.0
    for index, card in enumerate(deck):
        remaining = deck[:index] + deck[index + 1 :]
        setup_now = setup_secured
        rescue_hand = rescue_in_hand
        connector_hand = connector_in_hand
        disposable_hand = disposable_in_hand

        if card.startswith("T"):
            setup_now = True
        elif card.startswith("R"):
            rescue_hand += 1
        elif card.startswith("C"):
            connector_hand += 1
        elif card.startswith("D"):
            disposable_hand += 1

        actions = [
            _labeled_optimal(
                turns_remaining - 1,
                critical_remaining,
                setup_now,
                rescue_hand,
                connector_hand,
                disposable_hand,
                remaining,
                discard_cost,
            )
        ]

        if critical_remaining > 0 and rescue_hand > 0:
            actions.append(
                _labeled_optimal(
                    turns_remaining - 1,
                    critical_remaining - 1,
                    setup_now,
                    rescue_hand - 1,
                    connector_hand,
                    disposable_hand,
                    remaining,
                    discard_cost,
                )
            )

        connector_payable = (
            connector_hand > 0 and disposable_hand >= discard_cost
        )
        if connector_payable:
            setup_index = next(
                (
                    i
                    for i, candidate in enumerate(remaining)
                    if candidate.startswith("T")
                ),
                None,
            )
            if not setup_now and setup_index is not None:
                after_search = (
                    remaining[:setup_index] + remaining[setup_index + 1 :]
                )
                actions.append(
                    _labeled_optimal(
                        turns_remaining - 1,
                        critical_remaining,
                        True,
                        rescue_hand,
                        connector_hand - 1,
                        disposable_hand - discard_cost,
                        after_search,
                        discard_cost,
                    )
                )
                if critical_remaining > 0 and rescue_hand > 0:
                    actions.append(
                        _labeled_optimal(
                            turns_remaining - 1,
                            critical_remaining - 1,
                            True,
                            rescue_hand - 1,
                            connector_hand - 1,
                            disposable_hand - discard_cost,
                            after_search,
                            discard_cost,
                        )
                    )

            rescue_index = next(
                (
                    i
                    for i, candidate in enumerate(remaining)
                    if candidate.startswith("R")
                ),
                None,
            )
            if critical_remaining > 0 and rescue_index is not None:
                after_search = (
                    remaining[:rescue_index] + remaining[rescue_index + 1 :]
                )
                actions.append(
                    _labeled_optimal(
                        turns_remaining - 1,
                        critical_remaining,
                        setup_now,
                        rescue_hand + 1,
                        connector_hand - 1,
                        disposable_hand - discard_cost,
                        after_search,
                        discard_cost,
                    )
                )
                actions.append(
                    _labeled_optimal(
                        turns_remaining - 1,
                        critical_remaining - 1,
                        setup_now,
                        rescue_hand,
                        connector_hand - 1,
                        disposable_hand - discard_cost,
                        after_search,
                        discard_cost,
                    )
                )

        probability += max(actions) / len(deck)

    return probability


@lru_cache(maxsize=None)
def _labeled_priority(
    policy: str,
    turns_remaining: int,
    critical_remaining: int,
    setup_secured: bool,
    rescue_in_hand: int,
    connector_in_hand: int,
    disposable_in_hand: int,
    deck: tuple[str, ...],
    discard_cost: int,
) -> float:
    if setup_secured and critical_remaining == 0:
        return 1.0
    if turns_remaining == 0 or not deck:
        return 0.0

    probability = 0.0
    for index, card in enumerate(deck):
        remaining = deck[:index] + deck[index + 1 :]
        setup_now = setup_secured
        rescue_hand = rescue_in_hand
        connector_hand = connector_in_hand
        disposable_hand = disposable_in_hand

        if card.startswith("T"):
            setup_now = True
        elif card.startswith("R"):
            rescue_hand += 1
        elif card.startswith("C"):
            connector_hand += 1
        elif card.startswith("D"):
            disposable_hand += 1

        connector_payable = (
            connector_hand > 0 and disposable_hand >= discard_cost
        )
        setup_index = next(
            (
                i
                for i, candidate in enumerate(remaining)
                if candidate.startswith("T")
            ),
            None,
        )
        rescue_index = next(
            (
                i
                for i, candidate in enumerate(remaining)
                if candidate.startswith("R")
            ),
            None,
        )
        setup_search_available = (
            connector_payable and not setup_now and setup_index is not None
        )
        rescue_search_available = (
            connector_payable
            and critical_remaining > 0
            and rescue_hand == 0
            and rescue_index is not None
        )

        if policy == "setup_priority":
            if setup_search_available:
                remaining = (
                    remaining[:setup_index] + remaining[setup_index + 1 :]
                )
                setup_now = True
                connector_hand -= 1
                disposable_hand -= discard_cost
            elif rescue_search_available:
                remaining = (
                    remaining[:rescue_index] + remaining[rescue_index + 1 :]
                )
                rescue_hand += 1
                connector_hand -= 1
                disposable_hand -= discard_cost
        elif policy == "rescue_priority":
            if rescue_search_available:
                remaining = (
                    remaining[:rescue_index] + remaining[rescue_index + 1 :]
                )
                rescue_hand += 1
                connector_hand -= 1
                disposable_hand -= discard_cost
            elif setup_search_available:
                remaining = (
                    remaining[:setup_index] + remaining[setup_index + 1 :]
                )
                setup_now = True
                connector_hand -= 1
                disposable_hand -= discard_cost
        elif policy != "never_connector":
            raise ValueError(f"unsupported policy: {policy}")

        if critical_remaining > 0 and rescue_hand > 0:
            critical_after = critical_remaining - 1
            rescue_after = rescue_hand - 1
        else:
            critical_after = critical_remaining
            rescue_after = rescue_hand

        probability += _labeled_priority(
            policy,
            turns_remaining - 1,
            critical_after,
            setup_now,
            rescue_after,
            connector_hand,
            disposable_hand,
            remaining,
            discard_cost,
        ) / len(deck)

    return probability


def _small_labeled_validation() -> None:
    cards = (
        "K1",
        "K2",
        "T1",
        "R1",
        "C1",
        "D1",
        "D2",
        "S1",
        "S2",
        "P1",
    )
    opening_size = 3
    prize_count = 2
    discard_cost = 1
    turns = 3

    accepted_hands = [
        hand
        for hand in combinations(cards, opening_size)
        if any(card.startswith("S") for card in hand)
    ]

    _labeled_optimal.cache_clear()
    _labeled_priority.cache_clear()

    any_critical = 0.0
    optimal_success = 0.0
    setup_priority_success = 0.0
    rescue_priority_success = 0.0
    no_connector_success = 0.0

    for hand in accepted_hands:
        remaining_after_hand = tuple(card for card in cards if card not in hand)
        prize_sets = tuple(combinations(remaining_after_hand, prize_count))

        for prizes in prize_sets:
            state_mass = 1.0 / len(accepted_hands) / len(prize_sets)
            critical_prized = sum(
                card.startswith("K") for card in prizes
            )
            if critical_prized == 0:
                continue

            any_critical += state_mass
            deck = tuple(
                card for card in remaining_after_hand if card not in prizes
            )
            setup_secured = any(card.startswith("T") for card in hand)
            rescue_in_hand = sum(card.startswith("R") for card in hand)
            connector_in_hand = sum(card.startswith("C") for card in hand)
            disposable_in_hand = sum(card.startswith("D") for card in hand)
            state = (
                turns,
                critical_prized,
                setup_secured,
                rescue_in_hand,
                connector_in_hand,
                disposable_in_hand,
                deck,
                discard_cost,
            )

            optimal_success += state_mass * _labeled_optimal(*state)
            setup_priority_success += state_mass * _labeled_priority(
                "setup_priority", *state
            )
            rescue_priority_success += state_mass * _labeled_priority(
                "rescue_priority", *state
            )
            no_connector_success += state_mass * _labeled_priority(
                "never_connector", *state
            )

    exact = competing_connector_success(
        10,
        2,
        starter_cards=2,
        critical_singletons=2,
        setup_target_copies=1,
        rescue_supporters=1,
        disposable_nonstarters=2,
        discard_cost=1,
        opening_hand_size=3,
        turns=3,
    )

    _assert_close(exact.state_mass, 1.0)
    _assert_close(any_critical, exact.any_critical_prized)
    _assert_close(
        optimal_success / any_critical,
        exact.conditional_optimal_success,
    )
    _assert_close(
        setup_priority_success / any_critical,
        exact.conditional_setup_priority_success,
    )
    _assert_close(
        rescue_priority_success / any_critical,
        exact.conditional_rescue_priority_success,
    )
    _assert_close(
        no_connector_success / any_critical,
        exact.conditional_no_connector_success,
    )


def _baseline() -> None:
    expected = {
        1: (0.11687612691313781, 0.11687612691313781, 0.11687612691313781, 0.08201848708646932),
        2: (0.15387245498607133, 0.15050208492166112, 0.15216836217931032, 0.10437977558731433),
        3: (0.19122464427917124, 0.1841739153536938, 0.18771041940069066, 0.1276137120683506),
        4: (0.229390360672003, 0.2185430385117814, 0.22407582038840165, 0.15212942579630498),
        5: (0.2677682065081644, 0.2531342390049138, 0.2607221505564673, 0.17769949480789177),
        6: (0.3059497847993439, 0.2876380429455436, 0.2972845818728851, 0.2041140914365229),
    }

    print("Horizon | optimal | setup-priority | rescue-priority | no connector")
    for turns, values in expected.items():
        result = competing_connector_success(
            60,
            6,
            starter_cards=12,
            critical_singletons=4,
            setup_target_copies=4,
            rescue_supporters=2,
            disposable_nonstarters=20,
            discard_cost=2,
            turns=turns,
        )
        _assert_close(result.state_mass, 1.0)
        _assert_close(
            result.any_critical_prized,
            0.35383107569006184,
        )
        actual = (
            result.conditional_optimal_success,
            result.conditional_setup_priority_success,
            result.conditional_rescue_priority_success,
            result.conditional_no_connector_success,
        )
        for got, want in zip(actual, values):
            _assert_close(got, want)

        print(
            f"{turns:7d} | "
            f"{actual[0]:.6%} | "
            f"{actual[1]:.6%} | "
            f"{actual[2]:.6%} | "
            f"{actual[3]:.6%}"
        )


if __name__ == "__main__":
    _small_labeled_validation()
    _baseline()
    print()
    print("All competing-connector validations passed.")
