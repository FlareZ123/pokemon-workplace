"""Reproduce and independently validate the Harto Raichu access result."""

from __future__ import annotations

from itertools import combinations
from math import comb, isclose

from raichu_prize_access import RaichuAccessResult, raichu_access_snapshot


def pct(value: float) -> str:
    return f"{100 * value:.6f}%"


def labeled_small_case() -> dict[str, float]:
    cards = (
        "target",
        "gladion",
        "ultra",
        "computer",
        "disposable-1",
        "disposable-2",
        "starter-1",
        "starter-2",
        "other-1",
        "other-2",
    )
    starters = {"starter-1", "starter-2"}
    disposables = {"disposable-1", "disposable-2"}
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
        "ultra_plus_gladion_gated_access": 0.0,
        "static_computer_gated_access": 0.0,
        "adaptive_computer_gated_access": 0.0,
        "adaptive_computer_no_cost_access": 0.0,
        "target_prized_static_access": 0.0,
        "target_prized_adaptive_access": 0.0,
    }

    opening_weight = 1 / len(accepted_openings)
    for opening_tuple in accepted_openings:
        opening = set(opening_tuple)
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
                hand = opening | {drawn}
                deck = set(post_prize) - {drawn}
                mass = opening_weight * prize_weight * draw_weight

                target_in_hand = "target" in hand
                target_prized = "target" in prizes
                target_in_deck = "target" in deck
                gladion_in_hand = "gladion" in hand
                gladion_in_deck = "gladion" in deck
                ultra_in_hand = "ultra" in hand
                computer_in_hand = "computer" in hand
                payable = len(disposables & hand) >= 1

                ultra_plus_gladion = target_in_hand or (
                    target_in_deck and payable and ultra_in_hand
                ) or (target_prized and gladion_in_hand)
                static_computer = target_in_hand or (
                    target_in_deck
                    and payable
                    and (ultra_in_hand or computer_in_hand)
                ) or (target_prized and gladion_in_hand)
                adaptive_computer = target_in_hand or (
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
                adaptive_no_cost = target_in_hand or (
                    target_in_deck and (ultra_in_hand or computer_in_hand)
                ) or (
                    target_prized
                    and (
                        gladion_in_hand
                        or (computer_in_hand and gladion_in_deck)
                    )
                )

                out["state_mass"] += mass
                out["target_prized_probability"] += mass * target_prized
                out["target_in_exposed_hand_probability"] += mass * target_in_hand
                out["connector_payable_probability"] += mass * payable
                out["ultra_plus_gladion_gated_access"] += mass * ultra_plus_gladion
                out["static_computer_gated_access"] += mass * static_computer
                out["adaptive_computer_gated_access"] += mass * adaptive_computer
                out["adaptive_computer_no_cost_access"] += mass * adaptive_no_cost
                if target_prized:
                    out["target_prized_static_access"] += mass * static_computer
                    out["target_prized_adaptive_access"] += mass * adaptive_computer

    return out


def assert_result_matches_dict(result: RaichuAccessResult, expected: dict[str, float]) -> None:
    for key, value in expected.items():
        actual = getattr(result, key)
        assert isclose(actual, value, rel_tol=0.0, abs_tol=1e-12), (key, actual, value)


def main() -> None:
    baseline = raichu_access_snapshot(extra_random_draws=1, disposable_cards=12)
    assert isclose(baseline.state_mass, 1.0, rel_tol=0.0, abs_tol=1e-11)
    assert isclose(baseline.valid_opening_probability, 0.9007771067385328, abs_tol=1e-15)
    assert isclose(baseline.target_prized_probability, 0.10052903453464862, abs_tol=1e-12)
    assert isclose(baseline.adaptive_computer_gated_access, 0.305787002572374, abs_tol=1e-12)
    assert isclose(baseline.conditional_target_prized_adaptive_access, 0.2920900027948247, abs_tol=1e-12)

    print("Harto direct-access baseline after one random draw")
    print("valid opening:", pct(baseline.valid_opening_probability))
    print("singleton Raichu Prized:", pct(baseline.target_prized_probability))
    print("Raichu already exposed in hand:", pct(baseline.target_in_exposed_hand_probability))
    print("2-card connector cost payable from modeled pool:", pct(baseline.connector_payable_probability))
    print("Ultra Ball + direct Gladion:", pct(baseline.ultra_plus_gladion_gated_access))
    print("+ Computer Search as static target search:", pct(baseline.static_computer_gated_access))
    print("+ zone-adaptive Computer Search:", pct(baseline.adaptive_computer_gated_access))
    print("zone-adaptive no-cost ceiling:", pct(baseline.adaptive_computer_no_cost_access))
    print("adaptive gain over static Computer Search:", pct(baseline.adaptive_gain_over_static))
    print("total Computer Search gain:", pct(baseline.total_computer_gain))
    print("modeled discard-gate loss:", pct(baseline.discard_gate_loss))
    print("Prized-target static access:", pct(baseline.conditional_target_prized_static_access))
    print("Prized-target adaptive access:", pct(baseline.conditional_target_prized_adaptive_access))

    print("\nRandom-exposure sensitivity")
    for draws in range(4):
        result = raichu_access_snapshot(extra_random_draws=draws, disposable_cards=12)
        print(
            draws,
            pct(result.target_in_exposed_hand_probability),
            pct(result.ultra_plus_gladion_gated_access),
            pct(result.adaptive_computer_gated_access),
            pct(result.conditional_target_prized_adaptive_access),
        )

    print("\nDiscard-pool sensitivity after one random draw")
    for disposable in (8, 11, 12, 15, 20):
        result = raichu_access_snapshot(extra_random_draws=1, disposable_cards=disposable)
        print(
            disposable,
            pct(result.connector_payable_probability),
            pct(result.adaptive_computer_gated_access),
            pct(result.conditional_target_prized_adaptive_access),
        )

    exact_small = raichu_access_snapshot(
        deck_size=10,
        prize_count=2,
        opening_hand_size=3,
        extra_random_draws=1,
        starter_cards=2,
        gladion_copies=1,
        ultra_ball_copies=1,
        computer_search_copies=1,
        disposable_cards=2,
        discard_cost=1,
    )
    exhaustive = labeled_small_case()
    assert_result_matches_dict(exact_small, exhaustive)
    assert isclose(exact_small.state_mass, 1.0, abs_tol=1e-12)
    print("\nIndependent labeled-card exhaustive regression: PASS")
    print("small-case adaptive access:", pct(exact_small.adaptive_computer_gated_access))


if __name__ == "__main__":
    main()
