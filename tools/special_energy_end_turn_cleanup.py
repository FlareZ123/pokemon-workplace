"""Conserve Special Energy cards that self-discard at end of turn."""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Iterable

from energy_board_conservation import ATTACHED, DISCARD, EnergyBoardState
from retreat_energy_transaction import RetreatEnergyTransactionState


@dataclass(frozen=True, order=True)
class EndTurnSpecialEnergyRule:
    print_id: str
    card_name: str
    attachment_turn_only: bool


END_TURN_SPECIAL_ENERGY_RULES = (
    EndTurnSpecialEnergyRule("dc1-33", "Double Aqua Energy", True),
    EndTurnSpecialEnergyRule("dc1-34", "Double Magma Energy", True),
    EndTurnSpecialEnergyRule("sm10-190", "Triple Acceleration Energy", False),
    EndTurnSpecialEnergyRule("sm10-234", "Triple Acceleration Energy", False),
)
_RULE_BY_PRINT = {
    rule.print_id: rule
    for rule in END_TURN_SPECIAL_ENERGY_RULES
}


@dataclass(frozen=True)
class EndTurnEnergyDiscard:
    instance_id: str
    print_id: str
    card_name: str
    holder_id: str
    attachment_turn_only: bool


@dataclass(frozen=True)
class EndTurnEnergyCleanupResult:
    state: RetreatEnergyTransactionState
    discarded: tuple[EndTurnEnergyDiscard, ...] = ()


def cleanup_end_turn_special_energy(
    state: RetreatEnergyTransactionState,
    *,
    attached_this_turn_ids: Iterable[str] = (),
) -> EndTurnEnergyCleanupResult | None:
    """Resolve represented self-discard clauses after the turn has ended.

    Triple Acceleration Energy discards whenever it remains attached at the end
    of the turn. Double Aqua and Double Magma Energy discard only at the end of
    the turn in which that physical instance was attached, so callers must
    provide attachment-this-turn provenance for those two families.
    """

    budget = state.unified.turn_budget
    if budget is None or not budget.turn_ended:
        return None

    attached_this_turn = frozenset(attached_this_turn_ids)
    zones = state.energy.zones
    instance_classes = dict(state.energy.instance_classes)
    discarded: list[EndTurnEnergyDiscard] = []
    next_objects = []

    for pokemon in state.energy.board.objects:
        kept = []
        for energy in pokemon.energy:
            rule = (
                _RULE_BY_PRINT.get(energy.print_id)
                if energy.print_id is not None
                else None
            )
            applies = (
                rule is not None
                and energy.card_name == rule.card_name
                and (
                    not rule.attachment_turn_only
                    or energy.instance_id in attached_this_turn
                )
            )
            if not applies:
                kept.append(energy)
                continue

            card_class = instance_classes.pop(energy.instance_id)
            zones = zones.move(card_class, ATTACHED, DISCARD)
            discarded.append(
                EndTurnEnergyDiscard(
                    instance_id=energy.instance_id,
                    print_id=rule.print_id,
                    card_name=rule.card_name,
                    holder_id=pokemon.object_id,
                    attachment_turn_only=rule.attachment_turn_only,
                )
            )

        next_objects.append(replace(pokemon, energy=tuple(kept)))

    if not discarded:
        return EndTurnEnergyCleanupResult(state)

    board = replace(state.energy.board, objects=tuple(next_objects))
    board.validate()
    energy_state = EnergyBoardState(
        zones=zones,
        board=board,
        instance_classes=tuple(sorted(instance_classes.items())),
    )
    return EndTurnEnergyCleanupResult(
        state=RetreatEnergyTransactionState(
            unified=state.unified,
            energy=energy_state,
        ),
        discarded=tuple(discarded),
    )
