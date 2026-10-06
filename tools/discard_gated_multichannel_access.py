"""Exact multichannel access through a discard-gated capacity-one connector.

The model separates three quantities:

1. raw naive joint reachability, which ignores the discard cost and reuses the
   same connector independently across target channels;
2. cost-aware naive reachability, which enforces connector payability but still
   ignores one-use capacity;
3. exact joint access, which enforces both the discard gate and connector
   capacity.

Targets, the connector, disposable cards, and protected filler are modeled as
non-starters. Setup-eligible starters are protected from the discard pool.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import comb
from typing import Iterator, Sequence


@dataclass(frozen=True)
class DiscardGatedMultichannelResult:
    """Exact decomposition of raw graph, cost, and capacity effects."""

    state_mass: float
    raw_naive_joint_probability: float
    cost_aware_naive_joint_probability: float
    exact_joint_probability: float
    cost_gate_overstatement_probability: float
    capacity_overstatement_probability: float
    total_overstatement_probability: float


def _choose(n: int, k: int) -> int:
    if k < 0 or k > n:
        return 0
    return comb(n, k)


def _bounded_compositions(
    total: int,
    bounds: tuple[int, ...],
) -> Iterator[tuple[int, ...]]:
    """Yield non-negative tuples summing to total within category bounds."""

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


def accepted_opening_probability(
    deck_size: int,
    starter_cards: int,
    opening_hand_size: int = 7,
) -> float:
    """Return P(opening hand contains at least one setup-eligible starter)."""

    return 1.0 - _choose(
        deck_size - starter_cards,
        opening_hand_size,
    ) / _choose(deck_size, opening_hand_size)


def discard_gated_multichannel_access(
    deck_size: int,
    prize_count: int,
    *,
    starter_cards: int,
    target_copies: Sequence[int],
    connector_copies: int,
    disposable_nonstarters: int,
    discard_cost: int,
    opening_hand_size: int = 7,
    extra_random_draws: int = 0,
) -> DiscardGatedMultichannelResult:
    """Return exact joint access for one discard-gated any-target connector.

    Each usable connector copy can search exactly one missing target channel.
    Disposable cards are exchangeable non-starters that are currently acceptable
    to discard. Connector copies are not counted as disposable in this baseline.
    """

    targets = tuple(target_copies)
    if not targets:
        raise ValueError("target_copies must contain at least one target channel")
    if deck_size <= 0:
        raise ValueError("deck_size must be positive")
    if not 0 <= prize_count <= deck_size:
        raise ValueError("prize_count must fit in the deck")
    if not 0 <= opening_hand_size <= deck_size - prize_count:
        raise ValueError("opening hand must fit before Prize cards")
    if not 0 < starter_cards <= deck_size:
        raise ValueError("starter_cards must be positive and fit in the deck")
    if min(
        *targets,
        connector_copies,
        disposable_nonstarters,
        discard_cost,
        extra_random_draws,
    ) < 0:
        raise ValueError("counts and discard_cost must be non-negative")

    used_nonstarters = (
        sum(targets)
        + connector_copies
        + disposable_nonstarters
    )
    nonstarter_capacity = deck_size - starter_cards
    if used_nonstarters > nonstarter_capacity:
        raise ValueError("modeled non-starter cards exceed deck capacity")

    post_prize_deck = deck_size - opening_hand_size - prize_count
    if extra_random_draws > post_prize_deck:
        raise ValueError("extra_random_draws must fit in the post-Prize deck")

    protected_nonstarters = nonstarter_capacity - used_nonstarters
    target_count = len(targets)
    connector_index = target_count
    disposable_index = target_count + 1
    starter_index = target_count + 2
    sizes = targets + (
        connector_copies,
        disposable_nonstarters,
        starter_cards,
        protected_nonstarters,
    )

    accepted = accepted_opening_probability(
        deck_size,
        starter_cards,
        opening_hand_size,
    )
    if accepted == 0.0:
        raise ValueError("conditioning event has zero probability")

    state_mass = 0.0
    raw_naive = 0.0
    cost_aware_naive = 0.0
    exact = 0.0

    for hand in _bounded_compositions(opening_hand_size, sizes):
        if hand[starter_index] == 0:
            continue

        hand_mass = (
            _multivariate_probability(
                hand,
                sizes,
                opening_hand_size,
            )
            / accepted
        )
        after_hand = tuple(
            size - count
            for size, count in zip(sizes, hand)
        )

        for prizes in _bounded_compositions(
            prize_count,
            after_hand,
        ):
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
                extra_random_draws,
                after_prizes,
            ):
                draw_mass = _multivariate_probability(
                    draws,
                    after_prizes,
                    extra_random_draws,
                )
                mass = hand_mass * prize_mass * draw_mass
                state_mass += mass

                target_in_hand = tuple(
                    hand[index] + draws[index]
                    for index in range(target_count)
                )
                target_in_deck = tuple(
                    after_prizes[index] - draws[index]
                    for index in range(target_count)
                )

                exposed_connectors = (
                    hand[connector_index]
                    + draws[connector_index]
                )
                disposable_cards = (
                    hand[disposable_index]
                    + draws[disposable_index]
                )
                if discard_cost == 0:
                    usable_connectors = exposed_connectors
                else:
                    usable_connectors = min(
                        exposed_connectors,
                        disposable_cards // discard_cost,
                    )

                def naive_joint(connector_count: int) -> bool:
                    return all(
                        in_hand > 0
                        or (
                            connector_count > 0
                            and in_deck > 0
                        )
                        for in_hand, in_deck in zip(
                            target_in_hand,
                            target_in_deck,
                        )
                    )

                raw_success = naive_joint(exposed_connectors)
                cost_aware_success = naive_joint(usable_connectors)

                missing_channels = sum(
                    in_hand == 0
                    for in_hand in target_in_hand
                )
                all_targets_exist = all(
                    in_hand > 0 or in_deck > 0
                    for in_hand, in_deck in zip(
                        target_in_hand,
                        target_in_deck,
                    )
                )
                exact_success = (
                    all_targets_exist
                    and usable_connectors >= missing_channels
                )

                raw_naive += mass * raw_success
                cost_aware_naive += mass * cost_aware_success
                exact += mass * exact_success

    cost_gate_overstatement = raw_naive - cost_aware_naive
    capacity_overstatement = cost_aware_naive - exact
    total_overstatement = raw_naive - exact

    return DiscardGatedMultichannelResult(
        state_mass=state_mass,
        raw_naive_joint_probability=raw_naive,
        cost_aware_naive_joint_probability=cost_aware_naive,
        exact_joint_probability=exact,
        cost_gate_overstatement_probability=cost_gate_overstatement,
        capacity_overstatement_probability=capacity_overstatement,
        total_overstatement_probability=total_overstatement,
    )
