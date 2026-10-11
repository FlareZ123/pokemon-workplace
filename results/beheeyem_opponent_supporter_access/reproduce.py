"""Exact test of opponent's Supporter access, Prize gate, and public signal."""
from fractions import Fraction
from itertools import combinations
import json
from math import comb
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
from beheeyem_opponent_supporter_access import (
    probability_not_seen,opponent_supporter_access,optimal_reply_with_access
)
from beheeyem_physical_tutor import MODES


def brute_toy() -> Fraction:
    """Independent full permutation-class enumeration of toy Prize/draw union."""
    cards = tuple(range(10))  # Basics 0..2, named Supporters 3..4.
    total = missing = 0
    for hand in combinations(cards,3):
        if not any(v < 3 for v in hand):
            continue
        leftover = tuple(v for v in cards if v not in hand)
        for prizes in combinations(leftover,2):
            deck = tuple(v for v in leftover if v not in prizes)
            for draw in combinations(deck,1):
                for reward in combinations(prizes,1):
                    total += 1
                    seen = set(hand+draw+reward)
                    missing += not any(v in seen for v in (3,4))
    assert total == 17850
    return Fraction(missing,total)


def run() -> dict:
    assert brute_toy() == probability_not_seen(
        3,2,1,1,deck_size=10,opener=3,starting_prizes=2
    )
    assert probability_not_seen(12,0,2,0) == 1
    assert probability_not_seen(12,4,2,0) == Fraction(
        33168688,62752371
    )
    seen = opponent_supporter_access(12,4,4,2,0)
    assert sum(seen.values()) == 1
    assert seen["ace_only"] + seen["both"] == Fraction(
        29583683,62752371
    )
    assert seen["neither"] > 0 and seen["both"] > 0

    report = []
    for r,q in ((0,6),(1,6),(1,5),(2,6),(2,5),(2,4)):
        z = optimal_reply_with_access(4,4,1,"computer_search",r,q,12,4,4,2)
        report.append({
            "beheeyem_prizes_taken":r,
            "opponent_prizes_remaining":q,
            "chance_seen_ace_percent":round(100*float(z["chance_seen_ace"]),8),
            "no_reset_joint_percent":round(100*float(z["no_hand_reset_joint"]),8),
            "aggregate_policy_joint_percent":round(
                100*float(z["optimal_aggregate_joint"]),8
            ),
            "public_tutor_policy_joint_percent":round(
                100*float(z["optimal_public_tutor_signal_joint"]),8
            )
        })
        assert z["signal_value"] >= 0
        if (r,q) in ((0,6),(1,5),(2,4)):
            assert z["signal_value"] == 0
    assert optimal_reply_with_access(
        4,4,1,"computer_search",1,6,12,4,4,2
    )["optimal_aggregate_joint"] == Fraction(
        59977412074,5327705077695
    )
    assert optimal_reply_with_access(
        4,4,1,"computer_search",1,6,12,4,4,2
    )["optimal_public_tutor_signal_joint"] == Fraction(
        96932786442777275968258,8899913430268088056203375
    )
    assert optimal_reply_with_access(
        4,4,1,"computer_search",2,4,12,4,4,2
    )["signal_value"] == 0

    configs = 0
    positive_aggregate = positive_signal = 0
    for B in range(1,5):
        for T in range(1,5):
            for tutor in MODES:
                for d in range(6):
                    for r in range(3):
                        z = optimal_reply_with_access(
                            B,T,d,tutor,r,6,12,4,4,2
                        )
                        assert (
                            z["optimal_public_tutor_signal_joint"]
                            <= z["optimal_aggregate_joint"]
                            <= z["no_hand_reset_joint"]
                        )
                        positive_aggregate += (
                            z["optimal_aggregate_joint"] <
                            z["no_hand_reset_joint"]
                        )
                        positive_signal += z["signal_value"] > 0
                        configs += 1
    assert configs == 1152
    return {
        "toy_physical_enumeration":str(brute_toy()),
        "exact_grid_configurations":configs,
        "instances_access_reduces_packet_success":positive_aggregate,
        "instances_public_route_signal_improves_response":positive_signal,
        "representative":report
    }


if __name__ == "__main__":
    print(json.dumps(run(),indent=2))
