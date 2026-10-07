"""Exact search-to-gate access for Harto Miki's Aichi Raichu list.

This extends the direct-ready Forest Seal Stone component with two executable
Pokemon-search routes that can complete the missing Crobat V gate:

* Quick Ball -> Crobat V -> Forest Seal Stone -> Star Alchemy;
* Ultra Ball -> inspect deck -> Crobat V when Raichu is Prized ->
  Forest Seal Stone -> Gladion.

The model preserves the one-card versus two-card discard thresholds and the
same conservative discardable-card policy used by the earlier Raichu results.
It still omits Crobat V's Dark Asset draw Ability and other draw-engine lines.
"""

from __future__ import annotations

from dataclasses import dataclass

from raichu_prize_access import (
    _bounded_compositions,
    _choose,
    _multivariate_probability,
    accepted_opening_probability,
)


@dataclass(frozen=True)
class SearchToSealAccessResult:
    """Exact probabilities for direct and search-completed Forest Seal access."""

    state_mass: float
    valid_opening_probability: float
    target_prized_probability: float
    baseline_access: float
    direct_ready_forest_seal_access: float
    sequenced_forest_seal_access: float
    ungated_forest_seal_access: float
    forest_seal_exposed_probability: float
    crobat_available_probability: float
    forest_seal_ready_probability: float
    quick_ball_exposed_probability: float
    one_card_discard_payable_probability: float
    two_card_discard_payable_probability: float
    quick_ball_gate_route_probability: float
    ultra_ball_pivot_route_probability: float
    incremental_quick_ball_access: float
    incremental_ultra_ball_access: float
    incremental_quick_low_cost_access: float
    incremental_target_in_deck_access: float
    incremental_target_prized_access: float
    target_prized_direct_ready_access: float
    target_prized_sequenced_access: float
    target_prized_ungated_access: float

    @property
    def search_to_gate_gain(self) -> float:
        return self.sequenced_forest_seal_access - self.direct_ready_forest_seal_access

    @property
    def remaining_gate_overstatement(self) -> float:
        return self.ungated_forest_seal_access - self.sequenced_forest_seal_access

    @property
    def conditional_target_prized_direct_ready_access(self) -> float:
        if self.target_prized_probability == 0.0:
            return 1.0
        return self.target_prized_direct_ready_access / self.target_prized_probability

    @property
    def conditional_target_prized_sequenced_access(self) -> float:
        if self.target_prized_probability == 0.0:
            return 1.0
        return self.target_prized_sequenced_access / self.target_prized_probability

    @property
    def conditional_target_prized_ungated_access(self) -> float:
        if self.target_prized_probability == 0.0:
            return 1.0
        return self.target_prized_ungated_access / self.target_prized_probability


def search_to_seal_access_snapshot(
    *,
    deck_size: int = 60,
    prize_count: int = 6,
    opening_hand_size: int = 7,
    gladion_copies: int = 2,
    ultra_ball_copies: int = 3,
    computer_search_copies: int = 1,
    forest_seal_copies: int = 1,
    crobat_v_copies: int = 2,
    quick_ball_copies: int = 2,
    disposable_nonstarter_copies: int = 11,
    disposable_starter_copies: int = 1,
    other_starter_copies: int = 13,
    quick_ball_discard_cost: int = 1,
    two_card_discard_cost: int = 2,
) -> SearchToSealAccessResult:
    """Return exact access after setup, Prizes, and one later random draw.

    For calculation, the later random draw is integrated before the six random
    Prize cards. Conditional on the accepted opening this is the same joint
    partition of the remaining cards, while the modeled gameplay policy still
    receives Prize information only after a deck search begins.
    """

    counts = (
        gladion_copies,
        ultra_ball_copies,
        computer_search_copies,
        forest_seal_copies,
        crobat_v_copies,
        quick_ball_copies,
        disposable_nonstarter_copies,
        disposable_starter_copies,
        other_starter_copies,
        quick_ball_discard_cost,
        two_card_discard_cost,
    )
    if deck_size <= 0:
        raise ValueError("deck_size must be positive")
    if opening_hand_size < 0 or prize_count < 0:
        raise ValueError("opening and Prize counts must be non-negative")
    if opening_hand_size + prize_count + 1 > deck_size:
        raise ValueError("opening, Prize cards, and later draw exceed deck size")
    if min(counts) < 0:
        raise ValueError("card counts and discard costs must be non-negative")

    target_copies = 1
    starter_cards = crobat_v_copies + disposable_starter_copies + other_starter_copies
    if starter_cards <= 0:
        raise ValueError("at least one setup-eligible starter is required")

    used = (
        target_copies
        + gladion_copies
        + ultra_ball_copies
        + computer_search_copies
        + forest_seal_copies
        + crobat_v_copies
        + quick_ball_copies
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
        quick_ball_copies,
        disposable_nonstarter_copies,
        disposable_starter_copies,
        other_starter_copies,
        protected_other,
    )

    accepted = accepted_opening_probability(deck_size, starter_cards, opening_hand_size)
    if accepted == 0.0:
        raise ValueError("valid-opening conditioning event has zero probability")

    metrics = {
        "state_mass": 0.0,
        "target_prized_probability": 0.0,
        "baseline_access": 0.0,
        "direct_ready_forest_seal_access": 0.0,
        "sequenced_forest_seal_access": 0.0,
        "ungated_forest_seal_access": 0.0,
        "forest_seal_exposed_probability": 0.0,
        "crobat_available_probability": 0.0,
        "forest_seal_ready_probability": 0.0,
        "quick_ball_exposed_probability": 0.0,
        "one_card_discard_payable_probability": 0.0,
        "two_card_discard_payable_probability": 0.0,
        "quick_ball_gate_route_probability": 0.0,
        "ultra_ball_pivot_route_probability": 0.0,
        "incremental_quick_ball_access": 0.0,
        "incremental_ultra_ball_access": 0.0,
        "incremental_quick_low_cost_access": 0.0,
        "incremental_target_in_deck_access": 0.0,
        "incremental_target_prized_access": 0.0,
        "target_prized_direct_ready_access": 0.0,
        "target_prized_sequenced_access": 0.0,
        "target_prized_ungated_access": 0.0,
    }

    draw_pool_size = deck_size - opening_hand_size
    prize_pool_size = draw_pool_size - 1
    prize_denominator = _choose(prize_pool_size, prize_count)

    for opening in _bounded_compositions(opening_hand_size, sizes):
        if opening[5] + opening[8] + opening[9] == 0:
            continue

        opening_mass = _multivariate_probability(opening, sizes) / accepted
        remaining_after_opening = [
            size - count for size, count in zip(sizes, opening)
        ]

        action_hand = list(opening)
        crobat_in_play = False
        if opening[5] > 0:
            action_hand[5] -= 1
            crobat_in_play = True
        elif opening[9] > 0:
            action_hand[9] -= 1
        else:
            action_hand[8] -= 1

        for draw_category, draw_count in enumerate(remaining_after_opening):
            if draw_count == 0:
                continue

            draw_mass = draw_count / draw_pool_size
            hand = action_hand.copy()
            hand[draw_category] += 1
            prize_pool = remaining_after_opening.copy()
            prize_pool[draw_category] -= 1

            target_pool = prize_pool[0]
            gladion_pool = prize_pool[1]
            crobat_pool = prize_pool[5]
            other_pool = prize_pool_size - target_pool - gladion_pool - crobat_pool

            for target_prizes in range(min(target_pool, prize_count) + 1):
                for gladion_prizes in range(min(gladion_pool, prize_count) + 1):
                    for crobat_prizes in range(min(crobat_pool, prize_count) + 1):
                        named_prizes = target_prizes + gladion_prizes + crobat_prizes
                        other_prizes = prize_count - named_prizes
                        prize_ways = (
                            _choose(target_pool, target_prizes)
                            * _choose(gladion_pool, gladion_prizes)
                            * _choose(crobat_pool, crobat_prizes)
                            * _choose(other_pool, other_prizes)
                        )
                        if prize_ways == 0:
                            continue

                        mass = opening_mass * draw_mass * prize_ways / prize_denominator

                        target_in_hand = hand[0] > 0
                        target_prized = target_prizes > 0
                        target_in_deck = target_pool - target_prizes > 0
                        gladion_in_hand = hand[1] > 0
                        gladion_in_deck = gladion_pool - gladion_prizes > 0
                        ultra_in_hand = hand[2] > 0
                        computer_in_hand = hand[3] > 0
                        forest_seal_exposed = hand[4] > 0
                        crobat_available = crobat_in_play or hand[5] > 0
                        crobat_in_deck = crobat_pool - crobat_prizes > 0
                        quick_ball_in_hand = hand[6] > 0
                        disposable_count = hand[7] + hand[8]
                        quick_payable = disposable_count >= quick_ball_discard_cost
                        two_card_payable = disposable_count >= two_card_discard_cost

                        baseline_access = target_in_hand or (
                            target_in_deck
                            and two_card_payable
                            and (ultra_in_hand or computer_in_hand)
                        ) or (
                            target_prized
                            and (
                                gladion_in_hand
                                or (
                                    two_card_payable
                                    and computer_in_hand
                                    and gladion_in_deck
                                )
                            )
                        )

                        seal_output_works = target_in_deck or (
                            target_prized and gladion_in_deck
                        )
                        forest_seal_ready = forest_seal_exposed and crobat_available
                        direct_ready_access = baseline_access or (
                            forest_seal_ready and seal_output_works
                        )
                        ungated_access = baseline_access or (
                            forest_seal_exposed and seal_output_works
                        )

                        quick_ball_route = (
                            forest_seal_exposed
                            and not crobat_available
                            and crobat_in_deck
                            and quick_ball_in_hand
                            and quick_payable
                            and seal_output_works
                        )

                        ultra_ball_pivot = (
                            forest_seal_exposed
                            and not crobat_available
                            and crobat_in_deck
                            and ultra_in_hand
                            and two_card_payable
                            and target_prized
                            and gladion_in_deck
                        )

                        sequenced_access = (
                            direct_ready_access
                            or quick_ball_route
                            or ultra_ball_pivot
                        )
                        incremental_quick = quick_ball_route and not direct_ready_access
                        incremental_ultra = (
                            ultra_ball_pivot
                            and not direct_ready_access
                            and not quick_ball_route
                        )
                        incremental = incremental_quick or incremental_ultra

                        metrics["state_mass"] += mass
                        metrics["target_prized_probability"] += mass * target_prized
                        metrics["baseline_access"] += mass * baseline_access
                        metrics["direct_ready_forest_seal_access"] += mass * direct_ready_access
                        metrics["sequenced_forest_seal_access"] += mass * sequenced_access
                        metrics["ungated_forest_seal_access"] += mass * ungated_access
                        metrics["forest_seal_exposed_probability"] += mass * forest_seal_exposed
                        metrics["crobat_available_probability"] += mass * crobat_available
                        metrics["forest_seal_ready_probability"] += mass * forest_seal_ready
                        metrics["quick_ball_exposed_probability"] += mass * quick_ball_in_hand
                        metrics["one_card_discard_payable_probability"] += mass * quick_payable
                        metrics["two_card_discard_payable_probability"] += mass * two_card_payable
                        metrics["quick_ball_gate_route_probability"] += mass * quick_ball_route
                        metrics["ultra_ball_pivot_route_probability"] += mass * ultra_ball_pivot
                        metrics["incremental_quick_ball_access"] += mass * incremental_quick
                        metrics["incremental_ultra_ball_access"] += mass * incremental_ultra
                        metrics["incremental_quick_low_cost_access"] += mass * (
                            incremental_quick and not two_card_payable
                        )
                        metrics["incremental_target_in_deck_access"] += mass * (
                            incremental and target_in_deck
                        )
                        metrics["incremental_target_prized_access"] += mass * (
                            incremental and target_prized
                        )
                        metrics["target_prized_direct_ready_access"] += mass * (
                            target_prized and direct_ready_access
                        )
                        metrics["target_prized_sequenced_access"] += mass * (
                            target_prized and sequenced_access
                        )
                        metrics["target_prized_ungated_access"] += mass * (
                            target_prized and ungated_access
                        )

    return SearchToSealAccessResult(
        valid_opening_probability=accepted,
        **metrics,
    )
