"""First-order Crobat V Dark Asset value after search-to-Crobat actions.

This component extends the exact Harto Miki Raichu search-to-Forest-Seal model.
It allows Quick Ball or, when Alolan Raichu is known Prized, Ultra Ball to search
a deck-resident Crobat V, play it from hand, and use Dark Asset immediately.
Only the direct cards drawn by Dark Asset are credited: Alolan Raichu, Gladion,
or Forest Seal Stone. Secondary search connectors drawn by Dark Asset remain
outside this first-order layer.
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
class DarkAssetSearchResult:
    state_mass: float
    valid_opening_probability: float
    target_prized_probability: float
    sequenced_forest_seal_access: float
    dark_asset_access: float
    incremental_dark_asset_access: float
    incremental_quick_dark_asset_access: float
    incremental_ultra_dark_asset_access: float
    quick_dark_asset_candidate_probability: float
    ultra_dark_asset_candidate_probability: float
    incremental_target_in_deck_access: float
    incremental_target_prized_access: float
    target_prized_sequenced_access: float
    target_prized_dark_asset_access: float

    @property
    def conditional_target_prized_sequenced_access(self) -> float:
        if self.target_prized_probability == 0.0:
            return 1.0
        return self.target_prized_sequenced_access / self.target_prized_probability

    @property
    def conditional_target_prized_dark_asset_access(self) -> float:
        if self.target_prized_probability == 0.0:
            return 1.0
        return self.target_prized_dark_asset_access / self.target_prized_probability


def _hit_probability(population: int, good: int, draws: int) -> float:
    if draws <= 0 or good <= 0:
        return 0.0
    if good >= population:
        return 1.0
    return 1.0 - _choose(population - good, draws) / _choose(population, draws)


def dark_asset_search_snapshot(
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
) -> DarkAssetSearchResult:
    """Return exact first-order Dark Asset access after one ordinary draw."""

    counts = (
        gladion_copies, ultra_ball_copies, computer_search_copies,
        forest_seal_copies, crobat_v_copies, quick_ball_copies,
        disposable_nonstarter_copies, disposable_starter_copies,
        other_starter_copies, quick_ball_discard_cost, two_card_discard_cost,
    )
    if deck_size <= 0:
        raise ValueError("deck_size must be positive")
    if opening_hand_size < 0 or prize_count < 0:
        raise ValueError("opening and Prize counts must be non-negative")
    if opening_hand_size + prize_count + 2 > deck_size:
        raise ValueError("deck is too small for setup, Prizes, search, and draw")
    if min(counts) < 0:
        raise ValueError("card counts and discard costs must be non-negative")

    target_copies = 1
    starter_cards = crobat_v_copies + disposable_starter_copies + other_starter_copies
    if starter_cards <= 0:
        raise ValueError("at least one setup-eligible starter is required")

    used = (
        target_copies + gladion_copies + ultra_ball_copies + computer_search_copies
        + forest_seal_copies + crobat_v_copies + quick_ball_copies
        + disposable_nonstarter_copies + disposable_starter_copies
        + other_starter_copies
    )
    if used > deck_size:
        raise ValueError("modeled categories exceed deck size")

    sizes = (
        target_copies, gladion_copies, ultra_ball_copies, computer_search_copies,
        forest_seal_copies, crobat_v_copies, quick_ball_copies,
        disposable_nonstarter_copies, disposable_starter_copies,
        other_starter_copies, deck_size - used,
    )
    accepted = accepted_opening_probability(deck_size, starter_cards, opening_hand_size)
    if accepted == 0.0:
        raise ValueError("valid-opening conditioning event has zero probability")

    metrics = {
        "state_mass": 0.0,
        "target_prized_probability": 0.0,
        "sequenced_forest_seal_access": 0.0,
        "dark_asset_access": 0.0,
        "incremental_dark_asset_access": 0.0,
        "incremental_quick_dark_asset_access": 0.0,
        "incremental_ultra_dark_asset_access": 0.0,
        "quick_dark_asset_candidate_probability": 0.0,
        "ultra_dark_asset_candidate_probability": 0.0,
        "incremental_target_in_deck_access": 0.0,
        "incremental_target_prized_access": 0.0,
        "target_prized_sequenced_access": 0.0,
        "target_prized_dark_asset_access": 0.0,
    }

    draw_pool_size = deck_size - opening_hand_size
    prize_pool_size = draw_pool_size - 1
    prize_denominator = _choose(prize_pool_size, prize_count)
    post_search_deck_size = deck_size - opening_hand_size - 1 - prize_count - 1

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

            for tp in range(min(target_pool, prize_count) + 1):
                for gp in range(min(gladion_pool, prize_count) + 1):
                    for fp in range(min(fss_pool, prize_count) + 1):
                        for cp in range(min(crobat_pool, prize_count) + 1):
                            named = tp + gp + fp + cp
                            op = prize_count - named
                            ways = (
                                _choose(target_pool, tp)
                                * _choose(gladion_pool, gp)
                                * _choose(fss_pool, fp)
                                * _choose(crobat_pool, cp)
                                * _choose(other_pool, op)
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
                                target_in_deck and two_payable and (ultra_in_hand or computer_in_hand)
                            ) or (
                                target_prized and (
                                    gladion_in_hand
                                    or (two_payable and computer_in_hand and gladion_in_deck > 0)
                                )
                            )
                            seal_output_works = target_in_deck or (target_prized and gladion_in_deck > 0)
                            direct_ready = baseline or (fss_in_hand and crobat_available and seal_output_works)
                            quick_gate = (
                                fss_in_hand and not crobat_available and crobat_in_deck
                                and quick_in_hand and quick_payable and seal_output_works
                            )
                            ultra_gate = (
                                fss_in_hand and not crobat_available and crobat_in_deck
                                and ultra_in_hand and two_payable and target_prized
                                and gladion_in_deck > 0
                            )
                            sequenced = direct_ready or quick_gate or ultra_gate

                            quick_candidate = quick_in_hand and quick_payable and crobat_in_deck
                            ultra_candidate = (
                                target_prized and ultra_in_hand and two_payable and crobat_in_deck
                            )

                            quick_success = 0.0
                            if quick_candidate:
                                if target_in_deck:
                                    quick_success = _hit_probability(
                                        post_search_deck_size,
                                        int(target_in_deck) + fss_in_deck,
                                        1,
                                    )
                                elif target_prized and gladion_in_deck > 0:
                                    quick_success = _hit_probability(
                                        post_search_deck_size,
                                        gladion_in_deck + fss_in_deck,
                                        1,
                                    )

                            ultra_success = 0.0
                            if ultra_candidate and gladion_in_deck > 0:
                                ultra_success = _hit_probability(
                                    post_search_deck_size,
                                    gladion_in_deck + fss_in_deck,
                                    2,
                                )

                            if sequenced:
                                dark_success = 1.0
                                quick_increment = 0.0
                                ultra_increment = 0.0
                            elif ultra_success >= quick_success:
                                dark_success = ultra_success
                                quick_increment = 0.0
                                ultra_increment = ultra_success
                            else:
                                dark_success = quick_success
                                quick_increment = quick_success
                                ultra_increment = 0.0

                            increment = dark_success - float(sequenced)
                            metrics["state_mass"] += mass
                            metrics["target_prized_probability"] += mass * target_prized
                            metrics["sequenced_forest_seal_access"] += mass * sequenced
                            metrics["dark_asset_access"] += mass * dark_success
                            metrics["incremental_dark_asset_access"] += mass * increment
                            metrics["incremental_quick_dark_asset_access"] += mass * quick_increment
                            metrics["incremental_ultra_dark_asset_access"] += mass * ultra_increment
                            metrics["quick_dark_asset_candidate_probability"] += mass * quick_candidate
                            metrics["ultra_dark_asset_candidate_probability"] += mass * ultra_candidate
                            metrics["incremental_target_in_deck_access"] += mass * increment * target_in_deck
                            metrics["incremental_target_prized_access"] += mass * increment * target_prized
                            metrics["target_prized_sequenced_access"] += mass * target_prized * sequenced
                            metrics["target_prized_dark_asset_access"] += mass * target_prized * dark_success

    return DarkAssetSearchResult(valid_opening_probability=accepted, **metrics)
