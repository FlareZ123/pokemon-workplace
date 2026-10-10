"""State-conditioned T2 prefetch versus T3 deferral under uncertain tutor lock.

Model is the conditioned Beheeyem+TAE packet system in this repository. A
single physical tutor can either be held to T3 or used on T2 to prefetch a
future packet card when the T2 first packet already exists. A Bernoulli
exogenous event before T3 may prevent playing THAT tutor class (Items for
Computer Search/Mysterious Treasure/Ultra Ball; Supporters for Guzma & Hala).
The probability is independent of physical draw and the player's policy.

At T2 the player is K1-informed: the full remaining deck and Prize
composition are known when selecting among B/T prefetch targets. Policy
maximizes expected T2+T3 packet access for the specified lock probability,
without conditioning on whether the future lock actually materializes.

Search costs consume only strategically disposable filler cards. All other
board, attack and draw prerequisites remain exogenous and favorable.
"""
from __future__ import annotations

from fractions import Fraction
from functools import lru_cache
from math import comb

from beheeyem_multi_draw_packet import exact_multi_draw_packet
from beheeyem_physical_tutor import MODES, choose, exact_physical_tutor
from beheeyem_tutor_timing import exact_deferred_or_rescue


def at_least_one(copies: int, population: int, draws: int) -> Fraction:
    return 1 - Fraction(choose(population - copies, draws), comb(population, draws))


def blind_packet(
    held_b: int, held_t: int, deck_b: int, deck_t: int, deck_size: int, draws: int
) -> Fraction:
    """Exact probability hand plus d blind draws has at least one B and T."""
    if held_b and held_t:
        return Fraction(1)
    if held_b:
        return at_least_one(deck_t, deck_size, draws)
    if held_t:
        return at_least_one(deck_b, deck_size, draws)
    return 1 - Fraction(
        choose(deck_size - deck_b, draws)
        + choose(deck_size - deck_t, draws)
        - choose(deck_size - deck_b - deck_t, draws),
        comb(deck_size, draws),
    )


def held_tutor_packet(
    held_b: int, held_t: int, deck_b: int, deck_t: int, draws: int, mode: str
) -> Fraction:
    """T3 packet probability when tutor and sufficient payment are in hand."""
    target, _ = MODES[mode]
    if held_b and held_t:
        return Fraction(1)
    if held_b:
        return Fraction(1) if target in ("energy", "either") else at_least_one(deck_t, 48, draws)
    if held_t:
        return Fraction(1) if target in ("pokemon", "either") else at_least_one(deck_b, 48, draws)
    if target == "either":
        return at_least_one(deck_b + deck_t, 48, draws)
    if target == "pokemon":
        return at_least_one(deck_t, 48, draws)
    return at_least_one(deck_b, 48, draws)


def prefetch_targets(
    hand_b: int, hand_t: int, deck_b: int, deck_t: int, draws: int, mode: str
) -> dict[str, Fraction]:
    """Accessible B/T targets in the 45-card T2 deck with resulting T3 odds.

    deck_b and deck_t include the future recycled T2 packet, and therefore
    each exceeds actual pre-attack 45-card stock by one.
    """
    target, _ = MODES[mode]
    outcomes = {}
    if deck_b >= 2 and target in ("pokemon", "either"):
        outcomes["B"] = blind_packet(hand_b, hand_t - 1, deck_b - 1, deck_t, 47, draws)
    if deck_t >= 2 and target in ("energy", "either"):
        outcomes["T"] = blind_packet(hand_b - 1, hand_t, deck_b, deck_t - 1, 47, draws)
    return outcomes


@lru_cache(maxsize=None)
def exact_prefetch_policy(
    beheeyem: int, tae: int, turn3_draws: int, tutor: str,
    tutor_lock_probability: Fraction
) -> tuple[Fraction, Fraction, Fraction, Fraction, int, int]:
    """Return first rate, deferred-only both rate, optimal both rate, uplift,
    eligible K1 states, and K1 states choosing prefetch.

    Policy is contingent on observed T2 hand and known Prizes but must be
    committed before independently sampled tutor-play denial on T3.
    """
    if not 1 <= beheeyem <= 4 or not 1 <= tae <= 4:
        raise ValueError("Packet copies must be 1..4")
    if not 0 <= turn3_draws <= 47:
        raise ValueError("Prefetch-branch T3 deck contains 47 cards")
    if tutor not in MODES:
        raise ValueError(f"Unknown tutor mode: {tutor}")
    if not 0 <= tutor_lock_probability <= 1:
        raise ValueError("Future denial probability must be in [0, 1]")

    B, T, d, q = beheeyem, tae, turn3_draws, tutor_lock_probability
    target, payment = MODES[tutor]
    filler = 56 - B - T
    hp_space = comb(57, 6) * comb(51, 6)

    # The T2 rescue branch already spends the one tutor. Hence a later
    # tutor play lock only changes the direct-first-packet branch.
    first_total, open_both, _, rescued_both = exact_deferred_or_rescue(B, T, d, tutor)
    blind_direct = exact_multi_draw_packet(B, T, d)[1]
    locked_both = blind_direct + rescued_both
    deferred_both = (1 - q) * open_both + q * locked_both

    improvement = Fraction(0)
    eligible = chosen = 0

    # T2 prefetch requires both packet cards and the physical tutor already
    # in the T2 hand. Its protected packet cards are never discarded.
    for b in range(1, B + 1):
        for t in range(1, T + 1):
            if b + t > 5:
                continue
            f = 5 - b - t  # the sixth hand card is the tutor
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
                    DB = B - b - pb + 1
                    DT = T - t - pt + 1
                    options = prefetch_targets(b, t, DB, DT, d, tutor)
                    if not options:
                        continue

                    eligible += 1
                    prefetch = max(options.values())
                    hb, ht = b - 1, t - 1
                    blind = blind_packet(hb, ht, DB, DT, 48, d)
                    open_search = held_tutor_packet(hb, ht, DB, DT, d, tutor)
                    defer = (1 - q) * open_search + q * blind
                    if prefetch > defer:
                        chosen += 1
                        state_weight = Fraction(hand_ways * prize_ways, hp_space)
                        improvement += state_weight * (prefetch - defer)

    return (
        first_total, deferred_both, deferred_both + improvement,
        improvement, eligible, chosen,
    )
