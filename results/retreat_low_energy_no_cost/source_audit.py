"""Check exact Energy-threshold no-Retreat-Cost sources against local prints."""
from __future__ import annotations

import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from retreat_attached_energy_free_cost import LOW_ENERGY_NO_RETREAT_SOURCES


def main() -> None:
    compiled = {source.print_id: source for source in LOW_ENERGY_NO_RETREAT_SOURCES}
    assert len(compiled) == 10
    source_ids = set()
    pattern = re.compile(
        r"if this pokémon has (no|2 or fewer) energy attached",
        re.IGNORECASE,
    )
    for path in sorted((ROOT / "resources" / "cards" / "en").glob("*.json")):
        records = json.loads(path.read_text(encoding="utf-8"))
        records = records.get("data", records) if isinstance(records, dict) else records
        for card in records:
            for ability in card.get("abilities") or ():
                match = pattern.search(ability.get("text", ""))
                if match is None:
                    continue
                source = compiled.get(card["id"])
                assert source is not None, card["id"]
                assert (source.card_name, source.ability_name) == (
                    card["name"], ability["name"],
                )
                assert source.max_attached_units == (
                    0 if match.group(1).lower() == "no" else 2
                )
                source_ids.add(card["id"])
    assert source_ids == set(compiled)
    assert len({(x.card_name, x.ability_name) for x in compiled.values()}) == 7
    print("Energy-threshold no-Retreat-Cost source audit: PASS")
    print({"verified_print_ids": len(compiled), "distinct_ability_families": 7})


if __name__ == "__main__":
    main()
