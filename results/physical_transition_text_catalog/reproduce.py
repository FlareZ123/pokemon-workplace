"""Reproduce high-confidence physical transition text catalog statistics."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from physical_transition_text_catalog import build, rows_for_card  # noqa: E402


def categories_for(catalog, card_id):
    return {
        category
        for row in rows_for_card(catalog, card_id)
        for category in row["categories"]
    }


def main() -> None:
    catalog = build(ROOT / "resources")

    huntail = categories_for(catalog, "sv10-55")
    assert "knock_out_trigger" in huntail
    assert "knock_out_zone_redirection" in huntail
    assert "knock_out_attached_recovery" in huntail

    exp_share = categories_for(catalog, "sv1-174")
    assert "knock_out_trigger" in exp_share
    assert "energy_move" in exp_share

    double_dragon = categories_for(catalog, "xy6-97")
    assert "restricted_special_energy_attachment" in double_dragon

    summary = catalog["summary"]
    assert summary["matched_cards"] > 0
    assert summary["cards_by_category"]["knock_out_trigger"] > 0
    assert summary["cards_by_category"]["energy_move"] > 0

    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
