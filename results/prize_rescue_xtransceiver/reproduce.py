"""Reproduce exact Xtransceiver-like Prize-rescue probabilities."""

from __future__ import annotations

from functools import lru_cache
from itertools import combinations
from math import isclose
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from prize_rescue_xtransceiver import rescue_success_with_stochastic_connector  # noqa: E402


def pct(value: float) -> str:
    return f"{100 * value:.6f}%"


def _remove_one(values: tuple[int, ...], value: int) -> tuple[int, ...]:
    out = list(values)
    out.remove(value)
    return tuple(sorted(out))


def _finish_labeled(
    cards: tuple[str, ...],
    turns_remaining: int,
    critical_remaining: int,
    hand: tuple[int, ...],
    deck: tuple[int, ...],
    p_num: int,
    p_den: int,
    same_turn_retries: bool,
) -> float:
    best = _future_labeled(
        cards,
        turns_remaining - 1,
        critical_remaining,
        hand,
        deck,
        p_num,
        p_den,
        same_turn_retries,
    )
    rescuer = next((i for i in hand if cards[i] == "R"), None)
    if rescuer is not None:
        best = max(
            best,
            _future_labeled(
                cards,
                turns_remaining - 1,
                critical_remaining - 1,
                _remove_one(hand, rescuer),
                deck,
                p_num,
                p_den,
                same_turn_retries,
            ),
        )
    return best


def _after_draw_labeled(
    cards: tuple[str, ...],
    turns_remaining: int,
    critical_remaining: int,
    hand: tuple[int, ...],
    deck: tuple[int, ...],
    p_num: int,
    p_den: int,
    same_turn_retries: bool,
) -> float:
    if critical_remaining == 0:
        return 1.0

    best = _finish_labeled(
        cards,
        turns_remaining,
        critical_remaining,
        hand,
        deck,
        p_num,
        p_den,
        same_turn_retries,
    )

    connector = next((i for i in hand if cards[i] == "X"), None)
    rescuer_deck = next((i for i in deck if cards[i] == "R"), None)
    if connector is None or rescuer_deck is None:
        return best

    next_hand = _remove_one(hand, connector)
    hit_hand = tuple(sorted(next_hand + (rescuer_deck,)))
    hit_deck = _remove_one(deck, rescuer_deck)
    if same_turn_retries:
        hit_value = _after_draw_labeled(
            cards,
            turns_remaining,
            critical_remaining,
            hit_hand,
            hit_deck,
            p_num,
            p_den,
            same_turn_retries,
        )
        miss_value = _after_draw_labeled(
            cards,
            turns_remaining,
            critical_remaining,
            next_hand,
            deck,
            p_num,
            p_den,
            same_turn_retries,
        )
    else:
        hit_value = _finish_labeled(
            cards,
            turns_remaining,
            critical_remaining,
            hit_hand,
            hit_deck,
            p_num,
            p_den,
            same_turn_retries,
        )
        miss_value = _finish_labeled(
            cards,
            turns_remaining,
            critical_remaining,
            next_hand,
            deck,
            p_num,
            p_den,
            same_turn_retries,
        )

    p = p_num / p_den
    return max(best, p * hit_value + (1.0 - p) * miss_value)


@lru_cache(maxsize=None)
def _future_labeled(
    cards: tuple[str, ...],
    turns_remaining: int,
    critical_remaining: int,
    hand: tuple[int, ...],
    deck: tuple[int, ...],
    p_num: int,
    p_den: int,
    same_turn_retries: bool,
) -> float:
    if critical_remaining == 0:
        return 1.0
    if turns_remaining == 0 or not deck:
        return 0.0

    total = 0.0
    for drawn in deck:
        next_deck = _remove_one(deck, drawn)
        next_hand = tuple(sorted(hand + (drawn,)))
        total += _after_draw_labeled(
            cards,
            turns_remaining,
            critical_remaining,
            next_hand,
            next_deck,
            p_num,
            p_den,
            same_turn_retries,
        )
    return total / len(deck)


def labeled_small_case(*, same_turn_retries: bool = True) -> tuple[float, float]:
    # 10 cards: 3 starters, 2 criticals, 2 rescuers, 2 Xtransceiver-like Items, 1 filler.
    cards = ("S", "S", "S", "C", "C", "R", "R", "X", "X", "O")
    indices = tuple(range(len(cards)))
    opening_size = 3
    prize_count = 2

    accepted = 0
    weighted_success = 0.0
    critical_states = 0
    for hand in combinations(indices, opening_size):
        if not any(cards[i] == "S" for i in hand):
            continue
        accepted += 1
        remaining = tuple(i for i in indices if i not in hand)
        for prizes in combinations(remaining, prize_count):
            critical = sum(cards[i] == "C" for i in prizes)
            if critical == 0:
                continue
            critical_states += 1
            deck = tuple(i for i in remaining if i not in prizes)
            _future_labeled.cache_clear()
            weighted_success += _future_labeled(
                cards,
                2,
                critical,
                tuple(sorted(hand)),
                tuple(sorted(deck)),
                1,
                2,
                same_turn_retries,
            )

    prize_states_per_hand = 21  # C(7, 2)
    any_critical = critical_states / (accepted * prize_states_per_hand)
    conditional_success = weighted_success / critical_states
    return any_critical, conditional_success


def main() -> None:
    baseline = {}
    for copies in range(5):
        baseline[copies] = []
        for turns in range(1, 5):
            result = rescue_success_with_stochastic_connector(
                60,
                6,
                starter_cards=12,
                critical_starter=0,
                critical_nonstarter=4,
                rescue_supporters=2,
                connector_copies=copies,
                rescue_turns=turns,
            )
            assert isclose(result.state_mass, 1.0, rel_tol=0.0, abs_tol=1e-12)
            baseline[copies].append(result.conditional_success_probability)

    expected = {
        0: [0.20988290, 0.23799232, 0.26377561, 0.28912644],
        1: [0.25320925, 0.28700941, 0.31665151, 0.34550311],
        2: [0.29401124, 0.33315653, 0.36601162, 0.39768253],
        3: [0.33241428, 0.37657648, 0.41205874, 0.44594014],
        4: [0.36853866, 0.41740626, 0.45498586, 0.49053592],
    }
    for copies, row in expected.items():
        for actual, target in zip(baseline[copies], row):
            assert isclose(actual, target, rel_tol=0.0, abs_tol=5e-9)

    # A certain-hit connector reduces exactly to the repository's published
    # deterministic preserving-connector baseline for four copies.
    deterministic_four = []
    for turns in range(1, 5):
        result = rescue_success_with_stochastic_connector(
            60,
            6,
            starter_cards=12,
            critical_starter=0,
            critical_nonstarter=4,
            rescue_supporters=2,
            connector_copies=4,
            rescue_turns=turns,
            hit_numerator=1,
            hit_denominator=1,
        )
        deterministic_four.append(result.conditional_success_probability)
    published = [0.49984029, 0.56572661, 0.60873648, 0.64797247]
    for actual, target in zip(deterministic_four, published):
        assert isclose(actual, target, rel_tol=0.0, abs_tol=5e-9)

    category_small = rescue_success_with_stochastic_connector(
        10,
        2,
        starter_cards=3,
        critical_starter=0,
        critical_nonstarter=2,
        rescue_supporters=2,
        connector_copies=2,
        opening_hand_size=3,
        rescue_turns=2,
    )
    labeled_any, labeled_success = labeled_small_case()
    assert isclose(category_small.any_critical_prized, labeled_any, rel_tol=0.0, abs_tol=1e-12)
    assert isclose(
        category_small.conditional_success_probability,
        labeled_success,
        rel_tol=0.0,
        abs_tol=1e-12,
    )

    category_single = rescue_success_with_stochastic_connector(
        10,
        2,
        starter_cards=3,
        critical_starter=0,
        critical_nonstarter=2,
        rescue_supporters=2,
        connector_copies=2,
        opening_hand_size=3,
        rescue_turns=2,
        same_turn_retries=False,
    )
    _, labeled_single = labeled_small_case(same_turn_retries=False)
    assert isclose(
        category_single.conditional_success_probability,
        labeled_single,
        rel_tol=0.0,
        abs_tol=1e-12,
    )

    print("prize_rescue_xtransceiver: all assertions passed")
    for copies in range(5):
        print(copies, *(pct(v) for v in baseline[copies]))
    print("small exact:", pct(category_small.conditional_success_probability))
    print("small labeled:", pct(labeled_success))


if __name__ == "__main__":
    main()
