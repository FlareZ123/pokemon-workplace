"""Reproduce the full-state Harto backup-Gladion rescue result."""

from __future__ import annotations

from itertools import combinations
import json
from math import comb
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from raichu_backup_rescue_full_state import full_backup_rescue_snapshot


def brute_small() -> tuple[float, float, float, float, float]:
    labels = (
        "T", "G", "G", "C", "F", "V", "V", "Q", "D", "DS", "S", "O"
    )
    starters = {"V", "DS", "S"}
    openings = [
        set(x) for x in combinations(range(len(labels)), 3)
        if any(labels[i] in starters for i in x)
    ]
    state = branch = topology = immediate = final = 0.0

    for opening in openings:
        hand = set(opening)
        active = next((i for i in sorted(opening) if labels[i] == "V"), None)
        if active is None:
            active = next((i for i in sorted(opening) if labels[i] == "S"), None)
        if active is None:
            active = next(i for i in sorted(opening) if labels[i] == "DS")
        hand.remove(active)
        remaining = [i for i in range(len(labels)) if i not in opening]

        for draw in remaining:
            action_hand = hand | {draw}
            prize_pool = [i for i in remaining if i != draw]
            for prize_tuple in combinations(prize_pool, 2):
                prizes = set(prize_tuple)
                weight = 1 / len(openings) / len(remaining) / comb(len(prize_pool), 2)
                state += weight
                if sum(labels[i] == "T" for i in prizes) != 1:
                    continue

                q = next((i for i in action_hand if labels[i] == "Q"), None)
                g = next((i for i in action_hand if labels[i] == "G"), None)
                deck = set(prize_pool) - prizes
                v = next((i for i in deck if labels[i] == "V"), None)
                if q is None or g is None or v is None:
                    continue
                branch += weight

                post_hand = set(action_hand)
                post_hand.remove(q)
                post_hand.remove(g)
                post_deck = set(deck)
                post_deck.remove(v)

                backup_hand = any(labels[i] == "G" for i in post_hand)
                backup_deck = any(labels[i] == "G" for i in post_deck)
                if backup_hand or backup_deck:
                    topology += weight

                disposable = sum(labels[i] in {"D", "DS"} for i in post_hand)
                forest = any(labels[i] == "F" for i in post_hand)
                computer = any(labels[i] == "C" for i in post_hand)
                ready = backup_hand or (
                    backup_deck and (
                        forest or (computer and disposable >= 2)
                    )
                )
                if ready:
                    immediate += weight
                    final += weight
                    continue
                if not backup_deck:
                    continue

                for top in post_deck:
                    kind = labels[top]
                    backup_after = any(
                        labels[i] == "G" and i != top for i in post_deck
                    )
                    success = (
                        kind == "G"
                        or (kind == "F" and backup_after)
                        or (kind == "C" and backup_after and disposable >= 2)
                        or (
                            kind in {"D", "DS"}
                            and backup_after
                            and computer
                            and disposable + 1 >= 2
                        )
                    )
                    if success:
                        final += weight / len(post_deck)

    return state, branch, topology, immediate, final


def main() -> None:
    baseline = full_backup_rescue_snapshot()
    assert abs(baseline.state_mass - 1.0) < 1e-10
    assert abs(baseline.branch_mass - 0.005264458882838137) < 1e-11
    assert abs(baseline.conditional_topology_ceiling - 0.9064937166768233) < 1e-11
    assert abs(baseline.conditional_immediate_rescue - 0.160541131396378) < 1e-11
    assert abs(baseline.conditional_final_rescue - 0.20482909438273136) < 1e-11
    assert abs(baseline.conditional_draw_increment - 0.044287962986357975) < 1e-11

    no_forest = full_backup_rescue_snapshot(forest_seal_live=False)
    no_computer = full_backup_rescue_snapshot(computer_search_live=False)
    no_dark = full_backup_rescue_snapshot(dark_asset_live=False)
    assert abs(no_forest.conditional_final_rescue - 0.10723378083823927) < 1e-11
    assert abs(no_computer.conditional_final_rescue - 0.1717261456700121) < 1e-11
    assert abs(no_dark.conditional_final_rescue - 0.160541131396378) < 1e-11

    brute = brute_small()
    grouped = full_backup_rescue_snapshot(
        deck_size=12,
        prize_count=2,
        opening_hand_size=3,
        quick_ball_copies=1,
        disposable_nonstarter_copies=1,
        disposable_starter_copies=1,
        other_starter_copies=1,
    )
    checks = (
        grouped.state_mass,
        grouped.branch_mass,
        grouped.topology_ceiling_mass,
        grouped.immediate_rescue_mass,
        grouped.final_rescue_mass,
    )
    for left, right in zip(brute, checks):
        assert abs(left - right) < 1e-11

    assert abs(
        sum(baseline.conditional_attributions.values())
        - baseline.conditional_final_rescue
    ) < 1e-11

    print(json.dumps({
        "valid_opening_probability": baseline.valid_opening_probability,
        "branch_probability_given_valid_opening": baseline.branch_mass,
        "branch_probability_before_conditioning": (
            baseline.valid_opening_probability * baseline.branch_mass
        ),
        "backup_zone_given_branch": {
            "hand": baseline.conditional_backup_in_hand,
            "deck": baseline.conditional_backup_in_deck,
            "prizes": baseline.conditional_backup_prized,
        },
        "two_disposable_gate_given_branch": baseline.conditional_two_disposable,
        "topology_ceiling_given_branch": baseline.conditional_topology_ceiling,
        "rescue_before_dark_asset": baseline.conditional_immediate_rescue,
        "rescue_after_dark_asset": baseline.conditional_final_rescue,
        "dark_asset_increment": baseline.conditional_draw_increment,
        "topology_minus_rescue": baseline.conditional_topology_gap,
        "disjoint_attribution": baseline.conditional_attributions,
        "small_labeled_validation": True,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
