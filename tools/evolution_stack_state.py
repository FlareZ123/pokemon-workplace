from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Iterable

from board_object_kernel import BoardState


@dataclass(frozen=True)
class StackCard:
    instance_id: str
    card_name: str
    stage_rank: int
    hp: int
    evolves_from: str | None = None
    tags: frozenset[str] = frozenset()
    print_id: str | None = None

    def __post_init__(self) -> None:
        if not self.instance_id or not self.card_name or self.stage_rank < 0 or self.hp <= 0:
            raise ValueError("invalid stack card")


@dataclass(frozen=True)
class PokemonStack:
    object_id: str
    cards: tuple[StackCard, ...]
    evolution_eligible: bool = True

    @property
    def top(self) -> StackCard:
        return self.cards[-1]


@dataclass(frozen=True)
class EvolutionState:
    board: BoardState
    stacks: tuple[PokemonStack, ...]
    evolution_allowed: bool = True

    def stack(self, object_id: str) -> PokemonStack:
        return next(row for row in self.stacks if row.object_id == object_id)

    def validate(self) -> None:
        board_ids = {row.object_id for row in self.board.objects}
        stack_ids = [row.object_id for row in self.stacks]
        if set(stack_ids) != board_ids or len(stack_ids) != len(set(stack_ids)):
            raise ValueError("stack objects must match board objects exactly")
        card_ids: list[str] = []
        for row in self.stacks:
            if not row.cards:
                raise ValueError("Pokemon stack cannot be empty")
            ranks = [card.stage_rank for card in row.cards]
            if any(left >= right for left, right in zip(ranks, ranks[1:])):
                raise ValueError("physical stack stage ranks must increase")
            board_top = self.board.get(row.object_id)
            if board_top.card_name != row.top.card_name:
                raise ValueError("board top-card name disagrees with evolution stack")
            if (
                row.top.print_id is not None
                and board_top.print_id != row.top.print_id
            ):
                raise ValueError("board top-card print ID disagrees with evolution stack")
            card_ids.extend(card.instance_id for card in row.cards)
        if len(card_ids) != len(set(card_ids)):
            raise ValueError("physical Pokemon card IDs must be unique")


def make_evolution_state(
    board: BoardState, stacks: Iterable[PokemonStack], *, evolution_allowed: bool = True,
) -> EvolutionState:
    state = EvolutionState(board, tuple(stacks), evolution_allowed)
    state.validate()
    return state


def replace_stack(state: EvolutionState, updated: PokemonStack) -> EvolutionState:
    next_state = replace(state, stacks=tuple(
        updated if row.object_id == updated.object_id else row for row in state.stacks
    ))
    next_state.validate()
    return next_state
