from __future__ import annotations

from pathlib import Path
import re
from typing import Any

from build_expanded_legality_baseline import OFFICIAL_BAN_OVERLAY, gameplay_fingerprint, load_json

CAPACITY_RE = re.compile(
    r"(?:can have up to (?P<up_to>\d+) Pokémon on (?:your|their) Bench|"
    r"can have (?P<can_have>\d+) Pokémon on (?:his or her|your|their) Bench|"
    r"can't have more than (?P<max_benched>\d+) Benched Pokémon)",
    re.IGNORECASE,
)


def scan_bench_capacity_effects(resources_root: Path) -> dict[str, Any]:
    sets = load_json(resources_root / "sets" / "en.json")
    expanded_sets = {
        row["id"]
        for row in sets
        if (row.get("legalities") or {}).get("expanded") == "Legal"
    }

    rows: list[dict[str, Any]] = []
    for path in sorted((resources_root / "cards" / "en").glob("*.json")):
        if path.stem not in expanded_sets:
            continue
        for card in load_json(path):
            status = (card.get("legalities") or {}).get("expanded")
            if card["id"] in OFFICIAL_BAN_OVERLAY or status == "Banned":
                continue

            sources: list[tuple[str, str | None, str]] = []
            if card.get("supertype") == "Trainer":
                sources.append(
                    (
                        "Trainer:" + ",".join(card.get("subtypes") or []),
                        None,
                        " ".join(card.get("rules") or []),
                    )
                )
            for ability in card.get("abilities") or []:
                sources.append(("Ability", ability.get("name"), ability.get("text", "")))

            for source_class, source_name, text in sources:
                match = CAPACITY_RE.search(text)
                if match is None:
                    continue
                capacity = int(next(value for value in match.groupdict().values() if value))
                lower = text.lower()
                if "your opponent can't have" in lower:
                    scope = "opponent"
                elif "this ↓ player can't have" in lower:
                    scope = "chosen_side"
                elif "each player" in lower:
                    scope = "both"
                elif "your bench" in lower:
                    scope = "self"
                else:
                    scope = "unknown"

                rows.append(
                    {
                        "id": card["id"],
                        "name": card["name"],
                        "fingerprint": gameplay_fingerprint(card),
                        "source_class": source_class,
                        "source_name": source_name,
                        "capacity": capacity,
                        "scope": scope,
                        "conditional": bool(
                            re.search(r"\bif\b|\bas long as\b", text, re.IGNORECASE)
                        ),
                        "active_dependent": bool(
                            re.search(
                                r"as long as this Pokémon is in the Active Spot",
                                text,
                                re.IGNORECASE,
                            )
                        ),
                        "collapse_instruction": bool(
                            re.search(
                                r"discard (?:Pokémon|Benched Pokémon) from .*Bench until",
                                text,
                                re.IGNORECASE,
                            )
                        ),
                        "text": text,
                    }
                )

    signatures: dict[tuple[str, str, str | None, int, str, str], dict[str, Any]] = {}
    for row in rows:
        key = (
            row["name"],
            row["source_class"],
            row["source_name"],
            row["capacity"],
            row["scope"],
            row["text"],
        )
        signatures.setdefault(key, row)

    return {
        "print_count": len(rows),
        "signature_count": len(signatures),
        "unique_names": len({row["name"] for row in rows}),
        "gameplay_variants": len({row["fingerprint"] for row in rows}),
        "names": sorted({row["name"] for row in rows}),
        "signatures": sorted(
            signatures.values(),
            key=lambda row: (row["capacity"], row["name"], row["text"]),
        ),
        "prints": rows,
    }
