from __future__ import annotations

from pathlib import Path
import re
from typing import Any

from build_expanded_legality_baseline import load_json
from setup_trigger_role_contention import scan_literal_bench_trigger_basics

SELF_VACATE_RE = re.compile(
    r"(?P<verb>shuffle|put) this Pokémon(?: and .*?)? into your (?P<destination>deck|hand)",
    re.IGNORECASE,
)


def scan_bench_trigger_lifecycle(resources_root: Path) -> dict[str, Any]:
    trigger_catalog = scan_literal_bench_trigger_basics(resources_root)
    trigger_ids = {row["id"] for row in trigger_catalog["prints"]}

    raw_by_id: dict[str, dict[str, Any]] = {}
    for path in sorted((resources_root / "cards" / "en").glob("*.json")):
        for card in load_json(path):
            if card["id"] in trigger_ids:
                raw_by_id[card["id"]] = card

    rows: list[dict[str, Any]] = []
    ability_cleanup: list[dict[str, Any]] = []
    for trigger_row in trigger_catalog["prints"]:
        card = raw_by_id[trigger_row["id"]]
        for attack in card.get("attacks") or []:
            text = attack.get("text", "")
            match = SELF_VACATE_RE.search(text)
            if match is None:
                continue
            rows.append(
                {
                    "id": card["id"],
                    "name": card["name"],
                    "fingerprint": trigger_row["fingerprint"],
                    "attack": attack.get("name"),
                    "attack_text": text,
                    "attack_cost": attack.get("cost") or [],
                    "destination": match.group("destination").lower(),
                    "optional_cleanup": bool(
                        re.search(r"you may (?:shuffle|put) this Pokémon", text, re.IGNORECASE)
                    ),
                    "gx_attack": "-GX" in (attack.get("name") or ""),
                }
            )

        for ability in card.get("abilities") or []:
            text = ability.get("text", "")
            match = SELF_VACATE_RE.search(text)
            if match is not None:
                ability_cleanup.append(
                    {
                        "id": card["id"],
                        "name": card["name"],
                        "ability": ability.get("name"),
                        "ability_text": text,
                    }
                )

    unique_variants: dict[str, dict[str, Any]] = {}
    for row in rows:
        unique_variants.setdefault(row["fingerprint"], row)

    return {
        "trigger_print_count": trigger_catalog["print_count"],
        "trigger_name_count": trigger_catalog["unique_names"],
        "self_vacating_print_count": len(rows),
        "self_vacating_name_count": len({row["name"] for row in rows}),
        "self_vacating_gameplay_variants": len(unique_variants),
        "self_vacating_names": sorted({row["name"] for row in rows}),
        "ability_cleanup_count": len(ability_cleanup),
        "variants": sorted(
            unique_variants.values(),
            key=lambda row: (row["name"], row["attack"], row["fingerprint"]),
        ),
        "prints": rows,
        "ability_cleanup": ability_cleanup,
    }
