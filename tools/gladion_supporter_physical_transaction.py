"""Supporter-budget wrapper for literal physical Gladion resolution."""

from __future__ import annotations

from dataclasses import dataclass

from gladion_physical_prize_transition import (
    GladionPhysicalOutcome,
    resolve_gladion_physical,
)
from lock_state_kernel import PlayerChannels
from top_prize_physical_bridge import TopPrizePhysicalState
from turn_action_budget import TurnAction, TurnActionBudget


@dataclass(frozen=True)
class GladionSupporterOutcome:
    physical: GladionPhysicalOutcome
    budget_before: TurnActionBudget
    budget_after: TurnActionBudget
    channels: PlayerChannels


def execute_gladion_supporter_physical(
    state: TopPrizePhysicalState,
    budget: TurnActionBudget,
    channels: PlayerChannels,
    *,
    gladion_instance_id: str,
    selected_position: int,
) -> tuple[GladionSupporterOutcome, ...]:
    """Consume the Supporter window and resolve Gladion's literal Prize cycle."""

    if not channels.supporter_play:
        raise ValueError("Supporter play is locked")

    next_budget = budget.consume(TurnAction.SUPPORTER)
    if next_budget is None:
        raise ValueError("Supporter action budget is exhausted")

    physical_outcomes = resolve_gladion_physical(
        state,
        gladion_instance_id=gladion_instance_id,
        selected_position=selected_position,
    )
    return tuple(
        GladionSupporterOutcome(
            physical=outcome,
            budget_before=budget,
            budget_after=next_budget,
            channels=channels,
        )
        for outcome in physical_outcomes
    )
