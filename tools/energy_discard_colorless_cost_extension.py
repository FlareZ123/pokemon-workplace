"""Colorless attack-cost extension of the DDE discard continuation theorem.

Colorless *attack costs* can be met by any provided Energy unit. This
intentionally differs from strict named Energy-type matching for effects.
"""
from __future__ import annotations

import json
from collections import Counter
from itertools import combinations_with_replacement
from typing import Any

from tools.energy_discard_solver import ENERGY_TYPES, max_typed_match

COLORS = tuple(t for t in ENERGY_TYPES if t != "Colorless")
C = "Colorless"


def pays_attack_cost(cards: list[dict[str, Any]], attack_cost: tuple[str, ...]) -> bool:
    """Reuse strict matching with an attack-cost-only Colorless wildcard.

    Every provided Energy unit can satisfy a Colorless cost symbol, so add
    Colorless to that unit's accepted symbols. Do *not* use this wrapper for
    effects that require specific typed Energy (e.g., discard Fire Energy).
    """
    transformed = []
    for card in cards:
        types = set(card["types"])
        types.add(C)
        transformed.append({"units": card["units"], "types": list(types)})
    return max_typed_match(transformed, list(attack_cost)) == len(attack_cost)


def verify_colorless_extension() -> dict[str, object]:
    demands = list(combinations_with_replacement(ENERGY_TYPES, 3))
    mixtures = list(combinations_with_replacement(COLORS, 3))
    assert len(demands) == 220
    assert len(mixtures) == 165
    assert not pays_attack_cost([{"units": 1, "types": ["Grass"]}], ("Fire",))
    assert pays_attack_cost([{"units": 1, "types": ["Grass"]}], (C,))
    assert max_typed_match([{"units": 1, "types": ["Grass"]}], [C]) == 0

    by_colorless: dict[str, Counter[str]] = {str(k): Counter() for k in range(4)}
    for cost in demands:
        bucket = by_colorless[str(cost.count(C))]
        bucket["cost_signatures"] += 1
        for triple in mixtures:
            basics = [{"units": 1, "types": [t]} for t in triple]
            dde = {"units": 2, "types": list(ENERGY_TYPES)}
            initial = pays_attack_cost([dde, *basics], cost)
            after_dde = pays_attack_cost(basics, cost)
            after_two_basics = any(pays_attack_cost([dde, basic], cost) for basic in basics)
            assert initial == after_two_basics, (cost, triple)
            if initial:
                bucket["initial_ready"] += 1
                if after_dde:
                    bucket["one_card_preserves"] += 1
                else:
                    bucket["one_card_loses_but_two_basics_preserve"] += 1

    expected = {
        "0": (165, 15393, 165, 15228),
        "1": (45, 7425, 405, 7020),
        "2": (9, 1485, 405, 1080),
        "3": (1, 165, 165, 0),
    }
    for k, (costs, initial, preserves, reversals) in expected.items():
        c = by_colorless[k]
        assert (c["cost_signatures"], c["initial_ready"], c["one_card_preserves"],
                c["one_card_loses_but_two_basics_preserve"]) == (
                    costs, initial, preserves, reversals
                )
    return {
        "total_cost_signatures": len(demands),
        "total_basic_type_mixes": len(mixtures),
        "total_cost_mix_pairs": len(demands) * len(mixtures),
        "initial_ready_pairs": sum(c["initial_ready"] for c in by_colorless.values()),
        "continuation_reversal_pairs": sum(
            c["one_card_loses_but_two_basics_preserve"] for c in by_colorless.values()
        ),
        "by_colorless_symbols": {k: dict(v) for k, v in by_colorless.items()},
    }


if __name__ == "__main__":
    print(json.dumps(verify_colorless_extension(), indent=2))
