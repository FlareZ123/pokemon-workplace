"""Nonanticipative Energy payment coverage for an unknown future attack cost.

Future cost is revealed either before or after choosing which two Basics
to discard from DDE plus a three-Basic attachment state.
"""
from __future__ import annotations

import json
from collections import Counter
from itertools import combinations_with_replacement
from math import comb
from pathlib import Path
from typing import Any

from tools.energy_discard_colorless_cost_extension import COLORS, pays_attack_cost
from tools.energy_discard_continuation_frontier import _load_card
from tools.energy_discard_solver import ENERGY_TYPES


def evaluate_state(
    types: tuple[str, str, str],
    costs: list[tuple[str, ...]],
) -> dict[str, int]:
    dde = {"units": 2, "types": list(ENERGY_TYPES)}
    basics = [{"units": 1, "types": [kind]} for kind in types]
    keep_options = sorted(set(types))
    one_payment_ready = sum(pays_attack_cost(basics, cost) for cost in costs)
    fixed_results = {
        kind: sum(pays_attack_cost([dde, {"units": 1, "types": [kind]}], cost)
                  for cost in costs)
        for kind in keep_options
    }
    clairvoyant = sum(
        any(pays_attack_cost([dde, {"units": 1, "types": [kind]}], cost)
            for kind in keep_options)
        for cost in costs
    )
    distinct = len(keep_options)
    expected_clairvoyant = len(costs) - comb(len(COLORS) - distinct + 2, 3)
    expected_basic = {1: 4, 2: 6, 3: 8}[distinct]
    assert one_payment_ready == expected_basic, types
    assert all(count == 100 for count in fixed_results.values()), types
    assert clairvoyant == expected_clairvoyant, types
    return {
        "distinct_basic_colors": distinct,
        "discard_dde_coverage": one_payment_ready,
        "retain_dde_fixed_basic_coverage": max(fixed_results.values()),
        "retain_dde_clairvoyant_coverage": clairvoyant,
        "information_advantage_cost_signatures": clairvoyant - max(fixed_results.values()),
    }


def build(resources_root: Path) -> dict[str, Any]:
    card = _load_card(resources_root, "xy6-97")
    assert card["name"] == "Double Dragon Energy"
    assert "provides every type of Energy" in " ".join(card.get("rules") or ())
    assert "provides only 2 Energy at a time" in " ".join(card.get("rules") or ())

    costs = list(combinations_with_replacement(ENERGY_TYPES, 3))
    mixes = list(combinations_with_replacement(COLORS, 3))
    assert len(costs) == 220
    assert len(mixes) == 165

    group = {d: Counter() for d in (1, 2, 3)}
    for types in mixes:
        row = evaluate_state(types, costs)
        bucket = group[row["distinct_basic_colors"]]
        bucket["mixtures"] += 1
        for field in (
            "discard_dde_coverage",
            "retain_dde_fixed_basic_coverage",
            "retain_dde_clairvoyant_coverage",
            "information_advantage_cost_signatures",
        ):
            bucket[field + "_aggregate"] += row[field]

    expected = {
        1: (9, 4, 100, 100, 0),
        2: (72, 6, 100, 136, 36),
        3: (84, 8, 100, 164, 64),
    }
    for distinct, (number, discarded, fixed, clairvoyant, advantage) in expected.items():
        c = group[distinct]
        assert c["mixtures"] == number
        assert c["discard_dde_coverage_aggregate"] == number * discarded
        assert c["retain_dde_fixed_basic_coverage_aggregate"] == number * fixed
        assert c["retain_dde_clairvoyant_coverage_aggregate"] == number * clairvoyant
        assert c["information_advantage_cost_signatures_aggregate"] == number * advantage

    return {
        "cost_signature_count": len(costs),
        "basic_mixture_count": len(mixes),
        "per_distinct_basic_type_count": {
            str(d): {
                "mixtures": expected[d][0],
                "discard_dde_coverage": expected[d][1],
                "fixed_payment_coverage": expected[d][2],
                "clairvoyant_coverage": expected[d][3],
                "cost_signature_gap": expected[d][4],
            }
            for d in (1, 2, 3)
        },
        "uniform_cost_prior_only": True,
        "validation": "all 165 Basic type multisets and 220 cost signatures per multiset",
    }


if __name__ == "__main__":
    print(json.dumps(build(Path("resources")), indent=2))
