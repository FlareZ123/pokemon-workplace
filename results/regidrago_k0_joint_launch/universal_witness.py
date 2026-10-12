"""Independent first-action intersection certificates over all Regidrago hands."""

from collections import Counter
from fractions import Fraction
from itertools import product
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from first_action_information_value import (
    ActionWorld, evaluate_first_action_information,
)
from regidrago_joint_launch import (
    analyze, candidates, can_achieve_joint, choose,
)
from regidrago_joint_launch_k0 import (
    analyze_k0, first_action_succeeds, first_actions,
)


def certify(build):
    all_others = build.total - sum((
        build.regidrago_v, build.other_basics, build.dragapult,
        build.vip, build.quick_ball, build.treasure, build.compressor,
        build.safe,
    ))
    groups = (
        build.regidrago_v, build.other_basics, build.dragapult,
        build.vip, build.quick_ball, build.treasure,
        build.compressor, build.safe, all_others,
    )
    seen_hands = 0
    winnable_hands = 0
    winners_intersection = Counter()
    total_mass = 0
    k0_mass = 0
    oracle_mass = 0
    universal_failures = []

    for partial in product(*(range(min(n, 8) + 1) for n in groups[:-1])):
        leftover = 8 - sum(partial)
        if not 0 <= leftover <= all_others:
            continue
        hand = (*partial, leftover)
        basics = hand[0] + hand[1]
        placements = 8 if basics >= 2 else 7 if basics == 1 else 0
        if not placements:
            continue
        hand_ways = placements
        for n, selected in zip(groups, hand):
            hand_ways *= choose(n, selected)
        unknown_rv = build.regidrago_v - hand[0]
        unknown_dp = build.dragapult - hand[2]
        remaining = build.total - 8 - unknown_rv - unknown_dp
        actions = first_actions(hand)
        if not actions:
            # A hand may be Basic-valid yet have no playable modeled Item.
            total_mass += hand_ways * choose(build.total - 8, 6)
            continue

        seen_hands += 1
        worlds = []
        for r in range(min(6, unknown_rv) + 1):
            for d in range(min(6-r, unknown_dp) + 1):
                ways = (choose(unknown_rv, r) * choose(unknown_dp, d)
                        * choose(remaining, 6-r-d))
                if not ways:
                    continue
                remaining_rv = unknown_rv - r
                remaining_dp = unknown_dp - d
                oracle = can_achieve_joint(
                    hand[0] > 0, hand[2], hand[3], hand[4],
                    hand[5], hand[6], hand[7],
                    remaining_rv, remaining_dp, False,
                )
                winners = frozenset(
                    action for action in actions
                    if first_action_succeeds(
                        action, hand, rv_deck=remaining_rv,
                        dp_deck=remaining_dp,
                    )
                )
                assert bool(winners) == oracle
                worlds.append(ActionWorld(Fraction(ways), winners))
        value = evaluate_first_action_information(
            worlds, legal_first_actions=actions,
        )
        if value.clairvoyant:
            winnable_hands += 1
            if value.universal_winning_action is None:
                universal_failures.append((hand, worlds))
            else:
                winners_intersection[value.universal_winning_action] += 1

        prize_mass = sum(w.probability for w in worlds)
        total_mass += hand_ways * prize_mass
        oracle_mass += hand_ways * prize_mass * value.clairvoyant
        k0_mass += hand_ways * prize_mass * value.nonanticipative

    assert not universal_failures, universal_failures[:3]
    result = analyze_k0(build)
    # The denominator also includes Basic-valid hands that have no modeled
    # Item first action, which cannot reach the endpoint.
    assert Fraction(k0_mass, total_mass) == result["k0_joint"]
    assert Fraction(oracle_mass, total_mass) == result["clairvoyant_joint"]
    assert Fraction(oracle_mass, total_mass) == analyze(build)["joint_any"]
    return seen_hands, winnable_hands, dict(winners_intersection)


def main():
    for label, build in (
        ("published", candidates(0)["published"]),
        ("+Dragapult -VIP", candidates(0)["+Dragapult -VIP"]),
    ):
        seen, winnable, witnesses = certify(build)
        print(label, "nonempty legal Item hands:", seen)
        print(label, "winnable observable hands:", winnable)
        print(label, "first-action universal witness classes:", witnesses)
        print("PASS no K0 first-action regret for every winnable hand")

if __name__ == "__main__":
    main()
