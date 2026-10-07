"""Audit Aichi decklist names against the bundled English card snapshot."""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

ALIASES = {"Target Whistle": "Target Whistle Team Flare Gear"}


@dataclass(frozen=True)
class Resolution:
    exact_names: tuple[str, ...]
    aliased_names: tuple[tuple[str, str], ...]
    missing_names: tuple[str, ...]
    missing_copies: int


def load_card_names(cards_dir: Path) -> dict[str, tuple[dict, ...]]:
    by_name: dict[str, list[dict]] = {}
    for path in sorted(cards_dir.glob("*.json")):
        for card in json.loads(path.read_text(encoding="utf-8")):
            by_name.setdefault(card["name"], []).append(card)
    return {name: tuple(cards) for name, cards in by_name.items()}


def normalize_display_name(name: str) -> str:
    return name.replace(" ♢", " ◇")


def resolve_counts(
    counts: dict[str, int],
    card_names: dict[str, tuple[dict, ...]],
) -> Resolution:
    exact: list[str] = []
    aliased: list[tuple[str, str]] = []
    missing: list[str] = []
    missing_copies = 0
    for display_name, copies in counts.items():
        name = normalize_display_name(display_name)
        if name in card_names:
            exact.append(display_name)
            continue
        alias = ALIASES.get(display_name)
        if alias and alias in card_names:
            aliased.append((display_name, alias))
            continue
        missing.append(display_name)
        missing_copies += copies
    return Resolution(
        tuple(sorted(exact)),
        tuple(sorted(aliased)),
        tuple(sorted(missing)),
        missing_copies,
    )
