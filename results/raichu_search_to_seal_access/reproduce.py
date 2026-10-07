"""Reproduce and independently validate Raichu search-to-seal access."""

from __future__ import annotations

from itertools import combinations
from math import comb, isclose

from raichu_search_to_seal_access import (
    SearchToSealAccessResult,
    search_to_seal_access_snapshot,
)


def pct(value: float) -> str:
    return f"{100 * value:.6f}%"


def labeled_small_case() -> tuple[float, dict[str, float]]:
    """Exhaustively enumerate labeled opening, Prize, and draw partitions."""

    cards = (
        "target",
        "gladion",
        "ultra",
        "computer",
        "forest-seal",
        "crobat",
        "quick",
        "disposable-1",
        "disposable-2",
        "giratina",
        "starter",
        "other-1",
        "other-2",
    )
    starters = {"crobat", "giratina", "starter"}
    disposables = {"disposable-1", "disposable-2", "giratina"}

    all_openings = list(combinations(cards, 3))
    accepted_openings = [
        opening
        for opening in all_openings
        if any(card in starters for card in opening)
    ]
    valid_opening_probability = len(accepted_openings) / len(all_openings)

    keys = (
        "state_mass",
        "target_prized_probability",
        "baseline_access",
        "direct_ready_forest_seal_access",
        "sequenced_forest_seal_access",
        "ungated_forest_seal_access",
        "forest_seal_exposed_probability",
        "crobat_available_probability",
        "forest_seal_ready_probability",
        "quick_ball_exposed_probability",
        "one_card_discard_payable_probability",
        "two_card_discard_payable_probability",
        "quick_ball_gate_route_probability",
        "ultra_ball_pivot_route_probability",
        "incremental_quick_ball_access",
        "incremental_ultra_ball_access",
        "incremental_quick_low_cost_access",
        "incremental_target_in_deck_access",
        "incremental_target_prized_access",
        "target_prized_direct_ready_access",
        "target_prized_sequenced_access",
        "target_prized_ungated_access",
    )
    out = {key: 0.0 for key in keys}

    opening_weight = 1 / len(accepted_openings)
    for opening_tuple in accepted_openings:
        opening = set(opening_tuple)
        hand_after_setup = set(opening)
        crobat_in_play = False

        if "crobat" in hand_after_setup:
            hand_after_setup.remove("crobat")
            crobat_in_play = True
        elif "starter" in hand_after_setup:
            hand_after_setup.remove("starter")
        else:
            hand_after_setup.remove("giratina")

        remaining_after_opening = [card for card in cards if card not in opening]
        prize_sets = list(combinations(remaining_after_opening, 2))
        prize_weight = 1 / len(prize_sets)

        for prize_tuple in prize_sets:
            prizes = set(prize_tuple)
            remaining_after_prizes = [
                card for card in remaining_after_opening if card not in prizes
            ]
            draw_weight = 1 / len(remaining_after_prizes)

            for drawn in remaining_after_prizes:
                hand = hand_after_setup | {drawn}
                deck = set(remaining_after_prizes) - {drawn}
                mass = opening_weight * prize_weight * draw_weight

                target_in_hand = "target" in hand
                target_prized = "target" in prizes
                target_in_deck = "target" in deck
                gladion_in_hand = "gladion" in hand
                gladion_in_deck = "gladion" in deck
                ultra_in_hand = "ultra" in hand
                computer_in_hand = "computer" in hand
                forest_seal_exposed = "forest-seal" in hand
                crobat_available = crobat_in_play or "crobat" in hand
                crobat_in_deck = "crobat" in deck
                quick_ball_in_hand = "quick" in hand
                disposable_count = len(hand & disposables)
                quick_payable = disposable_count >= 1
                two_card_payable = disposable_count >= 2

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
                quick_route = (
                    forest_seal_exposed
                    and not crobat_available
                    and crobat_in_deck
                    and quick_ball_in_hand
                    and quick_payable
                    and seal_output_works
                )
                ultra_pivot = (
                    forest_seal_exposed
                    and not crobat_available
                    and crobat_in_deck
                    and ultra_in_hand
                    and two_card_payable
                    and target_prized
                    and gladion_in_deck
                )
                sequenced_access = direct_ready_access or quick_route or ultra_pivot
                incremental_quick = quick_route and not direct_ready_access
                incremental_ultra = (
                    ultra_pivot
                    and not direct_ready_access
                    and not quick_route
                )
                incremental = incremental_quick or incremental_ultra

                values = {
                    "state_mass": True,
                    "target_prized_probability": target_prized,
                    "baseline_access": baseline_access,
                    "direct_ready_forest_seal_access": direct_ready_access,
                    "sequenced_forest_seal_access": sequenced_access,
                    "ungated_forest_seal_access": ungated_access,
                    "forest_seal_exposed_probability": forest_seal_exposed,
                    "crobat_available_probability": crobat_available,
                    "forest_seal_ready_probability": forest_seal_ready,
                    "quick_ball_exposed_probability": quick_ball_in_hand,
                    "one_card_discard_payable_probability": quick_payable,
                    "two_card_discard_payable_probability": two_card_payable,
                    "quick_ball_gate_route_probability": quick_route,
                    "ultra_ball_pivot_route_probability": ultra_pivot,
                    "incremental_quick_ball_access": incremental_quick,
                    "incremental_ultra_ball_access": incremental_ultra,
                    "incremental_quick_low_cost_access": (
                        incremental_quick and not two_card_payable
                    ),
                    "incremental_target_in_deck_access": (
                        incremental and target_in_deck
                    ),
                    "incremental_target_prized_access": (
                        incremental and target_prized
                    ),
                    "target_prized_direct_ready_access": (
                        target_prized and direct_ready_access
                    ),
                    "target_prized_sequenced_access": (
                        target_prized and sequenced_access
                    ),
                    "target_prized_ungated_access": (
                        target_prized and ungated_access
                    ),
                }
                for key, value in values.items():
                    out[key] += mass * value

    return valid_opening_probability, out


def assert_result_matches_dict(
    result: SearchToSealAccessResult,
    expected: dict[str, float],
) -> None:
    for key, value in expected.items():
        actual = getattr(result, key)
        assert isclose(actual, value, rel_tol=0.0, abs_tol=2e-12), (
            key,
            actual,
            value,
        )


def main() -> None:
    baseline = search_to_seal_access_snapshot()
    assert isclose(baseline.state_mass, 1.0, rel_tol=0.0, abs_tol=3e-11)
    assert isclose(
        baseline.valid_opening_probability,
        0.9007771067385328,
        rel_tol=0.0,
        abs_tol=1e-15,
    )
    assert isclose(
        baseline.baseline_access,
        0.3057870025724347,
        rel_tol=0.0,
        abs_tol=3e-11,
    )
    assert isclose(
        baseline.direct_ready_forest_seal_access,
        0.33139532600127414,
        rel_tol=0.0,
        abs_tol=3e-11,
    )
    assert isclose(
        baseline.sequenced_forest_seal_access,
        0.3446660915198057,
        rel_tol=0.0,
        abs_tol=3e-11,
    )
    assert isclose(
        baseline.ungated_forest_seal_access,
        0.4026157134830411,
        rel_tol=0.0,
        abs_tol=3e-11,
    )
    assert isclose(
        baseline.incremental_quick_ball_access,
        0.01253545076152759,
        rel_tol=0.0,
        abs_tol=3e-11,
    )
    assert isclose(
        baseline.incremental_ultra_ball_access,
        0.0007353147570059185,
        rel_tol=0.0,
        abs_tol=3e-11,
    )
    assert isclose(
        baseline.incremental_quick_low_cost_access,
        0.007638312774364112,
        rel_tol=0.0,
        abs_tol=3e-11,
    )
    assert isclose(
        baseline.conditional_target_prized_sequenced_access,
        0.33825012066971866,
        rel_tol=0.0,
        abs_tol=3e-11,
    )

    print("Harto search-to-seal access after one random draw")
    print("valid opening:", pct(baseline.valid_opening_probability))
    print("direct baseline:", pct(baseline.baseline_access))
    print("direct-ready Forest Seal access:", pct(baseline.direct_ready_forest_seal_access))
    print("search-completed Forest Seal access:", pct(baseline.sequenced_forest_seal_access))
    print("search-to-gate gain:", pct(baseline.search_to_gate_gain))
    print("incremental Quick Ball route:", pct(baseline.incremental_quick_ball_access))
    print("incremental Ultra Ball pivot:", pct(baseline.incremental_ultra_ball_access))
    print("Quick Ball gain below the two-card discard threshold:", pct(baseline.incremental_quick_low_cost_access))
    print("remaining ungated overstatement:", pct(baseline.remaining_gate_overstatement))
    print("Prized-target direct-ready access:", pct(baseline.conditional_target_prized_direct_ready_access))
    print("Prized-target sequenced access:", pct(baseline.conditional_target_prized_sequenced_access))
    print("Prized-target ungated access:", pct(baseline.conditional_target_prized_ungated_access))

    exact_small = search_to_seal_access_snapshot(
        deck_size=13,
        prize_count=2,
        opening_hand_size=3,
        gladion_copies=1,
        ultra_ball_copies=1,
        computer_search_copies=1,
        forest_seal_copies=1,
        crobat_v_copies=1,
        quick_ball_copies=1,
        disposable_nonstarter_copies=2,
        disposable_starter_copies=1,
        other_starter_copies=1,
        quick_ball_discard_cost=1,
        two_card_discard_cost=2,
    )
    valid_opening_probability, exhaustive = labeled_small_case()
    assert isclose(
        exact_small.valid_opening_probability,
        valid_opening_probability,
        rel_tol=0.0,
        abs_tol=1e-12,
    )
    assert_result_matches_dict(exact_small, exhaustive)
    print("\nIndependent labeled-card exhaustive regression: PASS")
    print("small-case sequenced access:", pct(exact_small.sequenced_forest_seal_access))


if __name__ == "__main__":
    main()
