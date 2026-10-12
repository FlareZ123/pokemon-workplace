"""Audit all bundled English Expanded-labeled Ability text for coin-gated Retreat."""
from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from retreat_goodra_coin_gate import GOODRA_SLIMY_SLIDING_PRINT_IDS


def main() -> None:
    identified = {}
    legal_prints = 0
    for path in sorted((ROOT / "resources" / "cards" / "en").glob("*.json")):
        records = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(records, dict):
            records = records["data"]
        for card in records:
            if card.get("legalities", {}).get("expanded") != "Legal":
                continue
            legal_prints += 1
            for ability in card.get("abilities") or ():
                text = ability.get("text", "").casefold()
                if "retreat" not in text or "coin" not in text:
                    continue
                assert card["id"] not in identified
                identified[card["id"]] = (card["name"], ability["name"], text)

    assert set(identified) == GOODRA_SLIMY_SLIDING_PRINT_IDS
    name, ability_name, printed = identified["me4-68"]
    assert (name, ability_name) == ("Goodra", "Slimy Sliding")
    assert "opponent flips a coin" in printed
    assert "energy for its retreat cost is not discarded" in printed
    assert "they don't switch pokémon" in printed
    assert "effect of slimy sliding doesn't stack" in printed
    print("Bundled English Expanded-labeled coin-Retreat Ability audit: PASS")
    print({"candidate_prints": legal_prints, "matching_abilities": len(identified),
           "source_ids": sorted(identified)})


if __name__ == "__main__":
    main()
