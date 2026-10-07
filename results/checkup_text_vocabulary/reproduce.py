"""Reproduce historical Pokémon Checkup wording audit."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from checkup_text_audit import audit_checkup_wording  # noqa: E402


def main() -> None:
    rows = audit_checkup_wording(ROOT / "resources")
    between = tuple(row for row in rows if row.wording == "between_turns")
    checkup = tuple(row for row in rows if row.wording == "pokemon_checkup")
    both = tuple(row for row in rows if row.wording == "both")

    assert len(rows) == 106
    assert len(between) == 62
    assert len(checkup) == 44
    assert not both
    assert len({row.text for row in rows}) == 59
    assert len({row.card_id for row in rows}) == 102

    latest_between = max(between, key=lambda row: row.release_date)
    earliest_checkup = min(checkup, key=lambda row: row.release_date)

    assert latest_between.release_date == "2019/11/01"
    assert latest_between.set_id == "sm12"
    assert earliest_checkup.release_date == "2020/02/07"
    assert earliest_checkup.set_id == "swsh1"
    assert latest_between.release_date < earliest_checkup.release_date

    print("timing-text rows:", len(rows))
    print("between-turns rows:", len(between))
    print("Pokémon Checkup rows:", len(checkup))
    print("unique texts:", len({row.text for row in rows}))
    print("latest legacy wording:", latest_between.release_date, latest_between.set_id)
    print("earliest Checkup wording:", earliest_checkup.release_date, earliest_checkup.set_id)
    print("Checkup vocabulary audit passed")


if __name__ == "__main__":
    main()
