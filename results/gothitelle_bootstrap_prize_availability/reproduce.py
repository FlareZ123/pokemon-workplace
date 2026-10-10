"""Reproduce joint Prize-limited Gothitelle bootstrap availability."""

from __future__ import annotations

import itertools
import sys
from collections import Counter
from fractions import Fraction
from math import comb
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from gothitelle_bootstrap_prize_availability import EvolutionSupply
from stadium_entry_channels import StadiumCopy, StadiumEntryState
from stadium_gothitelle_bootstrap import BootstrapState, maximize_built
from stadium_reentry_usage_bounds import StadiumReentryState
from turn_action_budget import TurnActionBudget


def brute_distribution(model: EvolutionSupply) -> dict[int, Fraction]:
    """Independent exhaustive labeled six-Prize subsets in tiny decks."""
    labels = (
        ("stage1",) * model.stage1
        + ("stage2",) * model.stage2
        + ("other",) * (model.unseen - model.stage1 - model.stage2)
    )
    counts: Counter[int] = Counter()
    for positions in itertools.combinations(range(model.unseen), model.prizes):
        chosen = [labels[i] for i in positions]
        k = min(
            model.action_cap,
            model.stage1 - chosen.count("stage1"),
            model.stage2 - chosen.count("stage2"),
        )
        counts[k] += 1
    denom = comb(model.unseen, model.prizes)
    return dict(sorted((k, Fraction(v, denom)) for k, v in counts.items()))


def exhaustive_small_checks() -> int:
    tested = 0
    for unseen in range(4, 11):
        for stage1 in range(3):
            for stage2 in range(3):
                if stage1 + stage2 > unseen:
                    continue
                for prizes in range(min(unseen, 4) + 1):
                    for cap in range(4):
                        model = EvolutionSupply(unseen, prizes, stage1, stage2, cap)
                        assert model.outcome_distribution() == brute_distribution(model)
                        tested += 1
    return tested


def real_line_action_cap() -> int:
    """Derive the pre-Prize target bound from the actual bootstrap kernel."""
    base = BootstrapState(
        stadium=StadiumReentryState(
            StadiumEntryState(
                budget=TurnActionBudget(),
                in_play=StadiumCopy("tree", "Grand Tree"),
                hand=(StadiumCopy("brooklet", "Brooklet Hill"),),
                teleport_room_sources=frozenset({"old-goth"}),
            )
        ),
        ready=3,
    )
    count, _ = maximize_built(base, "entry", allow_play=True)
    assert count == 3
    return count


def main() -> None:
    tests = exhaustive_small_checks()
    assert tests > 900

    model = EvolutionSupply(
        unseen=52, prizes=6,
        stage1=3, stage2=3,
        action_cap=real_line_action_cap(),
    )
    distribution = model.outcome_distribution()
    assert distribution == {
        0: Fraction(36847, 20358520),
        1: Fraction(252333, 4071704),
        2: Fraction(9693189, 20358520),
        3: Fraction(1338117, 2908360),
    }
    assert model.expected_completed() == Fraction(2437425, 1017926)
    assert distribution[3] == model.probability_full_supply()
    assert model.incorrect_independence_product() > distribution[3]

    # With 8 known non-Prize cards, the remaining 52 physical copies are
    # initially symmetric. Six prize positions among those 52 may capture
    # the six still-needed evolution cards. The prior is conditional on the
    # known state, without search-policy or hand-selection conditioning.
    print("tiny exhaustive comparisons", tests)
    for k, p in distribution.items():
        print("new Gothitelle", k, "p", str(p), "decimal", f"{float(p):.10f}")
    print("expected", str(model.expected_completed()),
          f"{float(model.expected_completed()):.10f}")
    print("P(3) exact", f"{float(distribution[3]):.10f}")
    print("independence product", f"{float(model.incorrect_independence_product()):.10f}")
    print("gothitelle_bootstrap_prize_availability: PASS")


if __name__ == "__main__":
    main()
