"""Exact Crobat V Dark Asset bridge for Harto Miki's Raichu access model.

This layer follows the one-draw action snapshot used by the preceding Raichu
results. After the mandatory setup Pokemon leaves the seven-card opening hand,
one later random card is exposed, so the action hand contains seven cards.

That fixed hand size makes the immediate Dark Asset consequence deterministic:

* Quick Ball -> discard 1 -> search Crobat V -> Bench Crobat leaves 5 cards,
  so Dark Asset draws exactly 1 card to reach 6.
* Ultra Ball -> discard 2 -> search Crobat V -> Bench Crobat leaves 4 cards,
  so Dark Asset draws exactly 2 cards to reach 6.

Dark Asset is modeled immediately after Crobat V is played from hand onto the
Bench. The subsequent Forest Seal Stone / Star Alchemy choice can then use the
post-draw state.

This is a narrow target-access policy. It does not value the extra random cards
for any purpose other than accessing Alolan Raichu, Gladion, or Forest Seal
Stone, and it does not model Bench, Ability, Tool, Item, or VSTAR locks.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import comb

from raichu_forest_seal_search_gate import _product_choose
from raichu_prize_access import (
    _bounded_compositions,
    _choose,
    accepted_opening_probability,
)


@dataclass(frozen=True)
class DarkAssetBridgeResult:
    """Exact target-access probabilities for the Dark Asset bridge."""

    state_mass: float
    valid_opening_probability: float
    target_prized_probability: float
    baseline_access: float
    direct_ready_access: float
    no_dark_search_gate_access: float
    quick_dark_policy_access: float
    ultra_dark_policy_access: float
    full_dark_asset_policy_access: float
    target_prized_no_dark_search_gate_access: float
    target_prized_full_dark_asset_policy_access: float

    @property
    def dark_asset_gain_over_no_dark(self) -> float:
        return self.full_dark_asset_policy_access - self.no_dark_search_gate_access

    @property
    def total_gain_over_baseline(self) -> float:
        return self.full_dark_asset_policy_access - self.baseline_access

    @property
    def conditional_target_prized_no_dark_access(self) -> float:
        if self.target_prized_probability == 0:
            return 1.0
        return (
            self.target_prized_no_dark_search_gate_access
            / self.target_prized_probability
        )

    @property
    def conditional_target_prized_dark_asset_access(self) -> float:
        if self.target_prized_probability == 0:
            return 1.0
        return (
            self.target_prized_full_dark_asset_policy_access
            / self.target_prized_probability
        )


def _draw_hit_probability(
    *,
    deck_size: int,
    successful_cards: int,
    draws: int,
) -> float:
    """Probability that at least one successful card appears without replacement."""
    if successful_cards <= 0 or draws <= 0:
        return 0.0
    draws = min(draws, deck_size)
    if successful_cards >= deck_size:
        return 1.0
    misses = deck_size - successful_cards
    return 1.0 - _choose(misses, draws) / _choose(deck_size, draws)


def dark_asset_bridge_snapshot(
    *,
    deck_size: int = 60,
    prize_count: int = 6,
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
) -> DarkAssetBridgeResult:
    """Return exact access for the fixed seven-card action-hand snapshot."""

    opening_hand_size = 7
    extra_random_draws = 1

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
    if prize_count < 0:
        raise ValueError("prize_count must be non-negative")
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
    opening_denominator = _choose(deck_size, opening_hand_size)
    prize_denominator = _choose(deck_size - opening_hand_size, prize_count)

    metrics = {
        "state_mass": 0.0,
        "target_prized_probability": 0.0,
        "baseline_access": 0.0,
        "direct_ready_access": 0.0,
        "no_dark_search_gate_access": 0.0,
        "quick_dark_policy_access": 0.0,
        "ultra_dark_policy_access": 0.0,
        "full_dark_asset_policy_access": 0.0,
        "target_prized_no_dark_search_gate_access": 0.0,
        "target_prized_full_dark_asset_policy_access": 0.0,
    }

    for opening in _bounded_compositions(opening_hand_size, opening_sizes):
        filler_in_opening = opening[9]
        filler_total_ways = _choose(filler_copies, filler_in_opening)
        filler_without_other_starter_ways = _choose(
            protected_other,
            filler_in_opening,
        )

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

            action_hand_before_draw = (
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
                total_before_draw = sum(post_prize_deck)

                for drawn_category, count in enumerate(post_prize_deck):
                    if count == 0:
                        continue

                    hand = list(action_hand_before_draw)
                    deck = list(post_prize_deck)
                    hand[drawn_category] += 1
                    deck[drawn_category] -= 1

                    mass = (
                        opening_mass
                        * prize_mass
                        * count
                        / total_before_draw
                    )

                    target_in_hand = hand[0] > 0
                    target_in_deck = deck[0] > 0
                    gladion_in_hand = hand[1] > 0
                    gladion_in_deck = deck[1]
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
                                and gladion_in_deck > 0
                            )
                        )
                    )

                    seal_output_works = target_in_deck or (
                        target_prized and gladion_in_deck > 0
                    )
                    direct_ready = (
                        forest_seal_in_hand
                        and crobat_available
                        and seal_output_works
                    )
                    direct_access = baseline or direct_ready

                    no_dark_quick = (
                        forest_seal_in_hand
                        and quick_in_hand
                        and quick_payable
                        and crobat_in_deck
                        and seal_output_works
                    )
                    no_dark_ultra = (
                        forest_seal_in_hand
                        and ultra_in_hand
                        and ultra_payable
                        and crobat_in_deck
                        and target_prized
                        and gladion_in_deck > 0
                    )
                    no_dark_search_gate = (
                        direct_access or no_dark_quick or no_dark_ultra
                    )

                    quick_probability = 0.0
                    ultra_probability = 0.0

                    if crobat_in_deck:
                        post_search_deck_size = sum(deck) - 1
                        forest_seal_in_deck = deck[4]

                        if quick_in_hand and quick_payable:
                            if forest_seal_in_hand:
                                quick_probability = (
                                    1.0 if seal_output_works else 0.0
                                )
                            elif target_in_deck:
                                successful_cards = (
                                    deck[0] + forest_seal_in_deck
                                )
                                quick_probability = _draw_hit_probability(
                                    deck_size=post_search_deck_size,
                                    successful_cards=successful_cards,
                                    draws=1,
                                )
                            elif target_prized and gladion_in_deck > 0:
                                successful_cards = (
                                    gladion_in_deck
                                    + forest_seal_in_deck
                                )
                                quick_probability = _draw_hit_probability(
                                    deck_size=post_search_deck_size,
                                    successful_cards=successful_cards,
                                    draws=1,
                                )

                        if ultra_in_hand and ultra_payable:
                            if target_in_deck:
                                ultra_probability = 1.0
                            elif target_prized and gladion_in_deck > 0:
                                if forest_seal_in_hand:
                                    ultra_probability = 1.0
                                else:
                                    successful_cards = (
                                        gladion_in_deck
                                        + forest_seal_in_deck
                                    )
                                    ultra_probability = _draw_hit_probability(
                                        deck_size=post_search_deck_size,
                                        successful_cards=successful_cards,
                                        draws=2,
                                    )

                    if direct_access:
                        quick_policy = 1.0
                        ultra_policy = 1.0
                        full_policy = 1.0
                    else:
                        quick_policy = quick_probability
                        ultra_policy = ultra_probability

                        # Under this narrow target-access objective, a payable
                        # Ultra Ball weakly dominates Quick Ball: it guarantees
                        # an unprized target directly and, in Prized states,
                        # creates two Dark Asset draws instead of one. If the
                        # two-card cost is unavailable, fall back to Quick Ball.
                        if (
                            ultra_in_hand
                            and ultra_payable
                            and crobat_in_deck
                        ):
                            full_policy = ultra_probability
                        else:
                            full_policy = quick_probability

                    metrics["state_mass"] += mass
                    metrics["target_prized_probability"] += (
                        mass * target_prized
                    )
                    metrics["baseline_access"] += mass * baseline
                    metrics["direct_ready_access"] += mass * direct_access
                    metrics["no_dark_search_gate_access"] += (
                        mass * no_dark_search_gate
                    )
                    metrics["quick_dark_policy_access"] += (
                        mass * quick_policy
                    )
                    metrics["ultra_dark_policy_access"] += (
                        mass * ultra_policy
                    )
                    metrics["full_dark_asset_policy_access"] += (
                        mass * full_policy
                    )

                    if target_prized:
                        metrics[
                            "target_prized_no_dark_search_gate_access"
                        ] += mass * no_dark_search_gate
                        metrics[
                            "target_prized_full_dark_asset_policy_access"
                        ] += mass * full_policy

    return DarkAssetBridgeResult(
        valid_opening_probability=accepted,
        **metrics,
    )
