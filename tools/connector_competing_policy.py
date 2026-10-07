"""Exact finite-horizon allocation of one universal connector between two goals.

The model extends the repository's Prize-rescue and discard-gate work with one
competing setup target. A single Computer Search-like connector can search
either a setup resource or a Gladion-like rescue Supporter. Dynamic programming
chooses whether to spend it, which target to take, and whether waiting has
higher future value.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from math import comb
from typing import Iterator, Literal


PriorityPolicy = Literal["setup_priority", "rescue_priority", "never_connector"]


@dataclass(frozen=True)
class CompetingConnectorResult:
    """Exact success probabilities for competing connector uses."""

    state_mass: float
    any_critical_prized: float
    optimal_success_probability: float
    conditional_optimal_success: float
    setup_priority_success_probability: float
    conditional_setup_priority_success: float
    rescue_priority_success_probability: float
    conditional_rescue_priority_success: float
    no_connector_success_probability: float
    conditional_no_connector_success: float


def _choose(n: int, k: int) -> int:
    if k < 0 or k > n:
        return 0
    return comb(n, k)


def _bounded_compositions(
    total: int, bounds: tuple[int, ...]
) -> Iterator[tuple[int, ...]]:
    def visit(
        index: int, remaining: int, prefix: tuple[int, ...]
    ) -> Iterator[tuple[int, ...]]:
        if index == len(bounds) - 1:
            if 0 <= remaining <= bounds[index]:
                yield prefix + (remaining,)
            return

        for value in range(min(bounds[index], remaining) + 1):
            yield from visit(
                index + 1, remaining - value, prefix + (value,)
            )

    yield from visit(0, total, ())


def _multivariate_probability(
    counts: tuple[int, ...], sizes: tuple[int, ...], sample_size: int
) -> float:
    numerator = 1
    for size, count in zip(sizes, counts):
        numerator *= _choose(size, count)
    return numerator / _choose(sum(sizes), sample_size)


def accepted_opening_probability(
    deck_size: int, starter_cards: int, opening_hand_size: int = 7
) -> float:
    return 1.0 - _choose(
        deck_size - starter_cards, opening_hand_size
    ) / _choose(deck_size, opening_hand_size)


@lru_cache(maxsize=None)
def _optimal_success_from_state(
    turns_remaining: int,
    critical_remaining: int,
    setup_secured: bool,
    rescue_in_hand: int,
    connector_in_hand: int,
    disposable_in_hand: int,
    setup_in_deck: int,
    rescue_in_deck: int,
    connector_in_deck: int,
    disposable_in_deck: int,
    other_in_deck: int,
    discard_cost: int,
) -> float:
    if setup_secured and critical_remaining == 0:
        return 1.0
    if turns_remaining == 0:
        return 0.0

    deck_size = (
        setup_in_deck
        + rescue_in_deck
        + connector_in_deck
        + disposable_in_deck
        + other_in_deck
    )
    if deck_size == 0:
        return 0.0

    probability = 0.0
    draw_counts = (
        setup_in_deck,
        rescue_in_deck,
        connector_in_deck,
        disposable_in_deck,
        other_in_deck,
    )

    for category, count in enumerate(draw_counts):
        if count == 0:
            continue

        setup_now = setup_secured
        rescue_hand = rescue_in_hand
        connector_hand = connector_in_hand
        disposable_hand = disposable_in_hand
        setup_deck = setup_in_deck
        rescue_deck = rescue_in_deck
        connector_deck = connector_in_deck
        disposable_deck = disposable_in_deck
        other_deck = other_in_deck

        if category == 0:
            setup_deck -= 1
            setup_now = True
        elif category == 1:
            rescue_deck -= 1
            rescue_hand += 1
        elif category == 2:
            connector_deck -= 1
            connector_hand += 1
        elif category == 3:
            disposable_deck -= 1
            disposable_hand += 1
        else:
            other_deck -= 1

        action_values = [
            _optimal_success_from_state(
                turns_remaining - 1,
                critical_remaining,
                setup_now,
                rescue_hand,
                connector_hand,
                disposable_hand,
                setup_deck,
                rescue_deck,
                connector_deck,
                disposable_deck,
                other_deck,
                discard_cost,
            )
        ]

        if critical_remaining > 0 and rescue_hand > 0:
            action_values.append(
                _optimal_success_from_state(
                    turns_remaining - 1,
                    critical_remaining - 1,
                    setup_now,
                    rescue_hand - 1,
                    connector_hand,
                    disposable_hand,
                    setup_deck,
                    rescue_deck,
                    connector_deck,
                    disposable_deck,
                    other_deck,
                    discard_cost,
                )
            )

        connector_payable = (
            connector_hand > 0 and disposable_hand >= discard_cost
        )
        if connector_payable:
            if not setup_now and setup_deck > 0:
                action_values.append(
                    _optimal_success_from_state(
                        turns_remaining - 1,
                        critical_remaining,
                        True,
                        rescue_hand,
                        connector_hand - 1,
                        disposable_hand - discard_cost,
                        setup_deck - 1,
                        rescue_deck,
                        connector_deck,
                        disposable_deck,
                        other_deck,
                        discard_cost,
                    )
                )
                if critical_remaining > 0 and rescue_hand > 0:
                    action_values.append(
                        _optimal_success_from_state(
                            turns_remaining - 1,
                            critical_remaining - 1,
                            True,
                            rescue_hand - 1,
                            connector_hand - 1,
                            disposable_hand - discard_cost,
                            setup_deck - 1,
                            rescue_deck,
                            connector_deck,
                            disposable_deck,
                            other_deck,
                            discard_cost,
                        )
                    )

            if critical_remaining > 0 and rescue_deck > 0:
                action_values.append(
                    _optimal_success_from_state(
                        turns_remaining - 1,
                        critical_remaining,
                        setup_now,
                        rescue_hand + 1,
                        connector_hand - 1,
                        disposable_hand - discard_cost,
                        setup_deck,
                        rescue_deck - 1,
                        connector_deck,
                        disposable_deck,
                        other_deck,
                        discard_cost,
                    )
                )
                action_values.append(
                    _optimal_success_from_state(
                        turns_remaining - 1,
                        critical_remaining - 1,
                        setup_now,
                        rescue_hand,
                        connector_hand - 1,
                        disposable_hand - discard_cost,
                        setup_deck,
                        rescue_deck - 1,
                        connector_deck,
                        disposable_deck,
                        other_deck,
                        discard_cost,
                    )
                )

        probability += (count / deck_size) * max(action_values)

    return probability


@lru_cache(maxsize=None)
def _priority_success_from_state(
    policy: PriorityPolicy,
    turns_remaining: int,
    critical_remaining: int,
    setup_secured: bool,
    rescue_in_hand: int,
    connector_in_hand: int,
    disposable_in_hand: int,
    setup_in_deck: int,
    rescue_in_deck: int,
    connector_in_deck: int,
    disposable_in_deck: int,
    other_in_deck: int,
    discard_cost: int,
) -> float:
    if setup_secured and critical_remaining == 0:
        return 1.0
    if turns_remaining == 0:
        return 0.0

    deck_size = (
        setup_in_deck
        + rescue_in_deck
        + connector_in_deck
        + disposable_in_deck
        + other_in_deck
    )
    if deck_size == 0:
        return 0.0

    probability = 0.0
    draw_counts = (
        setup_in_deck,
        rescue_in_deck,
        connector_in_deck,
        disposable_in_deck,
        other_in_deck,
    )

    for category, count in enumerate(draw_counts):
        if count == 0:
            continue

        setup_now = setup_secured
        rescue_hand = rescue_in_hand
        connector_hand = connector_in_hand
        disposable_hand = disposable_in_hand
        setup_deck = setup_in_deck
        rescue_deck = rescue_in_deck
        connector_deck = connector_in_deck
        disposable_deck = disposable_in_deck
        other_deck = other_in_deck

        if category == 0:
            setup_deck -= 1
            setup_now = True
        elif category == 1:
            rescue_deck -= 1
            rescue_hand += 1
        elif category == 2:
            connector_deck -= 1
            connector_hand += 1
        elif category == 3:
            disposable_deck -= 1
            disposable_hand += 1
        else:
            other_deck -= 1

        connector_payable = (
            connector_hand > 0 and disposable_hand >= discard_cost
        )
        setup_search_available = (
            connector_payable and not setup_now and setup_deck > 0
        )
        rescue_search_available = (
            connector_payable
            and critical_remaining > 0
            and rescue_hand == 0
            and rescue_deck > 0
        )

        if policy == "setup_priority":
            if setup_search_available:
                setup_deck -= 1
                setup_now = True
                connector_hand -= 1
                disposable_hand -= discard_cost
            elif rescue_search_available:
                rescue_deck -= 1
                rescue_hand += 1
                connector_hand -= 1
                disposable_hand -= discard_cost
        elif policy == "rescue_priority":
            if rescue_search_available:
                rescue_deck -= 1
                rescue_hand += 1
                connector_hand -= 1
                disposable_hand -= discard_cost
            elif setup_search_available:
                setup_deck -= 1
                setup_now = True
                connector_hand -= 1
                disposable_hand -= discard_cost
        elif policy != "never_connector":
            raise ValueError(f"unsupported policy: {policy}")

        if critical_remaining > 0 and rescue_hand > 0:
            critical_remaining_after = critical_remaining - 1
            rescue_hand_after = rescue_hand - 1
        else:
            critical_remaining_after = critical_remaining
            rescue_hand_after = rescue_hand

        probability += (count / deck_size) * _priority_success_from_state(
            policy,
            turns_remaining - 1,
            critical_remaining_after,
            setup_now,
            rescue_hand_after,
            connector_hand,
            disposable_hand,
            setup_deck,
            rescue_deck,
            connector_deck,
            disposable_deck,
            other_deck,
            discard_cost,
        )

    return probability


def competing_connector_success(
    deck_size: int,
    prize_count: int,
    *,
    starter_cards: int,
    critical_singletons: int,
    setup_target_copies: int,
    rescue_supporters: int,
    disposable_nonstarters: int,
    discard_cost: int,
    opening_hand_size: int = 7,
    turns: int = 1,
) -> CompetingConnectorResult:
    """Return exact joint success for setup plus Prize rescue by a horizon.

    The model contains one universal connector. Target A is an abstract setup
    resource that is considered secured as soon as one copy reaches hand.
    Target B is a Gladion-like rescue Supporter. One rescue Supporter can be
    played per modeled turn and resolves one modeled critical Prize.

    Reported conditional values condition on at least one critical singleton
    being initially Prized.
    """

    if deck_size <= 0:
        raise ValueError("deck_size must be positive")
    if not 0 <= prize_count <= deck_size:
        raise ValueError("prize_count must be between 0 and deck_size")
    if opening_hand_size < 0 or opening_hand_size + prize_count > deck_size:
        raise ValueError("opening hand and Prize cards must fit in the deck")
    if not 0 < starter_cards <= deck_size:
        raise ValueError("starter_cards must be positive and fit in the deck")
    if min(
        critical_singletons,
        setup_target_copies,
        rescue_supporters,
        disposable_nonstarters,
        discard_cost,
        turns,
    ) < 0:
        raise ValueError("counts, cost, and horizon must be non-negative")
    if critical_singletons == 0:
        raise ValueError("critical_singletons must be positive")
    if setup_target_copies == 0:
        raise ValueError("setup_target_copies must be positive")
    if rescue_supporters == 0:
        raise ValueError("rescue_supporters must be positive")

    connector_copies = 1
    nonstarter_specials = (
        critical_singletons
        + setup_target_copies
        + rescue_supporters
        + connector_copies
        + disposable_nonstarters
    )
    nonstarter_capacity = deck_size - starter_cards
    if nonstarter_specials > nonstarter_capacity:
        raise ValueError("non-starter categories exceed non-starter capacity")

    protected_nonstarters = nonstarter_capacity - nonstarter_specials
    sizes = (
        critical_singletons,
        setup_target_copies,
        rescue_supporters,
        connector_copies,
        disposable_nonstarters,
        starter_cards,
        protected_nonstarters,
    )

    accepted = accepted_opening_probability(
        deck_size, starter_cards, opening_hand_size
    )
    if accepted == 0.0:
        raise ValueError("conditioning event has zero probability")

    _optimal_success_from_state.cache_clear()
    _priority_success_from_state.cache_clear()

    total_mass = 0.0
    any_critical = 0.0
    optimal_success = 0.0
    setup_priority_success = 0.0
    rescue_priority_success = 0.0
    no_connector_success = 0.0

    for hand in _bounded_compositions(opening_hand_size, sizes):
        if hand[5] == 0:
            continue

        hand_mass = (
            _multivariate_probability(hand, sizes, opening_hand_size) / accepted
        )
        after_hand = tuple(size - count for size, count in zip(sizes, hand))

        for prizes in _bounded_compositions(prize_count, after_hand):
            prize_mass = _multivariate_probability(
                prizes, after_hand, prize_count
            )
            state_mass = hand_mass * prize_mass
            total_mass += state_mass

            critical_prized = prizes[0]
            if critical_prized == 0:
                continue
            any_critical += state_mass

            post_prize = tuple(
                count - prized for count, prized in zip(after_hand, prizes)
            )
            setup_secured = hand[1] > 0
            rescue_in_hand = hand[2]
            connector_in_hand = hand[3]
            disposable_in_hand = hand[4]
            setup_in_deck = post_prize[1]
            rescue_in_deck = post_prize[2]
            connector_in_deck = post_prize[3]
            disposable_in_deck = post_prize[4]
            post_prize_deck_size = deck_size - opening_hand_size - prize_count
            other_in_deck = (
                post_prize_deck_size
                - setup_in_deck
                - rescue_in_deck
                - connector_in_deck
                - disposable_in_deck
            )

            state = (
                turns,
                critical_prized,
                setup_secured,
                rescue_in_hand,
                connector_in_hand,
                disposable_in_hand,
                setup_in_deck,
                rescue_in_deck,
                connector_in_deck,
                disposable_in_deck,
                other_in_deck,
                discard_cost,
            )

            optimal_success += state_mass * _optimal_success_from_state(*state)
            setup_priority_success += state_mass * _priority_success_from_state(
                "setup_priority", *state
            )
            rescue_priority_success += state_mass * _priority_success_from_state(
                "rescue_priority", *state
            )
            no_connector_success += state_mass * _priority_success_from_state(
                "never_connector", *state
            )

    if any_critical == 0.0:
        raise ValueError("conditioning event has zero probability")

    return CompetingConnectorResult(
        state_mass=total_mass,
        any_critical_prized=any_critical,
        optimal_success_probability=optimal_success,
        conditional_optimal_success=optimal_success / any_critical,
        setup_priority_success_probability=setup_priority_success,
        conditional_setup_priority_success=setup_priority_success / any_critical,
        rescue_priority_success_probability=rescue_priority_success,
        conditional_rescue_priority_success=rescue_priority_success / any_critical,
        no_connector_success_probability=no_connector_success,
        conditional_no_connector_success=no_connector_success / any_critical,
    )


def competing_action_values(
    *,
    turns_remaining: int,
    critical_remaining: int,
    setup_secured: bool,
    rescue_in_hand: int,
    connector_in_hand: int,
    disposable_in_hand: int,
    setup_in_deck: int,
    rescue_in_deck: int,
    connector_in_deck: int,
    disposable_in_deck: int,
    other_in_deck: int,
    discard_cost: int,
) -> dict[str, float]:
    """Return exact action values for a state after the current natural draw.

    Each value is the probability of completing setup plus all modeled Prize
    rescues by the horizon when the named action is taken now and future turns
    are optimized.

    The state is evaluated after the current turn's natural draw. Therefore,
    every returned action transitions directly to the next modeled turn.
    """

    if turns_remaining <= 0:
        raise ValueError("turns_remaining must be positive")
    if min(
        critical_remaining,
        rescue_in_hand,
        connector_in_hand,
        disposable_in_hand,
        setup_in_deck,
        rescue_in_deck,
        connector_in_deck,
        disposable_in_deck,
        other_in_deck,
        discard_cost,
    ) < 0:
        raise ValueError("state counts and discard_cost must be non-negative")
    if connector_in_hand + connector_in_deck > 1:
        raise ValueError("the model contains at most one universal connector")

    next_turns = turns_remaining - 1
    values: dict[str, float] = {
        "wait": _optimal_success_from_state(
            next_turns,
            critical_remaining,
            setup_secured,
            rescue_in_hand,
            connector_in_hand,
            disposable_in_hand,
            setup_in_deck,
            rescue_in_deck,
            connector_in_deck,
            disposable_in_deck,
            other_in_deck,
            discard_cost,
        )
    }

    if critical_remaining > 0 and rescue_in_hand > 0:
        values["play_rescue"] = _optimal_success_from_state(
            next_turns,
            critical_remaining - 1,
            setup_secured,
            rescue_in_hand - 1,
            connector_in_hand,
            disposable_in_hand,
            setup_in_deck,
            rescue_in_deck,
            connector_in_deck,
            disposable_in_deck,
            other_in_deck,
            discard_cost,
        )

    connector_payable = (
        connector_in_hand > 0 and disposable_in_hand >= discard_cost
    )
    if connector_payable:
        if not setup_secured and setup_in_deck > 0:
            values["search_setup"] = _optimal_success_from_state(
                next_turns,
                critical_remaining,
                True,
                rescue_in_hand,
                connector_in_hand - 1,
                disposable_in_hand - discard_cost,
                setup_in_deck - 1,
                rescue_in_deck,
                connector_in_deck,
                disposable_in_deck,
                other_in_deck,
                discard_cost,
            )
            if critical_remaining > 0 and rescue_in_hand > 0:
                values["search_setup_play_rescue"] = (
                    _optimal_success_from_state(
                        next_turns,
                        critical_remaining - 1,
                        True,
                        rescue_in_hand - 1,
                        connector_in_hand - 1,
                        disposable_in_hand - discard_cost,
                        setup_in_deck - 1,
                        rescue_in_deck,
                        connector_in_deck,
                        disposable_in_deck,
                        other_in_deck,
                        discard_cost,
                    )
                )

        if critical_remaining > 0 and rescue_in_deck > 0:
            values["search_rescue_hold"] = _optimal_success_from_state(
                next_turns,
                critical_remaining,
                setup_secured,
                rescue_in_hand + 1,
                connector_in_hand - 1,
                disposable_in_hand - discard_cost,
                setup_in_deck,
                rescue_in_deck - 1,
                connector_in_deck,
                disposable_in_deck,
                other_in_deck,
                discard_cost,
            )
            values["search_rescue_play"] = _optimal_success_from_state(
                next_turns,
                critical_remaining - 1,
                setup_secured,
                rescue_in_hand,
                connector_in_hand - 1,
                disposable_in_hand - discard_cost,
                setup_in_deck,
                rescue_in_deck - 1,
                connector_in_deck,
                disposable_in_deck,
                other_in_deck,
                discard_cost,
            )

    return values
