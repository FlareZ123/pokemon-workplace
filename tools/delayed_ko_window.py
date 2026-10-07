"""Analytic delayed-KO windows plus corpus coverage for two-stage damage lines."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import json
from pathlib import Path
import re

from build_expanded_legality_baseline import (
    classify_effective_legality,
    gameplay_fingerprint,
)


@dataclass(frozen=True)
class DelayedKoWindow:
    first_damage: int
    later_damage_counters: int

    def __post_init__(self) -> None:
        if self.first_damage < 0 or self.first_damage % 10 != 0:
            raise ValueError("first_damage must be a non-negative multiple of 10")
        if self.later_damage_counters < 0:
            raise ValueError("later_damage_counters must be non-negative")

    @property
    def min_remaining_hp(self) -> int:
        """Smallest pre-first-hit remaining HP that survives the first hit."""

        return self.first_damage + 10

    @property
    def max_remaining_hp(self) -> int:
        """Largest pre-first-hit remaining HP finished by the later counters."""

        return self.first_damage + 10 * self.later_damage_counters

    def qualifies(
        self,
        *,
        hp: int,
        existing_damage_counters: int = 0,
    ) -> bool:
        if hp <= 0 or hp % 10 != 0:
            raise ValueError("hp must be a positive multiple of 10")
        if existing_damage_counters < 0:
            raise ValueError("existing_damage_counters must be non-negative")
        remaining = hp - 10 * existing_damage_counters
        return self.min_remaining_hp <= remaining <= self.max_remaining_hp


_PRIZE_RE = re.compile(r"takes? (\d+) Prize card", re.IGNORECASE)


def printed_prize_value(card: dict) -> int:
    value = 1
    for rule in card.get("rules") or ():
        match = _PRIZE_RE.search(rule)
        if match is not None:
            value = max(value, int(match.group(1)))
    return value


def build_window_catalog(
    resources_root: Path,
    window: DelayedKoWindow,
) -> dict[str, object]:
    sets = json.loads(
        (resources_root / "sets" / "en.json").read_text(encoding="utf-8")
    )
    expanded_sets = {
        row["id"]
        for row in sets
        if (row.get("legalities") or {}).get("expanded") == "Legal"
    }

    all_pokemon = []
    matching = []
    for path in sorted((resources_root / "cards" / "en").glob("*.json")):
        if path.stem not in expanded_sets:
            continue
        for card in json.loads(path.read_text(encoding="utf-8")):
            if classify_effective_legality(card)[0] != "Legal":
                continue
            if card.get("supertype") != "Pokémon" or not card.get("hp"):
                continue
            try:
                hp = int(card["hp"])
            except (TypeError, ValueError):
                continue

            row = {
                "card_id": card["id"],
                "name": card["name"],
                "hp": hp,
                "prize_value": printed_prize_value(card),
                "fingerprint": gameplay_fingerprint(card),
            }
            all_pokemon.append(row)
            if window.qualifies(hp=hp):
                matching.append(row)

    by_fingerprint = {}
    for row in matching:
        by_fingerprint.setdefault(row["fingerprint"], row)

    hp_counts = Counter(row["hp"] for row in matching)
    prize_counts = Counter(row["prize_value"] for row in matching)
    fingerprint_prize_counts = Counter(
        row["prize_value"] for row in by_fingerprint.values()
    )

    return {
        "window": {
            "min_remaining_hp": window.min_remaining_hp,
            "max_remaining_hp": window.max_remaining_hp,
        },
        "legal_pokemon_prints": len(all_pokemon),
        "matching_prints": len(matching),
        "matching_unique_names": len({row["name"] for row in matching}),
        "matching_distinct_fingerprints": len(by_fingerprint),
        "matching_prints_by_hp": dict(sorted(hp_counts.items())),
        "matching_prints_by_prize_value": dict(sorted(prize_counts.items())),
        "matching_fingerprints_by_prize_value": dict(
            sorted(fingerprint_prize_counts.items())
        ),
    }
