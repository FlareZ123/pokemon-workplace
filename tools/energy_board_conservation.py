"""Conserve Energy copies between zone counts and board attachments."""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Iterable

from board_object_kernel import BoardState, EnergyAttachment, retreat
from multicopy_zone_state import ZoneCountState


HAND = "hand"
ATTACHED = "attached"
DISCARD = "discard"


@dataclass(frozen=True)
class EnergyBoardState:
    zones: ZoneCountState
    board: BoardState
    instance_classes: tuple[tuple[str, str], ...] = ()

    def __post_init__(self) -> None:
        self.validate()

    def validate(self) -> None:
        self.board.validate()
        ids = [instance_id for instance_id, _ in self.instance_classes]
        if len(ids) != len(set(ids)):
            raise ValueError("Energy instance IDs must be unique")
        if self.instance_classes != tuple(sorted(self.instance_classes)):
            raise ValueError("instance_classes must be canonically sorted")

        board_ids = {
            energy.instance_id
            for pokemon in self.board.objects
            for energy in pokemon.energy
        }
        if board_ids != set(ids):
            raise ValueError("Energy instance index must match board attachments")

        expected: dict[str, int] = {}
        for _instance_id, card_class in self.instance_classes:
            expected[card_class] = expected.get(card_class, 0) + 1

        ledger_classes = {
            card_class
            for card_class, zone, _count in self.zones.counts
            if zone == ATTACHED
        }
        if ledger_classes != set(expected):
            raise ValueError("Attached Energy classes disagree with board index")

        for card_class, count in expected.items():
            if self.zones.count(card_class, ATTACHED) != count:
                raise ValueError("Attached Energy count disagrees with board index")


def _replace_energy(
    board: BoardState,
    object_id: str,
    energy: tuple[EnergyAttachment, ...],
) -> BoardState:
    pokemon = board.get(object_id)
    next_pokemon = replace(pokemon, energy=energy)
    next_board = replace(
        board,
        objects=tuple(
            next_pokemon if row.object_id == object_id else row
            for row in board.objects
        ),
    )
    next_board.validate()
    return next_board


def materialize_energy_from_hand(
    state: EnergyBoardState,
    *,
    object_id: str,
    card_class: str,
    instance_id: str,
    card_name: str,
    units: tuple[str, ...],
    print_id: str | None = None,
) -> EnergyBoardState | None:
    if state.zones.count(card_class, HAND) <= 0:
        return None
    if any(current_id == instance_id for current_id, _ in state.instance_classes):
        return None

    try:
        pokemon = state.board.get(object_id)
    except KeyError:
        return None

    attachment = EnergyAttachment(
        instance_id,
        card_name,
        units,
        print_id=print_id,
    )
    board = _replace_energy(
        state.board,
        object_id,
        pokemon.energy + (attachment,),
    )
    zones = state.zones.move(card_class, HAND, ATTACHED)
    index = tuple(sorted(state.instance_classes + ((instance_id, card_class),)))
    return EnergyBoardState(zones, board, index)


def retreat_with_energy_conservation(
    state: EnergyBoardState,
    bench_object_id: str,
    *,
    retreat_cost: int,
    discard_energy_ids: Iterable[str],
) -> EnergyBoardState | None:
    result = retreat(
        state.board,
        bench_object_id,
        retreat_cost=retreat_cost,
        discard_energy_ids=discard_energy_ids,
    )
    if result is None:
        return None

    board, discarded = result
    index = dict(state.instance_classes)
    zones = state.zones
    for energy in discarded:
        card_class = index.pop(energy.instance_id)
        zones = zones.move(card_class, ATTACHED, DISCARD)

    return EnergyBoardState(
        zones,
        board,
        tuple(sorted(index.items())),
    )
