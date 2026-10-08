"""Audit exact paper Expanded card-print Trainer-play reaction surface."""
from __future__ import annotations

from collections import Counter
from datetime import date
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools.trainer_play_reactivity_catalog import catalog


def main():
    rows = catalog(ROOT / "resources", as_of=date(2026, 10, 8))
    kinds = Counter(row.classification for row in rows)
    sources = Counter(row.source for row in rows)
    unique_names = {row.card_name for row in rows}

    assert len(rows) == 32, len(rows)
    assert len(unique_names) == 24, unique_names
    assert kinds == Counter({
        "deterministic_card_effect_protection": 31,
        "coin_gated_card_nullification": 1,
    }), kinds
    assert sources == Counter({
        "abilities": 22,
        "rules": 8,
        "attacks": 2,
    }), sources

    exceptional = [row for row in rows if row.classification != "deterministic_card_effect_protection"]
    assert len(exceptional) == 1
    assert exceptional[0].card_id == "xy4-2"
    assert exceptional[0].card_name == "Venomoth"
    assert exceptional[0].label == "Dizzying Wind"
    assert "flips a coin" in exceptional[0].text.lower()

    assert any(
        row.card_id == "bw8-104" and row.card_name == "Togekiss"
        for row in rows
    )
    assert any(
        row.card_name == "Greninja V-UNION"
        and "Item card" in row.text
        for row in rows
    )
    assert all(row.classification != "uncategorized" for row in rows)

    # For a generous cutover date, no legal print is falsely added from the
    # base-era or pre-Black-White expansion series.
    older = catalog(ROOT / "resources", as_of=date(2014, 11, 5))
    assert any(row.card_id == "xy4-2" for row in older)
    assert all(row.card_id.split("-")[0] in {
        "bw8", "xy4",
    } for row in older), older
    assert len(older) == 2, older

    print(
        "trainer_play_reactivity_catalog regression: PASS; "
        f"{len(rows)} eligible prints, {len(unique_names)} names, "
        f"categories={dict(kinds)}, source types={dict(sources)}"
    )
    for row in exceptional:
        print("Interpretation requiring additional ruling:", row.card_id, row.card_name, row.label)


if __name__ == "__main__":
    main()
