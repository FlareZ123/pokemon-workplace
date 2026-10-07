"""Catalog paper-Expanded Trainer effects that discard from hand before deck search.

This is a conservative text-order catalog. It looks for legal Trainer cards whose
literal rules text contains an explicit hand-discard instruction before the first
"search your deck" instruction.

The catalog is intentionally narrower than a full timing compiler. It does not
infer reordered timing for effects whose printed search clause appears first,
such as TAG TEAM Supporters with a later "When you play this card" clause.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
import json
from pathlib import Path
import re
from typing import Iterable

from build_expanded_legality_baseline import (
    classify_effective_legality,
    gameplay_fingerprint,
    load_json,
)


HAND_DISCARD_RE = re.compile(
    r"(discard(?:\s+up to)?[^.]{0,120}?from your hand|discard your hand)",
    re.IGNORECASE,
)
SEARCH_RE = re.compile(r"search your deck", re.IGNORECASE)


@dataclass(frozen=True)
class CostBeforeSearchPrint:
    card_id: str
    name: str
    subtypes: tuple[str, ...]
    rules_text: str
    discard_clause: str
    discard_mode: str
    stochastic_after_discard: bool
    gameplay_fingerprint: str


def normalize_space(text: str) -> str:
    return " ".join(text.split())


def discard_mode(clause: str) -> str:
    low = normalize_space(clause).lower()
    if low == "discard your hand":
        return "whole_hand"
    if "other card" in low or "cards from your hand" in low or "a card from your hand" in low:
        # Some typed costs also contain "cards from your hand", so classify them first.
        if any(
            token in low
            for token in (
                "water energy",
                "metal energy",
                "item card",
            )
        ):
            return "typed_selective"
        return "selective"
    return "typed_selective"


def scan_card(card: dict) -> CostBeforeSearchPrint | None:
    if card.get("supertype") != "Trainer":
        return None

    status, _source = classify_effective_legality(card)
    if status != "Legal":
        return None

    rules = card.get("rules") or []
    if not rules:
        return None
    text = normalize_space(" ".join(rules))

    search = SEARCH_RE.search(text)
    if search is None:
        return None

    discard_matches = [
        match
        for match in HAND_DISCARD_RE.finditer(text)
        if match.start() < search.start()
    ]
    if not discard_matches:
        return None

    match = discard_matches[0]
    between = text[match.end() : search.start()].lower()
    stochastic = "flip a coin" in between

    return CostBeforeSearchPrint(
        card_id=card["id"],
        name=card["name"],
        subtypes=tuple(card.get("subtypes") or ()),
        rules_text=text,
        discard_clause=normalize_space(match.group(0)),
        discard_mode=discard_mode(match.group(0)),
        stochastic_after_discard=stochastic,
        gameplay_fingerprint=gameplay_fingerprint(card),
    )


def iter_expanded_cards(resources_root: Path) -> Iterable[dict]:
    sets = load_json(resources_root / "sets" / "en.json")
    expanded_sets = {
        entry["id"]
        for entry in sets
        if (entry.get("legalities") or {}).get("expanded") == "Legal"
    }
    for path in sorted((resources_root / "cards" / "en").glob("*.json")):
        if path.stem not in expanded_sets:
            continue
        yield from load_json(path)


def build_catalog(resources_root: Path = Path("resources")) -> dict:
    prints = tuple(
        row
        for card in iter_expanded_cards(resources_root)
        if (row := scan_card(card)) is not None
    )

    by_name: dict[str, list[CostBeforeSearchPrint]] = defaultdict(list)
    for row in prints:
        by_name[row.name].append(row)

    names = []
    for name, rows in sorted(by_name.items()):
        modes = sorted({row.discard_mode for row in rows})
        clauses = sorted({row.discard_clause for row in rows})
        texts = sorted({row.rules_text for row in rows})
        names.append(
            {
                "name": name,
                "print_count": len(rows),
                "print_ids": sorted(row.card_id for row in rows),
                "subtypes": sorted({subtype for row in rows for subtype in row.subtypes}),
                "discard_modes": modes,
                "discard_clauses": clauses,
                "stochastic_after_discard": any(
                    row.stochastic_after_discard for row in rows
                ),
                "distinct_rules_texts": len(texts),
                "distinct_gameplay_fingerprints": len(
                    {row.gameplay_fingerprint for row in rows}
                ),
            }
        )

    mode_counts: dict[str, int] = defaultdict(int)
    for entry in names:
        for mode in entry["discard_modes"]:
            mode_counts[mode] += 1

    return {
        "print_count": len(prints),
        "unique_names": len(names),
        "unique_gameplay_fingerprints": len(
            {row.gameplay_fingerprint for row in prints}
        ),
        "name_counts_by_discard_mode": dict(sorted(mode_counts.items())),
        "stochastic_names": sorted(
            entry["name"] for entry in names if entry["stochastic_after_discard"]
        ),
        "names": names,
    }


def main() -> None:
    catalog = build_catalog()
    print(json.dumps(catalog, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
