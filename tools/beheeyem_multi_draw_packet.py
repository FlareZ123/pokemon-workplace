"""Exact packet recurrence after any number of blind T3 draws (0..48).

An already-established two-Elgyem plus anchor board is conditioned as given.
The six other T2 hand cards are sampled from a residual 57-card pool containing
B Beheeyem, T Triple Acceleration Energy and neutral filler. Six Prizes from
the 51 unseen leave 45 deck cards; first Mysterious Noise returns its three-
card evolved stack and attached TAE, making the T3 shuffled deck 48 cards.
"""
from __future__ import annotations

from fractions import Fraction
from functools import lru_cache
from math import comb


def choose(n: int, k: int) -> int:
    """Zero for impossible selections, exact integer binomial otherwise."""
    return comb(n, k) if 0 <= k <= n else 0


@lru_cache(maxsize=None)
def exact_multi_draw_packet(
    beheeyem: int, tae: int, turn3_draws: int
) -> tuple[Fraction, Fraction]:
    """Return probabilities (T2 packet, T2+T3 packets) in conditioned setup."""
    if not 1 <= beheeyem <= 4 or not 1 <= tae <= 4:
        raise ValueError("Each packet copy count must be between one and four")
    if not 0 <= turn3_draws <= 48:
        raise ValueError("T3 samples from a 48-card shuffled deck")

    filler = 57 - beheeyem - tae
    hand_space = comb(57, 6)
    prize_space = comb(51, 6)
    draw_space = comb(48, turn3_draws)
    first = second = Fraction(0)

    for b in range(beheeyem + 1):
        for t in range(tae + 1):
            rest = 6 - b - t
            if not 0 <= rest <= filler:
                continue
            hand = Fraction(
                choose(beheeyem, b) * choose(tae, t) * choose(filler, rest),
                hand_space,
            )
            if b == 0 or t == 0:
                continue

            first += hand
            remaining_b = beheeyem - b
            remaining_t = tae - t
            remaining_filler = filler - rest
            for prized_b in range(remaining_b + 1):
                for prized_t in range(remaining_t + 1):
                    prized_filler = 6 - prized_b - prized_t
                    if not 0 <= prized_filler <= remaining_filler:
                        continue
                    p_prizes = Fraction(
                        choose(remaining_b, prized_b)
                        * choose(remaining_t, prized_t)
                        * choose(remaining_filler, prized_filler),
                        prize_space,
                    )
                    # The spent B and T are shuffled back with the Elgyem
                    # stage below B. Count each physical card exactly once.
                    deck_b = remaining_b - prized_b + 1
                    deck_t = remaining_t - prized_t + 1
                    hand_has_b = b >= 2
                    hand_has_t = t >= 2
                    if hand_has_b and hand_has_t:
                        p_second = Fraction(1)
                    elif hand_has_b:
                        p_second = 1 - Fraction(
                            choose(48 - deck_t, turn3_draws), draw_space
                        )
                    elif hand_has_t:
                        p_second = 1 - Fraction(
                            choose(48 - deck_b, turn3_draws), draw_space
                        )
                    else:
                        # The T3 draw subset must intersect both missing
                        # categories; apply two-event inclusion-exclusion.
                        p_second = 1 - Fraction(
                            choose(48 - deck_b, turn3_draws)
                            + choose(48 - deck_t, turn3_draws)
                            - choose(48 - deck_b - deck_t, turn3_draws),
                            draw_space,
                        )
                    second += hand * p_prizes * p_second
    return first, second
