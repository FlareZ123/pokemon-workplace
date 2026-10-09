"""Finish a printed turn-ending Item, Ability, or Stadium effect.

The source card's *effect* was already legally executed by upstream code:
- An Item closes the turn after its effect resolves.
- A Pokémon Ability with 'If you use this Ability, your turn ends'
  closes after the Ability resolves.
- A Stadium's activated effect may close the turn; merely *playing*
  the Stadium from hand does not trigger that effect.

Supporter-specific Active Ability exemptions, legacy evolution rules,
and delayed attachment triggers have separate dedicated bridges.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json

from board_object_kernel import BoardState
from build_expanded_legality_baseline import classify_effective_legality
from turn_action_budget import TurnAction, TurnActionBudget


def _card(resources: Path, print_id: str) -> dict:
    cards = json.loads(
        (resources / "cards" / "en" / f"{print_id.split('-')[0]}.json")
        .read_text(encoding="utf-8")
    )
    card = next(x for x in cards if x["id"] == print_id)
    if classify_effective_legality(card)[0] != "Legal":
        raise ValueError("source print unavailable in bundled Expanded format")
    return card


@dataclass(frozen=True)
class DirectActionTurnEnd:
    budget: TurnActionBudget
    source_print_id: str
    source_name: str
    channel: str
    action_name: str


def close_after_completed_source_effect(
    resources: Path,
    *,
    source_print_id: str,
    channel: str,
    budget: TurnActionBudget,
    active_stadium_print_id: str | None = None,
    player_board: BoardState | None = None,
    ability_object_id: str | None = None,
    ability_name: str | None = None,
    suppressed_ability_object_ids: frozenset[str] = frozenset(),
) -> DirectActionTurnEnd:
    """Close turn only for an authenticated effect that has already resolved.

    Exact channels accepted: item_effect, stadium_activation, ability_use.
    A caller must not use this function to announce/pay an unresolved action.
    """
    card = _card(resources, source_print_id)
    rules = card.get("rules") or ()
    action_name = card["name"]

    if channel == "item_effect":
        if (
            card["supertype"] != "Trainer"
            or "Item" not in (card.get("subtypes") or ())
            or not any(rule.endswith("Your turn ends.") for rule in rules)
        ):
            raise ValueError("source lacks a printed turn-ending Item effect")

    elif channel == "stadium_activation":
        if (
            card["supertype"] != "Trainer"
            or "Stadium" not in (card.get("subtypes") or ())
            or source_print_id != active_stadium_print_id
            or not any("their turn ends" in rule.lower() for rule in rules)
        ):
            raise ValueError("Stadium is not current or lacks end-turn activation")

    elif channel == "ability_use":
        if (
            card["supertype"] != "Pokémon"
            or player_board is None
            or ability_object_id is None
            or ability_name is None
        ):
            raise ValueError("Ability requires an in-play physical source")
        physical = player_board.get(ability_object_id)
        if physical.print_id != source_print_id or physical.card_name != card["name"]:
            raise ValueError("Ability source is not bound to physical print")
        if (
            not physical.abilities_enabled
            or ability_object_id in suppressed_ability_object_ids
        ):
            raise ValueError("source Ability is suppressed")
        abilities = [
            row for row in card.get("abilities") or ()
            if row["name"] == ability_name
            and "your turn ends" in row.get("text", "").lower()
        ]
        if len(abilities) != 1:
            raise ValueError("selected Ability lacks a printed turn-ending effect")
        action_name = ability_name

    else:
        raise ValueError("unsupported direct turn-ending effect channel")

    used = budget.consume(TurnAction.END_TURN)
    if used is None:
        raise ValueError("cannot resolve another action on an ended turn")
    return DirectActionTurnEnd(
        budget=used, source_print_id=source_print_id,
        source_name=card["name"], channel=channel, action_name=action_name,
    )
