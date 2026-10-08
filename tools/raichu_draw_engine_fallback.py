"""Paired simulation of Harto Raichu draw-engine fallback after Quick Ball.

The initial seven-card opening, six Prize cards, and one ordinary draw are
sampled from Harto Miki's 60-card list partition. Once Quick Ball establishes
K1, each candidate draw-engine continuation is evaluated exactly over its later
without-replacement draw rather than sampled again.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
from functools import lru_cache
from math import comb, sqrt

import numpy as np

TARGET, GLADION, ULTRA, COMPUTER, FOREST, CROBAT, DEDENNE, SQUAWK, QUICK, DISP, GIRATINA, OTHER_STARTER, OTHER = range(13)

DECK_COUNTS = np.array((1, 2, 3, 1, 1, 2, 2, 1, 2, 11, 1, 10, 23), dtype=np.int16)
DECK_LABELS = np.concatenate(
    [np.full(int(count), category, dtype=np.int8) for category, count in enumerate(DECK_COUNTS)]
)
EXACT_COMBINED_VISIBLE_BASELINE = 0.48690299111
EXACT_OBSERVABLE_BRANCH_GIVEN_VALID = 0.03616756


def _bounded_compositions(total: int, sizes: tuple[int, ...]):
    count = len(sizes)
    suffix = [0] * (count + 1)
    for index in range(count - 1, -1, -1):
        suffix[index] = suffix[index + 1] + sizes[index]
    current = [0] * count

    def visit(index: int, remaining: int):
        if index == count - 1:
            if 0 <= remaining <= sizes[index]:
                current[index] = remaining
                yield tuple(current)
            return
        low = max(0, remaining - suffix[index + 1])
        high = min(sizes[index], remaining)
        for value in range(low, high + 1):
            current[index] = value
            yield from visit(index + 1, remaining - value)

    yield from visit(0, total)


def _compress(cards: np.ndarray | tuple[int, ...]) -> tuple[int, ...]:
    """Keep only categories that can change the modeled local endpoint."""

    return (
        int(cards[TARGET]),
        int(cards[GLADION]),
        int(cards[ULTRA]),
        int(cards[COMPUTER]),
        int(cards[FOREST]),
        int(cards[CROBAT]),
        int(cards[DISP] + cards[GIRATINA]),
        int(cards[DEDENNE] + cards[SQUAWK] + cards[QUICK] + cards[OTHER_STARTER] + cards[OTHER]),
    )


def _endpoint_success(
    hand: tuple[int, ...],
    deck: tuple[int, ...],
    target_prized: bool,
    crobat_host_in_play: bool,
) -> bool:
    target, gladion, ultra, computer, forest, crobat, disposable, _ = hand
    _, gladion_deck, *_ = deck
    forest_host = crobat_host_in_play or crobat > 0

    if not target_prized:
        return (
            target > 0
            or (forest > 0 and forest_host)
            or (disposable >= 2 and (ultra > 0 or computer > 0))
        )

    return (
        gladion > 0
        or (
            gladion_deck > 0
            and (
                (forest > 0 and forest_host)
                or (disposable >= 2 and computer > 0)
            )
        )
    )


@lru_cache(maxsize=None)
def _draw_success_probability(
    deck: tuple[int, ...],
    draw_count: int,
    preserved_hand: tuple[int, ...],
    target_prized: bool,
    crobat_host_in_play: bool,
) -> float:
    denominator = comb(sum(deck), draw_count)
    successful = 0
    for draw in _bounded_compositions(draw_count, deck):
        ways = 1
        for available, selected in zip(deck, draw):
            ways *= comb(available, selected)
        if ways == 0:
            continue
        hand = tuple(old + new for old, new in zip(preserved_hand, draw))
        remaining = tuple(old - new for old, new in zip(deck, draw))
        if _endpoint_success(hand, remaining, target_prized, crobat_host_in_play):
            successful += ways
    return successful / denominator


def _legacy_payment_choice(hand: np.ndarray) -> str:
    """The exact five-clause K0 policy from raichu_k0_discard_policy."""

    if hand[GLADION] >= 2:
        return "gladion"
    if hand[FOREST] > 0:
        return "disposable"
    if hand[DISP] + hand[GIRATINA] >= 3:
        return "disposable"
    if hand[ULTRA] > 0 or hand[COMPUTER] > 0:
        return "gladion"
    return "disposable"


def _pay_quick_ball(hand: np.ndarray, payment: str) -> np.ndarray:
    paid = hand.copy()
    paid[QUICK] -= 1
    if payment == "gladion":
        paid[GLADION] -= 1
    elif paid[DISP] > 0:
        paid[DISP] -= 1
    else:
        paid[GIRATINA] -= 1
    return paid


def _legacy_quick_ball_value(
    hand: np.ndarray,
    deck: np.ndarray,
    payment: str,
) -> float:
    """Reproduce the preceding searched-Crobat-only continuation."""

    hand = _pay_quick_ball(hand, payment)
    if deck[CROBAT] == 0:
        return 0.0
    deck = deck.copy()
    deck[CROBAT] -= 1
    target_prized = deck[TARGET] == 0
    compressed_hand = _compress(hand)
    compressed_deck = _compress(deck)
    if _endpoint_success(compressed_hand, compressed_deck, target_prized, True):
        return 1.0
    return _draw_success_probability(
        compressed_deck,
        1,
        compressed_hand,
        target_prized,
        True,
    )


def _expanded_quick_ball_value(
    hand: np.ndarray,
    deck: np.ndarray,
    active: int,
    payment: str,
    first_turn: bool,
) -> tuple[float, str]:
    """Choose the best modeled K1 continuation after paying Quick Ball."""

    hand = _pay_quick_ball(hand, payment)
    target_prized = deck[TARGET] == 0
    active_crobat = active == CROBAT
    compressed_hand = _compress(hand)
    compressed_deck = _compress(deck)

    if _endpoint_success(compressed_hand, compressed_deck, target_prized, active_crobat):
        return 1.0, "immediate_k1"

    candidates: list[tuple[float, str]] = []

    if hand[CROBAT] > 0:
        remaining_hand = hand.copy()
        remaining_hand[CROBAT] -= 1
        candidates.append(
            (
                _draw_success_probability(
                    compressed_deck,
                    6 - int(remaining_hand.sum()),
                    _compress(remaining_hand),
                    target_prized,
                    True,
                ),
                "crobat_hand",
            )
        )

    if deck[CROBAT] > 0:
        remaining_deck = deck.copy()
        remaining_deck[CROBAT] -= 1
        candidates.append(
            (
                _draw_success_probability(
                    _compress(remaining_deck),
                    6 - int(hand.sum()),
                    compressed_hand,
                    target_prized,
                    True,
                ),
                "crobat_deck",
            )
        )

    reset_host = active_crobat or hand[CROBAT] > 0
    empty_hand = (0,) * 8

    if hand[DEDENNE] > 0:
        candidates.append(
            (
                _draw_success_probability(
                    compressed_deck, 6, empty_hand, target_prized, reset_host
                ),
                "dedenne_hand",
            )
        )

    if deck[DEDENNE] > 0:
        remaining_deck = deck.copy()
        remaining_deck[DEDENNE] -= 1
        candidates.append(
            (
                _draw_success_probability(
                    _compress(remaining_deck), 6, empty_hand, target_prized, reset_host
                ),
                "dedenne_deck",
            )
        )

    if first_turn:
        if hand[SQUAWK] > 0:
            candidates.append(
                (
                    _draw_success_probability(
                        compressed_deck, 6, empty_hand, target_prized, reset_host
                    ),
                    "squawk_hand",
                )
            )
        if deck[SQUAWK] > 0:
            remaining_deck = deck.copy()
            remaining_deck[SQUAWK] -= 1
            candidates.append(
                (
                    _draw_success_probability(
                        _compress(remaining_deck), 6, empty_hand, target_prized, reset_host
                    ),
                    "squawk_deck",
                )
            )
        if active == SQUAWK:
            candidates.append(
                (
                    _draw_success_probability(
                        compressed_deck,
                        6,
                        empty_hand,
                        target_prized,
                        hand[CROBAT] > 0,
                    ),
                    "squawk_in_play",
                )
            )

    if not candidates:
        return 0.0, "none"

    best_value = max(value for value, _ in candidates)
    best_route = next(route for value, route in candidates if abs(value - best_value) < 1e-15)
    return best_value, best_route


def _active_from_opening(hand: np.ndarray) -> int:
    """Refine the prior setup abstraction while preserving Crobat-first behavior."""

    if hand[CROBAT] > 0:
        return CROBAT
    if hand[OTHER_STARTER] > 0:
        return OTHER_STARTER
    if hand[SQUAWK] > 0:
        return SQUAWK
    if hand[DEDENNE] > 0:
        return DEDENNE
    return GIRATINA


def _mean_and_se(total: float, squared: float, count: int) -> tuple[float, float]:
    mean = total / count
    variance = max(0.0, (squared - count * mean * mean) / (count - 1))
    return mean, sqrt(variance / count)


def simulate(samples: int = 1_000_000, seed: int = 20261008, batch_size: int = 50_000) -> dict:
    rng = np.random.default_rng(seed)
    valid_openings = 0
    branch_states = 0
    old_total = new_nonfirst_total = new_first_total = 0.0
    nonfirst_delta = first_delta = squawk_delta = 0.0
    nonfirst_sq = first_sq = squawk_sq = 0.0
    route_gain_nonfirst: defaultdict[str, float] = defaultdict(float)
    route_gain_first: defaultdict[str, float] = defaultdict(float)

    for offset in range(0, samples, batch_size):
        batch = min(batch_size, samples - offset)
        order = np.argsort(rng.random((batch, 60)), axis=1)
        exposed = DECK_LABELS[order[:, :14]]
        openings = exposed[:, :7]
        prizes = exposed[:, 7:13]
        draws = exposed[:, 13]

        opening_counts = np.zeros((batch, 13), dtype=np.int8)
        prize_counts = np.zeros((batch, 13), dtype=np.int8)
        rows = np.arange(batch)
        for slot in range(7):
            np.add.at(opening_counts, (rows, openings[:, slot]), 1)
        for slot in range(6):
            np.add.at(prize_counts, (rows, prizes[:, slot]), 1)

        valid = (
            opening_counts[:, CROBAT]
            + opening_counts[:, DEDENNE]
            + opening_counts[:, SQUAWK]
            + opening_counts[:, GIRATINA]
            + opening_counts[:, OTHER_STARTER]
        ) > 0
        valid_openings += int(valid.sum())

        for row in np.flatnonzero(valid):
            hand = opening_counts[row].astype(np.int16).copy()
            active = _active_from_opening(hand)
            hand[active] -= 1
            hand[int(draws[row])] += 1

            if (
                hand[TARGET] > 0
                or hand[QUICK] == 0
                or hand[GLADION] == 0
                or hand[DISP] + hand[GIRATINA] == 0
            ):
                continue

            branch_states += 1
            deck = DECK_COUNTS - opening_counts[row].astype(np.int16) - prize_counts[row].astype(np.int16)
            deck[int(draws[row])] -= 1

            direct_visible = hand[ULTRA] > 0 or hand[COMPUTER] > 0
            hosted_forest = hand[FOREST] > 0 and (active == CROBAT or hand[CROBAT] > 0)

            if direct_visible or hosted_forest:
                old = new_nonfirst = new_first = 1.0
            else:
                payment = _legacy_payment_choice(hand)
                old = _legacy_quick_ball_value(hand, deck, payment)
                new_nonfirst, route_nonfirst = _expanded_quick_ball_value(
                    hand, deck, active, payment, False
                )
                new_first, route_first = _expanded_quick_ball_value(
                    hand, deck, active, payment, True
                )
                route_gain_nonfirst[route_nonfirst] += new_nonfirst - old
                route_gain_first[route_first] += new_first - old

            delta_nonfirst = new_nonfirst - old
            delta_first = new_first - old
            delta_squawk = new_first - new_nonfirst
            old_total += old
            new_nonfirst_total += new_nonfirst
            new_first_total += new_first
            nonfirst_delta += delta_nonfirst
            first_delta += delta_first
            squawk_delta += delta_squawk
            nonfirst_sq += delta_nonfirst * delta_nonfirst
            first_sq += delta_first * delta_first
            squawk_sq += delta_squawk * delta_squawk

    nonfirst_mean, nonfirst_se = _mean_and_se(nonfirst_delta, nonfirst_sq, branch_states)
    first_mean, first_se = _mean_and_se(first_delta, first_sq, branch_states)
    squawk_mean, squawk_se = _mean_and_se(squawk_delta, squawk_sq, branch_states)

    def interval(mean: float, se: float) -> list[float]:
        return [mean - 1.96 * se, mean + 1.96 * se]

    return {
        "samples": samples,
        "seed": seed,
        "valid_openings": valid_openings,
        "observable_branch_states": branch_states,
        "branch_given_valid": branch_states / valid_openings,
        "exact_observable_branch_given_valid": EXACT_OBSERVABLE_BRANCH_GIVEN_VALID,
        "paired_sample_baseline": old_total / branch_states,
        "paired_sample_non_first_turn": new_nonfirst_total / branch_states,
        "paired_sample_first_turn": new_first_total / branch_states,
        "paired_gain_non_first_turn": nonfirst_mean,
        "paired_gain_non_first_turn_se": nonfirst_se,
        "paired_gain_non_first_turn_95ci": interval(nonfirst_mean, nonfirst_se),
        "paired_gain_first_turn": first_mean,
        "paired_gain_first_turn_se": first_se,
        "paired_gain_first_turn_95ci": interval(first_mean, first_se),
        "squawk_first_turn_increment": squawk_mean,
        "squawk_first_turn_increment_se": squawk_se,
        "squawk_first_turn_increment_95ci": interval(squawk_mean, squawk_se),
        "exact_existing_combined_visible_baseline": EXACT_COMBINED_VISIBLE_BASELINE,
        "calibrated_non_first_turn": EXACT_COMBINED_VISIBLE_BASELINE + nonfirst_mean,
        "calibrated_non_first_turn_95ci": [
            EXACT_COMBINED_VISIBLE_BASELINE + x for x in interval(nonfirst_mean, nonfirst_se)
        ],
        "calibrated_first_turn": EXACT_COMBINED_VISIBLE_BASELINE + first_mean,
        "calibrated_first_turn_95ci": [
            EXACT_COMBINED_VISIBLE_BASELINE + x for x in interval(first_mean, first_se)
        ],
        "gain_attribution_non_first_turn": {
            route: value / branch_states for route, value in sorted(route_gain_nonfirst.items())
        },
        "gain_attribution_first_turn": {
            route: value / branch_states for route, value in sorted(route_gain_first.items())
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--samples", type=int, default=1_000_000)
    parser.add_argument("--seed", type=int, default=20261008)
    args = parser.parse_args()
    import json
    print(json.dumps(simulate(samples=args.samples, seed=args.seed), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
