"""Catalog legal effects that depend on a Bench-to-Active movement event."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import json
from pathlib import Path
import re
from typing import Any, Literal

from build_expanded_legality_baseline import classify_effective_legality


DependencyKind = Literal[
    "self_move_ability_trigger",
    "named_ally_move_ability_trigger",
    "self_move_attack_condition",
    "opponent_last_turn_attack_condition",
]


@dataclass(frozen=True)
class BenchToActiveDependency:
    card_id: str
    card_name: str
    source_kind: str
    source_name: str
    source_text: str
    dependency_kind: DependencyKind


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _normalized(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _legal_expanded_cards(resources_root: Path) -> tuple[dict[str, Any], ...]:
    sets = _load_json(resources_root / "sets" / "en.json")
    expanded_sets = {
        row["id"]
        for row in sets
        if (row.get("legalities") or {}).get("expanded") == "Legal"
    }

    cards: list[dict[str, Any]] = []
    for path in sorted((resources_root / "cards" / "en").glob("*.json")):
        if path.stem not in expanded_sets:
            continue
        for card in _load_json(path):
            if classify_effective_legality(card)[0] == "Legal":
                cards.append(card)
    return tuple(cards)


def _ability_kind(text: str) -> DependencyKind | None:
    if "when this Pokémon moves from your Bench to the Active Spot" in text:
        return "self_move_ability_trigger"
    if "when your Mega Latias ex moves from your Bench to the Active Spot" in text:
        return "named_ally_move_ability_trigger"
    return None


def _attack_kind(text: str) -> DependencyKind | None:
    if text.startswith(
        "If this Pokémon moved from your Bench to the Active Spot this turn"
    ):
        return "self_move_attack_condition"
    if text.startswith(
        "If your opponent's Active Pokémon moved from the Bench to the Active Spot "
        "during your opponent's last turn"
    ):
        return "opponent_last_turn_attack_condition"
    return None


def build_bench_to_active_dependency_catalog(
    resources_root: Path = Path("resources"),
) -> tuple[BenchToActiveDependency, ...]:
    rows: list[BenchToActiveDependency] = []
    for card in _legal_expanded_cards(resources_root):
        if card.get("supertype") != "Pokémon":
            continue

        for ability in card.get("abilities") or ():
            text = _normalized(ability.get("text") or "")
            kind = _ability_kind(text)
            if kind is None:
                continue
            rows.append(
                BenchToActiveDependency(
                    card_id=card["id"],
                    card_name=card["name"],
                    source_kind="ability",
                    source_name=ability["name"],
                    source_text=text,
                    dependency_kind=kind,
                )
            )

        for attack in card.get("attacks") or ():
            text = _normalized(attack.get("text") or "")
            kind = _attack_kind(text)
            if kind is None:
                continue
            rows.append(
                BenchToActiveDependency(
                    card_id=card["id"],
                    card_name=card["name"],
                    source_kind="attack",
                    source_name=attack["name"],
                    source_text=text,
                    dependency_kind=kind,
                )
            )

    return tuple(
        sorted(
            rows,
            key=lambda row: (
                row.dependency_kind,
                row.card_name,
                row.card_id,
                row.source_name,
            ),
        )
    )


def summarize_catalog(
    rows: tuple[BenchToActiveDependency, ...],
) -> dict[str, object]:
    return {
        "profiles": len(rows),
        "names": len({row.card_name for row in rows}),
        "source_kind": dict(sorted(Counter(row.source_kind for row in rows).items())),
        "dependency_kind": dict(
            sorted(Counter(row.dependency_kind for row in rows).items())
        ),
    }
