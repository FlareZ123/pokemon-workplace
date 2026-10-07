"""Execute compiled direct-to-Bench Basic-Pokemon searches in physical state.

The direct-Bench compiler preserves a destination that is mechanically distinct
from reveal-to-hand search. This module carries one exact target selection into
``StackBoardMaterialState`` by materializing selected deck copies as Basic
Pokemon board objects.

It deliberately resolves only the search/placement body. Playing the Trainer
itself, paying unrelated costs, ending a turn after an attack, shuffling the
deck, and observer-relative information updates remain in their own layers.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Sequence

from board_position_state import BoardPokemon, PokemonCard
from direct_bench_search_profile_compiler import DirectBenchSearchProfile
from identity_materialization import (
    assert_conserved,
    materialize,
    put_in_play_instance,
)
from pokemon_board_metadata import PokemonBoardMetadata
from search_zone_transition import SearchZoneTarget
from stack_knockout_conservation import StackBoardMaterialState
from typed_search_target_allocator import (
    TargetGroup,
    selector_from_label,
)


@dataclass(frozen=True)
class DirectBenchTarget:
    """One exact searchable Basic-Pokemon class plus board metadata."""

    search_target: SearchZoneTarget
    card_name: str
    retreat_cost: int
    evolves_from: str | None = None

    def __post_init__(self) -> None:
        if not self.card_name:
            raise ValueError("card_name must be non-empty")
        if self.retreat_cost < 0:
            raise ValueError("retreat_cost must be non-negative")


def direct_bench_target_from_metadata(
    metadata: PokemonBoardMetadata,
    *,
    copies: int,
) -> DirectBenchTarget:
    """Bind exact legal Pokemon metadata to one direct-Bench target class."""

    if copies < 0:
        raise ValueError("copies must be non-negative")
    return DirectBenchTarget(
        SearchZoneTarget(
            metadata.card_id,
            TargetGroup(
                metadata.name,
                copies,
                metadata.tags,
            ),
        ),
        metadata.name,
        metadata.retreat_cost,
        metadata.evolves_from,
    )


@dataclass(frozen=True)
class DirectBenchPlacement:
    """One requested physical copy to place from a represented target class."""

    target_index: int
    instance_id: str
    pokemon_id: str

    def __post_init__(self) -> None:
        if self.target_index < 0:
            raise ValueError("target_index must be non-negative")
        if not self.instance_id or not self.pokemon_id:
            raise ValueError("placement IDs must be non-empty")


@dataclass(frozen=True)
class MaterializedBenchPlacement:
    """One executed deck-to-Bench physical movement."""

    target_index: int
    card_class: str
    card_name: str
    instance_id: str
    pokemon_id: str


@dataclass(frozen=True)
class DirectBenchSearchTransition:
    """Physical result of resolving one direct-Bench search effect body."""

    before: StackBoardMaterialState
    after: StackBoardMaterialState
    placements: tuple[MaterializedBenchPlacement, ...]
    search_performed: bool
    skipped_full_bench_attack: bool = False


def _validate_targets(
    state: StackBoardMaterialState,
    profile: DirectBenchSearchProfile,
    targets: Sequence[DirectBenchTarget],
) -> tuple[DirectBenchTarget, ...]:
    if state.board is None:
        raise ValueError("direct Bench search requires a live board")

    bound = tuple(targets)
    classes = tuple(row.search_target.card_class for row in bound)
    if len(classes) != len(set(classes)):
        raise ValueError("direct Bench target card classes must be unique")

    selector = selector_from_label(profile.output.label)
    for row in bound:
        if not selector.matches(row.search_target.group):
            raise ValueError(
                f"{row.card_name!r} does not match {profile.output.label!r}"
            )
        represented = row.search_target.group.copies
        physical = state.ledger.exchangeable.count(
            row.search_target.card_class,
            "deck",
        )
        if represented != physical:
            raise ValueError(
                f"stale direct Bench target capacity for "
                f"{row.search_target.card_class!r}: "
                f"typed={represented}, physical={physical}"
            )
    return bound


def execute_direct_bench_search(
    state: StackBoardMaterialState,
    profile: DirectBenchSearchProfile,
    *,
    targets: Sequence[DirectBenchTarget],
    placements: Sequence[DirectBenchPlacement],
) -> DirectBenchSearchTransition:
    """Materialize an exact compiled Basic-Pokemon search into Bench objects.

    A Trainer profile is rejected when the Bench is already full. An attack
    profile with a full Bench resolves its search body as the rulebook's
    no-search branch, provided no placement was requested.
    """

    bound = _validate_targets(state, profile, targets)
    assert state.board is not None
    requested = tuple(placements)
    open_slots = state.board.bench_capacity - len(state.board.bench_ids)

    if open_slots <= 0:
        if profile.source_kind == "trainer":
            raise ValueError(
                "Trainer direct-Bench search cannot be used with a full Bench"
            )
        if requested:
            raise ValueError(
                "full-Bench attack branch cannot materialize search targets"
            )
        return DirectBenchSearchTransition(
            before=state,
            after=state,
            placements=(),
            search_performed=False,
            skipped_full_bench_attack=True,
        )

    maximum = profile.output.max_units
    assert maximum is not None
    if len(requested) > maximum:
        raise ValueError(
            f"search requests {len(requested)} placements but profile maximum is {maximum}"
        )
    if len(requested) > open_slots:
        raise ValueError(
            f"search requests {len(requested)} placements but only "
            f"{open_slots} Bench slots are open"
        )

    seen_instance_ids: set[str] = set()
    seen_pokemon_ids = {row.pokemon_id for row in state.board.pokemon}
    requested_by_target = [0] * len(bound)
    for row in requested:
        if row.target_index >= len(bound):
            raise ValueError("placement target_index is out of range")
        if row.instance_id in seen_instance_ids:
            raise ValueError("placement instance IDs must be unique")
        seen_instance_ids.add(row.instance_id)
        try:
            state.ledger.instance(row.instance_id)
        except KeyError:
            pass
        else:
            raise ValueError(f"instance_id already exists: {row.instance_id}")
        if row.pokemon_id in seen_pokemon_ids:
            raise ValueError(f"pokemon_id already exists: {row.pokemon_id}")
        seen_pokemon_ids.add(row.pokemon_id)
        requested_by_target[row.target_index] += 1

    for index, amount in enumerate(requested_by_target):
        if amount > bound[index].search_target.group.copies:
            raise ValueError(
                f"search requests {amount} copies of "
                f"{bound[index].card_name!r}, but only "
                f"{bound[index].search_target.group.copies} are represented"
            )

    ledger = state.ledger
    pokemon = list(state.board.pokemon)
    executed: list[MaterializedBenchPlacement] = []
    for row in requested:
        target = bound[row.target_index]
        card_class = target.search_target.card_class
        ledger = materialize(
            ledger,
            card_class=card_class,
            card_name=target.card_name,
            source_zone="deck",
            instance_id=row.instance_id,
        )
        ledger = put_in_play_instance(
            ledger,
            row.instance_id,
            row.pokemon_id,
        )
        pokemon.append(
            BoardPokemon(
                row.pokemon_id,
                (
                    PokemonCard(
                        row.instance_id,
                        target.card_name,
                        target.evolves_from,
                    ),
                ),
                retreat_cost=target.retreat_cost,
                evolution_eligible=False,
            )
        )
        executed.append(
            MaterializedBenchPlacement(
                target_index=row.target_index,
                card_class=card_class,
                card_name=target.card_name,
                instance_id=row.instance_id,
                pokemon_id=row.pokemon_id,
            )
        )

    after_board = replace(
        state.board,
        pokemon=tuple(pokemon),
    )
    after = StackBoardMaterialState(ledger, after_board)
    assert_conserved(state.ledger, after.ledger)

    return DirectBenchSearchTransition(
        before=state,
        after=after,
        placements=tuple(executed),
        search_performed=True,
    )
