"""Exact physical one-search policy against downstream Trainer execution goals.

Every candidate is an already compiled, trusted retrieval branch. This solver
chooses between *physical* transactions, including their played hand card and
precisely selected discard payments. It evaluates generic downstream Trainer
execution windows using the shared finite-capacity scheduler.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from acquired_trainer_execution_capacity import (
    ExecutionTurnWindow,
    TrainerExecutionCapacityResult,
    TrainerExecutionRequirement,
    evaluate_trainer_execution_capacity,
    execution_window_from_state,
)
from discard_cost_witness import (
    DiscardCandidate,
    DiscardSelection,
    enumerate_discard_selections,
)
from search_zone_transition import SearchZoneTarget
from trainer_search_profile_compiler import CompiledTrainerSearchProfile
from trainer_search_transaction import (
    RESOLVING_TRAINER_ZONE,
    TrainerSearchExecutionState,
    TrainerSearchTransaction,
    execute_trainer_retrieval_transaction,
)
from typed_search_retrieval import TypedRetrievalAction


@dataclass(frozen=True)
class PhysicalSearchOption:
    """A trusted branch of a search Trainer physically present in hand."""

    name: str
    profile: CompiledTrainerSearchProfile
    action_card_class: str
    targets: tuple[SearchZoneTarget, ...]
    retrieval_action: TypedRetrievalAction
    discard_candidates: tuple[DiscardCandidate, ...] = ()
    pay_optional_discard: bool | None = None
    play_condition_met: bool | None = None

    def __post_init__(self) -> None:
        if not self.name or not self.action_card_class:
            raise ValueError("option and played card class must be non-empty")


@dataclass(frozen=True)
class PhysicalSearchPolicyResult:
    """Best one-action continuation, including the exact conserved zones."""

    chosen_option: str | None
    discard_selection: DiscardSelection | None
    discard_spent: int
    after: TrainerSearchExecutionState
    transaction: TrainerSearchTransaction | None
    execution: TrainerExecutionCapacityResult
    completed_units: int
    total_units: int

    @property
    def all_goals_feasible(self) -> bool:
        return self.completed_units == self.total_units


def _payment_cost(option: PhysicalSearchOption) -> int:
    """Cost to enumerate; actual branch validation remains in the executor."""

    p = option.profile
    extra = option.retrieval_action.axis_usage[len(p.base_outputs):]
    paid = (
        option.pay_optional_discard
        if option.pay_optional_discard is not None
        else any(extra)
    )
    return (
        p.required_discard_other_cards
        + (p.optional_discard_other_cards if paid else 0)
    )


def _possible_payments(
    state: TrainerSearchExecutionState,
    option: PhysicalSearchOption,
) -> tuple[DiscardSelection | None, ...]:
    if option.profile.discards_entire_hand:
        return (None,)
    cost = _payment_cost(option)
    if cost == 0:
        return (None,)
    if state.zones.count(option.action_card_class, "hand") == 0:
        return ()
    if any(zone == RESOLVING_TRAINER_ZONE for _, zone, _ in state.zones.counts):
        return ()

    # The resolving copy is physically absent before the "other cards"
    # payment. A second copy of the same class may remain as valid fodder.
    remaining_hand = state.zones.move(
        option.action_card_class, "hand", RESOLVING_TRAINER_ZONE
    )
    return enumerate_discard_selections(
        remaining_hand, option.discard_candidates, cost
    )


def choose_physical_search(
    state: TrainerSearchExecutionState,
    *,
    options: Sequence[PhysicalSearchOption],
    execution_requirements: Sequence[TrainerExecutionRequirement],
    current_turn: int = 0,
    future_windows: Sequence[ExecutionTurnWindow] = (),
) -> PhysicalSearchPolicyResult:
    """Optimize generic execution after zero or one exact search action.

    A no-action policy is included. Future windows must be explicitly supplied
    as scenario assumptions; this function does not predict opponent locks or
    draw steps. Inaccessible branches are skipped after the canonical executor
    rejects them. Ties prefer less discard and no redundant connector.
    """

    goals = tuple(execution_requirements)
    if not goals:
        raise ValueError("at least one downstream execution goal is required")
    if current_turn < 0:
        raise ValueError("current_turn must be non-negative")
    if any(w.turn <= current_turn for w in future_windows):
        raise ValueError("future windows must follow current_turn")
    if len({w.turn for w in future_windows}) != len(future_windows):
        raise ValueError("future execution turns must be distinct")

    def evaluate(
        after: TrainerSearchExecutionState,
    ) -> TrainerExecutionCapacityResult:
        hand = {
            card_class: count
            for card_class, zone, count in after.zones.counts
            if zone == "hand"
        }
        return evaluate_trainer_execution_capacity(
            hand,
            goals,
            (
                execution_window_from_state(current_turn, after),
                *future_windows,
            ),
        )

    base_execution = evaluate(state)
    total = sum(goal.copies for goal in goals)
    best = PhysicalSearchPolicyResult(
        chosen_option=None,
        discard_selection=None,
        discard_spent=0,
        after=state,
        transaction=None,
        execution=base_execution,
        completed_units=base_execution.maximum_executed_units,
        total_units=total,
    )
    best_score = (best.completed_units, 0, 0)

    for option in options:
        for selection in _possible_payments(state, option):
            try:
                tx = execute_trainer_retrieval_transaction(
                    state,
                    profile=option.profile,
                    action_card_class=option.action_card_class,
                    targets=option.targets,
                    retrieval_action=option.retrieval_action,
                    discard_candidates=option.discard_candidates,
                    discard_selection=selection,
                    pay_optional_discard=option.pay_optional_discard,
                    play_condition_met=option.play_condition_met,
                )
            except ValueError:
                continue

            execution = evaluate(tx.after)
            score = (execution.maximum_executed_units, -tx.discard_cost, -1)
            if score <= best_score:
                continue
            best_score = score
            best = PhysicalSearchPolicyResult(
                chosen_option=option.name,
                discard_selection=selection,
                discard_spent=tx.discard_cost,
                after=tx.after,
                transaction=tx,
                execution=execution,
                completed_units=execution.maximum_executed_units,
                total_units=total,
            )

    return best
