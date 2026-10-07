"""Prepare attached Energy state for Retreat payment."""

from __future__ import annotations

from dataclasses import dataclass

from restricted_special_energy_attachment import (
    RestrictedEnergyDiscard,
    revalidate_restricted_special_energy,
)
from retreat_dynamic_energy_units import (
    RetreatEnergyProviderContext,
    refresh_active_retreat_energy_units,
)
from retreat_energy_transaction import RetreatEnergyTransactionState


@dataclass(frozen=True)
class EnergyProviderRefresh:
    instance_id: str
    before_units: tuple[str, ...]
    after_units: tuple[str, ...]


@dataclass(frozen=True)
class RetreatEnergyNormalization:
    state: RetreatEnergyTransactionState
    restriction_discards: tuple[RestrictedEnergyDiscard, ...] = ()
    provider_refreshes: tuple[EnergyProviderRefresh, ...] = ()


def normalize_retreat_energy_state(
    state: RetreatEnergyTransactionState,
    *,
    provider_context: RetreatEnergyProviderContext | None = None,
) -> RetreatEnergyNormalization:
    """Discard invalid attachments, then refresh surviving provider units."""

    active_id = state.energy.board.active_id
    before = {
        energy.instance_id: energy.units
        for energy in state.energy.board.get(active_id).energy
    }

    restriction = revalidate_restricted_special_energy(state.energy)
    restricted = RetreatEnergyTransactionState(
        unified=state.unified,
        energy=restriction.state,
    )
    refreshed = refresh_active_retreat_energy_units(
        restricted,
        context=provider_context,
    )
    after = {
        energy.instance_id: energy.units
        for energy in refreshed.energy.board.get(active_id).energy
    }

    refreshes = tuple(
        EnergyProviderRefresh(instance_id, before[instance_id], after[instance_id])
        for instance_id in sorted(before)
        if instance_id in after and before[instance_id] != after[instance_id]
    )
    return RetreatEnergyNormalization(
        state=refreshed,
        restriction_discards=restriction.discarded,
        provider_refreshes=refreshes,
    )
