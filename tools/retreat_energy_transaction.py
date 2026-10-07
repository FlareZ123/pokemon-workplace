"""Compose Retreat quota, physical Energy movement, and destination routing."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from canonical_turn_budget_owner import (
    CanonicalCompositeTurnState,
    retreat_with_canonical_budget,
)
from energy_board_conservation import ATTACHED, EnergyBoardState
from retreat_destination_conflicts import (
    RetreatDestinationAnalysis,
    analyze_successful_retreat_energy_destination,
)
from unified_state_kernel import UnifiedState


@dataclass(frozen=True)
class RetreatEnergyDestination:
    instance_id: str
    card_class: str
    destination_zone: str


@dataclass(frozen=True)
class RetreatEnergyConflict:
    instance_id: str
    analysis: RetreatDestinationAnalysis


@dataclass(frozen=True)
class RetreatEnergyTransactionState:
    unified: UnifiedState
    energy: EnergyBoardState

    def __post_init__(self) -> None:
        budget = self.unified.turn_budget
        if budget is None:
            raise ValueError("UnifiedState must own a canonical turn budget")
        if self.energy.board.retreat_used != budget.retreat_used:
            raise ValueError(
                "board Retreat compatibility bit must mirror canonical budget"
            )


@dataclass(frozen=True)
class RetreatEnergyTransactionResult:
    state: RetreatEnergyTransactionState
    committed: bool
    destinations: tuple[RetreatEnergyDestination, ...] = ()
    conflicts: tuple[RetreatEnergyConflict, ...] = ()


def retreat_with_energy_destinations(
    state: RetreatEnergyTransactionState,
    bench_object_id: str,
    *,
    retreat_cost: int,
    discard_energy_ids: Iterable[str],
    opposing_scoop_up_block_active: bool = False,
    prism_star_energy_ids: Iterable[str] = (),
) -> RetreatEnergyTransactionResult | None:
    """Execute one normal Retreat transaction when all destinations resolve.

    Mechanical Retreat legality and quota consumption are evaluated first on an
    immutable candidate state. If any selected Energy has an unresolved
    replacement conflict, the original state is returned uncommitted.
    """

    outgoing = state.energy.board.get(state.energy.board.active_id)
    dashing_pouch_active = (
        outgoing.tool is not None
        and outgoing.tool.card_name == "Dashing Pouch"
        and outgoing.pokemon_state.tool_effect_enabled
    )
    holder_has_damage = outgoing.damage_counters > 0
    prism_ids = frozenset(prism_star_energy_ids)

    composite = CanonicalCompositeTurnState(
        unified=state.unified,
        board=state.energy.board,
    )
    resolved = retreat_with_canonical_budget(
        composite,
        bench_object_id,
        retreat_cost=retreat_cost,
        discard_energy_ids=discard_energy_ids,
    )
    if resolved is None:
        return None

    next_composite, discarded = resolved
    analyses: list[tuple[object, RetreatDestinationAnalysis]] = []
    conflicts: list[RetreatEnergyConflict] = []

    for energy in discarded:
        analysis = analyze_successful_retreat_energy_destination(
            dashing_pouch_active=dashing_pouch_active,
            opposing_scoop_up_block_active=opposing_scoop_up_block_active,
            holder_has_damage=holder_has_damage,
            energy_is_prism_star=energy.instance_id in prism_ids,
        )
        analyses.append((energy, analysis))
        if not analysis.resolved:
            conflicts.append(
                RetreatEnergyConflict(
                    instance_id=energy.instance_id,
                    analysis=analysis,
                )
            )

    if conflicts:
        return RetreatEnergyTransactionResult(
            state=state,
            committed=False,
            conflicts=tuple(conflicts),
        )

    zones = state.energy.zones
    instance_classes = dict(state.energy.instance_classes)
    destinations: list[RetreatEnergyDestination] = []

    for energy, analysis in analyses:
        card_class = instance_classes.pop(energy.instance_id)
        destination = analysis.destination_zone
        assert destination is not None
        zones = zones.move(card_class, ATTACHED, destination)
        destinations.append(
            RetreatEnergyDestination(
                instance_id=energy.instance_id,
                card_class=card_class,
                destination_zone=destination,
            )
        )

    next_energy = EnergyBoardState(
        zones=zones,
        board=next_composite.board,
        instance_classes=tuple(sorted(instance_classes.items())),
    )
    next_state = RetreatEnergyTransactionState(
        unified=next_composite.unified,
        energy=next_energy,
    )
    return RetreatEnergyTransactionResult(
        state=next_state,
        committed=True,
        destinations=tuple(destinations),
    )
