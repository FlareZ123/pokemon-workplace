"""Exhaustive tiny decision matrices plus published Regidrago application."""

from fractions import Fraction as F
from itertools import product
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from first_action_information_value import (
    ActionWorld, evaluate_first_action_information,
)
from regidrago_joint_launch import candidates
from regidrago_joint_launch_k0 import analyze_k0


def oracle(states, actions, weights):
    full = sum(
        (weights[i] for i, winners in enumerate(states) if winners), F(),
    ) / sum(weights)
    policies = [
        sum(
            (weights[i] for i, winners in enumerate(states) if action in winners),
            F(),
        ) / sum(weights)
        for action in actions
    ]
    return full, max(policies)


def exhaustive():
    cases = 0
    zero_gap = 0
    positive_gap = 0
    for n in range(1, 4):
        actions = tuple(chr(65+i) for i in range(n))
        legal_winner_sets = tuple(
            frozenset(
                action for bit, action in enumerate(actions) if mask & (1 << bit)
            )
            for mask in range(1 << n)
        )
        for sets in product(legal_winner_sets, repeat=3):
            weights = (F(1), F(2), F(3))
            decision = evaluate_first_action_information(
                (ActionWorld(weight, winners)
                 for weight, winners in zip(weights, sets)),
                legal_first_actions=actions,
            )
            full, limited = oracle(sets, actions, weights)
            assert (decision.clairvoyant, decision.nonanticipative) == (
                full, limited,
            )
            supporting_winners = [set_ for set_ in sets if set_]
            common = set.intersection(*map(set, supporting_winners)) if supporting_winners else set(actions)
            assert (decision.universal_winning_action is not None) == bool(common)
            assert decision.information_gap == full - limited
            zero_gap += decision.information_gap == 0
            positive_gap += decision.information_gap > 0
            cases += 1
    assert cases == 584
    assert zero_gap and positive_gap
    print("PASS exhaustive 584 asymmetric-weight decision matrices")
    print("no-gap", zero_gap, "positive-gap", positive_gap)


def targeted():
    uncertain = evaluate_first_action_information(
        (
            ActionWorld(F(1, 2), frozenset(("VIP",))),
            ActionWorld(F(1, 2), frozenset(("Treasure",))),
        ),
        legal_first_actions=("VIP", "Treasure"),
    )
    assert uncertain.clairvoyant == 1
    assert uncertain.nonanticipative == F(1, 2)
    assert uncertain.information_gap == F(1, 2)
    assert uncertain.universal_winning_action is None

    sufficient = evaluate_first_action_information(
        (
            ActionWorld(F(1, 2), frozenset(("VIP", "Treasure"))),
            ActionWorld(F(1, 2), frozenset(("Treasure",))),
        ),
        legal_first_actions=("VIP", "Treasure"),
    )
    assert sufficient.clairvoyant == sufficient.nonanticipative == 1
    assert sufficient.universal_winning_action == "Treasure"

    for bad_worlds, actions in (
        ((ActionWorld(F(-1), frozenset(("A",))),), ("A",)),
        ((ActionWorld(F(0), frozenset(("A",))),), ("A",)),
        ((ActionWorld(F(1), frozenset(("B",))),), ("A",)),
        ((ActionWorld(F(1), frozenset(("A",))),), ()),
    ):
        try:
            evaluate_first_action_information(
                bad_worlds, legal_first_actions=actions,
            )
        except ValueError:
            continue
        raise AssertionError("invalid hidden-world action model accepted")
    print("PASS contested-payoff toy value of information = 1/2")


def published():
    for safe in (0, 10):
        for label, build in candidates(safe).items():
            outcome = analyze_k0(build)
            assert outcome["information_gap"] == 0, (safe, label)
            assert outcome["clairvoyant_joint"] == outcome["k0_joint"]
        print(f"PASS K0 Regidrago first-action null gap across five builds at D={safe}")


if __name__ == "__main__":
    exhaustive()
    targeted()
    published()
