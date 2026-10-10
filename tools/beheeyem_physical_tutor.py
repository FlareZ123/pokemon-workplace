"""Exact physical one-copy T3 tutor access for a conditioned Beheeyem loop.

Three T1 Basic board cards are fixed. T2 sees six uniformly sampled cards
from the remaining 57, then six Prizes from 51 and a 45-card deck. A direct
Beheeyem + TAE hand packet attacks and returns B, T and its Elgyem base
to the 45-card deck. On T3, d cards are drawn from the shuffled 48-card
deck. One physical tutor (among the 57) may then find ONE missing packet
type when held and its discard payment can use neutral filler cards.

Computer Search searches either type and costs two discards; Mysterious
Treasure searches the Psychic Beheeyem and costs one; Ultra Ball searches
Beheeyem and costs two; Guzma & Hala searches TAE and costs two.
The 57-card filler pool includes the tutor replacement slot, but neutral
filler is optimistically assumed disposable. This is packet availability
conditioned on an established board, not attack or win probability.
"""
from __future__ import annotations

from functools import lru_cache
from fractions import Fraction
from math import comb

# (searchable missing category, number of other cards discarded)
MODES = {
    "computer_search": ("either", 2),
    "mysterious_treasure": ("pokemon", 1),
    "ultra_ball": ("pokemon", 2),
    "guzma_hala": ("energy", 2),
}


def choose(n: int, k: int) -> int:
    return comb(n, k) if 0 <= k <= n else 0


@lru_cache(maxsize=None)
def exact_physical_tutor(
    beheeyem: int, tae: int, turn3_draws: int, tutor: str
) -> tuple[Fraction, Fraction, Fraction, Fraction]:
    """Return (T2 packet, blind T2+T3, physical-tutor T2+T3, ideal-tutor bound)."""
    if not (1 <= beheeyem <= 4 and 1 <= tae <= 4):
        raise ValueError("Packet counts must be 1..4")
    if not 0 <= turn3_draws <= 48:
        raise ValueError("T3 blind draws must be 0..48")
    if tutor not in MODES:
        raise ValueError(f"Unknown tutor: {tutor}")
    target, payment = MODES[tutor]
    B, T, d = beheeyem, tae, turn3_draws
    filler = 56 - B - T  # one of 57 residual cards is the physical tutor
    denominator = comb(57, 6) * comb(51, 6) * comb(48, d)
    first = blind = assisted = ideal = 0

    for b in range(1, min(B, 6) + 1):
        for t in range(1, min(T, 6 - b) + 1):
            for u in (0, 1):
                f = 6 - b - t - u
                hand_ways = choose(B, b) * choose(T, t) * choose(1, u) * choose(filler, f)
                if not hand_ways:
                    continue
                for pb in range(B - b + 1):
                    for pt in range(T - t + 1):
                        for pu in range(2 - u):
                            pf = 6 - pb - pt - pu
                            prize_ways = (
                                choose(B - b, pb) * choose(T - t, pt)
                                * choose(1 - u, pu) * choose(filler - f, pf)
                            )
                            if not prize_ways:
                                continue
                            # B, T and the evolved-from Elgyem return to deck.
                            DB, DT, DU = B - b - pb + 1, T - t - pt + 1, 1 - u - pu
                            DF = 48 - DB - DT - DU
                            first += hand_ways * prize_ways * comb(48, d)

                            for db in range(min(d, DB) + 1):
                                for dt in range(min(d - db, DT) + 1):
                                    for du in range(min(d - db - dt, DU) + 1):
                                        df = d - db - dt - du
                                        draw_ways = (
                                            choose(DB, db) * choose(DT, dt)
                                            * choose(DU, du) * choose(DF, df)
                                        )
                                        if not draw_ways:
                                            continue
                                        ways = hand_ways * prize_ways * draw_ways
                                        have_b = b - 1 + db > 0
                                        have_t = t - 1 + dt > 0
                                        complete = have_b and have_t
                                        has_tutor = u + du > 0
                                        can_pay = f + df >= payment
                                        tutor_finds_missing = (
                                            (not have_b and have_t and target in ("pokemon", "either"))
                                            or (have_b and not have_t and target in ("energy", "either"))
                                        )
                                        blind += ways * complete
                                        assisted += ways * (
                                            complete or (has_tutor and can_pay and tutor_finds_missing)
                                        )
                                        # Upper bound: one guaranteed free universal
                                        # tutor available after blind draws.
                                        ideal += ways * (have_b or have_t)

    return tuple(Fraction(n, denominator) for n in (first, blind, assisted, ideal))
