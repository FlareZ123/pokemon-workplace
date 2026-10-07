"""Reproduce exact setup access for Aichi's Japanese-only draw-engine cards."""

from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools.aichi_regional_engine_access import build_aichi_regional_engine_analysis


def probability(row: dict, metric: str) -> float:
    return row["after_first_normal_draw"]["metrics"][metric]["probability"]


def main() -> None:
    result = build_aichi_regional_engine_analysis()
    rows = {row["name"]: row for row in result["lists"]}

    kazuma = rows["Kazuma Kashi Iron Thorns"]
    ryoya = rows["Ryoya Fujii Iron Thorns"]
    kohei = rows["Kohei Hamamichi Iron Thorns"]

    assert kazuma["deck_counts"] == {
        "forced_basics": 4,
        "tag_call": 2,
        "guzma_hala": 2,
        "palace_book": 1,
        "palace_belt": 1,
        "players_ceremony": 1,
        "regional_draw_engine_copies": 3,
    }
    assert ryoya["deck_counts"] == {
        "forced_basics": 4,
        "tag_call": 2,
        "guzma_hala": 2,
        "palace_book": 2,
        "palace_belt": 0,
        "players_ceremony": 2,
        "regional_draw_engine_copies": 4,
    }
    assert kohei["deck_counts"] == {
        "forced_basics": 4,
        "tag_call": 2,
        "guzma_hala": 2,
        "palace_book": 0,
        "palace_belt": 2,
        "players_ceremony": 1,
        "regional_draw_engine_copies": 3,
    }

    expected = {
        "Kazuma Kashi Iron Thorns": {
            "direct_or_tag_call_guzma_hala_access": 0.409905423,
            "palace_book_in_hand": 0.121043581,
            "players_ceremony_ready": 0.444343565,
            "palace_belt_ready": 0.444343565,
            "belt_plus_ceremony_ready": 0.337815057,
            "end_turn_draw_ready": 0.516974395,
            "any_regional_piece_in_hand": 0.325925701,
        },
        "Ryoya Fujii Iron Thorns": {
            "direct_or_tag_call_guzma_hala_access": 0.409905423,
            "palace_book_in_hand": 0.229303611,
            "players_ceremony_ready": 0.550872073,
            "palace_belt_ready": 0.0,
            "belt_plus_ceremony_ready": 0.0,
            "end_turn_draw_ready": 0.664787229,
            "any_regional_piece_in_hand": 0.411971805,
        },
        "Kohei Hamamichi Iron Thorns": {
            "direct_or_tag_call_guzma_hala_access": 0.409905423,
            "palace_book_in_hand": 0.0,
            "players_ceremony_ready": 0.444343565,
            "palace_belt_ready": 0.550872073,
            "belt_plus_ceremony_ready": 0.380806800,
            "end_turn_draw_ready": 0.444343565,
            "any_regional_piece_in_hand": 0.325925701,
        },
    }

    for name, metrics in expected.items():
        row = rows[name]
        for metric, value in metrics.items():
            actual = probability(row, metric)
            assert math.isclose(actual, value, abs_tol=5e-10), (
                name,
                metric,
                actual,
                value,
            )

    assert probability(kazuma, "end_turn_draw_ready") > probability(
        kazuma, "any_regional_piece_in_hand"
    )
    assert probability(ryoya, "end_turn_draw_ready") > probability(
        ryoya, "any_regional_piece_in_hand"
    )
    assert probability(kohei, "belt_plus_ceremony_ready") > 0.38

    print("aichi regional draw-engine access: PASS")
    for name in (
        "Kazuma Kashi Iron Thorns",
        "Ryoya Fujii Iron Thorns",
        "Kohei Hamamichi Iron Thorns",
    ):
        row = rows[name]
        print(
            name,
            "G&H access",
            f"{probability(row, 'direct_or_tag_call_guzma_hala_access'):.6%}",
            "end-turn draw option",
            f"{probability(row, 'end_turn_draw_ready'):.6%}",
            "Belt+Ceremony",
            f"{probability(row, 'belt_plus_ceremony_ready'):.6%}",
        )


if __name__ == "__main__":
    main()
