"""Exact search-to-gate sequencing for Forest Seal Stone in Harto Miki's Raichu list.

The model extends the direct-ready Forest Seal Stone layer with Harto's two
Quick Ball and the existing Ultra Ball package. It asks whether a Pokemon-search
Item can materialize Crobat V after setup so Forest Seal Stone becomes usable.

The important sequencing distinction is:

* Quick Ball cannot search for Stage 1 Alolan Raichu, so when Forest Seal Stone
  is exposed it can spend one discard to search Crobat V and unlock Star Alchemy.
* Ultra Ball can search Alolan Raichu directly when the target remains in the
  deck. If the search reveals that Raichu is absent and therefore Prized, it can
  pivot to Crobat V, after which Star Alchemy can take a remaining Gladion.

Computer Search is already modeled as a direct or Prize-adaptive universal
connector, so searching Crobat V with Computer Search does not improve this
narrow target-access objective.

This is still a component model. It does not use Dark Asset, model Bench
capacity, Tool-slot contention, lock effects, or competing strategic objectives.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache

from raichu_prize_access import (
    _bounded_compositions,
    _choose,
    accepted_opening_probability,
)


@dataclass(frozen=True)
class ForestSealSearchGateResult:
    """Exact probabilities for the typed Forest Seal search-to-gate layer."""

    state_mass: float
    valid_opening_probability: float
    target_prized_probability: float
    baseline_access: float
    direct_ready_access: float
    direct_plus_quick_access: float
    direct_plus_ultra_gate_access: float
    full_search_gate_access: float
    quick_gate_route_probability: float
    ultra_gate_route_probability: float
    ungated_forest_seal_access: float
    target_prized_baseline_access: float
    target_prized_direct_ready_access: float
    target_prized_direct_plus_quick_access: float
    target_prized_direct_plus_ultra_gate_access: float
    target_prized_full_search_gate_access: float

    @property
    def quick_marginal_over_direct(self) -> float:
        return self.direct_plus_quick_access - self.direct_ready_access

    @property
    def ultra_marginal_over_direct(self) -> float:
        return self.direct_plus_ultra_gate_access - self.direct_ready_access

    @property
    def ultra_residual_after_quick(self) -> float:
        return self.full_search_gate_access - self.direct_plus_quick_access

    @property
    def quick_residual_after_ultra(self) -> float:
        return self.full_search_gate_access - self.direct_plus_ultra_gate_access

    @property
    def search_gate_gain_over_direct(self) -> float:
        return self.full_search_gate_access - self.direct_ready_access

    @property
    def total_gain_over_baseline(self) -> float:
        return self.full_search_gate_access - self.baseline_access

    @property
    def remaining_gap_to_ungated(self) -> float:
        return self.ungated_forest_seal_access - self.full_search_gate_access

    def _conditional(self, mass: float) -> float:
        if self.target_prized_probability == 0:
            return 1.0
        return mass / self.target_prized_probability

    @property
    def conditional_target_prized_baseline_access(self) -> float:
        return self._conditional(self.target_prized_baseline_access)

    @property
    def conditional_target_prized_direct_ready_access(self) -> float:
        return self._conditional(self.target_prized_direct_ready_access)

    @property
    def conditional_target_prized_direct_plus_quick_access(self) -> float:
        return self._conditional(self.target_prized_direct_plus_quick_access)

    @property
    def conditional_target_prized_direct_plus_ultra_gate_access(self) -> float:
        return self._conditional(self.target_prized_direct_plus_ultra_gate_access)

    @property
    def conditional_target_prized_full_search_gate_access(self) -> float:
        return self._conditional(self.target_prized_full_search_gate_access)


def _product_choose(sizes: tuple[int, ...], counts: tuple[int, ...]) -> int:
    product = 1
    for size, count in zip(sizes, counts):
        product *= _choose(size, count)
    return product


def forest_seal_search_gate_snapshot(
    *,
    deck_size: int = 60,
    prize_count: int = 6,
    opening_hand_size: int = 7,
    extra_random_draws: int = 1,
    gladion_copies: int = 2,
    ultra_ball_copies: int = 3,
    computer_search_copies: int = 1,
    forest_seal_copies: int = 1,
    quick_ball_copies: int = 2,
    crobat_v_copies: int = 2,
    disposable_nonstarter_copies: int = 11,
    disposable_starter_copies: int = 1,
    other_starter_copies: int = 13,
    ultra_discard_cost: int = 2,
    quick_discard_cost: int = 1,
) -> ForestSealSearchGateResult:
    """Return exact access probabilities after typed search-to-gate sequencing."""

    counts = (
        gladion_copies,
        ultra_ball_copies,
        computer_search_copies,
        forest_seal_copies,
        quick_ball_copies,
        crobat_v_copies,
        disposable_nonstarter_copies,
        disposable_starter_copies,
        other_starter_copies,
        ultra_discard_cost,
        quick_discard_cost,
    )
    if deck_size <= 0:
        raise ValueError("deck_size must be positive")
    if opening_hand_size < 0 or prize_count < 0 or extra_random_draws < 0:
        raise ValueError("hand, Prize, and draw counts must be non-negative")
    if opening_hand_size + prize_count + extra_random_draws > deck_size:
        raise ValueError("requested zones exceed deck size")
    if min(counts) < 0:
        raise ValueError("card counts and discard costs must be non-negative")
    if computer_search_copies > 1:
        raise ValueError("this model supports at most one Computer Search ACE SPEC")

    target_copies = 1
    starter_cards = (
        crobat_v_copies + disposable_starter_copies + other_starter_copies
    )
    if starter_cards <= 0:
        raise ValueError("at least one setup-eligible starter is required")

    explicit = (
        target_copies
        + gladion_copies
        + ultra_ball_copies
        + computer_search_copies
        + forest_seal_copies
        + quick_ball_copies
        + crobat_v_copies
        + disposable_nonstarter_copies
        + disposable_starter_copies
        + other_starter_copies
    )
    if explicit > deck_size:
        raise ValueError("modeled categories exceed deck size")

    protected_other = deck_size - explicit
    filler_copies = other_starter_copies + protected_other

    # Opening categories preserve starter/discard overlap. After setup, the
    # disposable classes can be collapsed and the non-disposable filler classes
    # can be collapsed because their later identities do not affect this objective.
    opening_sizes = (
        target_copies,
        gladion_copies,
        ultra_ball_copies,
        computer_search_copies,
        forest_seal_copies,
        quick_ball_copies,
        crobat_v_copies,
        disposable_nonstarter_copies,
        disposable_starter_copies,
        filler_copies,
    )

    accepted = accepted_opening_probability(
        deck_size,
        starter_cards,
        opening_hand_size,
    )
    if accepted == 0.0:
        raise ValueError("valid-opening conditioning event has zero probability")

    opening_denominator = _choose(deck_size, opening_hand_size)
    prize_denominator = _choose(deck_size - opening_hand_size, prize_count)

    metrics = {
        "state_mass": 0.0,
        "target_prized_probability": 0.0,
        "baseline_access": 0.0,
        "direct_ready_access": 0.0,
        "direct_plus_quick_access": 0.0,
        "direct_plus_ultra_gate_access": 0.0,
        "full_search_gate_access": 0.0,
        "quick_gate_route_probability": 0.0,
        "ultra_gate_route_probability": 0.0,
        "ungated_forest_seal_access": 0.0,
        "target_prized_baseline_access": 0.0,
        "target_prized_direct_ready_access": 0.0,
        "target_prized_direct_plus_quick_access": 0.0,
        "target_prized_direct_plus_ultra_gate_access": 0.0,
        "target_prized_full_search_gate_access": 0.0,
    }

    for opening in _bounded_compositions(opening_hand_size, opening_sizes):
        filler_in_opening = opening[9]
        filler_total_ways = _choose(filler_copies, filler_in_opening)
        filler_without_other_starter_ways = _choose(
            protected_other,
            filler_in_opening,
        )

        # Each subcase stores:
        # (number of labeled filler realizations, Crobat already in play,
        #  whether the disposable starter was forced Active).
        setup_subcases: list[tuple[int, bool, bool]] = []

        if opening[6] > 0:
            setup_subcases.append((filler_total_ways, True, False))
        else:
            filler_with_other_starter_ways = (
                filler_total_ways - filler_without_other_starter_ways
            )
            if filler_with_other_starter_ways > 0:
                setup_subcases.append(
                    (filler_with_other_starter_ways, False, False)
                )
            if (
                filler_without_other_starter_ways > 0
                and opening[8] > 0
            ):
                setup_subcases.append(
                    (filler_without_other_starter_ways, False, True)
                )

        if not setup_subcases:
            continue

        fixed_opening_ways = _product_choose(
            opening_sizes[:9],
            opening[:9],
        )

        # Post-opening categories:
        # target, Gladion, Ultra Ball, Computer Search, Forest Seal Stone,
        # Quick Ball, Crobat V, all disposable cards, all irrelevant filler.
        after_opening = (
            target_copies - opening[0],
            gladion_copies - opening[1],
            ultra_ball_copies - opening[2],
            computer_search_copies - opening[3],
            forest_seal_copies - opening[4],
            quick_ball_copies - opening[5],
            crobat_v_copies - opening[6],
            (
                disposable_nonstarter_copies - opening[7]
                + disposable_starter_copies - opening[8]
            ),
            filler_copies - opening[9],
        )

        prize_states = tuple(
            _bounded_compositions(prize_count, after_opening)
        )

        for filler_ways, crobat_in_play, disposable_starter_active in setup_subcases:
            opening_mass = (
                fixed_opening_ways
                * filler_ways
                / opening_denominator
                / accepted
            )

            action_hand = (
                opening[0],
                opening[1],
                opening[2],
                opening[3],
                opening[4],
                opening[5],
                opening[6] - (1 if crobat_in_play else 0),
                (
                    opening[7]
                    + opening[8]
                    - (1 if disposable_starter_active else 0)
                ),
                opening[9]
                - (
                    1
                    if not crobat_in_play
                    and not disposable_starter_active
                    else 0
                ),
            )

            for prizes in prize_states:
                prize_ways = _product_choose(after_opening, prizes)
                if prize_ways == 0:
                    continue

                prize_mass = prize_ways / prize_denominator
                post_prize_deck = tuple(
                    remaining - prized
                    for remaining, prized in zip(after_opening, prizes)
                )
                target_prized = prizes[0] > 0

                @lru_cache(maxsize=None)
                def expose(
                    hand: tuple[int, ...],
                    deck: tuple[int, ...],
                    draws_remaining: int,
                ) -> tuple[float, ...]:
                    if draws_remaining == 0:
                        target_in_hand = hand[0] > 0
                        target_in_deck = deck[0] > 0
                        gladion_in_hand = hand[1] > 0
                        gladion_in_deck = deck[1] > 0
                        ultra_in_hand = hand[2] > 0
                        computer_in_hand = hand[3] > 0
                        forest_seal_in_hand = hand[4] > 0
                        quick_in_hand = hand[5] > 0
                        crobat_available = crobat_in_play or hand[6] > 0
                        crobat_in_deck = deck[6] > 0
                        disposable_count = hand[7]

                        ultra_payable = (
                            disposable_count >= ultra_discard_cost
                        )
                        quick_payable = (
                            disposable_count >= quick_discard_cost
                        )

                        baseline = target_in_hand or (
                            target_in_deck
                            and ultra_payable
                            and (ultra_in_hand or computer_in_hand)
                        ) or (
                            target_prized
                            and (
                                gladion_in_hand
                                or (
                                    ultra_payable
                                    and computer_in_hand
                                    and gladion_in_deck
                                )
                            )
                        )

                        seal_output_works = target_in_deck or (
                            target_prized and gladion_in_deck
                        )
                        direct_ready = (
                            forest_seal_in_hand
                            and crobat_available
                            and seal_output_works
                        )
                        direct_access = baseline or direct_ready

                        quick_gate_route = (
                            forest_seal_in_hand
                            and quick_in_hand
                            and quick_payable
                            and crobat_in_deck
                            and seal_output_works
                        )

                        # Ultra Ball already solves an unprized Raichu directly.
                        # Its gate-completion option adds only states where the
                        # search itself reveals that Raichu is Prized.
                        ultra_gate_route = (
                            forest_seal_in_hand
                            and ultra_in_hand
                            and ultra_payable
                            and crobat_in_deck
                            and target_prized
                            and gladion_in_deck
                        )

                        direct_plus_quick = (
                            direct_access or quick_gate_route
                        )
                        direct_plus_ultra = (
                            direct_access or ultra_gate_route
                        )
                        full_search_gate = (
                            direct_access
                            or quick_gate_route
                            or ultra_gate_route
                        )
                        ungated = baseline or (
                            forest_seal_in_hand and seal_output_works
                        )

                        return tuple(
                            float(flag)
                            for flag in (
                                baseline,
                                direct_access,
                                direct_plus_quick,
                                direct_plus_ultra,
                                full_search_gate,
                                quick_gate_route,
                                ultra_gate_route,
                                ungated,
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

                values = expose(
                    action_hand,
                    post_prize_deck,
                    extra_random_draws,
                )
                mass = opening_mass * prize_mass

                metrics["state_mass"] += mass
                metrics["target_prized_probability"] += (
                    mass * target_prized
                )

                keys = (
                    "baseline_access",
                    "direct_ready_access",
                    "direct_plus_quick_access",
                    "direct_plus_ultra_gate_access",
                    "full_search_gate_access",
                    "quick_gate_route_probability",
                    "ultra_gate_route_probability",
                    "ungated_forest_seal_access",
                )
                for key, value in zip(keys, values):
                    metrics[key] += mass * value

                if target_prized:
                    prize_keys = (
                        "target_prized_baseline_access",
                        "target_prized_direct_ready_access",
                        "target_prized_direct_plus_quick_access",
                        "target_prized_direct_plus_ultra_gate_access",
                        "target_prized_full_search_gate_access",
                    )
                    for key, value in zip(prize_keys, values[:5]):
                        metrics[key] += mass * value

    return ForestSealSearchGateResult(
        valid_opening_probability=accepted,
        **metrics,
    )
