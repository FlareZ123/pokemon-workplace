"""Exact Prize rescue through Battle Compressor -> VS Seeker -> Gladion.

This model preserves zone provenance. Battle Compressor may move Gladion from the
deck to the discard pile, VS Seeker may move a discarded Gladion to the hand, and
a Gladion that is actually played moves to the Prize zone after taking a Prize.
An optional incorrect counterfactual sends played Gladion to discard so the
post-play recycling error can be quantified inside the same access chain.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from math import comb
from typing import Iterator


@dataclass(frozen=True)
class CompressorSeekerResult:
    state_mass: float
    any_critical_prized: float
    success_probability: float
    conditional_success_probability: float


def _choose(n: int, k: int) -> int:
    if k < 0 or k > n:
        return 0
    return comb(n, k)


def _bounded_compositions(total: int, bounds: tuple[int, ...]) -> Iterator[tuple[int, ...]]:
    def visit(index: int, remaining: int, prefix: tuple[int, ...]) -> Iterator[tuple[int, ...]]:
        if index == len(bounds) - 1:
            if 0 <= remaining <= bounds[index]:
                yield prefix + (remaining,)
            return
        for value in range(min(bounds[index], remaining) + 1):
            yield from visit(index + 1, remaining - value, prefix + (value,))

    yield from visit(0, total, ())


def _multivariate_probability(
    counts: tuple[int, ...], sizes: tuple[int, ...], sample_size: int
) -> float:
    numerator = 1
    for size, count in zip(sizes, counts):
        numerator *= _choose(size, count)
    return numerator / _choose(sum(sizes), sample_size)


def _accepted_opening_probability(deck_size: int, starters: int, opening: int) -> float:
    return 1.0 - _choose(deck_size - starters, opening) / _choose(
        deck_size, opening
    )


@lru_cache(maxsize=None)
def _success(
    turns: int,
    critical: int,
    g_hand: int,
    g_discard: int,
    g_prize: int,
    b_hand: int,
    v_hand: int,
    g_deck: int,
    b_deck: int,
    v_deck: int,
    other_deck: int,
    played_to_discard: bool,
) -> float:
    if critical == 0:
        return 1.0
    if turns == 0:
        return 0.0

    deck_size = g_deck + b_deck + v_deck + other_deck
    if deck_size == 0:
        return 0.0

    probability = 0.0
    draw_counts = (g_deck, b_deck, v_deck, other_deck)
    for category, count in enumerate(draw_counts):
        if count == 0:
            continue

        gh, gx, gp = g_hand, g_discard, g_prize
        bh, vh = b_hand, v_hand
        gd, bd, vd, od = g_deck, b_deck, v_deck, other_deck
        if category == 0:
            gh += 1
            gd -= 1
        elif category == 1:
            bh += 1
            bd -= 1
        elif category == 2:
            vh += 1
            vd -= 1
        else:
            od -= 1

        best = 0.0

        for compressors in range(bh + 1):
            max_compressed = min(gd, 3 * compressors)
            for compressed in range(max_compressed + 1):
                if compressors > 0 and compressed == 0:
                    continue
                if compressors > 0 and compressed <= 3 * (compressors - 1):
                    continue

                abh = bh - compressors
                agd = gd - compressed
                agx = gx + compressed

                for recoveries in range(min(vh, agx) + 1):
                    agh = gh + recoveries
                    agx2 = agx - recoveries
                    avh = vh - recoveries

                    best = max(
                        best,
                        _success(
                            turns - 1,
                            critical,
                            agh,
                            agx2,
                            gp,
                            abh,
                            avh,
                            agd,
                            bd,
                            vd,
                            od,
                            played_to_discard,
                        ),
                    )

                    if agh > 0:
                        next_discard = agx2 + int(played_to_discard)
                        next_prize = gp + int(not played_to_discard)
                        best = max(
                            best,
                            _success(
                                turns - 1,
                                critical - 1,
                                agh - 1,
                                next_discard,
                                next_prize,
                                abh,
                                avh,
                                agd,
                                bd,
                                vd,
                                od,
                                played_to_discard,
                            ),
                        )

        probability += (count / deck_size) * best

    return probability


def compressor_seeker_rescue_success(
    deck_size: int,
    prize_count: int,
    *,
    starter_cards: int,
    critical_starter: int,
    critical_nonstarter: int,
    gladion_copies: int,
    compressor_copies: int,
    vs_seeker_copies: int,
    opening_hand_size: int = 7,
    rescue_turns: int = 1,
    played_to_discard: bool = False,
) -> CompressorSeekerResult:
    if deck_size <= 0:
        raise ValueError("deck_size must be positive")
    if not 0 <= prize_count <= deck_size:
        raise ValueError("prize_count must fit in deck")
    if opening_hand_size < 0 or opening_hand_size + prize_count > deck_size:
        raise ValueError("opening and Prize cards must fit")
    if not 0 < starter_cards <= deck_size:
        raise ValueError("starter_cards must be positive")
    if min(
        critical_starter,
        critical_nonstarter,
        gladion_copies,
        compressor_copies,
        vs_seeker_copies,
        rescue_turns,
    ) < 0:
        raise ValueError("counts and horizon must be non-negative")
    if critical_starter > starter_cards:
        raise ValueError("critical_starter exceeds starter count")

    special_nonstarters = (
        critical_nonstarter
        + gladion_copies
        + compressor_copies
        + vs_seeker_copies
    )
    if special_nonstarters > deck_size - starter_cards:
        raise ValueError("non-starter categories exceed capacity")

    filler_starter = starter_cards - critical_starter
    filler_nonstarter = deck_size - starter_cards - special_nonstarters
    sizes = (
        critical_starter,
        critical_nonstarter,
        gladion_copies,
        compressor_copies,
        vs_seeker_copies,
        filler_starter,
        filler_nonstarter,
    )
    accepted = _accepted_opening_probability(
        deck_size,
        starter_cards,
        opening_hand_size,
    )
    if accepted == 0.0:
        raise ValueError("conditioning event has zero probability")

    _success.cache_clear()
    total_mass = 0.0
    any_critical = 0.0
    success_mass = 0.0

    for hand in _bounded_compositions(opening_hand_size, sizes):
        if hand[0] + hand[5] == 0:
            continue
        hand_mass = (
            _multivariate_probability(hand, sizes, opening_hand_size) / accepted
        )
        after_hand = tuple(size - count for size, count in zip(sizes, hand))

        for prizes in _bounded_compositions(prize_count, after_hand):
            prize_mass = _multivariate_probability(
                prizes,
                after_hand,
                prize_count,
            )
            mass = hand_mass * prize_mass
            total_mass += mass
            critical = prizes[0] + prizes[1]
            if critical == 0:
                continue
            any_critical += mass

            gd = after_hand[2] - prizes[2]
            bd = after_hand[3] - prizes[3]
            vd = after_hand[4] - prizes[4]
            post_prize = deck_size - opening_hand_size - prize_count
            od = post_prize - gd - bd - vd

            value = _success(
                rescue_turns,
                critical,
                hand[2],
                0,
                prizes[2],
                hand[3],
                hand[4],
                gd,
                bd,
                vd,
                od,
                played_to_discard,
            )
            success_mass += mass * value

    return CompressorSeekerResult(
        state_mass=total_mass,
        any_critical_prized=any_critical,
        success_probability=success_mass,
        conditional_success_probability=(
            success_mass / any_critical if any_critical else 1.0
        ),
    )
