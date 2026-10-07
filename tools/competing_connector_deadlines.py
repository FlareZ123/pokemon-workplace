"""Exact competing connector policy with separate setup and rescue deadlines."""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from math import comb
from typing import Iterator


_MODES = ("none", "rescue", "setup", "flex")


@dataclass(frozen=True)
class CompetingDeadlineResult:
    state_mass: float
    any_critical_prized: float
    conditional_no_connector_success: float
    conditional_rescue_only_success: float
    conditional_setup_only_success: float
    conditional_flexible_success: float
    conditional_flexibility_gain: float


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


def _accepted_opening_probability(
    deck_size: int, starter_cards: int, opening_hand_size: int
) -> float:
    return 1.0 - _choose(deck_size - starter_cards, opening_hand_size) / _choose(
        deck_size, opening_hand_size
    )


@lru_cache(maxsize=None)
def _success_from_state(
    turns_remaining: int,
    setup_turns_remaining: int,
    critical_remaining: int,
    setup_acquired: bool,
    rescue_in_hand: int,
    connector_in_hand: int,
    disposable_in_hand: int,
    rescue_in_deck: int,
    setup_in_deck: int,
    connector_in_deck: int,
    disposable_in_deck: int,
    other_in_deck: int,
    discard_cost: int,
    mode: str,
) -> float:
    if not setup_acquired and setup_turns_remaining == 0:
        return 0.0
    if critical_remaining == 0 and setup_acquired:
        return 1.0
    if turns_remaining == 0:
        return 0.0

    deck_size = (
        rescue_in_deck
        + setup_in_deck
        + connector_in_deck
        + disposable_in_deck
        + other_in_deck
    )
    if deck_size == 0:
        return 0.0

    draw_counts = (
        rescue_in_deck,
        setup_in_deck,
        connector_in_deck,
        disposable_in_deck,
        other_in_deck,
    )
    probability = 0.0

    for category, count in enumerate(draw_counts):
        if count == 0:
            continue

        hand_rescue = rescue_in_hand
        hand_connector = connector_in_hand
        hand_disposable = disposable_in_hand
        deck_rescue = rescue_in_deck
        deck_setup = setup_in_deck
        deck_connector = connector_in_deck
        deck_disposable = disposable_in_deck
        deck_other = other_in_deck
        acquired = setup_acquired

        if category == 0:
            hand_rescue += 1
            deck_rescue -= 1
        elif category == 1:
            acquired = True
            deck_setup -= 1
        elif category == 2:
            hand_connector += 1
            deck_connector -= 1
        elif category == 3:
            hand_disposable += 1
            deck_disposable -= 1
        else:
            deck_other -= 1

        actions = [
            (
                critical_remaining,
                acquired,
                hand_rescue,
                hand_connector,
                hand_disposable,
                deck_rescue,
                deck_setup,
                deck_connector,
                deck_disposable,
                deck_other,
            )
        ]

        if critical_remaining > 0 and hand_rescue > 0:
            actions.append(
                (
                    critical_remainining - 1,
                    acquired,
                    hand_rescue - 1,
                    hand_connector,
                    hand_disposable,
                    deck_rescue,
                    deck_setup,
                    deck_connector,
                    deck_disposable,
                    deck_other,
                )
            )

        payable = hand_connector > 0 and hand_disposable >= discard_cost

        if (
            payable
            and mode in {"rescue", "flex"}
            and critical_remaining > 0
            and deck_rescue > 0
        ):
            actions.append(
                (
                    critical_remaining,
                    acquired,
                    hand_rescue + 1,
                    hand_connector - 1,
                    hand_disposable - discard_cost,
                    deck_rescue - 1,
                    deck_setup,
                    deck_connector,
                    deck_disposable,
                    deck_other,
                )
            )
            actions.append(
                (
                    critical_remaining - 1,
                    acquired,
                    hand_rescue,
                    hand_connector - 1,
                    hand_disposable - discard_cost,
                    deck_rescue - 1,
                    deck_setup,
                    deck_connector,
                    deck_disposable,
                    deck_other,
               )
            )

        if (
            payable
            and mode in {"setup", "flex"}
            and not acquired
            and deck_setup > 0
        ):
            actions.append(
                (
                    critical_remaining,
                    True,
                    hand_rescue,
                    hand_connector - 1,
                    hand_disposable - discard_cost,
                    deck_rescue,
                    deck_setup - 1,
                    deck_connector,
                    deck_disposable,
                    deck_other,
                )
            )
            if critical_remaining > 0 and hand_rescue > 0:
                actions.append(
                    (
                        critical_remainining - 1,
                        True,
                        hand_rescue - 1,
                        hand_connector - 1,
                        hand_disposable - discard_cost,
                        deck_rescue,
                        deck_setup - 1,
                        deck_connector,
                        deck_disposable,
                        deck_other,
                    )
                )

        next_setup_turns = max(0, setup_turns_remaining - 1)
        best = max(
            _success_from_state(
                turns_remaining - 1,
                next_setup_turns,
                *action,
                discard_cost,
                mode,
            )
            for action in actions
        )
        probability += (count / deck_size) * best

    return probability


def competing_connector_deadline_success(
    deck_size: int,
    prize_count: int,
    *,
    starter_cards: int,
    critical_nonstarter: int,
    rescue_supporters: int,
    setup_targets: int,
    disposable_nonstarters: int,
    discard_cost: int,
    opening_hand_size: int = 7,
    rescue_turns: int = 4,
    setup_deadline: int = 2,
) -> CompetingDeadlineResult:
    """Return exact joint success with separate setup and rescue deadlines."""
    if deck_size <= 0:
        raise ValueError("deck_size must be positive")
    if not 0 <= prize_count <= deck_size:
        raise ValueError("prize_count must fit in the deck")
    if opening_hand_size < 0 or opening_hand_size + prize_count > deck_size:
        raise ValueError("opening hand and Prize cards must fit in the deck")
    if not 0 < starter_cards <= deck_size:
        raise ValueError("starter_cards must be positive and fit in the deck")
    if min(
        critical_nonstarter,
        rescue_supporters,
        setup_targets,
        disposable_nonstarters,
        discard_cost,
        rescue_turns,
        setup_deadline,
    ) < 0:
        raise ValueError("counts, costs, and deadlines must be non-negative")
    if rescue_turns == 0:
        raise ValueError("rescue_turns must be positive")
    if not 1 <= setup_deadline <= rescue_turns:
        raise ValueError("setup_deadline must be between 1 and rescue_turns")
    if rescue_supporters == 0 or setup_targets == 0:
        raise ValueError("both target channels need at least one copy")

    connector_copies = 1
    used_nonstarters = (
        critical_nonstarter
        + rescue_supporters
        + setup_targets
        + connector_copies
        + disposable_nonstarters
    )
    if used_nonstarters > deck_size - starter_cards:
        raise ValueError("non-starter categories exceed non-starter capacity")

    protected_nonstarters = deck_size - starter_cards - used_nonstarters
    sizes = (
        critical_nonstarter,
        rescue_supporters,
        setup_targets,
        connector_copies,
        disposable_nonstarters,
        starter_cards,
        protected_nonstarters,
    )
    accepted = _accepted_opening_probability(
        deck_size, starter_cards, opening_hand_size
    )
    if accepted == 0.0:
        raise ValueError("conditioning event has zero probability")

    _success_from_state.cache_clear()
    total_mass = 0.0
    any_critical = 0.0
    success_mass = {mode: 0.0 for mode in _MODES}

    for hand in _bounded_compositions(opening_hand_size, sizes):
        if hand[5] == 0:
            continue
        hand_mass = _multivariate_probability(hand, sizes, opening_hand_size) / accepted
        after_hand = tuple(size - count for size, count in zip(sizes, hand))

        for prizes in _bounded_compositions(prize_count, after_hand):
            prize_mass = _multivariate_probability(prizes, after_hand, prize_count)
            state_mass = hand_mass * prize_mass
            total_mass += state_mass

            critical_prized = prizes[0]
            if critical_prized == 0:
                continue
            any_critical += state_mass

            setup_acquired = hand[2] > 0
            rescue_in_deck = after_hand[1] - prizes[1]
            setup_in_deck = after_hand[2] - prizes[2]
            connector_in_deck = after_hand[3] - prizes[3]
            disposable_in_deck = after_hand[4] - prizes[4]
            post_prize_deck_size = deck_size - opening_hand_size - prize_count
            other_in_deck = (
                post_prize_deck_size
                - rescue_in_deck
                - setup_in_deck
                - connector_in_deck
                - disposable_in_deck
            )

            for mode in _MODES:
                success_mass[mode] += state_mass * _success_from_state(
                    rescue_turns,
                    setup_deadline,
                    critical_prized,
                    setup_acquired,
                    hand[1],
                    hand[3],
                    hand[4],
                    rescue_in_deck,
                    setup_in_deck,
                    connector_in_deck,
                    disposable_in_deck,
                    other_in_deck,
                    discard_cost,
                    mode,
                )

    conditional = {mode: success_mass[mode] / any_critical for mode in _MODES}
    best_single = max(conditional["rescue"], conditional["setup"])
    return CompetingDeadlineResult(
        state_mass=total_mass,
        any_critical_prized=any_critical,
        conditional_no_connector_success=conditional["none"],
        conditional_rescue_only_success=conditional["rescue"],
        conditional_setup_only_success=conditional["setup"],
        conditional_flexible_success=conditional["flex"],
        conditional_flexibility_gain=conditional["flex"] - best_single,
    )
