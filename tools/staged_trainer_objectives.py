"""Joint planner for Trainer acquisition actions and downstream objectives.

Acquisition actions are assumed to be semantically validated before entering this
planner. Each action consumes a physical searchable-card pool, adds those cards
to hand, consumes its own Trainer play window, and may consume a shared
discardable-card pool. The resulting hand and remaining turn windows are then
evaluated by the acquired-Trainer execution-capacity solver.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence

from acquired_trainer_execution_capacity import (
    ExecutionTurnWindow,
    TrainerExecutionCapacityResult,
    TrainerExecutionRequirement,
    evaluate_trainer_execution_capacity,
)


_ACTION_CLASSES = frozenset(
    {"Item", "Pokémon Tool", "Supporter", "Stadium"}
)


@dataclass(frozen=True)
class TrainerAcquisitionAction:
    """One available acquisition action with trusted deck-to-hand outputs."""

    name: str
    action_class: str
    copies: int
    hand_outputs: tuple[tuple[str, int], ...]
    discard_cost: int = 0

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("action name must be non-empty")
        if self.action_class not in _ACTION_CLASSES:
            raise ValueError(
                f"unsupported action class: {self.action_class!r}"
            )
        if self.copies < 0 or self.discard_cost < 0:
            raise ValueError("copies and discard_cost must be non-negative")
        classes = [card_class for card_class, _count in self.hand_outputs]
        if len(classes) != len(set(classes)):
            raise ValueError("hand output card classes must be unique")
        if any(
            not card_class or count <= 0
            for card_class, count in self.hand_outputs
        ):
            raise ValueError(
                "hand outputs require non-empty classes and positive counts"
            )


@dataclass(frozen=True)
class TrainerAcquisitionRequirement:
    """Intermediate objective requiring a card to have reached hand."""

    name: str
    card_class: str
    copies: int = 1

    def __post_init__(self) -> None:
        if not self.name or not self.card_class:
            raise ValueError("requirement fields must be non-empty")
        if self.copies <= 0:
            raise ValueError("copies must be positive")


@dataclass(frozen=True)
class StagedTrainerObjectiveResult:
    exact_joint_feasible: bool
    maximum_completed_units: int
    total_objective_units: int
    minimum_unmet_units: int
    acquisition_actions: tuple[str, ...]
    discard_spent: int
    execution_result: TrainerExecutionCapacityResult
    hand_after_acquisition: tuple[tuple[str, int], ...]
    searchable_after_acquisition: tuple[tuple[str, int], ...]
    windows_after_acquisition: tuple[ExecutionTurnWindow, ...]


def _channel_open(window: ExecutionTurnWindow, action_class: str) -> bool:
    if action_class == "Item":
        return window.channels.item_play
    if action_class == "Pokémon Tool":
        return window.channels.tool_play
    if action_class == "Supporter":
        return window.channels.supporter_play
    if action_class == "Stadium":
        return window.channels.stadium_play
    raise ValueError(f"unsupported action class: {action_class!r}")


def _consume_action_window(
    window: ExecutionTurnWindow,
    action_class: str,
) -> ExecutionTurnWindow | None:
    if not _channel_open(window, action_class):
        return None
    if action_class == "Supporter":
        if window.supporter_plays_remaining <= 0:
            return None
        return ExecutionTurnWindow(
            turn=window.turn,
            supporter_plays_remaining=window.supporter_plays_remaining - 1,
            stadium_plays_remaining=window.stadium_plays_remaining,
            channels=window.channels,
        )
    if action_class == "Stadium":
        if window.stadium_plays_remaining <= 0:
            return None
        return ExecutionTurnWindow(
            turn=window.turn,
            supporter_plays_remaining=window.supporter_plays_remaining,
            stadium_plays_remaining=window.stadium_plays_remaining - 1,
            channels=window.channels,
        )
    return window


def _zero_execution_result() -> TrainerExecutionCapacityResult:
    return TrainerExecutionCapacityResult(
        exact_joint_feasible=True,
        individually_feasible=(),
        maximum_executed_units=0,
        minimum_unexecuted_units=0,
        witness=(),
    )


def evaluate_staged_trainer_objectives(
    initial_hand: Mapping[str, int],
    *,
    searchable_cards: Mapping[str, int],
    discardable_cards: int,
    acquisition_actions: Sequence[TrainerAcquisitionAction],
    acquisition_requirements: Sequence[TrainerAcquisitionRequirement] = (),
    execution_requirements: Sequence[TrainerExecutionRequirement] = (),
    windows: Sequence[ExecutionTurnWindow],
    acquisition_turn: int = 0,
) -> StagedTrainerObjectiveResult:
    """Choose acquisition actions, then score acquisition and execution goals.

    Every search output is removed from searchable_cards before it is added to
    hand, so alternative search routes cannot duplicate one physical target.

    Tie breaking prefers lower discard expenditure, then fewer acquisition
    actions, after maximizing completed objective units.
    """

    if discardable_cards < 0:
        raise ValueError("discardable_cards must be non-negative")
    if any(count < 0 for count in initial_hand.values()):
        raise ValueError("initial hand counts must be non-negative")
    if any(count < 0 for count in searchable_cards.values()):
        raise ValueError("searchable card counts must be non-negative")

    action_types = tuple(acquisition_actions)
    acquire_goals = tuple(acquisition_requirements)
    execute_goals = tuple(execution_requirements)
    window_tuple = tuple(sorted(windows, key=lambda window: window.turn))
    if not window_tuple:
        raise ValueError("at least one execution window is required")
    turns = [window.turn for window in window_tuple]
    if len(turns) != len(set(turns)):
        raise ValueError("execution window turns must be unique")
    try:
        acquisition_window_index = turns.index(acquisition_turn)
    except ValueError as exc:
        raise ValueError("acquisition_turn has no execution window") from exc

    hand_classes = sorted(
        set(initial_hand)
        | set(searchable_cards)
        | {
            card_class
            for action in action_types
            for card_class, _count in action.hand_outputs
        }
        | {goal.card_class for goal in acquire_goals}
        | {goal.card_class for goal in execute_goals}
    )
    hand_index = {
        card_class: index
        for index, card_class in enumerate(hand_classes)
    }
    initial_hand_tuple = tuple(
        initial_hand.get(card_class, 0)
        for card_class in hand_classes
    )
    initial_searchable_tuple = tuple(
        searchable_cards.get(card_class, 0)
        for card_class in hand_classes
    )

    for action in action_types:
        for card_class, _count in action.hand_outputs:
            if card_class not in searchable_cards:
                raise ValueError(
                    f"searchable_cards has no explicit count for {card_class!r}"
                )

    action_units = tuple(
        action
        for action in action_types
        for _ in range(action.copies)
    )
    total_objective_units = (
        sum(goal.copies for goal in acquire_goals)
        + sum(goal.copies for goal in execute_goals)
    )
    if total_objective_units == 0:
        raise ValueError("at least one staged objective is required")

    best = None

    def score_terminal(
        hand_state: tuple[int, ...],
        searchable_state: tuple[int, ...],
        remaining_discard: int,
        current_windows: tuple[ExecutionTurnWindow, ...],
    ):
        hand_map = {
            card_class: count
            for card_class, count in zip(hand_classes, hand_state)
        }
        acquired_units = sum(
            min(goal.copies, hand_map.get(goal.card_class, 0))
            for goal in acquire_goals
        )
        execution = (
            evaluate_trainer_execution_capacity(
                hand_map,
                execute_goals,
                current_windows,
            )
            if execute_goals
            else _zero_execution_result()
        )
        completed = acquired_units + execution.maximum_executed_units
        discard_spent = discardable_cards - remaining_discard
        key = (
            completed,
            -discard_spent,
        )
        searchable_map = {
            card_class: count
            for card_class, count in zip(hand_classes, searchable_state)
        }
        return (
            key,
            execution,
            discard_spent,
            hand_map,
            searchable_map,
        )

    def visit(
        action_index: int,
        hand_state: tuple[int, ...],
        searchable_state: tuple[int, ...],
        remaining_discard: int,
        current_windows: tuple[ExecutionTurnWindow, ...],
        used_actions: tuple[str, ...],
    ) -> None:
        nonlocal best

        if action_index == len(action_units):
            terminal = score_terminal(
                hand_state,
                searchable_state,
                remaining_discard,
                current_windows,
            )
            candidate = terminal + (used_actions, current_windows)
            candidate_key = (
                terminal[0][0],
                terminal[0][1],
                -len(used_actions),
            )
            if best is None or candidate_key > best[0]:
                best = (candidate_key,) + candidate[1:]
            return

        action = action_units[action_index]

        visit(
            action_index + 1,
            hand_state,
            searchable_state,
            remaining_discard,
            current_windows,
            used_actions,
        )

        if action.discard_cost > remaining_discard:
            return
        current = current_windows[acquisition_window_index]
        consumed = _consume_action_window(current, action.action_class)
        if consumed is None:
            return

        next_hand = list(hand_state)
        next_searchable = list(searchable_state)
        for card_class, count in action.hand_outputs:
            index = hand_index[card_class]
            if next_searchable[index] < count:
                return
            next_searchable[index] -= count
            next_hand[index] += count

        next_windows = list(current_windows)
        next_windows[acquisition_window_index] = consumed
        visit(
            action_index + 1,
            tuple(next_hand),
            tuple(next_searchable),
            remaining_discard - action.discard_cost,
            tuple(next_windows),
            used_actions + (action.name,),
        )

    visit(
        0,
        initial_hand_tuple,
        initial_searchable_tuple,
        discardable_cards,
        window_tuple,
        (),
    )
    if best is None:
        raise AssertionError("staged planner produced no terminal state")

    (
        key,
        execution,
        discard_spent,
        hand_map,
        searchable_map,
        used_actions,
        final_windows,
    ) = best
    maximum_completed = key[0]

    return StagedTrainerObjectiveResult(
        exact_joint_feasible=maximum_completed == total_objective_units,
        maximum_completed_units=maximum_completed,
        total_objective_units=total_objective_units,
        minimum_unmet_units=total_objective_units - maximum_completed,
        acquisition_actions=used_actions,
        discard_spent=discard_spent,
        execution_result=execution,
        hand_after_acquisition=tuple(sorted(hand_map.items())),
        searchable_after_acquisition=tuple(sorted(searchable_map.items())),
        windows_after_acquisition=final_windows,
    )
