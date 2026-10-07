"""Rulebook-backed cardinality for fixed unrestricted deck searches.

This module intentionally covers one semantic island: effects that literally
search the deck for exactly ``a card`` or exactly ``N cards`` without a target
restriction after ``card(s)``. Under the Advanced Player's Rulebook deck-search
rule, once such a search occurs the player must take the stated number, limited
only by how many cards physically remain in the deck.

That differs from restricted searches such as ``a Pokémon`` or ``an Item card``:
restricted deck searches may select fewer targets, including zero.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import json
from pathlib import Path
import re
from typing import Any, Mapping, Sequence

from build_expanded_legality_baseline import classify_effective_legality


_UNRESTRICTED_FIXED_RE = re.compile(
    r"search your deck for (?:(a) card|(\d+) cards)"
    r"(?=\s*(?:,|\.|and put|shuffle))",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class UnrestrictedSearchEffect:
    card_id: str
    name: str
    supertype: str
    source_kind: str
    source_name: str
    specified_count: int
    destination: str
    text: str


@dataclass(frozen=True)
class SelectionBounds:
    minimum: int
    maximum: int


@dataclass(frozen=True)
class SelectionWitness:
    group_names: tuple[str, ...]
    selected_counts: tuple[int, ...]

    @property
    def selected_total(self) -> int:
        return sum(self.selected_counts)


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _legal_expanded_cards(resources_root: Path) -> list[dict[str, Any]]:
    sets = _load_json(resources_root / "sets" / "en.json")
    expanded_sets = {
        entry["id"]
        for entry in sets
        if (entry.get("legalities") or {}).get("expanded") == "Legal"
    }

    cards: list[dict[str, Any]] = []
    for path in sorted((resources_root / "cards" / "en").glob("*.json")):
        if path.stem not in expanded_sets:
            continue
        for card in _load_json(path):
            if classify_effective_legality(card)[0] != "Legal":
                continue
            cards.append(card)
    return cards


def _effect_texts(card: Mapping[str, Any]) -> tuple[tuple[str, str, str], ...]:
    rows: list[tuple[str, str, str]] = []
    if card.get("supertype") == "Trainer":
        for index, rule in enumerate(card.get("rules") or []):
            rows.append(("trainer_rule", str(index), rule))
    for ability in card.get("abilities") or []:
        rows.append(("ability", ability.get("name", ""), ability.get("text", "")))
    for attack in card.get("attacks") or []:
        rows.append(("attack", attack.get("name", ""), attack.get("text", "")))
    return tuple(rows)


def _destination(text: str) -> str:
    if re.search(r"put (?:it|that card|those cards) into your hand", text, re.IGNORECASE):
        return "hand"
    if re.search(r"put (?:that card|those cards) on top", text, re.IGNORECASE):
        return "top_deck"
    raise ValueError(f"unsupported unrestricted-search destination: {text!r}")


def catalog_unrestricted_fixed_searches(
    resources_root: Path = Path("resources"),
) -> tuple[UnrestrictedSearchEffect, ...]:
    """Catalog literal exact-count unrestricted searches in legal Expanded prints."""

    rows: list[UnrestrictedSearchEffect] = []
    for card in _legal_expanded_cards(resources_root):
        for source_kind, source_name, text in _effect_texts(card):
            for match in _UNRESTRICTED_FIXED_RE.finditer(text):
                count = 1 if match.group(1) is not None else int(match.group(2))
                rows.append(
                    UnrestrictedSearchEffect(
                        card_id=card["id"],
                        name=card["name"],
                        supertype=card.get("supertype", ""),
                        source_kind=source_kind,
                        source_name=source_name,
                        specified_count=count,
                        destination=_destination(text),
                        text=text,
                    )
                )
    return tuple(sorted(rows, key=lambda row: (row.card_id, row.source_kind, row.source_name)))


def unrestricted_fixed_bounds(*, specified_count: int, deck_size: int) -> SelectionBounds:
    """Return legal selected-card bounds once an unrestricted fixed search occurs."""

    if specified_count <= 0:
        raise ValueError("specified_count must be positive")
    if deck_size < 0:
        raise ValueError("deck_size must be non-negative")
    required = min(specified_count, deck_size)
    return SelectionBounds(required, required)


def restricted_fixed_bounds(*, specified_count: int, eligible_count: int) -> SelectionBounds:
    """Return bounds for a type-limited deck search under the rulebook's fail-search rule."""

    if specified_count <= 0:
        raise ValueError("specified_count must be positive")
    if eligible_count < 0:
        raise ValueError("eligible_count must be non-negative")
    return SelectionBounds(0, min(specified_count, eligible_count))


def enumerate_unrestricted_fixed_selections(
    groups: Sequence[tuple[str, int]],
    *,
    specified_count: int,
) -> tuple[SelectionWitness, ...]:
    """Enumerate exact physical group-count witnesses for an unrestricted search.

    The selected total is forced to ``min(specified_count, deck_size)``. This
    exposes mandatory filler cards when the strategically desired subset is
    smaller than the physical search cardinality.
    """

    names = tuple(name for name, _ in groups)
    counts = tuple(count for _, count in groups)
    if len(names) != len(set(names)):
        raise ValueError("group names must be unique")
    if any(not name for name in names):
        raise ValueError("group names must be non-empty")
    if any(count < 0 for count in counts):
        raise ValueError("group counts must be non-negative")

    required = unrestricted_fixed_bounds(
        specified_count=specified_count,
        deck_size=sum(counts),
    ).minimum
    witnesses: list[SelectionWitness] = []

    def visit(index: int, remaining: int, selected: list[int]) -> None:
        if index == len(counts):
            if remaining == 0:
                witnesses.append(SelectionWitness(names, tuple(selected)))
            return
        max_take = min(counts[index], remaining)
        for take in range(max_take + 1):
            selected.append(take)
            visit(index + 1, remaining - take, selected)
            selected.pop()

    visit(0, required, [])
    return tuple(sorted(witnesses, key=lambda row: row.selected_counts))


def summarize_catalog(
    rows: Sequence[UnrestrictedSearchEffect],
) -> dict[str, Any]:
    source_counts = Counter(row.source_kind for row in rows)
    count_counts = Counter(row.specified_count for row in rows)
    destination_counts = Counter(row.destination for row in rows)
    return {
        "print_effects": len(rows),
        "unique_names": len({row.name for row in rows}),
        "source_kind_counts": dict(sorted(source_counts.items())),
        "specified_count_counts": {str(key): value for key, value in sorted(count_counts.items())},
        "destination_counts": dict(sorted(destination_counts.items())),
    }
