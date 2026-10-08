"""Reproduce and independently validate the Raichu K0 discard policy."""

from __future__ import annotations

from collections import defaultdict
from itertools import combinations
import json
from math import comb
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from raichu_k0_discard_policy import (
    k0_discard_policy_snapshot,
    visible_policy_choice,
)


def exhaustive_small() -> dict[str, float | int]:
    """Enumerate a labeled 15-card deck without using the grouped engine."""

    labels = (
        "T", "G", "G", "U", "C", "F", "V", "V", "Q",
        "D", "D", "DS", "S", "O", "O",
    )
    starter_kinds = {"V", "DS", "S"}
    openings = [
        set(x)
        for x in combinations(range(len(labels)), 3)
        if any(labels[index] in starter_kinds for index in x)
    ]

    observations: dict[tuple[str, tuple[int, ...]], list[float]] = defaultdict(
        lambda: [0.0, 0.0, 0.0]
    )
    state_mass = 0.0
    branch_mass = 0.0
    target_prized_mass = 0.0
    crobat_failure_mass = 0.0
    oracle_mass = 0.0

    kinds = ("T", "G", "U", "C", "F", "V", "Q", "D", "DS", "S", "O")

    def counts(indices: set[int]) -> tuple[int, ...]:
        return tuple(sum(labels[index] == kind for index in indices) for kind in kinds)

    def execute(
        action_hand: set[int],
        deck: set[int],
        choice: str,
    ) -> float:
        target_prized = not any(labels[index] == "T" for index in deck)
        crobat = next((index for index in deck if labels[index] == "V"), None)
        if crobat is None:
            return 0.0

        hand = set(action_hand)
        quick = next(index for index in hand if labels[index] == "Q")
        hand.remove(quick)

        if choice == "gladion":
            payment = next(index for index in hand if labels[index] == "G")
        else:
            payment = next(
                index for index in hand if labels[index] in {"D", "DS"}
            )
        hand.remove(payment)

        post_deck = set(deck)
        post_deck.remove(crobat)

        gladion_hand = any(labels[index] == "G" for index in hand)
        gladion_deck = any(labels[index] == "G" for index in post_deck)
        forest_hand = any(labels[index] == "F" for index in hand)
        ultra_hand = any(labels[index] == "U" for index in hand)
        computer_hand = any(labels[index] == "C" for index in hand)
        disposable = sum(labels[index] in {"D", "DS"} for index in hand)
        payable = disposable >= 2

        if not target_prized:
            immediate = forest_hand or (payable and (ultra_hand or computer_hand))
        else:
            immediate = gladion_hand or (
                gladion_deck and (forest_hand or (payable and computer_hand))
            )
        if immediate:
            return 1.0

        success = 0
        for top in post_deck:
            kind = labels[top]
            backup_after = any(
                labels[index] == "G" and index != top for index in post_deck
            )
            if not target_prized:
                top_success = (
                    kind == "T"
                    or kind == "F"
                    or (payable and kind in {"U", "C"})
                    or (
                        kind in {"D", "DS"}
                        and disposable == 1
                        and (ultra_hand or computer_hand)
                    )
                )
            else:
                top_success = (
                    kind == "G"
                    or (kind == "F" and backup_after)
                    or (kind == "C" and payable and backup_after)
                    or (
                        kind in {"D", "DS"}
                        and disposable == 1
                        and computer_hand
                        and backup_after
                    )
                )
            success += int(top_success)

        return success / len(post_deck)

    for opening in openings:
        visible_hand = set(opening)
        active = next(
            (index for index in sorted(opening) if labels[index] == "V"),
            None,
        )
        if active is None:
            active = next(
                (index for index in sorted(opening) if labels[index] == "S"),
                None,
            )
        if active is None:
            active = next(
                index for index in sorted(opening) if labels[index] == "DS"
            )
        active_kind = labels[active]
        visible_hand.remove(active)

        remaining = [index for index in range(len(labels)) if index not in opening]
        for draw in remaining:
            action_hand = visible_hand | {draw}
            prize_pool = [index for index in remaining if index != draw]
            base = 1 / len(openings) / len(remaining)

            for prize_tuple in combinations(prize_pool, 2):
                prizes = set(prize_tuple)
                mass = base / comb(len(prize_pool), 2)
                state_mass += mass

                hand_counts = counts(action_hand)
                if (
                    hand_counts[0] > 0
                    or hand_counts[6] < 1
                    or hand_counts[1] < 1
                    or hand_counts[7] + hand_counts[8] < 1
                ):
                    continue

                branch_mass += mass
                deck = set(prize_pool) - prizes
                target_prized = any(labels[index] == "T" for index in prizes)
                target_prized_mass += mass * target_prized
                if not any(labels[index] == "V" for index in deck):
                    crobat_failure_mass += mass

                gladion_value = execute(action_hand, deck, "gladion")
                disposable_value = execute(action_hand, deck, "disposable")
                observation = (active_kind, hand_counts)
                row = observations[observation]
                row[0] += mass
                row[1] += mass * gladion_value
                row[2] += mass * disposable_value
                oracle_mass += mass * max(gladion_value, disposable_value)

    fixed_gladion = sum(row[1] for row in observations.values())
    fixed_disposable = sum(row[2] for row in observations.values())
    optimal = sum(max(row[1], row[2]) for row in observations.values())

    policy_mass = 0.0
    for (_, hand), row in observations.items():
        choice = visible_policy_choice(hand)
        policy_mass += row[1] if choice == "gladion" else row[2]
    assert abs(policy_mass - optimal) < 1e-12

    return {
        "state_mass": state_mass,
        "branch_mass": branch_mass,
        "target_prized_mass": target_prized_mass,
        "crobat_failure_mass": crobat_failure_mass,
        "fixed_gladion_mass": fixed_gladion,
        "fixed_disposable_mass": fixed_disposable,
        "optimal_mass": optimal,
        "oracle_mass": oracle_mass,
        "observation_count": len(observations),
    }


def main() -> None:
    result = k0_discard_policy_snapshot()

    assert abs(result.state_mass - 1.0) < 1e-10
    assert abs(result.valid_opening_probability - 0.9007771067385328) < 1e-12
    assert abs(result.observable_branch_mass - 0.03616755972964512) < 1e-11
    assert abs(result.conditional_target_prized - 0.11538461538478578) < 1e-11
    assert abs(result.conditional_crobat_search_failure - 0.043430468174391265) < 1e-11
    assert abs(result.fixed_gladion_discard_success - 0.2805047173198911) < 1e-11
    assert abs(result.fixed_disposable_discard_success - 0.25868809645964835) < 1e-11
    assert abs(result.optimal_k0_success - 0.32988188974988253) < 1e-11
    assert abs(result.hidden_state_oracle_success - 0.36909665108233747) < 1e-11
    assert abs(result.oracle_advantage - 0.03921476133245494) < 1e-11
    assert result.observation_count == 1331
    assert result.choose_gladion_observations == 491
    assert result.choose_disposable_observations == 476
    assert result.tie_observations == 364

    choice_mass = result.conditional_choice_mass
    assert abs(choice_mass["discard_gladion"] - 0.28949682080249617) < 1e-11
    assert abs(choice_mass["discard_disposable"] - 0.6756822818207173) < 1e-11
    assert abs(choice_mass["tie"] - 0.034820897377264265) < 1e-11

    brute = exhaustive_small()
    grouped = k0_discard_policy_snapshot(
        deck_size=15,
        prize_count=2,
        opening_hand_size=3,
        ultra_ball_copies=1,
        quick_ball_copies=1,
        disposable_nonstarter_copies=2,
        disposable_starter_copies=1,
        other_starter_copies=1,
    )

    pairs = (
        (brute["state_mass"], grouped.state_mass),
        (brute["branch_mass"], grouped.observable_branch_mass),
        (brute["target_prized_mass"], grouped.target_prized_mass),
        (brute["crobat_failure_mass"], grouped.crobat_search_failure_mass),
        (brute["fixed_gladion_mass"], grouped.fixed_gladion_discard_success_mass),
        (brute["fixed_disposable_mass"], grouped.fixed_disposable_discard_success_mass),
        (brute["optimal_mass"], grouped.optimal_k0_success_mass),
        (brute["oracle_mass"], grouped.hidden_state_oracle_success_mass),
    )
    for left, right in pairs:
        assert abs(left - right) < 1e-11
    assert brute["observation_count"] == grouped.observation_count

    print(json.dumps({
        "valid_opening_probability": result.valid_opening_probability,
        "observable_branch_probability_given_valid_opening": (
            result.observable_branch_mass
        ),
        "target_prized_given_branch": result.conditional_target_prized,
        "crobat_search_failure_given_branch": (
            result.conditional_crobat_search_failure
        ),
        "fixed_gladion_discard_success": (
            result.fixed_gladion_discard_success
        ),
        "fixed_disposable_discard_success": (
            result.fixed_disposable_discard_success
        ),
        "optimal_k0_success": result.optimal_k0_success,
        "hidden_state_oracle_success": result.hidden_state_oracle_success,
        "oracle_advantage": result.oracle_advantage,
        "optimal_gain_over_fixed_gladion": (
            result.optimal_gain_over_fixed_gladion
        ),
        "optimal_gain_over_fixed_disposable": (
            result.optimal_gain_over_fixed_disposable
        ),
        "conditional_choice_mass": result.conditional_choice_mass,
        "observation_count": result.observation_count,
        "small_labeled_exhaustive_validation": True,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
