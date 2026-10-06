from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools.lock_effect_catalog import build_catalog  # noqa: E402


def _load_card(resources_root: Path, card_id: str) -> dict:
    set_id = card_id.split("-", 1)[0]
    cards = json.loads((resources_root / "cards" / "en" / f"{set_id}.json").read_text(encoding="utf-8"))
    return next(card for card in cards if card["id"] == card_id)


def _all_text(card: dict) -> str:
    chunks = [ability.get("text", "") for ability in card.get("abilities") or []]
    chunks.extend(attack.get("text", "") for attack in card.get("attacks") or [])
    chunks.extend(card.get("rules") or [])
    return " ".join(chunks)


def main() -> None:
    resources_root = ROOT / "resources"
    catalog = build_catalog(resources_root)

    expected_counts = {
        "source_prints": 177,
        "source_gameplay_variants": 116,
        "lock_effect_signatures": 109,
        "lock_effect_print_instances": 181,
        "stochastic_signatures": 4,
        "exclusive_choice_signatures": 1,
        "self_vacating_attack_signatures": 1,
    }
    assert catalog["counts"] == expected_counts

    assert catalog["activation"] == {
        "active": 26,
        "attack_applied": 51,
        "bench": 2,
        "one_shot": 1,
        "passive": 14,
        "stadium": 8,
        "stadium_required": 1,
        "tool": 1,
        "tool_attached": 5,
    }

    effects = catalog["effects"]
    self_vacating = [row for row in effects if row["self_vacates"]]
    assert len(self_vacating) == 1
    assert self_vacating[0]["card_name"] == "Beheeyem"
    assert self_vacating[0]["effect_name"] == "Mysterious Noise"

    choice_locks = [row for row in effects if row["exclusive_choice"]]
    assert len(choice_locks) == 1
    assert choice_locks[0]["card_name"] == "Crobat"
    assert choice_locks[0]["dimensions"] == ["item", "supporter"]

    garbodor = _load_card(resources_root, "xy9-57")
    vileplume = _load_card(resources_root, "xy7-3")
    hood = _load_card(resources_root, "sm10-186")
    tower = _load_card(resources_root, "sv6-153")
    beheeyem = _load_card(resources_root, "sm11-91")
    stoutland = _load_card(resources_root, "bw7-122")
    honchkrow = _load_card(resources_root, "sm10-109")

    assert "has a Pokémon Tool card attached" in _all_text(garbodor)
    assert "has no Abilities" in _all_text(garbodor)
    assert "can't play any Item cards" in _all_text(vileplume)
    assert "Prevent all effects of your opponent's Abilities" in _all_text(hood)
    assert "Pokémon Tools attached to each Pokémon" in _all_text(tower)
    assert "have no effect" in _all_text(tower)
    assert "Shuffle this Pokémon and all cards attached to it into your deck" in _all_text(beheeyem)
    assert "can't play any Supporter cards" in _all_text(stoutland)
    assert "Pokémon Tool, Special Energy, or Stadium" in _all_text(honchkrow)

    print("Catalog counts")
    print(json.dumps(catalog["counts"], indent=2))
    print("\nActivation geometry")
    print(json.dumps(catalog["activation"], indent=2))
    print("\nDenied/suppressed dimensions")
    print(json.dumps(catalog["dimensions"], indent=2))
    print("\nUnique self-vacating lock attack")
    print(f"{self_vacating[0]['card_name']} - {self_vacating[0]['effect_name']}")
    print("\nSource-text assertions for the Hood/Garbotoxin/Tower and Beheeyem handoff cases passed.")


if __name__ == "__main__":
    main()
