from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from combat_data_overrides import apply_combat_data_overrides  # noqa: E402


def card(set_id: str, card_id: str) -> dict:
    rows = json.loads(
        (ROOT / "resources" / "cards" / "en" / f"{set_id}.json").read_text(
            encoding="utf-8"
        )
    )
    return next(row for row in rows if row["id"] == card_id)


def main() -> None:
    murkrow = card("me55", "me55-93")
    assert murkrow["resistances"] == [
        {"type": "Fighting", "value": "×2"}
    ]
    corrected = apply_combat_data_overrides(murkrow)
    assert corrected["resistances"] == [
        {"type": "Fighting", "value": "-30"}
    ]
    assert murkrow["resistances"] == [
        {"type": "Fighting", "value": "×2"}
    ]

    uxie = card("me55c", "me55c-43")
    corrected_uxie = apply_combat_data_overrides(uxie)
    assert corrected_uxie["weaknesses"] == [
        {"type": "Psychic", "value": "+20"}
    ]

    print(
        {
            "raw_murkrow": murkrow["resistances"],
            "corrected_murkrow": corrected["resistances"],
            "uxie": corrected_uxie["weaknesses"],
        }
    )


if __name__ == "__main__":
    main()
