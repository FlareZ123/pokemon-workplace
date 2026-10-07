"""Exact destination error from treating played Gladion as discarded for VS Seeker.

The correct model preserves Gladion's card-text destination: after taking a Prize
card into hand, the played Gladion enters the remaining Prize cards. A deliberately
incorrect counterfactual sends played Gladion to the discard pile, where VS Seeker
can return it to hand. The difference measures a concrete failure of the otherwise
valid consumed-rescuer projection once discard-pile Supporter recovery is added.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from math import comb
from typing import Iterator


@dataclass(frozen=True)
class DestinationComparison:
    state_mass: float
    any_critical_prized: float
    literal_success_probability: float
    naive_discard_success_probability: float
    literal_conditional_success: float
    naive_discard_conditional_success: float

    @property
    def conditional_overstatement(self) -> float:
        return self.naive_discard_conditional_success - self.literal_conditional_success


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


def _accepted_opening_probability(deck_size: int, starter_cards: int, opening_hand_size: int) -> float:
    return 1.0 - _choose(deck_size - starter_cards, opening_hand_size) / _choose(
        deck_size, opening_hand_size
    )


@lru_cache(maxsize=None)
def _literal_success(
    turns: int,
    critical: int,
    gladion_hand: int,
    gladion_prize: int,
    seeker_hand: int,
    gladion_deck: int,
    seeker_deck: int,
    other_deck: int,
) -> float:
    if critical == 0:
        return 1.0
    if turns == 0:
        return 0.0
    deck_size = gladion_deck + seeker_deck + other_deck
    if deck_size == 0:
        return 0.0

    probability = 0.0
    for category, count in enumerate((gladion_deck, seeker_deck, other_deck)):
        if count == 0:
            continue
        gh = gladion_hand
        vh = seeker_hand
        gd = gladion_deck
        vd = seeker_deck
        od = other_deck
        if category == 0:
            gh += 1
            gd -= 1
        elif category == 1:
            vh += 1
            vd -= 1
        else:
            od -= 1

        best = _literal_success(
            turns - 1,
            critical,
            gh,
            gladion_prize,
            vh,
            gd,
            vd,
            od,
        )
        if gh > 0:
            best = max(
                best,
                _literal_success(
                    turns - 1,
                    critical - 1,
                    gh - 1,
                    gladion_prize + 1,
                    vh,
                    gd,
                    vd,
                    od,
                ),
            )
            if gladion_prize > 0:
                best = max(
                    best,
                    _literal_success(
                        turns - 1,
                        critical,
                        gh,
                        gladion_prize,
                        vh,
                        gd,
                        vd,
                        od,
                    ),
                )
        probability += (count / deck_size) * best
    return probability


@lru_cache(maxsize=None)
def _naive_discard_success(
    turns: int,
    critical: int,
    gladion_hand: int,
    gladion_discard: int,
    seeker_hand: int,
    gladion_deck: int,
    seeker_deck: int,
    other_deck: int,
) -> float:
    if critical == 0:
        return 1.0
    if turns == 0:
        return 0.0
    deck_size = gladion_deck + seeker_deck + other_deck
    if deck_size == 0:
        return 0.0

    probability = 0.0
    for category, count in enumerate((gladion_deck, seeker_deck, other_deck)):
        if count == 0:
            continue
        gh = gladion_hand
        gx = gladion_discard
        vh = seeker_hand
        gd = gladion_deck
        vd = seeker_deck
        od = other_deck
        if category == 0:
            gh += 1
            gd -= 1
        elif category == 1:
            vh += 1
            vd -= 1
        else:
            od -= 1

        best = 0.0
        max_recoveries = min(vh, gx)
        for recoveries in range(max_recoveries + 1):
            rh = gh + recoveries
            rx = gx - recoveries
            rv = vh - recoveries

            best = max(
                best,
                _naive_discard_success(
                    turns - 1,
                    critical,
                    rh,
                    rx,
                    rv,
                    gd,
                    vd,
                    od,
                ),
            )
            if rh > 0:
                best = max(
                    best,
                    _naive_discard_success(
                        turns - 1,
                        critical - 1,
                        rh - 1,
                        rx + 1,
                        rv,
                        gd,
                        vd,
                        od,
                    ),
                )
        probability += (count / deck_size) * best
    return probability


def compare_gladion_destination(
    deck_size: int,
    prize_count: int,
    *,
    starter_cards: int,
    critical_starter: int,
    critical_nonstarter: int,
    gladion_copies: int,
    vs_seeker_copies: int,
    opening_hand_size: int = 7,
    rescue_turns: int = 1,
) -> DestinationComparison:
    if deck_size <= 0:
        raise ValueError("deck_size must be positive")
    if not 0 <= prize_count <= deck_size:
        raise ValueError("prize_count must fit in deck")
    if opening_hand_size < 0 or opening_hand_size + prize_count > deck_size:
        raise ValueError("opening hand and Prize cards must fit")
    if not 0 < starter_cards <= deck_size:
        raise ValueError("starter_cards must be positive")
    if min(
        critical_starter,
        critical_nonstarter,
        gladion_copies,
        vs_seeker_copies,
        rescue_turns,
    ) < 0:
        raise ValueError("counts and horizon must be non-negative")
    if critical_starter > starter_cards:
        raise ValueError("critical_starter exceeds starters")
    special_nonstarters = critical_nonstarter + gladion_copies + vs_seeker_copies
    if special_nonstarters > deck_size - starter_cards:
        raise ValueError("non-starter categories exceed capacity")

    filler_starter = starter_cards - critical_starter
    filler_nonstarter = deck_size - starter_cards - special_nonstarters
    sizes = (
        critical_starter,
        critical_nonstarter,
        gladion_copies,
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

    _literal_success.cache_clear()
    _naive_discard_success.cache_clear()
    total_mass = 0.0
    any_critical = 0.0
    literal_mass = 0.0
    naive_mass = 0.0

    for hand in _bounded_compositions(opening_hand_size, sizes):
        if hand[0] + hand[4] == 0:
            continue
        hand_mass = _multivariate_probability(
            hand,
            sizes,
            opening_hand_size,
        ) / accepted
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
            vd = after_hand[3] - prizes[3]
            post_prize_deck = deck_size - opening_hand_size - prize_count
            od = post_prize_deck - gd - vd

            literal = _literal_success(
                rescue_turns,
                critical,
                hand[2],
                prizes[2],
                hand[3],
                gd,
                vd,
                od,
            )
            naive = _naive_discard_success(
                rescue_turns,
                critical,
                hand[2],
                0,
                hand[3],
                gd,
                vd,
                od,
            )
            literal_mass += mass * literal
            naive_mass += mass * naive

    return DestinationComparison(
        state_mass=total_mass,
        any_critical_prized=any_critical,
        literal_success_probability=literal_mass,
        naive_discard_success_probability=naive_mass,
        literal_conditional_success=(
            literal_mass / any_critical if any_critical else 1.0
        ),
        naive_discard_conditional_success=(
            naive_mass / any_critical if any_critical else 1.0
        ),
    )
