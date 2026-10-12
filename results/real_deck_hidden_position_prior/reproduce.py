"""Regidrago 60-card population: independent labeled-card exhaustive oracle."""

from collections import Counter
from fractions import Fraction as F
from itertools import product
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from exact_three_position_group_prior import (
    exact_three_position_group_masses,
    exact_three_position_hand_belief,
)
from prize_hand_copy_budget import condition_joint_hand_on_copy_budget
from prize_unknown_hand_composition import ObserverLatentHandCompositionBeliefs

MANIFEST = ROOT / "results/regidrago_aichi_top10_playable/yoshioka_regidrago_2026.json"


def deck_groups():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    counts = Counter()
    for entries in manifest["groups"].values():
        for entry in entries:
            counts[entry["name"]] += entry["count"]
    assert sum(counts.values()) == 60
    assert counts["Prime Catcher"] == 1
    assert counts["Quick Ball"] == 3
    return {"P": 1, "Q": 3, "O": 56}


def conditional_top(masses, observed):
    evidence = F(0)
    top_group_mass = Counter()
    for (top, tag, other), prior in masses.items():
        for outcome in (tag, other):
            if outcome == observed:
                weight = prior / 2
                evidence += weight
                top_group_mass[top] += weight
    return evidence, {
        group: top_group_mass[group] / evidence
        for group in ("P", "Q", "O")
    }


def independent_labeled_oracle(groups):
    """Enumerate every ordered triple of distinct physical card indices."""
    copies = [group for group, n in groups.items() for _ in range(n)]
    witness = Counter()
    observations = Counter()
    for i, top in enumerate(copies):
        for j, tag in enumerate(copies):
            if i == j:
                continue
            for k, other in enumerate(copies):
                if k == i or k == j:
                    continue
                witness[(top, tag, other)] += 1
                for discard in (tag, other):
                    if discard == "Q":
                        observations[top] += 1
    total = len(copies) * (len(copies) - 1) * (len(copies) - 2)
    return (
        {triple: F(m, total) for triple, m in witness.items()},
        {group: F(observations[group], sum(observations.values()))
         for group in groups},
    )


def copy_filtered_iid(groups):
    """Common but insufficient approximation: iid draws pruned by capacity."""
    mass = {}
    for triple in product(groups, repeat=3):
        required = Counter(triple)
        if all(required[g] <= groups[g] for g in groups):
            top, tag, other = triple
            mass[triple] = F(groups[top] * groups[tag] * groups[other], 60 ** 3)
    evidence = sum(mass.values())
    return evidence, {triple: p / evidence for triple, p in mass.items()}


def check(actual, expected):
    assert abs(actual - float(expected)) < 1e-12, (actual, expected)


def main():
    groups = deck_groups()
    prior = exact_three_position_group_masses(groups)
    independently_counted, observed_truth = independent_labeled_oracle(groups)
    assert prior == independently_counted
    evidence, correct = conditional_top(prior, "Q")
    assert evidence == F(1, 20)
    assert correct == {"P": F(1, 59), "Q": F(2, 59), "O": F(56, 59)}
    assert correct == observed_truth

    belief = exact_three_position_hand_belief(groups)
    assert belief.groups == ("P", "Q", "O")
    for (top, _prizes, tag, others), p in belief.masses:
        other = belief.groups[others.index(1)]
        check(p, prior[(top, tag, other)])

    # The exact prior is already copy-feasible. A copy ceiling doesn't
    # recover the true multiplicity weights from an iid approximation.
    observer = ObserverLatentHandCompositionBeliefs((("opponent", belief),))
    same = condition_joint_hand_on_copy_budget(
        observer, total_deck_copies=groups,
    ).belief_for("opponent")
    for (top, _prizes, tag, others), p in same.masses:
        other = belief.groups[others.index(1)]
        check(p, prior[(top, tag, other)])

    kept, iid_prior = copy_filtered_iid(groups)
    _, incorrect = conditional_top(iid_prior, "Q")
    assert kept == F(107911, 108000)
    assert incorrect["P"] == F(1, 61)
    assert incorrect["Q"] == F(180, 3599)
    assert incorrect["Q"] != correct["Q"]

    for invalid in ({}, {"P": 1, "Q": 1}, {"P": -1, "Q": 3}):
        try:
            exact_three_position_group_masses(invalid)
        except ValueError:
            pass
        else:
            raise AssertionError("invalid group counts accepted")

    print("Exact 60-card without-replacement top/tag/hand prior matches all")
    print("205,320 distinct physical triples and public-Q discard oracle")
    print("Correct P(top Q | public random Q discard) = 2/59")
    print("Capacity-pruned iid approximation = 180/3599")


if __name__ == "__main__":
    main()
