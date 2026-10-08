"""Exact no-modifier survival-frontier scan for Strong Bash-like reflection.

Printed optional boosts are already parsed by optional_attack_damage_catalog.
This module overlays an explicit target print's Weakness and Resistance and
enumerates damage-counter-aligned initial attacker damage states where the
lower branch survives while a higher branch knocks out the attacker.
"""

from __future__ import annotations

from collections import defaultdict
import json
from pathlib import Path
from typing import Any

from damage_calculation_kernel import (
    AttackDamage, AttackDamageMode, DamageContext, calculate_damage,
)
from optional_attack_damage_catalog import build_catalog


def final_damage_vs_print(
    attacker_types: list[str],
    defending_print: dict[str, Any],
    *,
    base_damage: int,
    bonus: int,
) -> int:
    weaknesses = defending_print.get("weaknesses") or ()
    resistances = defending_print.get("resistances") or ()
    weakness_multiplier = None
    resistance_reduction = 0
    for weakness in weaknesses:
        if weakness["type"] in attacker_types:
            value = weakness["value"]
            if value.startswith(("×", "x")):
                weakness_multiplier = int(value[1:])
            else:
                raise ValueError(f"unsupported Weakness value: {value!r}")
    for resistance in resistances:
        if resistance["type"] in attacker_types:
            value = resistance["value"]
            if value.startswith(("-", "−")):
                resistance_reduction = int(value[1:])
            else:
                raise ValueError(f"unsupported Resistance value: {value!r}")

    context = DamageContext(
        attack=AttackDamage(
            base_damage, mode=AttackDamageMode.PLUS, modifier=bonus,
        ),
        weakness_multiplier=weakness_multiplier,
        resistance_reduction=resistance_reduction,
    )
    return calculate_damage(context).final_damage


def scan_retaliation_frontier(
    resources: Path, *, defender_print_id: str,
) -> dict[str, object]:
    set_id = defender_print_id.split("-")[0]
    cards = json.loads(
        (resources / "cards" / "en" / f"{set_id}.json")
        .read_text(encoding="utf-8")
    )
    defender = next(card for card in cards if card["id"] == defender_print_id)
    defender_hp = int(defender["hp"])

    optional = build_catalog(resources)
    legal_rows = optional["rows"]
    by_set: dict[str, dict[str, dict[str, Any]]] = {}
    grouped: dict[tuple[Any, ...], dict[str, object]] = {}

    for row in legal_rows:
        if row["variable_bonus"]:
            continue

        attacker_id = str(row["card_id"])
        attacker_set = attacker_id.split("-")[0]
        if attacker_set not in by_set:
            by_set[attacker_set] = {
                card["id"]: card
                for card in json.loads(
                    (resources / "cards" / "en" / f"{attacker_set}.json")
                    .read_text(encoding="utf-8")
                )
            }
        attacker = by_set[attacker_set][attacker_id]
        attacker_hp = int(attacker["hp"])
        attacker_types = attacker["types"]
        base_damage = final_damage_vs_print(
            attacker_types, defender,
            base_damage=int(row["base_damage"]), bonus=0,
        )
        boosted_damage = final_damage_vs_print(
            attacker_types, defender,
            base_damage=int(row["base_damage"]),
            bonus=int(row["bonus_per_unit"]),
        )

        if base_damage < defender_hp:
            continue

        dangerous = tuple(
            current_damage
            for current_damage in range(0, attacker_hp, 10)
            if current_damage + base_damage < attacker_hp
            <= current_damage + boosted_damage
        )
        if not dangerous:
            continue

        signature = (
            row["card_name"], row["attack_name"],
            row["printed_damage"], row["text"],
            attacker_hp, tuple(attacker_types),
        )
        if signature not in grouped:
            grouped[signature] = {
                "card_name": row["card_name"],
                "attack_name": row["attack_name"],
                "hp": attacker_hp,
                "types": attacker_types,
                "base_final_damage": base_damage,
                "boosted_final_damage": boosted_damage,
                "dangerous_prior_damage": dangerous,
                "print_ids": [],
            }
        grouped[signature]["print_ids"].append(attacker_id)

    rows = sorted(grouped.values(), key=lambda r: (str(r["card_name"]), str(r["attack_name"])))
    for row in rows:
        row["print_ids"].sort()
    return {
        "defender_print_id": defender_print_id,
        "defender_hp": defender_hp,
        "legal_optional_fixed_boost_prints": (
            optional["print_rows"] - optional["variable_bonus_prints"]
        ),
        "frontier_signatures": len(rows),
        "frontier_prints": sum(len(row["print_ids"]) for row in rows),
        "frontiers": rows,
    }


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1] / "resources"
    print(json.dumps(
        scan_retaliation_frontier(root, defender_print_id="sv10-146"),
        indent=2,
    ))
