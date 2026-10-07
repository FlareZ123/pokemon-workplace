"""Bounded post-Dark-Asset connector continuation for Harto Miki Raichu.

This extends raichu_dark_asset_search.py by allowing one additional executable
search action after Dark Asset resolves. The continuation is deliberately
bounded: it credits Ultra Ball or Computer Search drawn by Dark Asset when
their two-card discard cost remains payable. It does not recurse into further
draw engines or arbitrary full-turn search.

The model preserves the preceding valid-opening conditioning, Prize-aware
Computer Search policy, Forest Seal Stone gate, and conservative disposable
pool. It analytically marginalizes unspecified Prize identities using first
and second hypergeometric survivor moments.
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
class DarkAssetFollowupResult:
    state_mass: float
    valid_opening_probability: float
    target_prized_probability: float
    sequenced_forest_seal_access: float
    first_order_dark_asset_access: float
    bounded_followup_access: float
    incremental_followup_access: float
    quick_enabled_access: float
    quick_followup_gain: float
    ultra_followup_gain_after_quick: float
    incremental_target_in_deck_access: float
    incremental_target_prized_access: float
    target_prized_first_order_access: float
    target_prized_bounded_followup_access: float

    @property
    def conditional_target_prized_first_order_access(self) -> float:
        if self.target_prized_probability == 0.0:
            return 1.0
        return self.target_prized_first_order_access / self.target_prized_probability

    @property
    def conditional_target_prized_bounded_followup_access(self) -> float:
        if self.target_prized_probability == 0.0:
            return 1.0
        return self.target_prized_bounded_followup_access / self.target_prized_probability


def _hit_probability(population: int, good: int, draws: int) -> float:
    if draws <= 0 or good <= 0:
        return 0.0
    if good >= population:
        return 1.0
    return 1.0 - _choose(population - good, draws) / _choose(population, draws)


def dark_asset_followup_snapshot(
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
) -> DarkAssetFollowupResult:
    """Return exact bounded connector continuation after Dark Asset.

    The hand arithmetic is the Harto snapshot used by the preceding result:
    a seven-card opening, one setup Basic materialized, then one ordinary draw.
    Quick Ball -> Crobat therefore leaves five cards before Dark Asset and
    draws one; Ultra Ball -> Crobat leaves four and draws two.
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
    if opening_hand_size != 7:
        raise ValueError("this bounded continuation currently requires a seven-card opening")
    if prize_count < 0:
        raise ValueError("prize_count must be non-negative")
    if min(counts) < 0:
        raise ValueError("card counts and discard costs must be non-negative")
    if quick_ball_discard_cost != 1 or two_card_discard_cost != 2:
        raise ValueError("this continuation is derived for one-card and two-card discard costs")

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
        deck_size - used,
    )
    accepted = accepted_opening_probability(deck_size, starter_cards, opening_hand_size)
    if accepted == 0.0:
        raise ValueError("valid-opening conditioning event has zero probability")

    draw_pool_size = deck_size - opening_hand_size
    prize_pool_size = draw_pool_size - 1
    post_search_deck_size = deck_size - opening_hand_size - 1 - prize_count - 1
    if post_search_deck_size < 2:
        raise ValueError("at least two cards must remain after the searched Crobat leaves the deck")
    prize_denominator = _choose(prize_pool_size, prize_count)
    if prize_denominator == 0:
        raise ValueError("Prize configuration is impossible for this deck size")

    metrics = {
        "state_mass": 0.0,
        "target_prized_probability": 0.0,
        "sequenced_forest_seal_access": 0.0,
        "first_order_dark_asset_access": 0.0,
        "bounded_followup_access": 0.0,
        "quick_enabled_access": 0.0,
        "incremental_target_in_deck_access": 0.0,
        "incremental_target_prized_access": 0.0,
        "target_prized_first_order_access": 0.0,
        "target_prized_bounded_followup_access": 0.0,
    }

    for opening in _bounded_compositions(opening_hand_size, sizes):
        if opening[5] + opening[8] + opening[9] == 0:
            continue
        opening_mass = _multivariate_probability(opening, sizes) / accepted
        remaining_after_opening = [size - count for size, count in zip(sizes, opening)]

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
            fss_pool = prize_pool[4]
            crobat_pool = prize_pool[5]
            other_pool = prize_pool_size - target_pool - gladion_pool - fss_pool - crobat_pool

            ultra_pool = prize_pool[2]
            computer_pool = prize_pool[3]
            disposable_pool = prize_pool[7] + prize_pool[8]

            for tp in range(min(target_pool, prize_count) + 1):
                for gp in range(min(gladion_pool, prize_count) + 1):
                    for fp in range(min(fss_pool, prize_count) + 1):
                        for cp in range(min(crobat_pool, prize_count) + 1):
                            other_prizes = prize_count - tp - gp - fp - cp
                            ways = (
                                _choose(target_pool, tp)
                                * _choose(gladion_pool, gp)
                                * _choose(fss_pool, fp)
                                * _choose(crobat_pool, cp)
                                * _choose(other_pool, other_prizes)
                            )
                            if ways == 0:
                                continue
                            mass = opening_mass * draw_mass * ways / prize_denominator

                            target_in_hand = hand[0] > 0
                            target_prized = tp > 0
                            target_in_deck = target_pool - tp > 0
                            gladion_in_hand = hand[1] > 0
                            gladion_in_deck = gladion_pool - gp
                            ultra_in_hand = hand[2] > 0
                            computer_in_hand = hand[3] > 0
                            fss_in_hand = hand[4] > 0
                            fss_in_deck = fss_pool - fp
                            crobat_available = crobat_in_play or hand[5] > 0
                            crobat_in_deck = crobat_pool - cp > 0
                            quick_in_hand = hand[6] > 0
                            disposable_count = hand[7] + hand[8]
                            quick_payable = disposable_count >= quick_ball_discard_cost
                            two_payable = disposable_count >= two_card_discard_cost

                            baseline = target_in_hand or (
                                target_in_deck
                                and two_payable
                                and (ultra_in_hand or computer_in_hand)
                            ) or (
                                target_prized
                                and (
                                    gladion_in_hand
                                    or (
                                        two_payable
                                        and computer_in_hand
                                        and gladion_in_deck > 0
                                    )
                                )
                            )
                            seal_output_works = target_in_deck or (
                                target_prized and gladion_in_deck > 0
                            )
                            direct_ready = baseline or (
                                fss_in_hand and crobat_available and seal_output_works
                            )
                            quick_gate = (
                                fss_in_hand
                                and not crobat_available
                                and crobat_in_deck
                                and quick_in_hand
                                and quick_payable
                                and seal_output_works
                            )
                            ultra_gate = (
                                fss_in_hand
                                and not crobat_available
                                and crobat_in_deck
                                and ultra_in_hand
                                and two_payable
                                and target_prized
                                and gladion_in_deck > 0
                            )
                            sequenced = direct_ready or quick_gate or ultra_gate

                            quick_candidate = quick_in_hand and quick_payable and crobat_in_deck
                            ultra_candidate = (
                                target_prized
                                and ultra_in_hand
                                and two_payable
                                and crobat_in_deck
                            )

                            quick_first = 0.0
                            if quick_candidate:
                                if target_in_deck:
                                    quick_first = _hit_probability(
                                        post_search_deck_size,
                                        int(target_in_deck) + fss_in_deck,
                                        1,
                                    )
                                elif target_prized and gladion_in_deck > 0:
                                    quick_first = _hit_probability(
                                        post_search_deck_size,
                                        gladion_in_deck + fss_in_deck,
                                        1,
                                    )

                            ultra_first = 0.0
                            if ultra_candidate and gladion_in_deck > 0:
                                ultra_first = _hit_probability(
                                    post_search_deck_size,
                                    gladion_in_deck + fss_in_deck,
                                    2,
                                )

                            quick_bounded = quick_first
                            if (
                                quick_candidate
                                and not sequenced
                                and disposable_count - quick_ball_discard_cost
                                >= two_card_discard_cost
                            ):
                                connector_pool = (
                                    ultra_pool + computer_pool
                                    if target_in_deck
                                    else (
                                        computer_pool
                                        if target_prized and gladion_in_deck > 0
                                        else 0
                                    )
                                )
                                survivors = other_pool - other_prizes
                                expected_connectors = (
                                    connector_pool * survivors / other_pool
                                    if other_pool > 0
                                    else 0.0
                                )
                                quick_bounded += expected_connectors / post_search_deck_size

                            ultra_bounded = ultra_first
                            if ultra_candidate and not sequenced and gladion_in_deck > 0:
                                remaining_disposables = disposable_count - two_card_discard_cost
                                survivors = other_pool - other_prizes
                                expected_computer = (
                                    computer_pool * survivors / other_pool
                                    if other_pool > 0
                                    else 0.0
                                )
                                if other_pool >= 2 and survivors >= 2:
                                    pair_survival = (
                                        survivors
                                        * (survivors - 1)
                                        / (other_pool * (other_pool - 1))
                                    )
                                    expected_computer_pairs = (
                                        _choose(computer_pool, 2) * pair_survival
                                    )
                                    expected_computer_disposable_pairs = (
                                        computer_pool * disposable_pool * pair_survival
                                    )
                                else:
                                    expected_computer_pairs = 0.0
                                    expected_computer_disposable_pairs = 0.0

                                direct_good = gladion_in_deck + fss_in_deck
                                pair_denominator = _choose(post_search_deck_size, 2)
                                if remaining_disposables >= two_card_discard_cost:
                                    non_direct_population = (
                                        post_search_deck_size - direct_good
                                    )
                                    expected_computer_squared = (
                                        expected_computer
                                        + 2.0 * expected_computer_pairs
                                    )
                                    computer_pairs_without_direct_hit = (
                                        non_direct_population * expected_computer
                                        - (
                                            expected_computer_squared
                                            + expected_computer
                                        )
                                        / 2.0
                                    )
                                    ultra_bounded += (
                                        computer_pairs_without_direct_hit
                                        / pair_denominator
                                    )
                                elif remaining_disposables == 1:
                                    ultra_bounded += (
                                        expected_computer_disposable_pairs
                                        / pair_denominator
                                    )

                            if sequenced:
                                first_order = 1.0
                                quick_enabled = 1.0
                                bounded = 1.0
                            else:
                                first_order = max(quick_first, ultra_first)
                                quick_enabled = max(quick_bounded, ultra_first)
                                bounded = max(quick_bounded, ultra_bounded)

                            increment = bounded - first_order
                            metrics["state_mass"] += mass
                            metrics["target_prized_probability"] += mass * target_prized
                            metrics["sequenced_forest_seal_access"] += mass * sequenced
                            metrics["first_order_dark_asset_access"] += mass * first_order
                            metrics["bounded_followup_access"] += mass * bounded
                            metrics["quick_enabled_access"] += mass * quick_enabled
                            metrics["incremental_target_in_deck_access"] += (
                                mass * increment * target_in_deck
                            )
                            metrics["incremental_target_prized_access"] += (
                                mass * increment * target_prized
                            )
                            metrics["target_prized_first_order_access"] += (
                                mass * target_prized * first_order
                            )
                            metrics["target_prized_bounded_followup_access"] += (
                                mass * target_prized * bounded
                            )

    first_order = metrics["first_order_dark_asset_access"]
    quick_enabled = metrics["quick_enabled_access"]
    bounded = metrics["bounded_followup_access"]
    return DarkAssetFollowupResult(
        valid_opening_probability=accepted,
        incremental_followup_access=bounded - first_order,
        quick_followup_gain=quick_enabled - first_order,
        ultra_followup_gain_after_quick=bounded - quick_enabled,
        **metrics,
    )
