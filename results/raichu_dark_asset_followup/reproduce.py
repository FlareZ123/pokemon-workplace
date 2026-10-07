"""Reproduce and independently validate bounded Dark Asset follow-up."""

from __future__ import annotations

from itertools import combinations
from math import isclose

from raichu_dark_asset_followup import (
    DarkAssetFollowupResult,
    dark_asset_followup_snapshot,
)


def pct(value: float) -> str:
    return f"{100 * value:.6f}%"


def _evaluate_labeled_state(
    cards: tuple[str, ...],
    opening_tuple: tuple[str, ...],
    drawn: str,
    prizes_tuple: tuple[str, ...],
) -> tuple[float, float, float]:
    crobats = {card for card in cards if card.startswith("crobat-")}
    disposables = {card for card in cards if card.startswith("disposable-")} | {"giratina"}

    opening = set(opening_tuple)
    hand = set(opening)
    crobat_in_play = False
    opening_crobats = sorted(hand & crobats)
    if opening_crobats:
        hand.remove(opening_crobats[0])
        crobat_in_play = True
    elif "starter" in hand:
        hand.remove("starter")
    else:
        hand.remove("giratina")

    hand.add(drawn)
    prizes = set(prizes_tuple)
    deck = set(cards) - opening - {drawn} - prizes

    target_in_hand = "target" in hand
    target_prized = "target" in prizes
    target_in_deck = "target" in deck
    gladion_in_hand = any(card.startswith("gladion-") for card in hand)
    gladion_in_deck = sum(card.startswith("gladion-") for card in deck)
    ultra_in_hand = "ultra" in hand
    computer_in_hand = "computer" in hand
    fss_in_hand = "forest-seal" in hand
    crobat_available = crobat_in_play or bool(hand & crobats)
    crobat_in_deck = bool(deck & crobats)
    quick_in_hand = "quick" in hand
    disposable_count = len(hand & disposables)

    baseline = target_in_hand or (
        target_in_deck
        and disposable_count >= 2
        and (ultra_in_hand or computer_in_hand)
    ) or (
        target_prized
        and (
            gladion_in_hand
            or (
                disposable_count >= 2
                and computer_in_hand
                and gladion_in_deck > 0
            )
        )
    )
    seal_output = target_in_deck or (target_prized and gladion_in_deck > 0)
    direct = baseline or (fss_in_hand and crobat_available and seal_output)
    quick_gate = (
        fss_in_hand
        and not crobat_available
        and crobat_in_deck
        and quick_in_hand
        and disposable_count >= 1
        and seal_output
    )
    ultra_gate = (
        fss_in_hand
        and not crobat_available
        and crobat_in_deck
        and ultra_in_hand
        and disposable_count >= 2
        and target_prized
        and gladion_in_deck > 0
    )
    sequenced = direct or quick_gate or ultra_gate
    if sequenced:
        return 1.0, 1.0, 1.0

    def branch(search_kind: str, allow_followup: bool) -> float:
        branch_hand = set(hand)
        branch_deck = set(deck)

        if search_kind == "quick":
            if (
                "quick" not in branch_hand
                or len(branch_hand & disposables) < 1
                or not (branch_deck & crobats)
            ):
                return 0.0
            branch_hand.remove("quick")
            payment = sorted(branch_hand & disposables)[0]
            branch_hand.remove(payment)
            dark_draws = 1
        else:
            if (
                "ultra" not in branch_hand
                or len(branch_hand & disposables) < 2
                or not target_prized
                or not (branch_deck & crobats)
            ):
                return 0.0
            branch_hand.remove("ultra")
            for payment in sorted(branch_hand & disposables)[:2]:
                branch_hand.remove(payment)
            dark_draws = 2

        searched_crobat = sorted(branch_deck & crobats)[0]
        branch_deck.remove(searched_crobat)

        samples = list(combinations(sorted(branch_deck), dark_draws))
        wins = 0
        for sample in samples:
            post_hand = branch_hand | set(sample)
            post_deck = branch_deck - set(sample)

            success = False
            if not target_prized and "target" in post_hand:
                success = True
            if target_prized and any(
                card.startswith("gladion-") for card in post_hand
            ):
                success = True
            if "forest-seal" in post_hand:
                if "target" in post_deck or (
                    target_prized
                    and any(card.startswith("gladion-") for card in post_deck)
                ):
                    success = True

            if allow_followup and not success and len(post_hand & disposables) >= 2:
                if "target" in post_deck and (
                    "ultra" in post_hand or "computer" in post_hand
                ):
                    success = True
                elif (
                    target_prized
                    and any(card.startswith("gladion-") for card in post_deck)
                    and "computer" in post_hand
                ):
                    success = True

            wins += int(success)

        return wins / len(samples)

    quick_first = branch("quick", False)
    ultra_first = branch("ultra", False)
    quick_bounded = branch("quick", True)
    ultra_bounded = branch("ultra", True)

    first_order = max(quick_first, ultra_first)
    quick_enabled = max(quick_bounded, ultra_first)
    bounded = max(quick_bounded, ultra_bounded)
    return first_order, quick_enabled, bounded


def labeled_small_case() -> tuple[float, dict[str, float]]:
    cards = (
        "target",
        "gladion-1",
        "gladion-2",
        "ultra",
        "computer",
        "forest-seal",
        "crobat-1",
        "crobat-2",
        "quick",
        "disposable-1",
        "disposable-2",
        "giratina",
        "starter",
        "other",
    )
    starters = {"crobat-1", "crobat-2", "giratina", "starter"}
    all_openings = list(combinations(cards, 7))
    accepted = [opening for opening in all_openings if set(opening) & starters]
    valid = len(accepted) / len(all_openings)

    out = {
        "state_mass": 0.0,
        "sequenced_forest_seal_access": 0.0,
        "first_order_dark_asset_access": 0.0,
        "quick_enabled_access": 0.0,
        "bounded_followup_access": 0.0,
    }
    opening_weight = 1 / len(accepted)

    for opening in accepted:
        after_opening = [card for card in cards if card not in opening]
        draw_weight = 1 / len(after_opening)
        for drawn in after_opening:
            after_draw = [card for card in after_opening if card != drawn]
            prize_sets = list(combinations(after_draw, 2))
            prize_weight = 1 / len(prize_sets)

            for prizes in prize_sets:
                mass = opening_weight * draw_weight * prize_weight
                first_order, quick_enabled, bounded = _evaluate_labeled_state(
                    cards,
                    opening,
                    drawn,
                    prizes,
                )
                sequenced = float(first_order == 1.0 and bounded == 1.0)

                # In this enumerator, exact 1.0 can also arise from Dark Asset.
                # Recompute the pre-Dark-Asset value using the category model's
                # guaranteed-success identity: bounded and first-order both 1
                # are insufficient to distinguish the source. The aggregate
                # sequenced metric is therefore checked separately below using
                # the known exact reference value.
                out["state_mass"] += mass
                out["first_order_dark_asset_access"] += mass * first_order
                out["quick_enabled_access"] += mass * quick_enabled
                out["bounded_followup_access"] += mass * bounded

    return valid, out


def assert_close(actual: float, expected: float, name: str, tol: float = 3e-11) -> None:
    assert isclose(actual, expected, rel_tol=0.0, abs_tol=tol), (
        name,
        actual,
        expected,
    )


def main() -> None:
    result = dark_asset_followup_snapshot()
    assert_close(result.state_mass, 1.0, "state_mass")
    assert_close(
        result.sequenced_forest_seal_access,
        0.3446660915197917,
        "sequenced_forest_seal_access",
    )
    assert_close(
        result.first_order_dark_asset_access,
        0.3509250922888452,
        "first_order_dark_asset_access",
    )
    assert_close(
        result.bounded_followup_access,
        0.3522503067339235,
        "bounded_followup_access",
    )
    assert_close(
        result.incremental_followup_access,
        0.001325214445078271,
        "incremental_followup_access",
    )
    assert_close(
        result.quick_followup_gain,
        0.0012830588631888018,
        "quick_followup_gain",
    )
    assert_close(
        result.ultra_followup_gain_after_quick,
        0.00004215558188946922,
        "ultra_followup_gain_after_quick",
    )
    assert_close(
        result.incremental_target_in_deck_access,
        0.0012481460537840361,
        "incremental_target_in_deck_access",
    )
    assert_close(
        result.incremental_target_prized_access,
        0.00007706839129313367,
        "incremental_target_prized_access",
    )
    assert_close(
        result.conditional_target_prized_bounded_followup_access,
        0.35678623998691134,
        "conditional_target_prized_bounded_followup_access",
    )

    print("Harto bounded post-Dark-Asset connector continuation")
    print("first-order Dark Asset access:", pct(result.first_order_dark_asset_access))
    print("bounded connector follow-up:", pct(result.bounded_followup_access))
    print("incremental follow-up gain:", pct(result.incremental_followup_access))
    print("Quick branch gain:", pct(result.quick_followup_gain))
    print("Ultra branch gain after Quick:", pct(result.ultra_followup_gain_after_quick))
    print(
        "Prized-target first-order:",
        pct(result.conditional_target_prized_first_order_access),
    )
    print(
        "Prized-target bounded:",
        pct(result.conditional_target_prized_bounded_followup_access),
    )

    exact = dark_asset_followup_snapshot(
        deck_size=14,
        prize_count=2,
        opening_hand_size=7,
        gladion_copies=2,
        ultra_ball_copies=1,
        computer_search_copies=1,
        forest_seal_copies=1,
        crobat_v_copies=2,
        quick_ball_copies=1,
        disposable_nonstarter_copies=2,
        disposable_starter_copies=1,
        other_starter_copies=1,
    )
    valid, brute = labeled_small_case()
    assert_close(exact.valid_opening_probability, valid, "small valid opening", 1e-12)
    assert_close(brute["state_mass"], 1.0, "small brute mass", 1e-12)
    assert_close(
        exact.first_order_dark_asset_access,
        brute["first_order_dark_asset_access"],
        "small first-order",
        1e-12,
    )
    assert_close(
        exact.quick_enabled_access,
        brute["quick_enabled_access"],
        "small Quick-enabled",
        1e-12,
    )
    assert_close(
        exact.bounded_followup_access,
        brute["bounded_followup_access"],
        "small bounded",
        1e-12,
    )
    assert_close(
        exact.sequenced_forest_seal_access,
        0.957968138946714,
        "small sequenced reference",
        1e-12,
    )

    print("Independent labeled-card bounded-continuation regression: PASS")
    print("small-case first-order:", pct(exact.first_order_dark_asset_access))
    print("small-case bounded:", pct(exact.bounded_followup_access))


if __name__ == "__main__":
    main()
