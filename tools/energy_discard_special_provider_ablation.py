"""Matched two-unit Special Energy provider ablation for three-cost continuations.

Compare Double Dragon Energy (two every-type units) with Double Colorless
Energy (two Colorless-only units), each plus three single-type Basics.
"""
from __future__ import annotations

import json
from collections import Counter
from itertools import combinations_with_replacement
from pathlib import Path
from typing import Any

from tools.energy_discard_colorless_cost_extension import COLORS, pays_attack_cost
from tools.energy_discard_continuation_frontier import _load_card
from tools.energy_discard_solver import ENERGY_TYPES


def build(resources_root: Path) -> dict[str, Any]:
    dde = _load_card(resources_root, "xy6-97")
    dce = _load_card(resources_root, "bw4-92")
    assert dde["name"] == "Double Dragon Energy"
    assert dce["name"] == "Double Colorless Energy"
    assert "provides every type of Energy" in " ".join(dde.get("rules") or ())
    assert "provides only 2 Energy at a time" in " ".join(dde.get("rules") or ())
    assert "provides ColorlessColorless Energy" in " ".join(dce.get("rules") or ())

    costs = list(combinations_with_replacement(ENERGY_TYPES, 3))
    basics = list(combinations_with_replacement(COLORS, 3))
    count = Counter()
    for cost in costs:
        for types in basics:
            basic_cards = [{"units": 1, "types": [t]} for t in types]
            dde_cards = [{"units": 2, "types": list(ENERGY_TYPES)}, *basic_cards]
            dce_cards = [{"units": 2, "types": ["Colorless"]}, *basic_cards]

            basic_ready = pays_attack_cost(basic_cards, cost)
            double_colorless_ready = pays_attack_cost(dce_cards, cost)
            double_dragon_ready = pays_attack_cost(dde_cards, cost)
            # Two Colorless units cannot add new three-unit attack-cost
            # solutions when three Basic cards already supply three units.
            assert double_colorless_ready == basic_ready, (cost, types)
            assert not double_colorless_ready or double_dragon_ready

            if double_dragon_ready:
                assert any(
                    pays_attack_cost([dde_cards[0], basic], cost)
                    for basic in basic_cards
                ), (cost, types)
            count["total_pairs"] += 1
            count["dde_initially_ready"] += int(double_dragon_ready)
            count["dce_initially_ready"] += int(double_colorless_ready)
            count["basics_only_ready"] += int(basic_ready)
            count["dde_extra_readiness"] += int(double_dragon_ready and not basic_ready)
            count["dde_min_card_discard_breaks_readiness"] += int(
                double_dragon_ready and not basic_ready
            )
            count["dce_min_card_discard_breaks_readiness"] += int(
                double_colorless_ready and not basic_ready
            )

    expected = {
        "total_pairs": 36300,
        "dde_initially_ready": 24468,
        "dce_initially_ready": 1140,
        "basics_only_ready": 1140,
        "dde_extra_readiness": 23328,
        "dde_min_card_discard_breaks_readiness": 23328,
        "dce_min_card_discard_breaks_readiness": 0,
    }
    assert dict(count) == expected, (count, expected)
    return {
        "cards": {"double_dragon": "xy6-97", "double_colorless": "bw4-92"},
        "scope": "one conditional two-unit provider + three Basic Energy; three attack-cost symbols",
        "result": dict(count),
        "identity": "DCE initially ready iff Basics alone ready; DDE additional readiness iff lost by discarding DDE",
    }


if __name__ == "__main__":
    print(json.dumps(build(Path("resources")), indent=2))
