"""Joint finite-horizon execution capacity for Trainers already in hand.

Acquisition is assumed to have happened. This module allocates physical hand
copies and typed action windows across one or more execution requirements.
Card-specific effect conditions remain downstream.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from functools import lru_cache
from typing import Mapping, Sequence

from lock_state_kernel import PlayerChannels
from trainer_search_transaction import TrainerSearchExecutionState
from turn_action_budget import TurnAction


_SUPPORTED_ACTION_CLASSES = frozenset(
    {"Item", "Pokémon Tool", "Supporter", "Stadium"}
)


@dataclass(frozen=True)
class ExecutionTurnWindow:
    """Generic Trainer play capacity available in one modeled turn."""

    turn: int
    supporter_plays_remaining: int = 1
    stadium_plays_remaining: int = 1
    channels: PlayerChannels = field(default_factory=PlayerChannels)

    def __post_init__(self) -> None:
        if self.turn < 0:
            raise ValueError("turn must be non-negative")
        if self.supporter_plays_remaining < 0:
            raise ValueError("supporter_plays_remaining must be non-negative")
        if self.stadium_plays_remaining < 0:
            raise ValueError("stadium_plays_remaining must be non-negative")


@dataclass(frozen=True)
class TrainerExecutionRequirement:
    """Copies of one acquired Trainer that must be playable inside a time window."""

    name: str
    card_class: str
    action_class: str
    copies: int = 1
    earliest_turn: int = 0
    deadline_turn: int = 0

    def __post_init__(self) -> None:
        if not self.name or not self.card_class:
            raise ValueError("requirement name and card_class must be non-empty")
        if self.action_class not in _SUPPORTED_ACTION_CLASSES:
            raise ValueError(
                f"unsupported Trainer action class: {self.action_class!r}"
            )
        if self.copies <= 0:
            raise ValueError("copies must be positive")
        if self.earliest_turn < 0 or self.deadline_turn < 0:
            raise ValueError("turn bounds must be non-negative")
        if self.earliest_turn > self.deadline_turn:
            raise ValueError("earliest_turn cannot exceed deadline_turn")


@dataclass(frozen=True)
class TrainerExecutionStep:
    requirement: str
    card_class: str
    action_class: str
    turn: int


@dataclass(frozen=True)
class TrainerExecutionCapacityResult:
    exact_joint_feasible: bool
    individually_feasible: tuple[bool, ...]
    maximum_executed_units: int
    minimum_unexecuted_units: int
    witness: tuple[TrainerExecutionStep, ...]


def execution_window_from_state(
    turn: int,
    state: TrainerSearchExecutionState,
) -> ExecutionTurnWindow:
    """Project one execution state into its generic Trainer play capacities."""

    return ExecutionTurnWindow(
        turn=turn,
        supporter_plays_remaining=state.budget.remaining(TurnAction.SUPPORTER),
        stadium_plays_remaining=state.budget.remaining(TurnAction.STADIUM_PLAY),
        channels=state.channels,
    )


def _channel_open(window: ExecutionTurnWindow, action_class: str) -> bool:
    if action_class == "Item":
        return window.channels.item_play
    if action_class == "Pokémon Tool":
        return window.channels.tool_play
    if action_class == "Supporter":
        return window.channels.supporter_play
    if action_class == "Stadium":
        return window.channels.stadium_play
    raise ValueError(f"unsupported Trainer action class: {action_class!r}")


def _quota_index(
    action_class: str,
    window_index: int,
    window_count: int,
) -> int | None:
    if action_class == "Supporter":
        return window_index
    if action_class == "Stadium":
        return window_count + window_index
    return None


def _maximize_execution(
    requirements: tuple[TrainerExecutionRequirement, ...],
    windows: tuple[ExecutionTurnWindow, ...],
    hand_counts: tuple[int, ...],
    hand_classes: tuple[str, ...],
) -> tuple[int, tuple[TrainerExecutionStep, ...]]:
    units = tuple(
        (requirement_index, copy_index)
        for requirement_index, requirement in enumerate(requirements)
        for copy_index in range(requirement.copies)
    )
    window_count = len(windows)
    starting_quotas = (
        tuple(window.supporter_plays_remaining for window in windows)
        + tuple(window.stadium_plays_remaining for window in windows)
    )
    class_index = {card_class: index for index, card_class in enumerate(hand_classes)}

    @lru_cache(maxsize=None)
    def solve(
        unit_index: int,
        remaining_hand: tuple[int, ...],
        remaining_quotas: tuple[int, ...],
    ) -> tuple[int, tuple[TrainerExecutionStep, ...]]:
        if unit_index == len(units):
            return 0, ()

        requirement_index, _copy_index = units[unit_index]
        requirement = requirements[requirement_index]

        best_count, best_steps = solve(
            unit_index + 1,
            remaining_hand,
            remaining_quotas,
        )

        hand_index = class_index[requirement.card_class]
        if remaining_hand[hand_index] <= 0:
            return best_count, best_steps

        for window_index, window in enumerate(windows):
            if not (
                requirement.earliest_turn
                <= window.turn
                <= requirement.deadline_turn
            ):
                continue
            if not _channel_open(window, requirement.action_class):
                continue

            quota_index = _quota_index(
                requirement.action_class,
                window_index,
                window_count,
            )
            if (
                quota_index is not None
                and remaining_quotas[quota_index] <= 0
            ):
                continue

            next_hand = list(remaining_hand)
            next_hand[hand_index] -= 1
            next_quotas = list(remaining_quotas)
            if quota_index is not None:
                next_quotas[quota_index] -= 1

            tail_count, tail_steps = solve(
                unit_index + 1,
                tuple(next_hand),
                tuple(next_quotas),
            )
            candidate_count = 1 + tail_count
            if candidate_count > best_count:
                best_count = candidate_count
                best_steps = (
                    TrainerExecutionStep(
                        requirement=requirement.name,
                        card_class=requirement.card_class,
                        action_class=requirement.action_class,
                        turn=window.turn,
                    ),
                ) + tail_steps

        return best_count, best_steps

    return solve(0, hand_counts, starting_quotas)


def evaluate_trainer_execution_capacity(
    hand_counts: Mapping[str, int],
    requirements: Sequence[TrainerExecutionRequirement],
    windows: Sequence[ExecutionTurnWindow],
) -> TrainerExecutionCapacityResult:
    """Allocate acquired cards and generic action windows exactly.

    ``individually_feasible`` evaluates each requirement against the same
    unmodified starting hand and turn windows. It deliberately does not allocate
    those resources across different requirements.

    ``exact_joint_feasible`` allocates each physical hand copy and each
    Supporter/Stadium quota unit once across the complete requirement set.
    """

    requirement_tuple = tuple(requirements)
    window_tuple = tuple(sorted(windows, key=lambda window: window.turn))
    if not requirement_tuple:
        raise ValueError("at least one execution requirement is required")
    if not window_tuple:
        raise ValueError("at least one execution window is required")
    turns = tuple(window.turn for window in window_tuple)
    if len(turns) != len(set(turns)):
        raise ValueError("execution window turns must be unique")
    if any(count < 0 for count in hand_counts.values()):
        raise ValueError("hand counts must be non-negative")

    hand_classes = tuple(
        sorted({requirement.card_class for requirement in requirement_tuple})
    )
    starting_hand = tuple(hand_counts.get(card_class, 0) for card_class in hand_classes)

    individually = []
    for requirement in requirement_tuple:
        count, _witness = _maximize_execution(
            (requirement,),
            window_tuple,
            starting_hand,
            hand_classes,
        )
        individually.append(count == requirement.copies)

    maximum, witness = _maximize_execution(
        requirement_tuple,
        window_tuple,
        starting_hand,
        hand_classes,
    )
    total_required = sum(requirement.copies for requirement in requirement_tuple)
    return TrainerExecutionCapacityResult(
        exact_joint_feasible=maximum == total_required,
        individually_feasible=tuple(individually),
        maximum_executed_units=maximum,
        minimum_unexecuted_units=total_required - maximum,
        witness=witness,
    )
