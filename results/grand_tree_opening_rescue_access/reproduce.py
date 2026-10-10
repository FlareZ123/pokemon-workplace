"""Independently enumerate small physical opening/Prize/draw worlds."""

from __future__ import annotations

import itertools
import json
import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from grand_tree_opening_rescue_access import OpeningRescueModel


def enumerate_physical(model: OpeningRescueModel) -> Fraction:
    labels = (
        ("B",) * model.basics
        + ("G",) * model.gladion
        + ("C",) * model.communication
        + ("T", "S1", "S2")
        + ("F",) * (
            model.total-model.basics-model.gladion-model.communication-3
        )
    )
    assert len(labels) == model.total
    universe = tuple(range(model.total))
    valid = 0
    success = 0
    for hand in itertools.combinations(universe, model.opening):
        H = {labels[i] for i in hand}
        if "B" not in H:
            continue
        hand_set = set(hand)
        in_hand = {
            label: sum(labels[i] == label for i in hand)
            for label in ("B", "G", "C", "T", "S1", "S2")
        }
        qualifies = (
            in_hand["B"] >= 1 and in_hand["G"] >= 1
            and in_hand["C"] >= 1 and in_hand["T"] == 1
            and in_hand["S1"] == 0 and in_hand["S2"] == 0
        )
        remaining = tuple(i for i in universe if i not in hand_set)
        for prizes in itertools.combinations(remaining, model.prizes):
            prizes_set = set(prizes)
            other = tuple(i for i in remaining if i not in prizes_set)
            for draws in itertools.combinations(other, model.draws):
                valid += 1
                if qualifies and (
                    sum(labels[i] == "S1" for i in prizes) == 1
                    and all(labels[i] != "S2" for i in prizes)
                    and all(labels[i] != "S2" for i in draws)
                ):
                    success += 1
    return Fraction(success, valid)


def main() -> None:
    models = [
        OpeningRescueModel(10,2,1,1,4,2,1),
        OpeningRescueModel(10,2,1,1,4,2,2),
        OpeningRescueModel(11,2,2,1,5,3,1),
        OpeningRescueModel(11,2,2,1,5,3,2),
        OpeningRescueModel(11,3,1,2,5,3,1),
        OpeningRescueModel(11,3,1,2,5,3,2),
        OpeningRescueModel(11,3,2,2,5,2,1),
        OpeningRescueModel(11,3,2,2,5,2,2),
        OpeningRescueModel(11,1,2,1,5,2,1),
        OpeningRescueModel(11,1,2,1,5,3,2),
    ]
    for m in models:
        calculated = m.probability()
        independent = enumerate_physical(m)
        assert calculated == independent, (m, calculated, independent)
    assert len(models) == 10

    p = {}
    for g in range(1,5):
        for c in range(1,5):
            model = OpeningRescueModel(gladion=g,communication=c)
            p[g,c] = model.probability()
            assert p[g,c] > 0
            assert model.qualifying_opening_hands() > 0
    assert p[4,4] > p[2,2] > p[1,1]
    assert p[1,4] == p[4,1]
    assert p[2,3] == p[3,2]

    for g,c in ((1,1),(2,2),(4,4)):
        print(
            "Gladion",g,"Communication",c,
            "P(event|Basic opener)", float(p[g,c]),
            "percent",float(p[g,c])*100,
        )
    print("tiny-world exact oracles",len(models))
    print("grand_tree_opening_rescue_access: PASS")


if __name__ == "__main__":
    main()
