from __future__ import annotations

import math

from iron_thorns_turn1_probability import (
    COUNTS,
    DECK_SIZE,
    OPENING_SIZE,
    PRIZE_COUNT,
    accepted_opening_probability,
    allocations,
)


def route_reachable(hand: list[int], deck: list[int]) -> bool:
    thunder_hand = hand[3] > 0
    dce_hand = hand[4] > 0
    if thunder_hand and dce_hand:
        return True

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
            return True
        return gladion_hand and (
            (thunder_prized and dce_hand)
            or (dce_prized and thunder_hand)
        )

    if gnh_hand:
        return (
            (not thunder_missing or thunder_deck)
            and (not dce_missing or dce_deck)
        )

    return gladion_hand and (
        (thunder_prized and dce_hand)
        or (dce_prized and thunder_hand)
    )


def exact_probability(bonus_draws: int) -> float:
    if bonus_draws < 0:
        raise ValueError("bonus_draws must be nonnegative")

    draw_count = bonus_draws + 1
    accepted = accepted_opening_probability()
    opening_denominator = math.comb(DECK_SIZE, OPENING_SIZE)
    total = 0.0
    success = 0.0

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

            for draws in allocations(draw_count, after_prizes):
                draw_probability = (
                    math.prod(
                        math.comb(after_prizes[index], draws[index])
                        for index in range(len(COUNTS))
                    )
                    / math.comb(
                        DECK_SIZE - OPENING_SIZE - PRIZE_COUNT,
                        draw_count,
                    )
                )
                probability = (
                    opening_probability
                    * prize_probability
                    * draw_probability
                )
                total += probability
                hand = [
                    opening[index] + draws[index]
                    for index in range(len(COUNTS))
                ]
                deck = [
                    after_prizes[index] - draws[index]
                    for index in range(len(COUNTS))
                ]
                if route_reachable(hand, deck):
                    success += probability

    if not math.isclose(total, 1.0, rel_tol=1e-12, abs_tol=1e-12):
        raise AssertionError(f"conditioned probability sums to {total}")
    return success


def main() -> None:
    for bonus_draws in range(7):
        print(
            bonus_draws,
            f"{exact_probability(bonus_draws):.12%}",
        )


if __name__ == "__main__":
    main()
