"""Atomic Trainer transaction for compiled direct-to-Bench searches.

The shared Trainer search engine owns Item/Supporter play permission, action
budget, play conditions, exact typed target selection, and Trainer lifecycle.
For direct placement, searched copies move into a private staging zone rather
than hand. This module then materializes those exact staged copies as Basic
Pokemon board objects.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Sequence

from board_position_state import BoardPokemon, PokemonCard
from direct_bench_search_execution import DirectBenchPlacement, DirectBenchTarget
from direct_bench_search_profile_compiler import (
    DirectBenchSearchProfile,
    project_direct_bench_trainer_profile,
)
from identity_materialization import (
    IdentityLedger,
    assert_conserved,
    materialize,
    put_in_play_instance,
)
from lock_state_kernel import PlayerChannels
from stack_knockout_conservation import StackBoardMaterialState
from trainer_search_transaction import (
    TrainerSearchExecutionState,
    TrainerSearchTransaction,
    execute_trainer_search_transaction,
)
from turn_action_budget import TurnActionBudget
from typed_search_target_allocator import (
    DemandChannel,
    TypedTargetAction,
    selector_from_label,
)


DIRECT_BENCH_SELECTED_ZONE = "direct_bench_selected"


@dataclass(frozen=True)
class DirectBenchTrainerExecutionState:
    material: StackBoardMaterialState
    budget: TurnActionBudget = field(default_factory=TurnActionBudget)
    channels: PlayerChannels = field(default_factory=PlayerChannels)


@dataclass(frozen=True)
class DirectBenchTrainerTransaction:
    before: DirectBenchTrainerExecutionState
    after: DirectBenchTrainerExecutionState
    trainer_transaction: TrainerSearchTransaction
    placements: tuple[DirectBenchPlacement, ...]


def _validate_request(
    state: DirectBenchTrainerExecutionState,
    profile: DirectBenchSearchProfile,
    targets: Sequence[DirectBenchTarget],
    action: TypedTargetAction,
    placements: Sequence[DirectBenchPlacement],
) -> tuple[DirectBenchTarget, ...]:
    if profile.source_kind != "trainer":
        raise ValueError("direct-Bench Trainer transaction requires a Trainer profile")
    if state.material.board is None:
        raise ValueError("direct-Bench Trainer transaction requires a live board")

    bound = tuple(targets)
    classes = tuple(row.search_target.card_class for row in bound)
    if len(classes) != len(set(classes)):
        raise ValueError("direct-Bench target card classes must be unique")
    if len(action.target_cost) != len(bound):
        raise ValueError("target_cost length does not match direct-Bench targets")

    selector = selector_from_label(profile.output.label)
    for row in bound:
        if not selector.matches(row.search_target.group):
            raise ValueError(
                f"{row.card_name!r} does not match {profile.output.label!r}"
            )
        represented = row.search_target.group.copies
        physical = state.material.ledger.exchangeable.count(
            row.search_target.card_class,
            "deck",
        )
        if represented != physical:
            raise ValueError(
                f"stale direct-Bench target capacity for "
                f"{row.search_target.card_class!r}: "
                f"typed={represented}, physical={physical}"
            )

    requested = tuple(placements)
    if sum(action.target_cost) != len(requested):
        raise ValueError("placement count must equal selected target count")

    open_slots = state.material.board.bench_capacity - len(
        state.material.board.bench_ids
    )
    if open_slots <= 0:
        raise ValueError("direct-Bench Trainer cannot be used with a full Bench")
    if len(requested) > open_slots:
        raise ValueError(
            f"selected {len(requested)} Pokemon but only {open_slots} Bench slots are open"
        )

    counts = [0] * len(bound)
    instance_ids: set[str] = set()
    pokemon_ids = {row.pokemon_id for row in state.material.board.pokemon}
    for placement in requested:
        if placement.target_index >= len(bound):
            raise ValueError("placement target_index is out of range")
        counts[placement.target_index] += 1
        if placement.instance_id in instance_ids:
            raise ValueError("placement instance IDs must be unique")
        instance_ids.add(placement.instance_id)
        try:
            state.material.ledger.instance(placement.instance_id)
        except KeyError:
            pass
        else:
            raise ValueError(f"instance_id already exists: {placement.instance_id}")
        if placement.pokemon_id in pokemon_ids:
            raise ValueError(f"pokemon_id already exists: {placement.pokemon_id}")
        pokemon_ids.add(placement.pokemon_id)

    if tuple(counts) != action.target_cost:
        raise ValueError("placement target classes must match exact target_cost")
    return bound


def execute_direct_bench_trainer_transaction(
    state: DirectBenchTrainerExecutionState,
    profile: DirectBenchSearchProfile,
    *,
    action_card_class: str,
    demands: Sequence[DemandChannel],
    targets: Sequence[DirectBenchTarget],
    search_action: TypedTargetAction,
    placements: Sequence[DirectBenchPlacement],
    play_condition_met: bool | None = None,
) -> DirectBenchTrainerTransaction:
    """Execute one positive direct-Bench Trainer search atomically."""

    bound = _validate_request(
        state,
        profile,
        targets,
        search_action,
        placements,
    )
    shared_profile = project_direct_bench_trainer_profile(profile)
    search_targets = tuple(row.search_target for row in bound)

    execution = TrainerSearchExecutionState(
        zones=state.material.ledger.exchangeable,
        budget=state.budget,
        channels=state.channels,
    )
    trainer = execute_trainer_search_transaction(
        execution,
        profile=shared_profile,
        action_card_class=action_card_class,
        demands=demands,
        targets=search_targets,
        search_action=search_action,
        play_condition_met=play_condition_met,
        search_destination_zone=DIRECT_BENCH_SELECTED_ZONE,
    )
    if trainer.search_destination_zone != DIRECT_BENCH_SELECTED_ZONE:
        raise AssertionError("shared Trainer transaction lost direct-Bench destination")

    ledger = IdentityLedger(
        trainer.after.zones,
        state.material.ledger.instances,
    )
    assert state.material.board is not None
    pokemon = list(state.material.board.pokemon)
    for placement in placements:
        target = bound[placement.target_index]
        ledger = materialize(
            ledger,
            card_class=target.search_target.card_class,
            card_name=target.card_name,
            source_zone=DIRECT_BENCH_SELECTED_ZONE,
            instance_id=placement.instance_id,
        )
        ledger = put_in_play_instance(
            ledger,
            placement.instance_id,
            placement.pokemon_id,
        )
        pokemon.append(
            BoardPokemon(
                placement.pokemon_id,
                (
                    PokemonCard(
                        placement.instance_id,
                        target.card_name,
                        target.evolves_from,
                    ),
                ),
                retreat_cost=target.retreat_cost,
                evolution_eligible=False,
            )
        )

    if any(
        zone == DIRECT_BENCH_SELECTED_ZONE
        for _card_class, zone, _count in ledger.exchangeable.counts
    ):
        raise AssertionError("direct-Bench staging zone was not fully consumed")

    board = replace(state.material.board, pokemon=tuple(pokemon))
    material = StackBoardMaterialState(ledger, board)
    assert_conserved(state.material.ledger, material.ledger)

    after = DirectBenchTrainerExecutionState(
        material=material,
        budget=trainer.after.budget,
        channels=trainer.after.channels,
    )
    return DirectBenchTrainerTransaction(
        before=state,
        after=after,
        trainer_transaction=trainer,
        placements=tuple(placements),
    )
