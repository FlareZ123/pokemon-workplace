"""Exact timed-access probabilities for Prize-rescue packages.

The model conditions on a valid starter-containing opening hand, samples initial
Prize cards from the remaining deck, and then asks whether enough rescue cards
are accessible from the opening hand plus a specified number of later random
draws before a deadline. A separate supporter_opportunities parameter caps how
many rescue Supporters can be played by that deadline.

It deliberately excludes targeted search, ordinary Prize-taking, and recovery of
a rescue card after it has been shuffled into the Prize cards.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import comb
from typing import Iterator


@dataclass(frozen=True)
class TimedRescueResult:
    """Exact probability summary for a timed rescue horizon."""

    state_mass: float
    any_critical_prized: float
    failure_probability: float
    conditional_failure_probability: float


def _choose(n: int, k: int) -> int:
    if k < 0 or k > n:
        return 0
    return comb(n, k)


def _bounded_compositions(total: int, bounds: tuple[int, ...]) -> Iterator[tuple[int, ...]]:
    """Yield tuples summing to total without exceeding per-category bounds."""

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
    ways = 1
    for size, count in zip(sizes, counts):
        ways *= _choose(size, count)
    return ways / _choose(sum(sizes), sample_size)


def _hypergeometric_less_than(
    population: int, successes: int, draws: int, threshold: int
) -> float:
    """Return P(X < threshold) for a hypergeometric random variable."""
    if threshold <= 0:
        return 0.0

    denominator = _choose(population, draws)
    minimum = max(0, draws - (population - successes))
    maximum = min(successes, draws, threshold - 1)
    if minimum > maximum:
        return 0.0

    numerator = sum(
        _choose(successes, value) * _choose(population - successes, draws - value)
        for value in range(minimum, maximum + 1)
    )
    return numerator / denominator


def _category_sizes(
    deck_size: int,
    starter_cards: int,
    critical_starter: int,
    critical_nonstarter: int,
    rescue_starter: int,
    rescue_nonstarter: int,
) -> tuple[int, int, int, int, int, int]:
    if min(critical_starter, critical_nonstarter, rescue_starter, rescue_nonstarter) < 0:
        raise ValueError("critical and rescue counts must be non-negative")
    if critical_starter + rescue_starter > starter_cards:
        raise ValueError("critical/rescue starter counts exceed starter_cards")
    if critical_nonstarter + rescue_nonstarter > deck_size - starter_cards:
        raise ValueError("critical/rescue non-starter counts exceed non-starters")

    return (
        critical_starter,
        critical_nonstarter,
        rescue_starter,
        rescue_nonstarter,
        starter_cards - critical_starter - rescue_starter,
        deck_size - starter_cards - critical_nonstarter - rescue_nonstarter,
    )


def accepted_opening_probability(
    deck_size: int, starter_cards: int, opening_hand_size: int = 7
) -> float:
    """Return P(a random opening hand contains a setup-eligible starter)."""
    return 1.0 - _choose(deck_size - starter_cards, opening_hand_size) / _choose(
        deck_size, opening_hand_size
    )


def timed_rescue_probabilities(
    deck_size: int,
    prize_count: int,
    *,
    starter_cards: int,
    critical_starter: int,
    critical_nonstarter: int,
    rescue_starter: int,
    rescue_nonstarter: int,
    opening_hand_size: int = 7,
    extra_random_draws: int = 0,
    supporter_opportunities: int = 1,
) -> TimedRescueResult:
    """Return exact timed failure probabilities after conditioning on a valid start.

    Category order is critical starter, critical non-starter, rescue starter,
    rescue non-starter, filler starter, filler non-starter. Rescue availability
    consists of rescuers in the accepted opening hand plus rescuers found in
    ``extra_random_draws`` from the post-Prize deck. Failure occurs when at
    least one critical card is Prized and either too few rescue cards are
    accessible by the deadline or too few Supporter play opportunities exist.
    """
    if deck_size <= 0:
        raise ValueError("deck_size must be positive")
    if not 0 <= prize_count <= deck_size:
        raise ValueError("prize_count must be between 0 and deck_size")
    if not 0 <= opening_hand_size <= deck_size - prize_count:
        raise ValueError("opening hand and Prize cards must fit in the deck")
    if not 0 <= starter_cards <= deck_size:
        raise ValueError("starter_cards must be between 0 and deck_size")
    post_prize_deck = deck_size - opening_hand_size - prize_count
    if not 0 <= extra_random_draws <= post_prize_deck:
        raise ValueError("extra_random_draws must fit in the post-Prize deck")
    if supporter_opportunities < 0:
        raise ValueError("supporter_opportunities must be non-negative")

    sizes = _category_sizes(
        deck_size,
        starter_cards,
        critical_starter,
        critical_nonstarter,
        rescue_starter,
        rescue_nonstarter,
    )
    accepted = accepted_opening_probability(deck_size, starter_cards, opening_hand_size)
    if accepted == 0.0:
        raise ValueError("conditioning event has zero probability")

    total_mass = 0.0
    any_critical = 0.0
    failure = 0.0

    for hand in _bounded_compositions(opening_hand_size, sizes):
        if hand[0] + hand[2] + hand[4] == 0:
            continue

        hand_mass = (
            _multivariate_probability(hand, sizes, opening_hand_size) / accepted
        )
        after_hand = tuple(size - count for size, count in zip(sizes, hand))

        for prizes in _bounded_compositions(prize_count, after_hand):
            prize_mass = _multivariate_probability(prizes, after_hand, prize_count)
            state_mass = hand_mass * prize_mass
            total_mass += state_mass

            critical_prized = prizes[0] + prizes[1]
            if critical_prized == 0:
                continue
            any_critical += state_mass

            if critical_prized > supporter_opportunities:
                failure += state_mass
                continue

            rescuers_in_hand = hand[2] + hand[3]
            additional_needed = critical_prized - rescuers_in_hand
            if additional_needed <= 0:
                continue

            after_prizes = tuple(
                size - count for size, count in zip(after_hand, prizes)
            )
            rescuers_in_deck = after_prizes[2] + after_prizes[3]
            draw_failure = _hypergeometric_less_than(
                post_prize_deck,
                rescuers_in_deck,
                extra_random_draws,
                additional_needed,
            )
            failure += state_mass * draw_failure

    conditional = failure / any_critical if any_critical else 0.0
    return TimedRescueResult(total_mass, any_critical, failure, conditional)
