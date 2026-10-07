"""Reproduce historical Pokémon Checkup wording audit."""

from __future__ import annotations

from collections import Counter
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from checkup_text_audit import audit_checkup_wording, semantic_classes  # noqa: E402


def main() -> None:
    rows = audit_checkup_wording(ROOT / "resources")
    between = tuple(row for row in rows if row.wording == "between_turns")
    checkup = tuple(row for row in rows if row.wording == "pokemon_checkup")
    both = tuple(row for row in rows if row.wording == "both")

    assert len(rows) == 114
    assert len(between) == 62
    assert len(checkup) == 52
    assert not both
    assert len({row.text for row in rows}) == 61
    assert len({row.card_id for row in rows}) == 110

    legacy_series = {row.series for row in between}
    checkup_series = {row.series for row in checkup}
    assert legacy_series == {"Black & White", "XY", "Sun & Moon"}
    assert checkup_series == {
        "Sword & Shield",
        "Scarlet & Violet",
        "Mega Evolution",
    }
    assert legacy_series.isdisjoint(checkup_series)

    classes = Counter()
    for row in rows:
        row_classes = semantic_classes(row.text)
        assert row_classes, (row.card_id, row.text)
        classes.update(row_classes)

    assert classes == Counter(
        {
            "counter_base_replace": 60,
            "direct_counter_put": 15,
            "coin_count": 12,
            "counter_add": 11,
            "heal": 9,
            "skip_checkup": 8,
            "recovery_suppress": 2,
        }
    )

    print("timing-text rows:", len(rows))
    print("between-turns rows:", len(between))
    print("Pokémon Checkup rows:", len(checkup))
    print("legacy series:", sorted(legacy_series))
    print("Checkup series:", sorted(checkup_series))
    print("semantic classes:", dict(sorted(classes.items())))
    print("Checkup vocabulary audit passed")


if __name__ == "__main__":
    main()
