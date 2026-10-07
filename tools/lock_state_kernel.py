from __future__ import annotations

from dataclasses import dataclass, replace


@dataclass(frozen=True)
class PlayerChannels:
    item_play: bool = True
    tool_play: bool = True
    supporter_play: bool = True
    stadium_play: bool = True
    pokemon_play: bool = True
    basic_energy_play: bool = True
    special_energy_play: bool = True


@dataclass(frozen=True)
class PokemonState:
    tool_attached: bool = False
    tool_effect_enabled: bool = True
    temporary_attack_lock: bool = False
    temporary_retreat_lock: bool = False


def apply_play_lock(channels: PlayerChannels, dimension: str) -> PlayerChannels:
    if dimension == "item":
        return replace(channels, item_play=False)
    if dimension == "tool":
        return replace(channels, tool_play=False)
    if dimension == "supporter":
        return replace(channels, supporter_play=False)
    if dimension == "stadium":
        return replace(channels, stadium_play=False)
    if dimension == "pokemon":
        return replace(channels, pokemon_play=False)
    if dimension == "basic_energy_play":
        return replace(channels, basic_energy_play=False)
    if dimension == "special_energy_play":
        return replace(channels, special_energy_play=False)
    if dimension == "trainer":
        return replace(
            channels,
            item_play=False,
            tool_play=False,
            supporter_play=False,
            stadium_play=False,
        )
    if dimension == "all_cards_from_hand":
        return PlayerChannels(
            item_play=False,
            tool_play=False,
            supporter_play=False,
            stadium_play=False,
            pokemon_play=False,
            basic_energy_play=False,
            special_energy_play=False,
        )
    raise ValueError(f"Unsupported play-lock dimension: {dimension}")


def suppress_tool_effect(pokemon: PokemonState) -> PokemonState:
    if not pokemon.tool_attached:
        return pokemon
    return replace(pokemon, tool_effect_enabled=False)


def restore_tool_effect(pokemon: PokemonState) -> PokemonState:
    if not pokemon.tool_attached:
        return pokemon
    return replace(pokemon, tool_effect_enabled=True)


def apply_temporary_attack_lock(pokemon: PokemonState) -> PokemonState:
    return replace(pokemon, temporary_attack_lock=True)


def apply_temporary_retreat_lock(pokemon: PokemonState) -> PokemonState:
    return replace(pokemon, temporary_retreat_lock=True)


def clear_attack_effects_on_position_or_evolution_change(pokemon: PokemonState) -> PokemonState:
    return replace(
        pokemon,
        temporary_attack_lock=False,
        temporary_retreat_lock=False,
    )


def garbotoxin_condition_met(garbodor: PokemonState) -> bool:
    return garbodor.tool_attached


def stealthy_hood_protects(holder: PokemonState) -> bool:
    return holder.tool_attached and holder.tool_effect_enabled
