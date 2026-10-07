from __future__ import annotations

import math
from collections import Counter
from itertools import product
from typing import Iterator

CATEGORIES = (
    "iron_thorns",
    "guzma_hala",
    "tag_call",
    "thunder_mountain",
    "double_colorless",
    "gladion",
    "other",
)
COUNTS = (4, 2, 2, 1, 1, 1, 49)
DECK_SIZE = 60
OPENING_SIZE = 7
PRIZE_COUNT = 6


def allocations(total: int, caps: tuple[int, ...]) -> Iterator[tuple[int, ...]]:
    def recurse(index: int, left: int, prefix: list[int]) -> Iterator[tuple[int, ...]]:
        if index == len(caps) - 1:
            if 0 <= left <= caps[index]:
                yield tuple(prefix + [left])
            return
        for count in range(min(caps[index], left) + 1):
            yield from recurse(index + 1, left - count, prefix + [count])

    yield from recurse(0, total, [])


def accepted_opening_probability() -> float:
    return 1.0 - math.comb(56, OPENING_SIZE) / math.comb(DECK_SIZE, OPENING_SIZE)


def _hand_and_deck(
    opening: tuple[int, ...],
    prizes: tuple[int, ...],
    draw_index: int,
) -> tuple[list[int], list[int]]:
    hand = [
        opening[index] + int(index == draw_index)
        for index in range(len(COUNTS))
    ]
    deck = [
        COUNTS[index]
        - opening[index]
        - prizes[index]
        - int(index == draw_index)
        for index in range(len(COUNTS))
    ]
    return hand, deck


def baseline_route(
    opening: tuple[int, ...],
    prizes: tuple[int, ...],
    draw_index: int,
) -> tuple[bool, str]:
    hand, deck = _hand_and_deck(opening, prizes, draw_index)
    thunder_hand = hand[3] > 0
    dce_hand = hand[4] > 0

    if thunder_hand and dce_hand:
        return True, "direct"

    gnh_access = hand[1] > 0 or (hand[2] > 0 and deck[1] > 0)
    if not gnh_access:
        return False, "no_guzma_hala_access"

    thunder_access = thunder_hand or deck[3] > 0
    dce_access = dce_hand or deck[4] > 0
    if thunder_access and dce_access:
        return True, "guzma_hala"
    if not thunder_access:
        return False, "thunder_mountain_prized"
    return False, "double_colorless_prized"


def information_aware_route(
    opening: tuple[int, ...],
    prizes: tuple[int, ...],
    draw_index: int,
) -> tuple[bool, str]:
    hand, deck = _hand_and_deck(opening, prizes, draw_index)
    thunder_hand = hand[3] > 0
    dce_hand = hand[4] > 0

    if thunder_hand and dce_hand:
        return True, "direct"

    thunder_missing = not thunder_hand
    dce_missing = not dce_hand
    thunder_deck = deck[3] > 0
    dce_deck = deck[4] > 0
    thunder_prized = thunder_missing and not thunder_deck
    dce_prized = dce_missing and not dce_deck

    gnh_hand = hand[1] > 0
    tag_to_gnh = hand[2] > 0 and deck[1] > 0
    gladion_hand = hand[5] > 0

    if tag_to_gnh:
        if (
            (not thunder_missing or thunder_deck)
            and (not dce_missing or dce_deck)
        ):
            return True, "tag_call_then_guzma_hala"

        if gladion_hand and thunder_prized and dce_hand:
            return True, "tag_call_k1_then_gladion_for_thunder"
        if gladion_hand and dce_prized and thunder_hand:
            return True, "tag_call_k1_then_gladion_for_dce"
        return False, "tag_call_line_cannot_complete"

    if gnh_hand:
        if (
            (not thunder_missing or thunder_deck)
            and (not dce_missing or dce_deck)
        ):
            return True, "guzma_hala_from_hand"
        return False, "guzma_hala_line_cannot_complete"

    if gladion_hand and thunder_prized and dce_hand:
        return True, "gladion_only_for_thunder"
    if gladion_hand and dce_prized and thunder_hand:
        return True, "gladion_only_for_dce"
    return False, "no_represented_route"


def exact_probability(route) -> tuple[float, Counter[str]]:
    opening_denominator = math.comb(DECK_SIZE, OPENING_SIZE)
    accepted = accepted_opening_probability()
    total = 0.0
    successes = Counter()

    for opening in allocations(OPENING_SIZE, COUNTS):
        if opening[0] < 1:
            continue
        opening_probability = (
            math.prod(
                math.comb(COUNTS[index], opening[index])
                for index in range(len(COUNTS))
            )
            / opening_denominator
            / accepted
        )
        remaining = tuple(
            COUNTS[index] - opening[index] for index in range(len(COUNTS))
        )

        for prizes in allocations(PRIZE_COUNT, remaining):
            prize_probability = (
                math.prod(
                    math.comb(remaining[index], prizes[index])
                    for index in range(len(COUNTS))
                )
                / math.comb(DECK_SIZE - OPENING_SIZE, PRIZE_COUNT)
            )
            after_prizes = tuple(
                remaining[index] - prizes[index]
                for index in range(len(COUNTS))
            )

            for draw_index, copies in enumerate(after_prizes):
                if copies == 0:
                    continue
                probability = (
                    opening_probability
                    * prize_probability
                    * copies
                    / (DECK_SIZE - OPENING_SIZE - PRIZE_COUNT)
                )
                total += probability
                success, reason = route(opening, prizes, draw_index)
                if success:
                    successes[reason] += probability

    if not math.isclose(total, 1.0, rel_tol=1e-12, abs_tol=1e-12):
        raise AssertionError(f"conditioned state probability sums to {total}")

    return sum(successes.values()), successes


def main() -> None:
    baseline, baseline_parts = exact_probability(baseline_route)
    informed, informed_parts = exact_probability(information_aware_route)

    print(f"Accepted-opening baseline route: {baseline:.12%}")
    for reason, probability in baseline_parts.most_common():
        print(f"  {reason}: {probability:.12%}")

    print(f"Information-aware route: {informed:.12%}")
    for reason, probability in informed_parts.most_common():
        print(f"  {reason}: {probability:.12%}")

    print(f"Increment: {informed - baseline:.12%}")


if __name__ == "__main__":
    main()
