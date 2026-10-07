"""Bridge Prize hand access to same-turn Supporter execution."""

from __future__ import annotations

from dataclasses import dataclass

from action_quota_effects import DUAL_BRAINS, derive_action_quotas
from peonia_arc_position import analyze_peonia_arc_position
from turn_action_budget import TurnAction, TurnActionBudget


@dataclass(frozen=True)
class PrizedSupporterExecutionMetrics:
    prize_count: int
    peonia_count: int
    supporter_limit: int
    direct_hand_access_probability: float
    direct_execution_probability: float
    direct_next_turn_execution_probability: float
    peonia_hand_access_probability: float
    peonia_execution_probability: float
    peonia_next_turn_execution_probability: float
    gladion_hand_access_probability: float
    gladion_execution_probability: float
    gladion_next_turn_execution_probability: float


def analyze_prized_supporter_execution(
    *,
    prize_count: int = 6,
    peonia_count: int = 3,
    supporter_limit: int = 1,
) -> PrizedSupporterExecutionMetrics:
    """Compare same-turn access and execution for one known Prized Supporter.

    The direct line represents Arc Phone -> Trekking Shoes and probes one
    physical Prize slot without consuming the Supporter channel.

    The Peonia line represents Peonia -> Arc Phone -> Trekking Shoes. Peonia
    checks the requested number of physical Prize slots and consumes one
    Supporter play before the recovered target could be played.
    """

    if prize_count <= 1:
        raise ValueError("prize_count must be at least 2")
    if not 1 <= peonia_count < prize_count:
        raise ValueError("peonia_count must be between 1 and prize_count - 1")
    if supporter_limit < 0:
        raise ValueError("supporter_limit must be non-negative")

    initial_budget = TurnActionBudget(supporter_play_limit=supporter_limit)

    direct_hand_access_probability = 1.0 / prize_count
    direct_execution_probability = (
        direct_hand_access_probability
        if initial_budget.can(TurnAction.SUPPORTER)
        else 0.0
    )
    direct_next_turn_execution_probability = (
        direct_hand_access_probability
        if initial_budget.next_turn().can(TurnAction.SUPPORTER)
        else 0.0
    )

    gladion_budget = initial_budget.consume(TurnAction.SUPPORTER)
    if gladion_budget is None:
        gladion_hand_access_probability = 0.0
        gladion_execution_probability = 0.0
        gladion_next_turn_execution_probability = 0.0
    else:
        gladion_hand_access_probability = 1.0
        gladion_execution_probability = (
            1.0 if gladion_budget.can(TurnAction.SUPPORTER) else 0.0
        )
        gladion_next_turn_execution_probability = (
            1.0
            if gladion_budget.next_turn().can(TurnAction.SUPPORTER)
            else 0.0
        )

    peonia_budget = initial_budget.consume(TurnAction.SUPPORTER)
    if peonia_budget is None:
        peonia_hand_access_probability = 0.0
        peonia_execution_probability = 0.0
        peonia_next_turn_execution_probability = 0.0
    else:
        peonia_result = analyze_peonia_arc_position(
            prize_count=prize_count,
            peonia_count=peonia_count,
        )
        peonia_hand_access_probability = (
            peonia_result.combined_target_probability
        )
        peonia_execution_probability = (
            peonia_hand_access_probability
            if peonia_budget.can(TurnAction.SUPPORTER)
            else 0.0
        )
        peonia_next_turn_execution_probability = (
            peonia_hand_access_probability
            if peonia_budget.next_turn().can(TurnAction.SUPPORTER)
            else 0.0
        )

    return PrizedSupporterExecutionMetrics(
        prize_count=prize_count,
        peonia_count=peonia_count,
        supporter_limit=supporter_limit,
        direct_hand_access_probability=direct_hand_access_probability,
        direct_execution_probability=direct_execution_probability,
        direct_next_turn_execution_probability=(
            direct_next_turn_execution_probability
        ),
        peonia_hand_access_probability=peonia_hand_access_probability,
        peonia_execution_probability=peonia_execution_probability,
        peonia_next_turn_execution_probability=(
            peonia_next_turn_execution_probability
        ),
        gladion_hand_access_probability=gladion_hand_access_probability,
        gladion_execution_probability=gladion_execution_probability,
        gladion_next_turn_execution_probability=(
            gladion_next_turn_execution_probability
        ),
    )


def analyze_with_dual_brains(
    *,
    prize_count: int = 6,
    peonia_count: int = 3,
) -> PrizedSupporterExecutionMetrics:
    """Run the comparison with Magnezone's Dual Brains quota grant."""

    budget = derive_action_quotas(
        TurnActionBudget(),
        (DUAL_BRAINS,),
    )
    return analyze_prized_supporter_execution(
        prize_count=prize_count,
        peonia_count=peonia_count,
        supporter_limit=budget.supporter_play_limit,
    )
