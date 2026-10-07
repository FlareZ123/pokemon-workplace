"""Compile legal Pokemon card metadata needed by physical board objects."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from build_expanded_legality_baseline import classify_effective_legality, load_json
from card_search_target_index import semantic_tags_for_card
from typed_search_target_allocator import POKEMON


@dataclass(frozen=True)
class PokemonBoardMetadata:
    card_id: str
    name: str
    evolves_from: str | None
    retreat_cost: int
    tags: frozenset[str]

    def __post_init__(self) -> None:
        if not self.card_id or not self.name:
            raise ValueError("card_id and name must be non-empty")
        if self.retreat_cost < 0:
            raise ValueError("retreat_cost must be non-negative")
        if POKEMON not in self.tags:
            raise ValueError("Pokemon board metadata must carry the Pokemon tag")


def _retreat_cost(card: dict) -> int:
    converted = card.get("convertedRetreatCost")
    if converted is not None:
        value = int(converted)
    else:
        value = len(card.get("retreatCost") or ())
    if value < 0:
        raise ValueError(f"negative retreat cost on {card.get('id')!r}")
    return value


def load_legal_pokemon_board_metadata(
    resources_root: Path = Path("resources"),
) -> tuple[PokemonBoardMetadata, ...]:
    """Load exact effectively legal Pokemon prints in the paper Expanded scope."""

    sets = load_json(resources_root / "sets" / "en.json")
    expanded_sets = {
        row["id"]
        for row in sets
        if (row.get("legalities") or {}).get("expanded") == "Legal"
    }

    rows: list[PokemonBoardMetadata] = []
    seen: set[str] = set()
    for path in sorted((resources_root / "cards" / "en").glob("*.json")):
        if path.stem not in expanded_sets:
            continue
        for card in load_json(path):
            if card.get("supertype") != "Pokémon":
                continue
            status, _source = classify_effective_legality(card)
            if status != "Legal":
                continue
            card_id = card["id"]
            if card_id in seen:
                raise ValueError(f"duplicate Pokemon card ID: {card_id}")
            seen.add(card_id)
            rows.append(
                PokemonBoardMetadata(
                    card_id=card_id,
                    name=card["name"],
                    evolves_from=card.get("evolvesFrom"),
                    retreat_cost=_retreat_cost(card),
                    tags=semantic_tags_for_card(card),
                )
            )

    return tuple(sorted(rows, key=lambda row: row.card_id))


def pokemon_board_metadata_by_id(
    resources_root: Path = Path("resources"),
) -> dict[str, PokemonBoardMetadata]:
    """Index legal Pokemon board metadata by exact print ID."""

    rows = load_legal_pokemon_board_metadata(resources_root)
    return {row.card_id: row for row in rows}
