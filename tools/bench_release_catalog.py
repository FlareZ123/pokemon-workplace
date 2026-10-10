from __future__ import annotations

from pathlib import Path
import re
from typing import Any

from build_expanded_legality_baseline import (
    classify_effective_legality,
    gameplay_fingerprint,
    load_json,
)

PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    (
        "to_hand",
        re.compile(
            r"\bput (?:1|any number) of your (?:Basic |Colorless )?Pokémon(?: in play)?\b.*?\binto your hand\b",
            re.IGNORECASE,
        ),
    ),
    (
        "benched_to_hand",
        re.compile(
            r"\bput 1 of your Benched Pokémon\b.*?\binto your hand\b",
            re.IGNORECASE,
        ),
    ),
    (
        "to_deck",
        re.compile(
            r"\bshuffle 1 of your (?:Benched )?Pokémon\b.*?\binto your deck\b",
            re.IGNORECASE,
        ),
    ),
    (
        "discard_bench",
        re.compile(
            r"\b(?:discard|you may discard) "
            r"(?:up to \d+ of |any number of |as many of |a number of |1 of |your other )"
            r"your Benched Pokémon(?: V| Dreepy)?\b",
            re.IGNORECASE,
        ),
    ),
    (
        "discard_bench",
        re.compile(r"\bthen, discard your other Benched Pokémon\b", re.IGNORECASE),
    ),
    (
        "species_bench_discard",
        re.compile(
            r"\bdiscard a number of your Benched [A-Z][A-Za-z' -]+ up to ",
            re.IGNORECASE,
        ),
    ),
    (
        "bench_limit_discard",
        re.compile(
            r"\beach player discards their Benched Pokémon until they have \d+ Benched Pokémon\b",
            re.IGNORECASE,
        ),
    ),
)


def _sources(card: dict[str, Any]) -> list[tuple[str, str | None, str]]:
    rows: list[tuple[str, str | None, str]] = []
    if card.get("supertype") == "Trainer":
        subtype = ",".join(card.get("subtypes") or [])
        rows.append(("Trainer:" + subtype, None, " ".join(card.get("rules") or [])))
    for ability in card.get("abilities") or []:
        rows.append(("Ability", ability.get("name"), ability.get("text", "")))
    for attack in card.get("attacks") or []:
        rows.append(("Attack", attack.get("name"), attack.get("text", "")))
    return rows


def scan_bench_release_catalog(resources_root: Path) -> dict[str, Any]:
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
            if classify_effective_legality(card)[0] != "Legal":
                continue
            for source_class, source_name, text in _sources(card):
                for release_kind, pattern in PATTERNS:
                    if not pattern.search(text):
                        continue
                    rows.append(
                        {
                            "id": card["id"],
                            "name": card["name"],
                            "fingerprint": gameplay_fingerprint(card),
                            "source_class": source_class,
                            "source_name": source_name,
                            "release_kind": release_kind,
                            "text": text,
                            "stochastic": bool(re.search(r"flip a coin", text, re.IGNORECASE)),
                            "ends_turn_by_rule": source_class == "Attack",
                            "uses_supporter_window": source_class.startswith("Trainer:Supporter"),
                        }
                    )
                    break

    signatures: dict[tuple[str, str, str | None, str, str], dict[str, Any]] = {}
    for row in rows:
        key = (
            row["name"],
            row["source_class"],
            row["source_name"],
            row["release_kind"],
            row["text"],
        )
        signatures.setdefault(key, row)

    source_counts: dict[str, int] = {}
    for row in signatures.values():
        source_counts[row["source_class"]] = source_counts.get(row["source_class"], 0) + 1

    return {
        "print_count": len(rows),
        "signature_count": len(signatures),
        "unique_names": len({row["name"] for row in rows}),
        "gameplay_variants": len({row["fingerprint"] for row in rows}),
        "source_signature_counts": dict(sorted(source_counts.items())),
        "names": sorted({row["name"] for row in rows}),
        "signatures": sorted(
            signatures.values(),
            key=lambda row: (
                row["source_class"],
                row["name"],
                row["source_name"] or "",
                row["release_kind"],
            ),
        ),
        "prints": rows,
    }
