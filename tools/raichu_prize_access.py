"""Exact zone-aware access to singleton Alolan Raichu in Harto Miki's Aichi list.

This component model conditions on a valid starter-containing opening hand, sets
Prize cards from the remaining deck, exposes a configurable number of later random
cards, then asks whether the singleton Alolan Raichu can be put into hand in one
action window using a deliberately narrow direct package:

* Alolan Raichu itself;
* Gladion;
* Ultra Ball;
* Computer Search;
* a caller-defined pool of cards acceptable to discard to the two-card costs.

Computer Search is treated as an adaptive any-card search. If Alolan Raichu is in
the deck it can take Raichu directly. If Raichu is Prized, inspecting the deck
reveals that fact and Computer Search can instead take a Gladion that remains in
the deck, after which Gladion can be played in the same Supporter-legal window.

The model intentionally excludes indirect draw/search routes such as Forest Seal
Stone, Dedenne-GX, Crobat V, Squawkabilly ex, Quick Ball chains, and ordinary
multi-action setup. It is a component analysis, not a full deck consistency model.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from math import comb
from typing import Iterator


@dataclass(frozen=True)
class RaichuAccessResult:
    """Exact probabilities for the modeled access snapshot."""

    state_mass: float
    valid_opening_probability: float
    target_prized_probability: float
    target_in_exposed_hand_probability: float
    connector_payable_probability: float
    ultra_plus_gladion_gated_access: float
    static_computer_gated_access: float
    adaptive_computer_gated_access: float
    adaptive_computer_no_cost_access: float
    target_prized_static_access: float
    target_prized_adaptive_access: float

    @property
    def adaptive_gain_over_static(self) -> float:
        return self.adaptive_computer_gated_access - self.static_computer_gated_access

    @property
    def total_computer_gain(self) -> float:
        return self.adaptive_computer_gated_access - self.ultra_plus_gladion_gated_access

    @property
    def discard_gate_loss(self) -> float:
        return self.adaptive_computer_no_cost_access - self.adaptive_computer_gated_access

    @property
    def conditional_target_prized_static_access(self) -> float:
        if self.target_prized_probability == 0:
            return 1.0
        return self.target_prized_static_access / self.target_prized_probability

    @property
    def conditional_target_prized_adaptive_access(self) -> float:
        if self.target_prized_probability == 0:
            return 1.0
        return self.target_prized_adaptive_access / self.target_prized_probability


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


def _multivariate_probability(counts: tuple[int, ...], sizes: tuple[int, ...]) -> float:
    sample_size = sum(counts)
    numerator = 1
    for size, count in zip(sizes, counts):
        numerator *= _choose(size, count)
    return numerator / _choose(sum(sizes), sample_size)


def accepted_opening_probability(deck_size: int, starter_cards: int, opening_hand_size: int) -> float:
    """P(the opening hand contains at least one setup-eligible starter)."""
    if deck_size <= 0:
        raise ValueError("deck_size must be positive")
    if not 0 <= starter_cards <= deck_size:
        raise ValueError("starter_cards must fit in the deck")
    if not 0 <= opening_hand_size <= deck_size:
        raise ValueError("opening_hand_size must fit in the deck")
    return 1.0 - _choose(deck_size - starter_cards, opening_hand_size) / _choose(
        deck_size, opening_hand_size
    )


def _snapshot_flags(
    hand: tuple[int, ...],
    prizes: tuple[int, ...],
    deck: tuple[int, ...],
    discard_cost: int,
) -> tuple[bool, bool, bool, bool, bool, bool]:
    """Return success flags for one fully exposed category state.

    Category order is target, Gladion, Ultra Ball, Computer Search, disposable,
    setup starter, protected other.
    """
    target_in_hand = hand[0] > 0
    target_prized = prizes[0] > 0
    target_in_deck = deck[0] > 0
    gladion_in_hand = hand[1] > 0
    gladion_in_deck = deck[1] > 0
    ultra_in_hand = hand[2] > 0
    computer_in_hand = hand[3] > 0
    connector_payable = hand[4] >= discard_cost

    # Computer Search is deliberately disabled here. This is the Harto direct
    # package after removing the ACE SPEC: Ultra Ball can take Raichu from the
    # deck, while a Gladion already in hand can take it from the Prizes.
    ultra_plus_gladion = target_in_hand or (
        target_in_deck and connector_payable and ultra_in_hand
    ) or (target_prized and gladion_in_hand)

    # Static Computer Search treats the ACE SPEC as just another direct target
    # search. This captures its extra connector copy while suppressing the
    # any-card fallback to Gladion when Raichu is absent from the deck.
    static_computer = target_in_hand or (
        target_in_deck
        and connector_payable
        and (ultra_in_hand or computer_in_hand)
    ) or (target_prized and gladion_in_hand)

    # The executable zone-adaptive route. If Raichu is Prized and no Gladion is
    # already in hand, Computer Search can inspect the deck, infer the Prize
    # state from Raichu's absence, take a remaining Gladion, and leave the normamª    # Supporter play available for that Gladion.
    adaptive_computer = target_in_hand or (
        target_in_deck
        and connector_payable
        and (ultra_in_hand or computer_in_hand)
    ) or (
        target_prized
        and (
            gladion_in_hand
            or (
                connector_payable
                and computer_in_hand
                and gladion_in_deck
            )
        )
    )

    adaptive_no_cost = target_in_hand or (
        target_in_deck and (ultra_in_hand or computer_in_hand)
    ) or (
        target_prized
        and (
            gladion_in_hand
            or (computer_in_hand and gladion_in_deck)
        )
    )

    return (
        target_in_hand,
        connector_payable,
        ultra_plus_gladion,
        static_computer,
        adaptive_computer,
        adaptive_no_cost,
    )


def raichu_access_snapshot(
    *,
    deck_size: int = 60,
    prize_count: int = 6,
    opening_hand_size: int = 7,
    extra_random_draws: int = 1,
    starter_cards: int = 16,
    gladion_copies: int = 2,
    ultra_ball_copies: int = 3,
    computer_search_copies: int = 1,
    disposable_cards: int = 12,
    discard_cost: int = 2,
) -> RaichuAccessResult:
    """Return exact direct access probabilities for the singleton target.

    The modeled target count is exactly one, matching Harto Miki's published
    Alolan Raichu count. ``disposable_cards`` is a policy input, not an immutable
    card property. In the preserved baseline it is 12: the 11 Special Energy plus
    Giratina, whose discard-pile Ability makes it a natural discard candidate.
    """
    if deck_size <= 0:
        raise ValueEError("deck_size must be positive")
    if opening_hand_size < 0 or prize_count < 0 or extra_random_draws < 0:
        raise ValueError("hand, Prize, and draw counts must be non-negative")
    if opening_hand_size + prize_count + extra_random_draws > deck_size:
        raise ValueEError("requested zones exceed deck size")
    if not 0 < starter_cards <= deck_size:
        raise ValueEError("starter_cards must be positive and fit in the deck")
    if min(gladion_copies, ultra_ball_copies, computer_search_copies, disposable_cards, discard_cost) < 0:
        raise ValueError("card counts and discard_cost must be non-negative")
    if computer_search_copies > 1:
        raise ValueEError("this model supports at most one Computer Search ACE SPEC")

    target_copies = 1
    used = (
        target_copies
        + gladion_copies
        + ultra_ball_copies
        + computer_search_copies
        + disposable_cards
        + starter_cards
    )
    if used > deck_size:
        raise ValueEError("modeled categories exceed deck size")
    protected_other = deck_size - used
    sizes = (
        target_copies,
        gladion_copies,
        ultra_ball_copies,
        computer_search_copies,
        disposable_cards,
        starter_cards,
        protected_other,
    )

    accepted = accepted_opening_probability(deck_size, starter_cards, opening_hand_size)
    if accepted == 0.0:
        raise ValueError("valid-opening conditioning event has zero probability")

    state_mass = 0.0
    target_prized_probability = 0.0
    target_in_exposed_hand_probability = 0.0
    connector_payable_probability = 0.0
    ultra_plus_gladion_gated_access = 0.0
    static_computer_gated_access = 0.0
    adaptive_computer_gated_access = 0.0
    adaptive_computer_no_cost_access = 0.0
    target_prized_static_access = 0.0
    target_prized_adaptive_access = 0.0

    for opening in _bounded_compositions(opening_hand_size, sizes):
        if opening[5] == 0:
            continue
        opening_mass = _multivariate_probability(opening, sizes) / accepted
        after_opening = tuple(size - count for size, count in zip(sizes, opening))

        for prizes in _bounded_compositions(prize_count, after_opening):
            prize_mass = _multivariate_probability(prizes, after_opening)
            base_mass = opening_mass * prize_mass
            post_prize = tuple(count - prized for count, prized in zip(after_opening, prizes))
            target_prized = prizes[0] > 0

            @lru_cache(maxsize=None)
            def expose(
                hand: tuple[int, ...], deck: tuple[int, ...], draws_remaining: int
            ) -> tuple[float, float, float, float, float, float]:
                if draws_remaining == 0:
                    flags = _snapshot_flags(hand, prizes, deck, discard_cost)
                    return tuple(float(flag) for flag in flags)

                total = sum(deck)
                accum = [0.0] * 6
                for category, count in enumerate(deck):
                    if count == 0:
                        continue
                    next_hand = list(hand)
                    next_deck = list(deck)
                    next_hand[category] += 1
                    next_deck[category] -= 1
                    branch = expose(tuple(next_hand), tuple(next_deck), draws_remaining - 1)
                    weight = count / total
                    for index, value in enumerate(branch):
                        accum[index] += weight * value
                return tuple(accum)

            values = expose(opening, post_prize, extra_random_draws)
            state_mass += base_mass
            target_prized_probability += base_mass * target_prized
            target_in_exposed_hand_probability += base_mass * values[0]
            connector_payable_probability += base_mass * values[1]
            ultra_plus_gladion_gated_access += base_mass * values[2]
            static_computer_gated_access += base_mass * values[3]
            adaptive_computer_gated_access += base_mass * values[4]
            adaptive_computer_no_cost_access += base_mass * values[5]
            if target_prized:
                target_prized_static_access += base_mass * values[3]
                target_prized_adaptive_access += base_mass * values[4]

    return RaichuAccessResult(
        state_mass=state_mass,
        valid_opening_probability=accepted,
        target_prized_probability=target_prized_probability,
        target_in_exposed_hand_probability=target_in_exposed_hand_probability,
        connector_payable_probability=connector_payable_probability,
        ultra_plus_gladion_gated_access=ultra_plus_gladion_gated_access,
        static_computer_gated_access=static_computer_gated_access,
        adaptive_computer_gated_access=adaptive_computer_gated_access,
        adaptive_computer_no_cost_access=adaptive_computer_no_cost_access,
        target_prized_static_access=target_prized_static_access,
        target_prized_adaptive_access=target_prized_adaptive_access,
    )
