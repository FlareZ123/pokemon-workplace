"""Reproduce Dream Ball Evolution-Pokemon Ability geometry catalog."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from dream_ball_evolution_ability_catalog import (
    ACTIVATION_PASSIVE,
    ACTIVATION_TURN_ACTION,
    GEOMETRY_HAND_EVOLVE_TRIGGER,
    GEOMETRY_IN_PLAY,
    build_dream_ball_evolution_ability_catalog,
    summarize_catalog,
)


def exact(rows, card_id: str, ability_name: str):
    matches = tuple(
        row
        for row in rows
        if row.card_id == card_id and row.ability_name == ability_name
    )
    if len(matches) != 1:
        raise AssertionError(
            f"expected one {card_id} {ability_name!r} row, found {len(matches)}"
        )
    return matches[0]


def main() -> None:
    rows = build_dream_ball_evolution_ability_catalog(ROOT / "resources")
    summary = summarize_catalog(rows)

    pidgeot = exact(rows, "sv3-164", "Quick Search")
    assert pidgeot.geometry == GEOMETRY_IN_PLAY
    assert pidgeot.activation == ACTIVATION_TURN_ACTION
    assert pidgeot.dream_ball_geometry_compatible
    assert pidgeot.evolves_from == "Pidgeotto"

    vileplume = exact(rows, "xy7-3", "Irritating Pollen")
    assert vileplume.geometry == GEOMETRY_IN_PLAY
    assert vileplume.activation == ACTIVATION_PASSIVE
    assert vileplume.dream_ball_geometry_compatible
    assert "can't play any Item cards" in vileplume.ability_text

    crobat = exact(rows, "sv10-122", "Biting Spree")
    assert crobat.geometry == GEOMETRY_HAND_EVOLVE_TRIGGER
    assert not crobat.dream_ball_geometry_compatible

    # The current Expanded ban overlay excludes Apple Drop Flapple prints even
    # though older database metadata may still mark those prints Expanded-legal.
    row_ids = {row.card_id for row in rows}
    assert "swsh2-22" not in row_ids
    assert "swsh45sv-SV013" not in row_ids
    assert "swsh10tg-TG02" not in row_ids
    assert "swshp-SWSH022" not in row_ids

    assert summary["dream_ball_geometry_compatible_rows"] > 0
    assert (
        summary["dream_ball_geometry_compatible_rows"]
        < summary["ability_rows"]
    )

    print(
        json.dumps(
            {
                **summary,
                "named_witnesses": {
                    "pidgeot_quick_search": {
                        "card_id": pidgeot.card_id,
                        "geometry": pidgeot.geometry,
                        "activation": pidgeot.activation,
                        "compatible": pidgeot.dream_ball_geometry_compatible,
                    },
                    "vileplume_irritating_pollen": {
                        "card_id": vileplume.card_id,
                        "geometry": vileplume.geometry,
                        "activation": vileplume.activation,
                        "compatible": vileplume.dream_ball_geometry_compatible,
                    },
                    "team_rockets_crobat_biting_spree": {
                        "card_id": crobat.card_id,
                        "geometry": crobat.geometry,
                        "activation": crobat.activation,
                        "compatible": crobat.dream_ball_geometry_compatible,
                    },
                },
                "current_flapple_ban_overlay_respected": True,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
