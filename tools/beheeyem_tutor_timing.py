"""Exact T2 tutor rescue versus T3 deferred tutor use for Beheeyem packets.

Uses the same conditioned three-Basic board, six T2 hand cards, six Prizes,
one physical tutor and T3 shuffled draw model as beheeyem_physical_tutor.
The fixed policy is: if the T2 packet is already in hand, keep tutor for T3;
otherwise, play it on T2 if exactly one packet type is missing, the target
is in the unprized T2 deck, and enough neutral cards pay its discard cost.
A T2-used tutor is spent, and searching a card reduces the T3 deck size
from 48 to 47 after first Mysterious Noise recycles B, T, and Elgyem.
"""
from __future__ import annotations

from fractions import Fraction
from functools import lru_cache
from math import comb

from beheeyem_physical_tutor import MODES, choose, exact_physical_tutor


@lru_cache(maxsize=None)
def exact_deferred_or_rescue(
    beheeyem: int, tae: int, turn3_draws: int, tutor: str
) -> tuple[Fraction, Fraction, Fraction, Fraction]:
    """Return (all first packets, both packets, T2-rescued first, rescued both).

    All events are unconditional within the fixed three-Basic established
    board and uniformly randomized remaining 57 cards.
    """
    if not (1 <= beheeyem <= 4 and 1 <= tae <= 4):
        raise ValueError("Packet card counts must be 1..4")
    if not 0 <= turn3_draws <= 47:
        raise ValueError("T2 tutor-rescue branch has at most 47 T3 deck cards")
    if tutor not in MODES:
        raise ValueError(f"Unknown tutor: {tutor}")

    target, payment = MODES[tutor]
    B, T, d = beheeyem, tae, turn3_draws
    filler = 56 - B - T
    hp_space = comb(57, 6) * comb(51, 6)
    d_space = comb(47, d)
    rescued_first = rescued_second = Fraction(0)

    # A T2 rescue requires the physical tutor in the initial hand.
    # If the hand already contains both B and T, the tutor is saved for T3,
    # and that disjoint branch is supplied by exact_physical_tutor.
    for b in range(min(B, 5) + 1):
        for t in range(min(T, 5 - b) + 1):
            if (b > 0) == (t > 0):
                continue  # exactly one category must be initially held
            missing_b = b == 0
            missing_t = t == 0
            if (missing_b and target not in ("pokemon", "either")) or (
                missing_t and target not in ("energy", "either")
            ):
                continue
            f = 5 - b - t  # physical tutor is the sixth T2 hand card
            if f < payment:
                continue
            hand_ways = choose(B, b) * choose(T, t) * choose(filler, f)
            if not hand_ways:
                continue
            for pb in range(B - b + 1):
                for pt in range(T - t + 1):
                    pf = 6 - pb - pt
                    prize_ways = (
                        choose(B - b, pb) * choose(T - t, pt)
                        * choose(filler - f, pf)
                    )
                    if not prize_ways:
                        continue
                    unprized_b = B - b - pb
                    unprized_t = T - t - pt
                    if (missing_b and unprized_b == 0) or (
                        missing_t and unprized_t == 0
                    ):
                        continue

                    p = Fraction(hand_ways * prize_ways, hp_space)
                    rescued_first += p
                    # Search removes exactly one packet card from the
                    # original 45-card deck; the attacking packet and base
                    # return, producing 47 T3 cards.
                    DB = unprized_b + 1 - int(missing_b)
                    DT = unprized_t + 1 - int(missing_t)
                    held_b = b - 1 if b else 0
                    held_t = t - 1 if t else 0
                    if held_b and held_t:
                        q = Fraction(1)
                    elif held_b:
                        q = 1 - Fraction(choose(47 - DT, d), d_space)
                    elif held_t:
                        q = 1 - Fraction(choose(47 - DB, d), d_space)
                    else:
                        q = 1 - Fraction(
                            choose(47 - DB, d) + choose(47 - DT, d)
                            - choose(47 - DB - DT, d), d_space
                        )
                    rescued_second += p * q

    direct_first, _, deferred_both, _ = exact_physical_tutor(B, T, d, tutor)
    return (
        direct_first + rescued_first,
        deferred_both + rescued_second,
        rescued_first,
        rescued_second,
    )
