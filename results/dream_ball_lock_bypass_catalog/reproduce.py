"""Reproduce Dream Ball Evolution-Pokemon lock-bypass candidate catalog."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

from dream_ball_lock_bypass_catalog import (
    build_dream_ball_lock_candidates,
    summarize_candidates,
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
    rows = build_dream_ball_lock_candidates(ROOT / "resources")
    summary = summarize_candidates(rows)

    vileplume = exact(rows, "xy7-3", "Irritating Pollen")
    assert vileplume.dream_ball_geometry_compatible
    assert vileplume.bench_position_compatible
    assert vileplume.extra_activation_prerequisite is None
    assert "item" in vileplume.lock_dimensions
    assert vileplume.lock_activation == "passive"

    alolan_muk = exact(rows, "sm1-58", "Power of Alchemy")
    assert alolan_muk.dream_ball_geometry_compatible
    assert alolan_muk.bench_position_compatible
    assert alolan_muk.extra_activation_prerequisite is None
    assert "ability" in alolan_muk.lock_dimensions
    assert alolan_muk.lock_activation == "passive"

    garbodor = exact(rows, "xy9-57", "Garbotoxin")
    assert garbodor.dream_ball_geometry_compatible
    assert garbodor.bench_position_compatible
    assert garbodor.extra_activation_prerequisite == "tool_attached"
    assert "ability" in garbodor.lock_dimensions

    weezing = exact(rows, "swsh2-113", "Neutralizing Gas")
    assert not weezing.dream_ball_geometry_compatible
    assert not weezing.bench_position_compatible
    assert weezing.extra_activation_prerequisite == "active"

    assert summary["evolution_lock_rows"] > 0
    assert summary["dream_ball_geometry_compatible_rows"] > 0
    assert (
        summary["no_recognized_extra_activation_prerequisite_rows"]
        < summary["dream_ball_geometry_compatible_rows"]
    )

    print(
        json.dumps(
            {
                **summary,
                "named_witnesses": {
                    "vileplume_irritating_pollen": {
                        "card_id": vileplume.card_id,
                        "dimensions": vileplume.lock_dimensions,
                        "activation": vileplume.lock_activation,
                        "geometry_compatible": (
                            vileplume.dream_ball_geometry_compatible
                        ),
                        "extra_prerequisite": (
                            vileplume.extra_activation_prerequisite
                        ),
                    },
                    "alolan_muk_power_of_alchemy": {
                        "card_id": alolan_muk.card_id,
                        "dimensions": alolan_muk.lock_dimensions,
                        "activation": alolan_muk.lock_activation,
                        "geometry_compatible": (
                            alolan_muk.dream_ball_geometry_compatible
                        ),
                        "extra_prerequisite": (
                            alolan_muk.extra_activation_prerequisite
                        ),
                    },
                    "garbodor_garbotoxin": {
                        "card_id": garbodor.card_id,
                        "dimensions": garbodor.lock_dimensions,
                        "activation": garbodor.lock_activation,
                        "geometry_compatible": (
                            garbodor.dream_ball_geometry_compatible
                        ),
                        "extra_prerequisite": (
                            garbodor.extra_activation_prerequisite
                        ),
                    },
                    "galarian_weezing_neutralizing_gas": {
                        "card_id": weezing.card_id,
                        "dimensions": weezing.lock_dimensions,
                        "activation": weezing.lock_activation,
                        "geometry_compatible": (
                            weezing.dream_ball_geometry_compatible
                        ),
                        "extra_prerequisite": (
                            weezing.extra_activation_prerequisite
                        ),
                    },
                },
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
