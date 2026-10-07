"""Resolve compiled zone-exit geometry into concrete physical target sets."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from typing import Mapping

from board_position_state import BoardPokemon, BoardState
from pokemon_zone_exit_target_geometry import ZoneExitTargetProfile


OWN = "own"
OPPONENT = "opponent"


@dataclass(frozen=True)
class TargetRef:
    side: str
    pokemon_id: str


def _types_for(
    pokemon_id: str,
    types: Mapping[str, frozenset[str]] | None,
) -> frozenset[str]:
    if types is None or pokemon_id not in types:
        raise ValueError(
            f"Pokemon type metadata required for {pokemon_id}"
        )
    return types[pokemon_id]


def _matches_filter(
    pokemon: BoardPokemon,
    target_filter: str,
    *,
    types: Mapping[str, frozenset[str]] | None,
) -> bool:
    if target_filter == "none":
        return True
    if target_filter == "damaged":
        return pokemon.damage_counters > 0
    if target_filter == "basic":
        return pokemon.stack[-1].evolves_from is None
    if target_filter == "colorless_and_damaged":
        return (
            pokemon.damage_counters > 0
            and "Colorless" in _types_for(
                pokemon.pokemon_id,
                types,
            )
        )
    if target_filter == "exclude_name_corviknight":
        return pokemon.name != "Corviknight"
    if target_filter == "name_combee":
        return pokemon.name == "Combee"
    if target_filter == "unqualified_scope":
        raise ValueError(
            "unqualified AZ target scope requires authoritative normalization"
        )
    raise ValueError(f"unknown target filter: {target_filter}")


def _eligible(
    pokemon: tuple[BoardPokemon, ...],
    target_filter: str,
    *,
    types: Mapping[str, frozenset[str]] | None,
) -> tuple[BoardPokemon, ...]:
    return tuple(
        row
        for row in pokemon
        if _matches_filter(
            row,
            target_filter,
            types=types,
        )
    )


def _refs(
    side: str,
    pokemon: tuple[BoardPokemon, ...],
) -> tuple[TargetRef, ...]:
    return tuple(
        TargetRef(side, row.pokemon_id)
        for row in pokemon
    )


def resolve_zone_exit_target_sets(
    profile: ZoneExitTargetProfile,
    *,
    own_board: BoardState,
    opponent_board: BoardState,
    source_id: str | None = None,
    own_types: Mapping[str, frozenset[str]] | None = None,
    opponent_types: Mapping[str, frozenset[str]] | None = None,
) -> tuple[tuple[TargetRef, ...], ...]:
    """Enumerate target sets for one compiled direct-effect profile."""

    geometry = profile.target_geometry
    target_filter = profile.target_filter

    own_all = own_board.pokemon
    opponent_all = opponent_board.pokemon
    own_bench = tuple(
        row for row in own_all
        if row.pokemon_id != own_board.active_id
    )
    opponent_bench = tuple(
        row for row in opponent_all
        if row.pokemon_id != opponent_board.active_id
    )

    if geometry == "self":
        if source_id is None:
            raise ValueError("self geometry requires source_id")
        try:
            source = own_board.get(source_id)
        except StopIteration:
            return ()
        if not _matches_filter(
            source,
            target_filter,
            types=own_types,
        ):
            return ()
        return ((TargetRef(OWN, source_id),),)

    if geometry == "own_one":
        eligible = _eligible(
            own_all,
            target_filter,
            types=own_types,
        )
        return tuple(
            (target,)
            for target in _refs(OWN, eligible)
        )

    if geometry == "own_bench_one":
        eligible = _eligible(
            own_bench,
            target_filter,
            types=own_types,
        )
        return tuple(
            (target,)
            for target in _refs(OWN, eligible)
        )

    if geometry == "opponent_active":
        active = opponent_board.get(
            opponent_board.active_id
        )
        if not _matches_filter(
            active,
            target_filter,
            types=opponent_types,
        ):
            return ()
        return (
            (
                TargetRef(
                    OPPONENT,
                    opponent_board.active_id,
                ),
            ),
        )

    if geometry == "opponent_bench_one":
        eligible = _eligible(
            opponent_bench,
            target_filter,
            types=opponent_types,
        )
        return tuple(
            (target,)
            for target in _refs(
                OPPONENT,
                eligible,
            )
        )

    if geometry == "opponent_one":
        eligible = _eligible(
            opponent_all,
            target_filter,
            types=opponent_types,
        )
        return tuple(
            (target,)
            for target in _refs(
                OPPONENT,
                eligible,
            )
        )

    if geometry == "own_any_number":
        eligible = _eligible(
            own_all,
            target_filter,
            types=own_types,
        )
        own_refs = _refs(OWN, eligible)
        return tuple(
            tuple(selected)
            for size in range(len(own_refs) + 1)
            for selected in combinations(
                own_refs,
                size,
            )
        )

    if geometry == "opponent_bench_one_and_self":
        if source_id is None:
            raise ValueError(
                "mixed self geometry requires source_id"
            )
        try:
            own_board.get(source_id)
        except StopIteration:
            return ()
        eligible = _eligible(
            opponent_bench,
            target_filter,
            types=opponent_types,
        )
        source_ref = TargetRef(OWN, source_id)
        return tuple(
            (
                source_ref,
                target,
            )
            for target in _refs(
                OPPONENT,
                eligible,
            )
        )

    if geometry == "opponent_bench_all":
        eligible = _eligible(
            opponent_bench,
            target_filter,
            types=opponent_types,
        )
        return (
            _refs(
                OPPONENT,
                eligible,
            ),
        )

    if geometry == "opponent_bench_all_except_selected_three":
        eligible = _eligible(
            opponent_bench,
            target_filter,
            types=opponent_types,
        )
        opponent_refs = _refs(
            OPPONENT,
            eligible,
        )
        survivor_count = min(3, len(opponent_refs))
        return tuple(
            tuple(
                ref
                for ref in opponent_refs
                if ref not in survivors
            )
            for survivors_tuple in combinations(
                opponent_refs,
                survivor_count,
            )
            for survivors in (set(survivors_tuple),)
        )

    if geometry == "both_active":
        return (
            (
                TargetRef(OWN, own_board.active_id),
                TargetRef(
                    OPPONENT,
                    opponent_board.active_id,
                ),
            ),
        )

    if geometry == "unqualified_one_to_your_hand":
        raise ValueError(
            "unqualified AZ target scope requires authoritative normalization"
        )

    raise ValueError(f"unknown target geometry: {geometry}")
