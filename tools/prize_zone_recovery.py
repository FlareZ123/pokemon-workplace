"""Exact zone-compatible Prize recovery for deck-search payloads.

The model conditions on a legal starter-containing opening, then separates Prize
cards from ordinary pre-search draws so Prize-reset effects can be represented
with their actual destination zones.

Target groups are assumed to be non-Basic and disjoint from the forced-starter
class. The model asks whether each target group retains a required number of
copies in the deck at the search window.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from math import comb
from typing import Iterator


@dataclass(frozen=True)
class PrizeZoneRecoveryMetrics:
    state_mass: float
    baseline_searchable: float
    blind_rotom_searchable: float
    blind_ticket_searchable: float
    rotom_rescue_mass: float
    rotom_break_mass: float
    ticket_rescue_mass: float
    ticket_break_mass: float
    baseline_failure_with_target_prized: float
    baseline_failure_without_target_prized: float

    @property
    def informed_rotom_searchable(self) -> float:
        return self.baseline_searchable + self.rotom_rescue_mass

    @property
    def informed_ticket_searchable(self) -> float:
        return self.baseline_searchable + self.ticket_rescue_mass


def _choose(n: int, k: int) -> int:
    if k < 0 or k > n:
        return 0
    return comb(n, k)


def _bounded_compositions(
    total: int,
    bounds: tuple[int, ...],
) -> Iterator[tuple[int, ...]]:
    def visit(
        index: int,
        remaining: int,
        prefix: tuple[int, ...],
    ) -> Iterator[tuple[int, ...]]:
        if index == len(bounds) - 1:
            if 0 <= remaining <= bounds[index]:
                yield prefix + (remaining,)
            return

        for value in range(min(bounds[index], remaining) + 1):
            yield from visit(
                index + 1,
                remaining - value,
                prefix + (value,),
            )

    yield from visit(0, total, ())


def _multivariate_probability(
    counts: tuple[int, ...],
    sizes: tuple[int, ...],
    sample_size: int,
) -> float:
    numerator = 1
    for size, count in zip(sizes, counts):
        numerator *= _choose(size, count)
    return numerator / _choose(sum(sizes), sample_size)


def analyze_prize_zone_recovery(
    deck_size: int,
    forced_starters: int,
    target_copies: tuple[int, ...],
    *,
    opening_hand_size: int = 7,
    prize_count: int = 6,
    pre_search_draws: int = 1,
    required_remaining: tuple[int, ...] | None = None,
) -> PrizeZoneRecoveryMetrics:
    """Return exact searchability before and after two Prize-reset effects.

    Rotom Dex is modeled as returning the current Prize cards to the deck,
    shuffling, then selecting a fresh Prize set from the combined pool.

    Redeemable Ticket is modeled as putting the current Prize cards on the
    bottom of the deck, then selecting the replacement Prize set from the
    pre-existing deck above them. Thus old Prizes are protected from immediate
    re-Prizing, while cards already in the deck can become new Prizes.

    The informed metrics apply the reset only in baseline-failing states.
    """
    target_copies = tuple(target_copies)
    if required_remaining is None:
        required_remaining = (1,) * len(target_copies)
    required_remaining = tuple(required_remaining)

    if deck_size <= 0:
        raise ValueError("deck_size must be positive")
    if forced_starters <= 0:
        raise ValueError("forced_starters must be positive")
    if len(target_copies) != len(required_remaining):
        raise ValueError("required_remaining must match target_copies")
    if any(copies < 0 for copies in target_copies):
        raise ValueError("target copy counts must be non-negative")
    if any(need < 0 for need in required_remaining):
        raise ValueError("required copy counts must be non-negative")
    if any(
        need > copies
        for need, copies in zip(required_remaining, target_copies)
    ):
        return PrizeZoneRecoveryMetrics(*(0.0 for _ in range(10)))
    if min(opening_hand_size, prize_count, pre_search_draws) < 0:
        raise ValueError("zone sizes must be non-negative")
    if opening_hand_size + prize_count + pre_search_draws > deck_size:
        raise ValueError("opening, Prize cards, and draws exceed deck size")

    target_total = sum(target_copies)
    filler = deck_size - forced_starters - target_total
    if filler < 0:
        raise ValueError("category counts exceed deck size")

    sizes = target_copies + (forced_starters, filler)
    target_count = len(target_copies)
    accepted = 1.0 - (
        _choose(deck_size - forced_starters, opening_hand_size)
        / _choose(deck_size, opening_hand_size)
    )
    if accepted == 0.0:
        raise ValueError("accepted opening has zero probability")

    @lru_cache(maxsize=None)
    def rotom_success_probability(
        pool_targets: tuple[int, ...],
    ) -> float:
        pool_size = deck_size - opening_hand_size - pre_search_draws
        other = pool_size - sum(pool_targets)
        bounds = pool_targets + (other,)
        denominator = _choose(pool_size, prize_count)
        favorable = 0

        for new_prizes in _bounded_compositions(prize_count, bounds):
            if not all(
                pool_targets[index] - new_prizes[index]
                >= required_remaining[index]
                for index in range(target_count)
            ):
                continue

            ways = 1
            for size, count in zip(bounds, new_prizes):
                ways *= _choose(size, count)
            favorable += ways

        return favorable / denominator

    @lru_cache(maxsize=None)
    def ticket_success_probability(
        deck_targets: tuple[int, ...],
        old_prize_targets: tuple[int, ...],
    ) -> float:
        current_deck_size = (
            deck_size
            - opening_hand_size
            - prize_count
            - pre_search_draws
        )
        other = current_deck_size - sum(deck_targets)
        bounds = deck_targets + (other,)
        denominator = _choose(current_deck_size, prize_count)
        favorable = 0

        for new_prizes in _bounded_compositions(prize_count, bounds):
            if not all(
                deck_targets[index]
                - new_prizes[index]
                + old_prize_targets[index]
                >= required_remaining[index]
                for index in range(target_count)
            ):
                continue

            ways = 1
            for size, count in zip(bounds, new_prizes):
                ways *= _choose(size, count)
            favorable += ways

        return favorable / denominator

    state_mass = 0.0
    baseline_searchable = 0.0
    blind_rotom_searchable = 0.0
    blind_ticket_searchable = 0.0
    rotom_rescue_mass = 0.0
    rotom_break_mass = 0.0
    ticket_rescue_mass = 0.0
    ticket_break_mass = 0.0
    failure_with_target_prized = 0.0
    failure_without_target_prized = 0.0

    for hand in _bounded_compositions(opening_hand_size, sizes):
        if hand[target_count] == 0:
            continue

        hand_mass = (
            _multivariate_probability(hand, sizes, opening_hand_size)
            / accepted
        )
        after_hand = tuple(
            size - count for size, count in zip(sizes, hand)
        )

        for prizes in _bounded_compositions(prize_count, after_hand):
            prize_mass = _multivariate_probability(
                prizes,
                after_hand,
                prize_count,
            )
            after_prizes = tuple(
                size - count
                for size, count in zip(after_hand, prizes)
            )

            for draws in _bounded_compositions(
                pre_search_draws,
                after_prizes,
            ):
                draw_mass = _multivariate_probability(
                    draws,
                    after_prizes,
                    pre_search_draws,
                )
                mass = hand_mass * prize_mass * draw_mass
                remaining_deck = tuple(
                    size - count
                    for size, count in zip(after_prizes, draws)
                )
                deck_targets = remaining_deck[:target_count]
                prize_targets = prizes[:target_count]

                baseline = all(
                    deck_targets[index] >= required_remaining[index]
                    for index in range(target_count)
                )

                returned_pool_targets = tuple(
                    deck_targets[index] + prize_targets[index]
                    for index in range(target_count)
                )
                rotom_success = rotom_success_probability(
                    returned_pool_targets
                )
                ticket_success = ticket_success_probability(
                    deck_targets,
                    prize_targets,
                )

                state_mass += mass
                baseline_searchable += mass * baseline
                blind_rotom_searchable += mass * rotom_success
                blind_ticket_searchable += mass * ticket_success

                if baseline:
                    rotom_break_mass += mass * (1.0 - rotom_success)
                    ticket_break_mass += mass * (1.0 - ticket_success)
                else:
                    rotom_rescue_mass += mass * rotom_success
                    ticket_rescue_mass += mass * ticket_success
                    if any(prize_targets):
                        failure_with_target_prized += mass
                    else:
                        failure_without_target_prized += mass

    return PrizeZoneRecoveryMetrics(
        state_mass=state_mass,
        baseline_searchable=baseline_searchable,
        blind_rotom_searchable=blind_rotom_searchable,
        blind_ticket_searchable=blind_ticket_searchable,
        rotom_rescue_mass=rotom_rescue_mass,
        rotom_break_mass=rotom_break_mass,
        ticket_rescue_mass=ticket_rescue_mass,
        ticket_break_mass=ticket_break_mass,
        baseline_failure_with_target_prized=failure_with_target_prized,
        baseline_failure_without_target_prized=failure_without_target_prized,
    )


def main() -> None:
    for profile in ((1,), (2,), (2, 2), (2, 1), (2, 2, 2, 1)):
        result = analyze_prize_zone_recovery(60, 14, profile)
        print(
            profile,
            f"baseline={100 * result.baseline_searchable:.6f}%",
            f"informed_rotom={100 * result.informed_rotom_searchable:.6f}%",
            f"informed_ticket={100 * result.informed_ticket_searchable:.6f}%",
        )


if __name__ == "__main__":
    main()
