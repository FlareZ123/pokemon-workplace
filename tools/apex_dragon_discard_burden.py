from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from build_expanded_legality_baseline import classify_effective_legality

GENERIC_ALL = re.compile(r"^Discard all Energy (?:attached to|from) this Pokémon$", re.I)
GENERIC_N = re.compile(r"^Discard (an|\d+) Energy (?:attached to|from) this Pokémon$", re.I)
TYPED_N = re.compile(
    r"^Discard (all|an|a|\d+) (?:(basic) )?([A-Za-z]+) Energy (?:attached to|from) this Pokémon$",
    re.I,
)
TYPED_PAIR = re.compile(
    r"^Discard (?:a|1) ([A-Za-z]+) Energy and (?:a|1) ([A-Za-z]+) Energy (?:attached to|from) this Pokémon$",
    re.I,
)
TYPED_PAIR_SHARED_ENERGY = re.compile(
    r"^Discard a ([A-Za-z]+) and a ([A-Za-z]+) Energy (?:attached to|from) this Pokémon$",
    re.I,
)


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def normalize(text: str) -> str:
    return " ".join(text.split())


def parse_first_discard(first_sentence: str) -> dict[str, Any]:
    if GENERIC_ALL.fullmatch(first_sentence):
        return {"kind": "generic_all"}

    match = GENERIC_N.fullmatch(first_sentence)
    if match:
        token = match.group(1).lower()
        return {"kind": "generic_count", "count": 1 if token == "an" else int(token)}

    match = TYPED_N.fullmatch(first_sentence)
    if match:
        token = match.group(1).lower()
        count: int | str = "all" if token == "all" else (
            1 if token in {"a", "an"} else int(token)
        )
        return {
            "kind": "typed_count",
            "energy_type": match.group(3).title(),
            "count": count,
            "basic_only": bool(match.group(2)),
        }

    for pattern in (TYPED_PAIR, TYPED_PAIR_SHARED_ENERGY):
        match = pattern.fullmatch(first_sentence)
        if match:
            return {
                "kind": "typed_pair",
                "energy_types": [match.group(1).title(), match.group(2).title()],
            }

    lower = first_sentence.lower()
    if (
        " or " in lower
        or "as many" in lower
        or "any number" in lower
        or "any amount" in lower
    ):
        return {"kind": "choice_or_variable"}

    return {"kind": "unsupported"}


def forced_discard_count(
    parsed: dict[str, Any],
    attached_basic: Counter[str],
) -> int | None:
    total = sum(attached_basic.values())
    kind = parsed["kind"]

    if kind == "generic_all":
        return total

    if kind == "generic_count":
        return min(total, parsed["count"])

    if kind == "typed_count":
        available = attached_basic[parsed["energy_type"]]
        requested = available if parsed["count"] == "all" else parsed["count"]
        return min(available, requested)

    if kind == "typed_pair":
        remaining = attached_basic.copy()
        discarded = 0
        for energy_type in parsed["energy_types"]:
            if remaining[energy_type] > 0:
                remaining[energy_type] -= 1
                discarded += 1
        return discarded

    return None


def build(
    resources_root: Path,
    attached_basic_energy: dict[str, int] | None = None,
) -> dict[str, Any]:
    attached = Counter(attached_basic_energy or {"Grass": 2, "Fire": 1})
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
            if classify_effective_legality(card)[0] != "Legal":
                continue
            if "Dragon" not in (card.get("types") or []):
                continue

            for attack in card.get("attacks") or []:
                text = normalize(attack.get("text") or "")
                first_sentence = text.split(".", 1)[0]
                if not text.startswith("Discard ") or "this Pokémon" not in first_sentence:
                    continue

                parsed = parse_first_discard(first_sentence)
                print_rows.append(
                    {
                        "card_id": card["id"],
                        "card_name": card["name"],
                        "attack_name": attack["name"],
                        "damage": attack.get("damage") or "",
                        "text": text,
                        "first_discard": parsed,
                        "forced_discard_count": forced_discard_count(parsed, attached),
                        "quantity_coupled": "discarded in this way" in text.lower(),
                    }
                )

    signatures: dict[tuple[str, str, str], dict[str, Any]] = {}
    sources: dict[tuple[str, str, str], list[str]] = defaultdict(list)
    for row in print_rows:
        key = (row["attack_name"], row["damage"], row["text"])
        signatures.setdefault(key, row)
        sources[key].append(row["card_id"])

    rows = []
    for key, row in signatures.items():
        out = dict(row)
        out["print_ids"] = sorted(sources[key])
        rows.append(out)

    deterministic = [row for row in rows if row["forced_discard_count"] is not None]
    variable = [row for row in rows if row["forced_discard_count"] is None]
    burden_counts = Counter(row["forced_discard_count"] for row in deterministic)
    zero_independent = [
        row
        for row in deterministic
        if row["forced_discard_count"] == 0 and not row["quantity_coupled"]
    ]

    return {
        "scenario": {
            "copy_attack": "Apex Dragon",
            "attached_basic_energy_cards": dict(sorted(attached.items())),
            "assumption": "Each listed attachment is a Basic Energy card of exactly its named type.",
        },
        "counts": {
            "matching_print_instances": len(print_rows),
            "distinct_attack_signatures": len(rows),
            "deterministic_burden_signatures": len(deterministic),
            "choice_or_variable_signatures": len(variable),
            "forced_discard_burden": {
                str(key): burden_counts[key] for key in sorted(burden_counts)
            },
            "zero_burden_independent_signatures": len(zero_independent),
        },
        "zero_burden_independent": sorted(
            zero_independent,
            key=lambda row: (row["attack_name"], row["card_name"]),
        ),
        "signatures": sorted(
            rows,
            key=lambda row: (
                row["forced_discard_count"] is None,
                row["forced_discard_count"]
                if row["forced_discard_count"] is not None
                else 99,
                row["attack_name"],
                row["card_name"],
            ),
        ),
    }


def main() -> None:
    import sys

    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("resources")
    result = build(root)
    print(
        json.dumps(
            {
                "scenario": result["scenario"],
                "counts": result["counts"],
                "zero_burden_independent": result["zero_burden_independent"],
            },
            indent=2,
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
