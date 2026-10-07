"""Reproduce the legal Basic-Ability surface suppressed by Power of Alchemy."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from alolan_muk_basic_ability_surface import (
    HAND_BENCH_TRIGGER,
    build_basic_ability_surface,
    summarize_surface,
)


def exact(rows, card_id: str, ability_name: str):
    matches = tuple(
        row
        for row in rows
        if row.card_id == card_id and row.ability_name == ability_name
    )
    if len(matches) != 1:
        raise AssertionError(
            f"expected one {card_id} {ability_name!r}, found {len(matches)}"
        )
    return matches[0]


def main() -> None:
    rows = build_basic_ability_surface(ROOT / "resources")
    summary = summarize_surface(rows)

    lele = exact(rows, "sm2-60", "Wonder Tag")
    assert lele.geometry == HAND_BENCH_TRIGGER

    dedenne = exact(rows, "sm10-57", "Dedechange")
    assert dedenne.geometry == HAND_BENCH_TRIGGER

    crobat = exact(rows, "swsh3-104", "Dark Asset")
    assert crobat.geometry == HAND_BENCH_TRIGGER

    # Shaymin-EX Set Up is currently banned in Expanded and therefore absent.
    ids = {row.card_id for row in rows}
    assert "xy6-77" not in ids
    assert "xy6-77a" not in ids
    assert "xy6-106" not in ids

    assert summary["ability_rows"] > 0
    assert summary["hand_bench_trigger_rows"] > 0

    print(
        json.dumps(
            {
                **summary,
                "named_hand_entry_support": {
                    "tapu_lele_gx_wonder_tag": lele.card_id,
                    "dedenne_gx_dedechange": dedenne.card_id,
                    "crobat_v_dark_asset": crobat.card_id,
                },
                "banned_shaymin_ex_set_up_excluded": True,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
