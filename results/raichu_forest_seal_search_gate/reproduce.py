"""Reproduce and independently validate Forest Seal Stone search-to-gate access."""

from __future__ import annotations

from itertools import combinations
from math import isclose

from raichu_forest_seal_search_gate import (
    ForestSealSearchGateResult,
    forest_seal_search_gate_snapshot,
)


def pct(value: float) -> str:
    return f"{100 * value:.6f}%"


def labeled_small_case() -> dict[str, float]:
    cards = (
        "target",
        "gladion",
        "ultra",
        "computer",
        "forest-seal",
        "quick",
        "crobat",
        "disposable",
        "giratina",
        "starter",
        "other-1",
        "other-2",
        "other-3",
    )
    starters = {"crobat", "giratina", "starter"}
    disposables = {"disposable", "giratina"}

    accepted_openings = [
        opening
        for opening in combinations(cards, 3)
        if any(card in starters for card in opening)
    ]

    out = {
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
        prize_subsets = list(combinations(remaining_after_opening, 2))
        prize_weight = 1 / len(prize_subsets)

        for prize_tuple in prize_subsets:
            prizes = set(prize_tuple)
            post_prize = [
                card
                for card in remaining_after_opening
                if card not in prizes
            ]
            draw_weight = 1 / len(post_prize)

            for drawn in post_prize:
                hand = hand_after_setup | {drawn}
                deck = set(post_prize) - {drawn}
                mass = opening_weight * prize_weight * draw_weight

                target_in_hand = "target" in hand
                target_prized = "target" in prizes
                target_in_deck = "target" in deck
                gladion_in_hand = "gladion" in hand
                gladion_in_deck = "gladion" in deck
                ultra_in_hand = "ultra" in hand
                computer_in_hand = "computer" in hand
                forest_seal_in_hand = "forest-seal" in hand
                quick_in_hand = "quick" in hand
                crobat_available = crobat_in_play or "crobat" in hand
                crobat_in_deck = "crobat" in deck
                disposable_count = len(disposables & hand)

                ultra_payable = disposable_count >= 1
                quick_payable = disposable_count >= 1

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
                ultra_gate_route = (
                    forest_seal_in_hand
                    and ultra_in_hand
                    and ultra_payable
                    and crobat_in_deck
                    and target_prized
                    and gladion_in_deck
                )

                direct_plus_quick = direct_access or quick_gate_route
                direct_plus_ultra = direct_access or ultra_gate_route
                full_search_gate = (
                    direct_access or quick_gate_route or ultra_gate_route
                )
                ungated = baseline or (
                    forest_seal_in_hand and seal_output_works
                )

                flags = {
                    "baseline_access": baseline,
                    "direct_ready_access": direct_access,
                    "direct_plus_quick_access": direct_plus_quick,
                    "direct_plus_ultra_gate_access": direct_plus_ultra,
                    "full_search_gate_access": full_search_gate,
                    "quick_gate_route_probability": quick_gate_route,
                    "ultra_gate_route_probability": ultra_gate_route,
                    "ungated_forest_seal_access": ungated,
                }

                out["state_mass"] += mass
                out["target_prized_probability"] += mass * target_prized
                for key, value in flags.items():
                    out[key] += mass * value

                if target_prized:
                    out["target_prized_baseline_access"] += mass * baseline
                    out["target_prized_direct_ready_access"] += (
                        mass * direct_access
                    )
                    out["target_prized_direct_plus_quick_access"] += (
                        mass * direct_plus_quick
                    )
                    out["target_prized_direct_plus_ultra_gate_access"] += (
                        mass * direct_plus_ultra
                    )
                    out["target_prized_full_search_gate_access"] += (
                        mass * full_search_gate
                    )

    return out


def assert_matches(
    result: ForestSealSearchGateResult,
    expected: dict[str, float],
) -> None:
    for key, value in expected.items():
        actual = getattr(result, key)
        assert isclose(actual, value, rel_tol=0.0, abs_tol=3e-12), (
            key,
            actual,
            value,
        )


def main() -> None:
    baseline = forest_seal_search_gate_snapshot()

    assert isclose(baseline.state_mass, 1.0, rel_tol=0.0, abs_tol=2e-11)
    assert isclose(
        baseline.valid_opening_probability,
        0.9007771067385328,
        rel_tol=0.0,
        abs_tol=1e-15,
    )
    assert isclose(
        baseline.target_prized_probability,
        0.10052903453442029,
        rel_tol=0.0,
        abs_tol=2e-12,
    )
    assert isclose(
        baseline.baseline_access,
        0.3057870025712963,
        rel_tol=0.0,
        abs_tol=2e-11,
    )
    assert isclose(
        baseline.direct_ready_access,
        0.3313953260000798,
        rel_tol=0.0,
        abs_tol=2e-11,
    )
    assert isclose(
        baseline.direct_plus_quick_access,
        0.3439307767615541,
        rel_tol=0.0,
        abs_tol=2e-11,
    )
    assert isclose(
        baseline.direct_plus_ultra_gate_access,
        0.3322683466064587,
        rel_tol=0.0,
        abs_tol=2e-11,
    )
    assert isclose(
        baseline.full_search_gate_access,
        0.34466609151855604,
        rel_tol=0.0,
        abs_tol=2e-11,
    )
    assert isclose(
        baseline.ungated_forest_seal_access,
        0.40261571348155,
        rel_tol=0.0,
        abs_tol=2e-11,
    )
    assert isclose(
        baseline.conditional_target_prized_full_search_gate_access,
        0.3382501206699865,
        rel_tol=0.0,
        abs_tol=2e-11,
    )

    print("Harto Forest Seal Stone search-to-gate access")
    print("corrected baseline:", pct(baseline.baseline_access))
    print("direct-ready Forest Seal:", pct(baseline.direct_ready_access))
    print("+ Quick Ball gate completion:", pct(baseline.direct_plus_quick_access))
    print(
        "+ Ultra Ball gate completion:",
        pct(baseline.direct_plus_ultra_gate_access),
    )
    print("all typed gate routes:", pct(baseline.full_search_gate_access))
    print("Quick Ball marginal over direct:", pct(baseline.quick_marginal_over_direct))
    print("Ultra Ball marginal over direct:", pct(baseline.ultra_marginal_over_direct))
    print(
        "Ultra Ball residual after Quick Ball:",
        pct(baseline.ultra_residual_after_quick),
    )
    print(
        "total search-to-gate gain over direct:",
        pct(baseline.search_gate_gain_over_direct),
    )
    print("total gain over corrected baseline:", pct(baseline.total_gain_over_baseline))
    print("ungated Forest Seal ceiling:", pct(baseline.ungated_forest_seal_access))
    print("remaining gap to ungated:", pct(baseline.remaining_gap_to_ungated))
    print(
        "Prized-target full typed access:",
        pct(baseline.conditional_target_prized_full_search_gate_access),
    )

    exact_small = forest_seal_search_gate_snapshot(
        deck_size=13,
        prize_count=2,
        opening_hand_size=3,
        extra_random_draws=1,
        gladion_copies=1,
        ultra_ball_copies=1,
        computer_search_copies=1,
        forest_seal_copies=1,
        quick_ball_copies=1,
        crobat_v_copies=1,
        disposable_nonstarter_copies=1,
        disposable_starter_copies=1,
        other_starter_copies=1,
        ultra_discard_cost=1,
        quick_discard_cost=1,
    )
    exhaustive = labeled_small_case()
    assert_matches(exact_small, exhaustive)
    assert isclose(exact_small.state_mass, 1.0, abs_tol=1e-12)
    print("\nIndependent labeled-card exhaustive regression: PASS")
    print("small-case full typed access:", pct(exact_small.full_search_gate_access))


if __name__ == "__main__":
    main()
