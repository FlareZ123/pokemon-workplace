"""Exact direct-ready Forest Seal Stone access in Harto Miki's Aichi Raichu list.

This extends the corrected Raichu direct-access component by splitting the
setup-starter class so the real Forest Seal Stone gate can be represented:

* Forest Seal Stone must be exposed in hand;
* a Crobat V must already be exposed and therefore playable/in play;
* the VSTAR Power is assumed unused;
* the chosen Crobat V is assumed to have an open Tool slot;
* Bench capacity and Ability/Tool locks are outside this layer.

The model deliberately does not let Ultra Ball, Computer Search, Quick Ball, or
Gladion fetch a missing Forest Seal Stone gate piece. It isolates the direct-ready
zero-discard connector layer before adding those multi-action routes.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache

from raichu_prize_access import (
    _bounded_compositions,
    _multivariate_probability,
    accepted_opening_probability,
)


@dataclass(frozen=True)
class ForestSealAccessResult:
    """Exact probabilities for the direct-ready Forest Seal Stone layer."""

    state_mass: float
    valid_opening_probability: float
    target_prized_probability: float
    target_in_exposed_hand_probability: float
    connector_payable_probability: float
    baseline_access: float
    forest_seal_exposed_probability: float
    crobat_available_probability: float
    forest_seal_ready_probability: float
    ungated_forest_seal_access: float
    typed_forest_seal_access: float
    target_prized_baseline_access: float
    target_prized_ungated_access: float
    target_prized_typed_access: float

    @property
    def typed_gain_over_baseline(self) -> float:
        return self.typed_forest_seal_access - self.baseline_access

    @property
    def ungated_gain_over_baseline(self) -> float:
        return self.ungated_forest_seal_access - self.baseline_access

    @property
    def gate_overstatement(self) -> float:
        return self.ungated_forest_seal_access - self.typed_forest_seal_access

    @property
    def conditional_target_prized_baseline_access(self) -> float:
        if self.target_prized_probability == 0:
            return 1.0
        return self.target_prized_baseline_access / self.target_prized_probability

    @property
    def conditional_target_prized_ungated_access(self) -> float:
        if self.target_prized_probability == 0:
            return 1.0
        return self.target_prized_ungated_access / self.target_prized_probability

    @property
    def conditional_target_prized_typed_access(self) -> float:
        if self.target_prized_probability == 0:
            return 1.0
        return self.target_prized_typed_access / self.target_prized_probability


def _snapshot_flags(
    hand: tuple[int, ...],
    prizes: tuple[int, ...],
    deck: tuple[int, ...],
    crobat_in_play: bool,
    discard_cost: int,
) -> tuple[bool, bool, bool, bool, bool, bool, bool, bool]:
    """Return access flags for one exposed state.

    Category order is:
    target, Gladion, Ultra Ball, Computer Search, Forest Seal Stone, Crobat V,
    disposable non-starter, disposable starter, other starter, protected other.
    """
    target_in_hand = hand[0] > 0
    target_prized = prizes[0] > 0
    target_in_deck = deck[0] > 0
    gladion_in_hand = hand[1] > 0
    gladion_in_deck = deck[1] > 0
    ultra_in_hand = hand[2] > 0
    computer_in_hand = hand[3] > 0
    forest_seal_exposed = hand[4] > 0
    crobat_available = crobat_in_play or hand[5] > 0
    connector_payable = hand[6] + hand[7] >= discard_cost

    baseline_access = target_in_hand or (
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

    forest_seal_ready = forest_seal_exposed and crobat_available
    seal_output_works = target_in_deck or (target_prized and gladion_in_deck)

    ungated_forest_seal_access = baseline_access or (
        forest_seal_exposed and seal_output_works
    )
    typed_forest_seal_access = baseline_access or (
        forest_seal_ready and seal_output_works
    )

    return (
        target_in_hand,
        connector_payable,
        baseline_access,
        forest_seal_exposed,
        crobat_available,
        forest_seal_ready,
        ungated_forest_seal_access,
        typed_forest_seal_access,
    )


def forest_seal_access_snapshot(
    *,
    deck_size: int = 60,
    prize_count: int = 6,
    opening_hand_size: int = 7,
    extra_random_draws: int = 1,
    gladion_copies: int = 2,
    ultra_ball_copies: int = 3,
    computer_search_copies: int = 1,
    forest_seal_copies: int = 1,
    crobat_v_copies: int = 2,
    disposable_nonstarter_copies: int = 11,
    disposable_starter_copies: int = 1,
    other_starter_copies: int = 13,
    discard_cost: int = 2,
) -> ForestSealAccessResult:
    """Return exact direct-ready Forest Seal Stone access probabilities."""

    counts = (
        gladion_copies,
        ultra_ball_copies,
        computer_search_copies,
        forest_seal_copies,
        crobat_v_copies,
        disposable_nonstarter_copies,
        disposable_starter_copies,
        other_starter_copies,
        discard_cost,
    )
    if deck_size <= 0:
        raise ValueError("deck_size must be positive")
    if opening_hand_size < 0 or prize_count < 0 or extra_random_draws < 0:
        raise ValueError("hand, Prize, and draw counts must be non-negative")
    if opening_hand_size + prize_count + extra_random_draws > deck_size:
        raise ValueError("requested zones exceed deck size")
    if min(counts) < 0:
        raise ValueError("card counts and discard_cost must be non-negative")
    if computer_search_copies > 1:
        raise ValueError("this model supports at most one Computer Search ACE SPEC")

    target_copies = 1
    starter_cards = (
        crobat_v_copies + disposable_starter_copies + other_starter_copies
    )
    if starter_cards <= 0:
        raise ValueError("at least one setup-eligible starter is required")

    used = (
        target_copies
        + gladion_copies
        + ultra_ball_copies
        + computer_search_copies
        + forest_seal_copies
        + crobat_v_copies
        + disposable_nonstarter_copies
        + disposable_starter_copies
        + other_starter_copies
    )
    if used > deck_size:
        raise ValueError("modeled categories exceed deck size")

    protected_other = deck_size - used
    sizes = (
        target_copies,
        gladion_copies,
        ultra_ball_copies,
        computer_search_copies,
        forest_seal_copies,
        crobat_v_copies,
        disposable_nonstarter_copies,
        disposable_starter_copies,
        other_starter_copies,
        protected_other,
    )

    accepted = accepted_opening_probability(
        deck_size, starter_cards, opening_hand_size
    )
    if accepted == 0.0:
        raise ValueError("valid-opening conditioning event has zero probability")

    state_mass = 0.0
    target_prized_probability = 0.0
    target_in_exposed_hand_probability = 0.0
    connector_payable_probability = 0.0
    baseline_access = 0.0
    forest_seal_exposed_probability = 0.0
    crobat_available_probability = 0.0
    forest_seal_ready_probability = 0.0
    ungated_forest_seal_access = 0.0
    typed_forest_seal_access = 0.0
    target_prized_baseline_access = 0.0
    target_prized_ungated_access = 0.0
    target_prized_typed_access = 0.0

    for opening in _bounded_compositions(opening_hand_size, sizes):
        if opening[5] + opening[7] + opening[8] == 0:
            continue

        opening_mass = _multivariate_probability(opening, sizes) / accepted
        after_opening = tuple(size - count for size, count in zip(sizes, opening))

        # Materialize the mandatory Active Pokemon. Prefer Crobat V when exposed,
        # otherwise a protected starter, preserving Giratina as discard fodder
        # whenever the opening permits that choice.
        action_opening = list(opening)
        crobat_in_play = False
        if opening[5] > 0:
            action_opening[5] -= 1
            crobat_in_play = True
        elif opening[8] > 0:
            action_opening[8] -= 1
        else:
            action_opening[7] -= 1
        action_opening = tuple(action_opening)

        for prizes in _bounded_compositions(prize_count, after_opening):
            prize_mass = _multivariate_probability(prizes, after_opening)
            base_mass = opening_mass * prize_mass
            post_prize = tuple(
                count - prized for count, prized in zip(after_opening, prizes)
            )
            target_prized = prizes[0] > 0

            @lru_cache(maxsize=None)
            def expose(
                hand: tuple[int, ...],
                deck: tuple[int, ...],
                draws_remaining: int,
            ) -> tuple[float, ...]:
                if draws_remaining == 0:
                    return tuple(
                        float(flag)
                        for flag in _snapshot_flags(
                            hand,
                            prizes,
                            deck,
                            crobat_in_play,
                            discard_cost,
                        )
                    )

                total = sum(deck)
                accum = [0.0] * 8
                for category, count in enumerate(deck):
                    if count == 0:
                        continue
                    next_hand = list(hand)
                    next_deck = list(deck)
                    next_hand[category] += 1
                    next_deck[category] -= 1
                    branch = expose(
                        tuple(next_hand),
                        tuple(next_deck),
                        draws_remaining - 1,
                    )
                    weight = count / total
                    for index, value in enumerate(branch):
                        accum[index] += weight * value
                return tuple(accum)

            values = expose(action_opening, post_prize, extra_random_draws)

            state_mass += base_mass
            target_prized_probability += base_mass * target_prized
            target_in_exposed_hand_probability += base_mass * values[0]
            connector_payable_probability += base_mass * values[1]
            baseline_access += base_mass * values[2]
            forest_seal_exposed_probability += base_mass * values[3]
            crobat_available_probability += base_mass * values[4]
            forest_seal_ready_probability += base_mass * values[5]
            ungated_forest_seal_access += base_mass * values[6]
            typed_forest_seal_access += base_mass * values[7]

            if target_prized:
                target_prized_baseline_access += base_mass * values[2]
                target_prized_ungated_access += base_mass * values[6]
                target_prized_typed_access += base_mass * values[7]

    return ForestSealAccessResult(
        state_mass=state_mass,
        valid_opening_probability=accepted,
        target_prized_probability=target_prized_probability,
        target_in_exposed_hand_probability=target_in_exposed_hand_probability,
        connector_payable_probability=connector_payable_probability,
        baseline_access=baseline_access,
        forest_seal_exposed_probability=forest_seal_exposed_probability,
        crobat_available_probability=crobat_available_probability,
        forest_seal_ready_probability=forest_seal_ready_probability,
        ungated_forest_seal_access=ungated_forest_seal_access,
        typed_forest_seal_access=typed_forest_seal_access,
        target_prized_baseline_access=target_prized_baseline_access,
        target_prized_ungated_access=target_prized_ungated_access,
        target_prized_typed_access=target_prized_typed_access,
    )
