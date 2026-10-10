"""Exact type-multiset theorem for multi-unit Energy discard continuations.

A controlled abstract model: one active two-unit every-type Energy and
three Basic Energy cards. The copied attack discards two generic Energy
units; the next attack needs three non-Colorless typed Energy units.
"""
from __future__ import annotations

from collections import Counter
from itertools import combinations_with_replacement
from math import comb

from tools.energy_discard_solver import ENERGY_TYPES, max_typed_match

BASIC_TYPES = tuple(t for t in ENERGY_TYPES if t != "Colorless")


def expected_initial_ready(support_size: int) -> int:
    """Unordered Basic triples meeting a three-colored-unit cost with DDE."""
    return comb(len(BASIC_TYPES) + 2, 3) - comb(len(BASIC_TYPES) - support_size + 2, 3)


def exhaustive_proof() -> dict[str, object]:
    demands = list(combinations_with_replacement(BASIC_TYPES, 3))
    mixes = list(combinations_with_replacement(BASIC_TYPES, 3))
    assert len(demands) == len(mixes) == 165

    by_support: dict[int, Counter[str]] = {d: Counter() for d in (1, 2, 3)}
    all_cases = 0
    for goal in demands:
        signature = len(set(goal))
        counter = by_support[signature]
        count_ready = 0
        count_exact = 0
        count_reversal = 0
        for triple in mixes:
            cards = [
                {"units": 2, "types": ENERGY_TYPES},
                *({"units": 1, "types": [kind]} for kind in triple),
            ]
            active_ready = max_typed_match(cards, list(goal)) == 3
            after_dde = max_typed_match(cards[1:], list(goal)) == 3
            two_basic_preserves = any(
                max_typed_match([cards[0], cards[i]], list(goal)) == 3
                for i in range(1, 4)
            )
            assert active_ready == any(kind in goal for kind in triple)
            assert after_dde == (tuple(triple) == tuple(goal))
            assert two_basic_preserves == active_ready
            if active_ready:
                count_ready += 1
                if after_dde:
                    count_exact += 1
                else:
                    assert two_basic_preserves
                    count_reversal += 1
            all_cases += 1
        assert count_ready == expected_initial_ready(signature)
        assert count_exact == 1
        assert count_reversal == count_ready - 1
        counter["cost_signatures"] += 1
        counter["initial_ready_cases"] += count_ready
        counter["one_card_retains_next_attack"] += count_exact
        counter["one_card_loses_but_two_basic_retains"] += count_reversal

    assert by_support[1]["cost_signatures"] == 9
    assert by_support[2]["cost_signatures"] == 72
    assert by_support[3]["cost_signatures"] == 84
    assert all_cases == 27_225
    return {
        "demand_signature_count": len(demands),
        "attachment_type_mix_count": len(mixes),
        "all_cost_mix_pairs_tested": all_cases,
        "by_distinct_required_types": {
            str(d): dict(by_support[d]) for d in (1, 2, 3)
        },
        "total_initial_ready_cases": sum(c["initial_ready_cases"] for c in by_support.values()),
        "total_minimum_card_continuation_reversals": sum(
            c["one_card_loses_but_two_basic_retains"] for c in by_support.values()
        ),
    }


if __name__ == "__main__":
    import json

    print(json.dumps(exhaustive_proof(), indent=2))
