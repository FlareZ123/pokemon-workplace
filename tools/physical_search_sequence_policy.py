"""Plan a bounded sequence of exact physical Trainer search transactions.

Each step operates on the immutable state returned by the prior step. Newly
searched Trainers may be played later in the turn, and generated outputs may
pay a later connector's discard cost.
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
from discard_cost_witness import DiscardSelection
from physical_staged_trainer_policy import (
    PhysicalSearchOption,
    _possible_payments,
)
from trainer_search_transaction import (
    TrainerSearchExecutionState,
    TrainerSearchTransaction,
    execute_trainer_retrieval_transaction,
)


@dataclass(frozen=True)
class PhysicalSearchSequenceResult:
    chosen_options: tuple[str, ...]
    discard_selections: tuple[DiscardSelection | None, ...]
    transactions: tuple[TrainerSearchTransaction, ...]
    after: TrainerSearchExecutionState
    discard_spent: int
    execution: TrainerExecutionCapacityResult
    completed_units: int
    total_units: int

    @property
    def all_goals_feasible(self) -> bool:
        return self.completed_units == self.total_units


def choose_physical_search_sequence(
    state: TrainerSearchExecutionState,
    *,
    options: Sequence[PhysicalSearchOption],
    execution_requirements: Sequence[TrainerExecutionRequirement],
    max_actions: int = 2,
    current_turn: int = 0,
    future_windows: Sequence[ExecutionTurnWindow] = (),
) -> PhysicalSearchSequenceResult:
    """Explore all ordered subsequences of physically validated search options.

    A supplied option is a concrete compiled retrieval choice usable at most
    once. Supply distinct options for multiple physical uses. No-action is
    included; ties preserve cards by preferring fewer discards and actions.
    """

    goals = tuple(execution_requirements)
    candidates = tuple(options)
    if not goals:
        raise ValueError("at least one downstream execution goal is required")
    if max_actions < 0 or current_turn < 0:
        raise ValueError("max_actions and current_turn must be non-negative")
    if any(w.turn <= current_turn for w in future_windows):
        raise ValueError("future windows must follow the current turn")
    if len({w.turn for w in future_windows}) != len(future_windows):
        raise ValueError("future execution turns must be distinct")

    total = sum(goal.copies for goal in goals)
    best: PhysicalSearchSequenceResult | None = None
    best_score: tuple[int, int, int] | None = None

    def visit(
        current: TrainerSearchExecutionState,
        remaining: tuple[int, ...],
        transactions: tuple[TrainerSearchTransaction, ...],
        names: tuple[str, ...],
        selections: tuple[DiscardSelection | None, ...],
        discard_spent: int,
    ) -> None:
        nonlocal best, best_score

        hand = {
            card_class: count
            for card_class, zone, count in current.zones.counts
            if zone == "hand"
        }
        execution = evaluate_trainer_execution_capacity(
            hand,
            goals,
            (
                execution_window_from_state(current_turn, current),
                *future_windows,
            ),
        )
        score = (execution.maximum_executed_units, -discard_spent, -len(names))
        if best_score is None or score > best_score:
            best_score = score
            best = PhysicalSearchSequenceResult(
                chosen_options=names,
                discard_selections=selections,
                transactions=transactions,
                after=current,
                discard_spent=discard_spent,
                execution=execution,
                completed_units=execution.maximum_executed_units,
                total_units=total,
            )
        if len(transactions) >= max_actions:
            return

        for index in remaining:
            option = candidates[index]
            for payment in _possible_payments(current, option):
                try:
                    tx = execute_trainer_retrieval_transaction(
                        current,
                        profile=option.profile,
                        action_card_class=option.action_card_class,
                        targets=option.targets,
                        retrieval_action=option.retrieval_action,
                        discard_candidates=option.discard_candidates,
                        discard_selection=payment,
                        pay_optional_discard=option.pay_optional_discard,
                        play_condition_met=option.play_condition_met,
                    )
                except ValueError:
                    continue
                visit(
                    tx.after,
                    tuple(other for other in remaining if other != index),
                    transactions + (tx,),
                    names + (option.name,),
                    selections + (payment,),
                    discard_spent + tx.discard_cost,
                )

    visit(state, tuple(range(len(candidates))), (), (), (), 0)
    assert best is not None
    return best
