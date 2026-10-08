"""Compose canonical Stadium-entry transitions with finite Bench capacity.

Uses physical Stadium copies and source-specific Teleport Room tracking from
stadium_entry_channels, then applies effective Bench capacity and forced
Benched-Pokémon discards after each Stadium transition.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from itertools import combinations

from bench_capacity_model import effective_capacity
from stadium_entry_channels import (
    StadiumCopy,
    StadiumEntryState,
    play_stadium_from_hand,
    teleport_room_options,
)
from turn_action_budget import TurnActionBudget


@dataclass(frozen=True)
class BenchPokemon:
    copy_id: str
    tera: bool = False
    teleport_room: bool = False


@dataclass(frozen=True)
class BenchTeleportState:
    stadiums: StadiumEntryState
    active: BenchPokemon
    bench: tuple[BenchPokemon, ...]
    hand_pokemon: tuple[BenchPokemon, ...]
    ability_locked: bool = False
    opponent_roadblock_live: bool = False

    def __post_init__(self) -> None:
        all_pokemon = (self.active,) + self.bench + self.hand_pokemon
        identifiers = [mon.copy_id for mon in all_pokemon]
        if len(identifiers) != len(set(identifiers)):
            raise ValueError("A physical Pokemon cannot occupy two zones")
        live_sources = frozenset(
            mon.copy_id for mon in (self.active,) + self.bench
            if mon.teleport_room
        )
        if live_sources != self.stadiums.teleport_room_sources:
            raise ValueError("Teleport Room source must physically be in play")
        if len(self.bench) > bench_capacity(self):
            raise ValueError("Initial Bench exceeds current effective capacity")


def _capacity_for(
    stadium: StadiumCopy | None,
    active: BenchPokemon,
    bench: tuple[BenchPokemon, ...],
    opponent_roadblock_live: bool,
) -> int:
    name = stadium.name if stadium else None
    expansion = (
        (8,) if name == "Sky Field"
        or (name == "Area Zero Underdepths"
            and any(mon.tera for mon in (active,) + bench))
        else ()
    )
    restriction = (
        (4,) if name == "Collapsed Stadium" or opponent_roadblock_live else ()
    )
    return effective_capacity(expansion, restriction)

def bench_capacity(state: BenchTeleportState) -> int:
    return _capacity_for(state.stadiums.in_play, state.active, state.bench, state.opponent_roadblock_live)

def _settle_stadium_change(
    state: BenchTeleportState, stadiums: StadiumEntryState
) -> tuple[BenchTeleportState, ...]:
    """Apply mandatory capacity contraction, enumerating owner's discard choices."""
    limit = _capacity_for(stadiums.in_play, state.active, state.bench, state.opponent_roadblock_live)
    occupied = len(state.bench)
    if occupied <= limit:
        return (replace(state, stadiums=stadiums),)
    outcomes = []
    for positions in combinations(range(occupied), limit):
        survivors = tuple(state.bench[i] for i in positions)
        sources = frozenset(
            mon.copy_id for mon in (state.active,) + survivors
            if mon.teleport_room
        )
        adjusted_stadiums = replace(
            stadiums,
            teleport_room_sources=sources,
            teleport_room_used=stadiums.teleport_room_used & sources,
        )
        outcomes.append(replace(state, stadiums=adjusted_stadiums, bench=survivors))
    return tuple(outcomes)


def teleport_room(state: BenchTeleportState, source_id: str) -> tuple[BenchTeleportState, ...]:
    """Effect-based Stadium removal/replacement; no Stadium-play quota consumed."""
    if state.ability_locked:
        return ()
    return tuple(
        outcome
        for next_stadiums in teleport_room_options(state.stadiums, source_id)
        for outcome in _settle_stadium_change(state, next_stadiums)
    )


def play_stadium(
    state: BenchTeleportState, copy_id: str
) -> tuple[BenchTeleportState, ...]:
    """Ordinary play from hand; consumes the canonical Stadium-play quota."""
    changed = play_stadium_from_hand(state.stadiums, copy_id)
    return () if changed is None else _settle_stadium_change(state, changed)


def bench_from_hand(
    state: BenchTeleportState, copy_id: str
) -> BenchTeleportState | None:
    if state.stadiums.budget.turn_ended or len(state.bench) >= bench_capacity(state):
        return None
    match = next((mon for mon in state.hand_pokemon if mon.copy_id == copy_id), None)
    if match is None:
        return None
    remaining = tuple(mon for mon in state.hand_pokemon if mon.copy_id != copy_id)
    sources = state.stadiums.teleport_room_sources
    if match.teleport_room:
        sources = sources | frozenset({match.copy_id})
    stadiums = replace(state.stadiums, teleport_room_sources=sources)
    return replace(
        state,
        stadiums=stadiums,
        bench=state.bench + (match,),
        hand_pokemon=remaining,
    )


def sample_state(
    *,
    discarded_stadiums: tuple[StadiumCopy, ...] = (),
    hand_stadiums: tuple[StadiumCopy, ...] = (),
    hand_pokemon: tuple[BenchPokemon, ...] = (),
    stadium_plays_used: int = 0,
    ability_locked: bool = False,
    opponent_roadblock_live: bool = False,
) -> BenchTeleportState:
    """Four full Bench occupants, a live Active Gothitelle, Collapsed Stadium."""
    goth = BenchPokemon("goth-1", teleport_room=True)
    stadiums = StadiumEntryState(
        budget=TurnActionBudget(stadium_plays_used=stadium_plays_used),
        in_play=StadiumCopy("collapsed-1", "Collapsed Stadium"),
        discard=discarded_stadiums,
        hand=hand_stadiums,
        teleport_room_sources=frozenset({goth.copy_id}),
    )
    return BenchTeleportState(
        stadiums=stadiums,
        active=goth,
        bench=tuple(BenchPokemon(f"core-{i}") for i in range(4)),
        hand_pokemon=hand_pokemon,
        ability_locked=ability_locked,
        opponent_roadblock_live=opponent_roadblock_live,
    )
