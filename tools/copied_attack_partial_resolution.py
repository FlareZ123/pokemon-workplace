from __future__ import annotations

import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.build_expanded_legality_baseline import (  # noqa: E402
    OFFICIAL_BAN_OVERLAY,
    load_json,
)

DISCARD_PREFIX = re.compile(
    r"^Discard all (?:(basic) )?([A-Za-z]+ )?Energy from this Pokémon(?:[,.]|$)",
    re.IGNORECASE,
)


def _normalize(text: str) -> str:
    return " ".join(text.split())


def _discard_scope(match: re.Match[str]) -> str:
    energy_type = (match.group(2) or "").strip().lower()
    if not energy_type:
        return "all_energy"
    if match.group(1):
        return f"basic_{energy_type}"
    return energy_type


def _has_independent_output(attack: dict[str, Any], text: str, match: re.Match[str]) -> bool:
    lower = text.lower()
    if "discarded in this way" in lower:
        return False
    if attack.get("damage"):
        return True
    remainder = text[match.end():].strip(" ,.")
    return bool(remainder)


def build(resources_root: Path) -> dict[str, Any]:
    sets = load_json(resources_root / "sets" / "en.json")
    expanded_sets = {
        entry["id"]
        for entry in sets
        if (entry.get("legalities") or {}).get("expanded") == "Legal"
    }

    print_rows: list[dict[str, Any]] = []
    for path in sorted((resources_root / "cards" / "en").glob("*.json")):
        if path.stem not in expanded_sets:
            continue
        for card in load_json(path):
            database_status = (card.get("legalities") or {}).get("expanded")
            if card["id"] in OFFICIAL_BAN_OVERLAY or database_status == "Banned":
                continue
            for attack in card.get("attacks") or []:
                text = _normalize(attack.get("text") or "")
                match = DISCARD_PREFIX.match(text)
                if match is None:
                    continue
                print_rows.append(
                    {
                        "card_id": card["id"],
                        "card_name": card["name"],
                        "types": card.get("types") or [],
                        "attack_name": attack["name"],
                        "damage": attack.get("damage") or "",
                        "text": text,
                        "discard_scope": _discard_scope(match),
                        "output_depends_on_discard_count": "discarded in this way" in text.lower(),
                        "independent_output": _has_independent_output(attack, text, match),
                    }
                )

    signatures: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in print_rows:
        signatures[(row["attack_name"], row["damage"], row["text"])].append(row)

    signature_rows: list[dict[str, Any]] = []
    for (attack_name, damage, text), rows in sorted(signatures.items()):
        signature_rows.append(
            {
                "attack_name": attack_name,
                "damage": damage,
                "text": text,
                "card_names": sorted({row["card_name"] for row in rows}),
                "print_ids": sorted(row["card_id"] for row in rows),
                "discard_scope": rows[0]["discard_scope"],
                "output_depends_on_discard_count": rows[0]["output_depends_on_discard_count"],
                "independent_output": rows[0]["independent_output"],
            }
        )

    scope_counts = Counter(
        row["discard_scope"] for row in signature_rows if row["independent_output"]
    )
    return {
        "scope": {
            "format": "paper Expanded",
            "copy_rule_family": "C-18 use it as this attack + general partial-resolution rule",
            "pattern": "attack text begins with 'Discard all ... Energy from this Pokémon'",
        },
        "counts": {
            "matching_prints": len(print_rows),
            "distinct_attack_signatures": len(signature_rows),
            "discard_count_dependent_signatures": sum(
                row["output_depends_on_discard_count"] for row in signature_rows
            ),
            "independent_output_signatures": sum(row["independent_output"] for row in signature_rows),
            "independent_specific_type_signatures": sum(
                row["independent_output"] and row["discard_scope"] != "all_energy"
                for row in signature_rows
            ),
            "independent_discard_scopes": dict(sorted(scope_counts.items())),
        },
        "signatures": signature_rows,
    }


def main() -> None:
    resources_root = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "resources"
    print(json.dumps(build(resources_root), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
