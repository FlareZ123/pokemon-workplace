"""Card-grounded Pokemon HP, type, weakness, resistance, and Prize profiles."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path

from build_expanded_legality_baseline import classify_effective_legality
from combat_data_overrides import apply_combat_data_overrides
from delayed_ko_window import printed_prize_value
from type_modifier_catalog import ParsedTypeModifier, parse_type_modifier


@dataclass(frozen=True)
class TypedModifier:
    energy_type: str
    modifier: ParsedTypeModifier


@dataclass(frozen=True)
class PokemonCardProfile:
    print_id: str
    name: str
    hp: int
    types: tuple[str, ...]
    weaknesses: tuple[TypedModifier, ...]
    resistances: tuple[TypedModifier, ...]
    prize_value: int


def compile_pokemon_card_profile(card: dict) -> PokemonCardProfile:
    row = apply_combat_data_overrides(card)
    if row.get("supertype") != "Pokémon":
        raise ValueError("profile requires a Pokemon card")
    hp = int(row["hp"])
    if hp <= 0 or hp % 10 != 0:
        raise ValueError("Pokemon HP must be a positive multiple of 10")
    weaknesses = tuple(
        TypedModifier(item["type"], parse_type_modifier(item["value"]))
        for item in (row.get("weaknesses") or ())
    )
    resistances = tuple(
        TypedModifier(item["type"], parse_type_modifier(item["value"]))
        for item in (row.get("resistances") or ())
    )
    return PokemonCardProfile(
        print_id=row["id"],
        name=row["name"],
        hp=hp,
        types=tuple(row.get("types") or ()),
        weaknesses=weaknesses,
        resistances=resistances,
        prize_value=printed_prize_value(row),
    )


def build_pokemon_card_profile_index(resources_root: Path) -> dict[str, PokemonCardProfile]:
    sets = json.loads((resources_root / "sets" / "en.json").read_text(encoding="utf-8"))
    expanded_sets = {
        row["id"] for row in sets
        if (row.get("legalities") or {}).get("expanded") == "Legal"
    }
    profiles: dict[str, PokemonCardProfile] = {}
    for path in sorted((resources_root / "cards" / "en").glob("*.json")):
        if path.stem not in expanded_sets:
            continue
        for card in json.loads(path.read_text(encoding="utf-8")):
            if classify_effective_legality(card)[0] != "Legal":
                continue
            if card.get("supertype") != "Pokémon" or not card.get("hp"):
                continue
            profile = compile_pokemon_card_profile(card)
            profiles[profile.print_id] = profile
    return profiles


def hp_by_board_object(board, profiles: dict[str, PokemonCardProfile]) -> dict[str, int]:
    result: dict[str, int] = {}
    for pokemon in board.objects:
        if pokemon.print_id is None:
            raise ValueError(f"board object {pokemon.object_id!r} has no print_id")
        profile = profiles.get(pokemon.print_id)
        if profile is None:
            raise ValueError(f"no legal profile for {pokemon.print_id!r}")
        result[pokemon.object_id] = profile.hp
    return result
