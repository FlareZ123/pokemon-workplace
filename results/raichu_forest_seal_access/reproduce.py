"""Reproduce and independently validate the Raichu Forest Seal Stone result."""

from __future__ import annotations

from itertools import combinations
from math import isclose

from raichu_forest_seal_access import (
    ForestSealAccessResult,
    forest_seal_access_snapshot,
)


def pct(value: float) -> str:
    return f"{100 * value:.6f}%"


def labeled_small_case() -> dict[str, float]:
    """Enumerate a labeled deck without using the category-model helpers."""
    cards = (
        "target",
        "gladion",
        "ultra",
        "computer",
        "forest-seal",
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
        "target_in_exposed_hand_probability": 0.0,
        "connector_payable_probability": 0.0,
        "baseline_access": 0.0,
        "forest_seal_exposed_probability": 0.0,
        "crobat_available_probability": 0.0,
        "forest_seal_ready_probability": 0.0,
        "ungated_forest_seal_access": 0.0,
        "typed_forest_seal_access": 0.0,
        "target_prized_baseline_access": 0.0,
        "target_prized_ungated_access": 0.0,
        "target_prized_typed_access": 0.0,
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
                forest_seal_exposed = "forest-seal" in hand
                crobat_available = crobat_in_play or "crobat" in hand
                payable = len(disposables & hand) >= 1

                baseline_access = target_in_hand or (
                    target_in_deck
                    and payable
                    and (ultra_in_hand or computer_in_hand)
                ) or (
                    target_prized
                    and (
                        gladion_in_hand
                        or (
                            payable
                            and computer_in_hand
                            and gladion_in_deck
                        )
                    )
                )

                forest_seal_ready = forest_seal_exposed and crobat_available
                seal_output_works = target_in_deck or (
                    target_prized and gladion_in_deck
                )
                ungated_access = baseline_access or (
                    forest_seal_exposed and seal_output_works
                )
                typed_access = baseline_access or (
                    forest_seal_ready and seal_output_works
                )

                out["state_mass"] += mass
                out["target_prized_probability"] += mass * target_prized
                out["target_in_exposed_hand_probability"] += mass * target_in_hand
                out["connector_payable_probability"] += mass * payable
                out["baseline_access"] += mass * baseline_access
                out["forest_seal_exposed_probability"] += (
                    mass * forest_seal_exposed
                )
                out["crobat_available_probability"] += mass * crobat_available
                out["forest_seal_ready_probability"] += mass * forest_seal_ready
                out["ungated_forest_seal_access"] += mass * ungated_access
                out["typed_forest_seal_access"] += mass * typed_access

                if target_prized:
                    out["target_prized_baseline_access"] += mass * baseline_access
                    out["target_prized_ungated_access"] += mass * ungated_access
                    out["target_prized_typed_access"] += mass * typed_access

    return out


def assert_result_matches_dict(
    result: ForestSealAccessResult,
    expected: dict[str, float],
) -> None:
    for key, value in expected.items():
        actual = getattr(result, key)
        assert isclose(actual, value, rel_tol=0.0, abs_tol=1e-12), (
            key,
            actual,
            value,
        )


def main() -> None:
    baseline = forest_seal_access_snapshot()

    assert isclose(baseline.state_mass, 1.0, rel_tol=0.0, abs_tol=2e-11)
    assert isclose(
        baseline.valid_opening_probability,
        0.9007771067385328,
        rel_tol=0.0,
        abs_tol=1e-15,
    )
    assert isclose(
        baseline.target_prized_probability,
        0.10052903453439374,
        rel_tol=0.0,
        abs_tol=2e-12,
    )
    assert isclose(
        baseline.baseline_access,
        0.3057870025684789,
        rel_tol=0.0,
        abs_tol=2e-11,
    )
    assert isclose(
        baseline.forest_seal_ready_probability,
        0.032645446039442014,
        rel_tol=0.0,
        abs_tol=2e-11,
    )
    assert isclose(
        baseline.ungated_forest_seal_access,
        0.4026157134765699,
        rel_tol=0.0,
        abs_tol=2e-11,
    )
    assert isclose(
        baseline.typed_forest_seal_access,
        0.33139532599706956,
        rel_tol=0.0,
        abs_tol=2e-11,
    )
    assert isclose(
        baseline.gate_overstatement,
        0.07122038747950032,
        rel_tol=0.0,
        abs_tol=2e-11,
    )
    assert isclose(
        baseline.conditional_target_prized_typed_access,
        0.31781058639444677,
        rel_tol=0.0,
        abs_tol=2e-11,
    )

    print("Harto direct-ready Forest Seal Stone access after one random draw")
    print("valid opening:", pct(baseline.valid_opening_probability))
    print("singleton Raichu Prized:", pct(baseline.target_prized_probability))
    print("corrected baseline access:", pct(baseline.baseline_access))
    print("Forest Seal Stone exposed:", pct(baseline.forest_seal_exposed_probability))
    print("Crobat V available:", pct(baseline.crobat_available_probability))
    print("typed Forest Seal Stone ready:", pct(baseline.forest_seal_ready_probability))
    print("ungated Forest Seal Stone access:", pct(baseline.ungated_forest_seal_access))
    print("typed Forest Seal Stone access:", pct(baseline.typed_forest_seal_access))
    print("typed gain over baseline:", pct(baseline.typed_gain_over_baseline))
    print("gate overstatement:", pct(baseline.gate_overstatement))
    print(
        "Prized-target baseline access:",
        pct(baseline.conditional_target_prized_baseline_access),
    )
    print(
        "Prized-target typed Forest Seal access:",
        pct(baseline.conditional_target_prized_typed_access),
    )
    print(
        "Prized-target ungated Forest Seal access:",
        pct(baseline.conditional_target_prized_ungated_access),
    )

    exact_small = forest_seal_access_snapshot(
        deck_size=12,
        prize_count=2,
        opening_hand_size=3,
        extra_random_draws=1,
        gladion_copies=1,
        ultra_ball_copies=1,
        computer_search_copies=1,
        forest_seal_copies=1,
        crobat_v_copies=1,
        disposable_nonstarter_copies=1,
        disposable_starter_copies=1,
        other_starter_copies=1,
        discard_cost=1,
    )
    exhaustive = labeled_small_case()
    assert_result_matches_dict(exact_small, exhaustive)
    assert isclose(exact_small.state_mass, 1.0, abs_tol=1e-12)
    print("\nIndependent labeled-card exhaustive regression: PASS")
    print("small-case typed Forest Seal access:", pct(exact_small.typed_forest_seal_access))


if __name__ == "__main__":
    main()
