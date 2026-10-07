"""Catalog damaging attacks that can remove opposing attachments before KO checks."""

from __future__ import annotations

import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from build_expanded_legality_baseline import classify_effective_legality, load_json


def normalize(text: str) -> str:
    return " ".join(text.split())


def matching_discard_clauses(text: str) -> tuple[tuple[str, tuple[str, ...]], ...]:
    """Return clauses that discard Energy or Tools from the opposing Active."""

    rows: list[tuple[str, tuple[str, ...]]] = []
    for clause in re.split(r"[.;]", normalize(text)):
        clause = clause.strip()
        if not clause:
            continue

        lower = clause.lower()
        if re.search(r"\\bdiscard\\b", lower) is None:
            continue
        if (
            "opponent's active pokémon" not in lower
            and "defending pokémon" not in lower
        ):
            continue

        kinds: list[str] = []
        if "energy" in lower:
            kinds.append("energy")
        if "pokémon tool" in lower or "pokemon tool" in lower:
            kinds.append("tool")
        if kinds:
            rows.append((clause, tuple(sorted(kinds))))

    return tuple(rows)


def timing_for_clauses(
    clauses: tuple[tuple[str, tuple[str, ...]], ...],
) -> str:
    timings = {
        (
            "before_damage"
            if "before doing damage" in clause.lower()
            else "effects_outside_damage"
        )
        for clause, _kinds in clauses
    }
    if len(timings) != 1:
        return "mixed"
    return next(iter(timings))


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
            effective_status, _source = classify_effective_legality(card)
            if effective_status != "Legal":
                continue

            for attack in card.get("attacks") or []:
                damage = str(attack.get("damage") or "").strip()
                if not damage:
                    continue

                text = normalize(attack.get("text") or "")
                clauses = matching_discard_clauses(text)
                if not clauses:
                    continue

                kinds = tuple(sorted({
                    kind
                    for _clause, clause_kinds in clauses
                    for kind in clause_kinds
                }))

                print_rows.append(
                    {
                        "card_id": card["id"],
                        "card_name": card["name"],
                        "attack_name": attack["name"],
                        "damage": damage,
                        "text": text,
                        "timing": timing_for_clauses(clauses),
                        "resource_kinds": list(kinds),
                        "matching_clauses": [
                            clause for clause, _clause_kinds in clauses
                        ],
                    }
                )

    by_signature: dict[tuple[str, str, str], dict[str, Any]] = {}
    print_ids: dict[tuple[str, str, str], list[str]] = defaultdict(list)
    for row in print_rows:
        key = (row["attack_name"], row["damage"], row["text"])
        by_signature.setdefault(key, row)
        print_ids[key].append(row["card_id"])

    signatures: list[dict[str, Any]] = []
    for key, row in by_signature.items():
        output = dict(row)
        output["print_ids"] = sorted(print_ids[key])
        signatures.append(output)

    categories = Counter(
        f"{row['timing']}:{'+'.join(row['resource_kinds'])}"
        for row in signatures
    )

    representative_ids = {
        "sv1-94",          # Dedenne / Energy Munch
        "swsh10tg-TG19",  # Galarian Zapdos V / Thunderous Kick
        "sv7-8",           # Mow Rotom / Reaping Dash
        "swsh3-118",       # Scizor V / Hack Off
        "swsh9-114",       # Dracovish V / Slosh 'n' Crash
    }
    representatives = [
        row
        for row in print_rows
        if row["card_id"] in representative_ids
    ]

    return {
        "counts": {
            "print_instances": len(print_rows),
            "distinct_signatures": len(signatures),
            "categories": dict(sorted(categories.items())),
        },
        "representatives": sorted(
            representatives,
            key=lambda row: row["card_id"],
        ),
        "signatures": sorted(
            signatures,
            key=lambda row: (
                row["timing"],
                row["resource_kinds"],
                row["attack_name"],
                row["card_name"],
            ),
        ),
    }
