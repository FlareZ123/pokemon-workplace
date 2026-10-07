"""Reproduce Retreat Cost algebra and fixed-delta card-text catalog."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from retreat_cost_effect_catalog import build
from retreat_cost_semantics import (
    RetreatCostModifier,
    effective_retreat_cost,
    no_retreat_cost,
)


def main() -> None:
    report = build(ROOT / "resources")
    fixed = report["fixed"]["rows"]
    variable = report["variable"]["rows"]

    def delta(card_id: str) -> int:
        rows = [row for row in fixed if row["card_id"] == card_id]
        assert len(rows) == 1, (card_id, rows)
        return int(rows[0]["delta"])

    air_balloon = RetreatCostModifier(
        "Air Balloon",
        delta=delta("me1-166"),
    )
    galar_mine = RetreatCostModifier(
        "Galar Mine",
        delta=delta("swsh2-160"),
    )
    ariados = RetreatCostModifier(
        "Ariados Big Net",
        delta=delta("sv6-5"),
    )
    sneasler = RetreatCostModifier(
        "Hisuian Sneasler Carry and Climb",
        delta=delta("swsh10-93"),
    )

    assert air_balloon.delta == -2
    assert galar_mine.delta == 2
    assert ariados.delta == 1
    assert sneasler.delta == -2

    assert effective_retreat_cost(
        3,
        (air_balloon, galar_mine, ariados),
    ) == 4
    assert effective_retreat_cost(
        1,
        (air_balloon, sneasler),
    ) == 0
    assert effective_retreat_cost(
        4,
        (
            air_balloon,
            galar_mine,
            ariados,
            no_retreat_cost("Float Stone"),
        ),
    ) == 0

    beldum = [row for row in variable if row["card_id"] == "sm7-92"]
    assert len(beldum) == 1
    assert all(row["card_id"] != "sm7-92" for row in fixed)

    summary = {
        "fixed_print_effect_rows": report["fixed"]["print_effect_rows"],
        "fixed_distinct_texts": report["fixed"]["distinct_texts"],
        "fixed_by_source_kind": report["fixed"]["by_source_kind"],
        "fixed_by_delta": report["fixed"]["by_delta"],
        "variable_print_effect_rows": report["variable"]["print_effect_rows"],
        "variable_distinct_texts": report["variable"]["distinct_texts"],
        "algebra_examples": {
            "base_3_air_balloon_galar_mine_ariados": 4,
            "base_1_two_reductions_floor": 0,
            "float_stone_priority": 0,
        },
    }
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
