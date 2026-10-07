"""Refresh state-dependent attached Energy units before Retreat payment."""

from __future__ import annotations

from dataclasses import replace
from typing import Iterable

from board_object_kernel import BoardState, EnergyAttachment
from energy_board_conservation import EnergyBoardState
from retreat_energy_transaction import (
    RetreatEnergyTransactionResult,
    RetreatEnergyTransactionState,
    retreat_with_energy_destinations,
)


IGNITION_ENERGY_PRINT_IDS = frozenset({
    "rsv10pt5-86",
    "me2-124",
})
_EVOLUTION_TAGS = frozenset({"Stage1", "Stage2", "Evolution"})


def holder_is_evolution(tags: frozenset[str]) -> bool:
    """Return the board-object Evolution trait used by this adapter."""

    return bool(tags & _EVOLUTION_TAGS)


def current_retreat_units(
    energy: EnergyAttachment,
    *,
    holder_tags: frozenset[str],
) -> tuple[str, ...]:
    """Resolve exact supported dynamic unit counts from current holder state.

    Ignition Energy provides one Colorless Energy normally and three while
    attached to an Evolution Pokemon. Unknown prints preserve their represented
    snapshot rather than being inferred by card name alone.
    """

    if (
        energy.card_name == "Ignition Energy"
        and energy.print_id in IGNITION_ENERGY_PRINT_IDS
    ):
        if holder_is_evolution(holder_tags):
            return ("C", "C", "C")
        return ("C",)
    return energy.units


def refresh_active_retreat_energy_units(
    state: RetreatEnergyTransactionState,
) -> RetreatEnergyTransactionState:
    """Refresh supported dynamic providers on the current Active Pokemon."""

    board = state.energy.board
    active = board.get(board.active_id)
    refreshed_energy = tuple(
        replace(
            energy,
            units=current_retreat_units(
                energy,
                holder_tags=active.tags,
            ),
        )
        for energy in active.energy
    )
    if refreshed_energy == active.energy:
        return state

    refreshed_active = replace(active, energy=refreshed_energy)
    refreshed_board = replace(
        board,
        objects=tuple(
            refreshed_active if pokemon.object_id == active.object_id else pokemon
            for pokemon in board.objects
        ),
    )
    refreshed_board.validate()
    refreshed_energy_state = EnergyBoardState(
        zones=state.energy.zones,
        board=refreshed_board,
        instance_classes=state.energy.instance_classes,
    )
    return RetreatEnergyTransactionState(
        unified=state.unified,
        energy=refreshed_energy_state,
    )


def retreat_with_dynamic_energy_units(
    state: RetreatEnergyTransactionState,
    bench_object_id: str,
    *,
    retreat_cost: int,
    discard_energy_ids: Iterable[str],
    opposing_scoop_up_block_active: bool = False,
    prism_star_energy_ids: Iterable[str] = (),
) -> RetreatEnergyTransactionResult | None:
    """Refresh supported providers, then execute the conserved Retreat."""

    refreshed = refresh_active_retreat_energy_units(state)
    return retreat_with_energy_destinations(
        refreshed,
        bench_object_id,
        retreat_cost=retreat_cost,
        discard_energy_ids=discard_energy_ids,
        opposing_scoop_up_block_active=opposing_scoop_up_block_active,
        prism_star_energy_ids=prism_star_energy_ids,
    )
