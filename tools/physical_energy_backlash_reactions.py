"""Physical Energy backlash triggered when an Active is damaged by an attack.

Supported printed legal sources:
- Turtonator Shell Spikes and Klawf ex Counterattacking Pincer discard one
  Energy from the Attacking Pokémon.
- Rugged Helmet returns one Energy from the attacker to its owner's hand.
- Handheld Fan moves a Basic Energy from the attacker onto its owner's Bench.

The caller supplies the opposing-Pokémon attack fact and card-selection
policy, while source print identities and attachment/Ability eligibility
are checked against the conserved materialized board.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
import json
from pathlib import Path
import re

from attack_copy_physical_ko_bridge import AttackCopyPhysicalBoardResolution
from board_position_state import AttachmentKind, replace_pokemon
from build_expanded_legality_baseline import classify_effective_legality
from identity_materialization import (
    assert_conserved, attach_instance, dematerialize, detach_instance,
)
from physical_copy_damage_reaction_bridge import PhysicalCopyReactionResult
from stack_knockout_conservation import StackBoardMaterialState


class EnergyReactionKind(str, Enum):
    DISCARD = "discard"
    RETURN_TO_HAND = "return_to_hand"
    MOVE_TO_BENCH = "move_to_bench"


@dataclass(frozen=True)
class PrintedEnergyReaction:
    kind: EnergyReactionKind
    source_print_id: str
    source_instance_id: str | None


@dataclass(frozen=True)
class EnergyReactionOutcome:
    reaction: PrintedEnergyReaction
    applied: bool
    reason: str
    energy_instance_id: str | None = None
    destination_pokemon_id: str | None = None


_BODY_TO_KIND = {
    "discard an Energy from the Attacking Pokémon": EnergyReactionKind.DISCARD,
    "put an Energy attached to the Attacking Pokémon into your opponent's hand":
        EnergyReactionKind.RETURN_TO_HAND,
    "move an Energy from the Attacking Pokémon to 1 of your opponent's Benched Pokémon":
        EnergyReactionKind.MOVE_TO_BENCH,
}

_ABILITY = re.compile(
    r"^If this Pokémon is in the Active Spot and is damaged by an attack "
    r"from your opponent's Pokémon \(even if this Pokémon is Knocked Out\), "
    r"(?P<body>.+)\.$"
)
_TOOL = re.compile(
    r"^If the Pokémon this card is attached to is in the Active Spot and "
    r"is damaged by an attack from your opponent's Pokémon "
    r"\(even if (?:this Pokémon|it) is Knocked Out\), (?P<body>.+)\.$"
)

_BASIC_NAMES = frozenset({
    "Grass Energy", "Fire Energy", "Water Energy", "Lightning Energy",
    "Psychic Energy", "Fighting Energy", "Darkness Energy",
    "Metal Energy", "Fairy Energy",
})


def _source_card(resources: Path, print_id: str) -> dict:
    set_id = print_id.split("-")[0]
    sets = json.loads(
        (resources / "sets" / "en.json").read_text(encoding="utf-8")
    )
    matching = next(row for row in sets if row["id"] == set_id)
    if (matching.get("legalities") or {}).get("expanded") != "Legal":
        raise ValueError("energy reaction source set is outside Expanded")

    cards = json.loads(
        (resources / "cards" / "en" / f"{set_id}.json")
        .read_text(encoding="utf-8")
    )
    card = next(row for row in cards if row["id"] == print_id)
    if classify_effective_legality(card)[0] != "Legal":
        raise ValueError("energy reaction source print is banned")
    return card


def eligible_printed_energy_backlash(
    copy_resolution: AttackCopyPhysicalBoardResolution,
    *,
    resources: Path,
    body_event: str,
    damaged_pokemon_id: str,
    source_print_id: str,
    source_instance_id: str | None,
    ability_is_enabled: bool,
    from_opponents_pokemon: bool,
) -> tuple[PrintedEnergyReaction, ...]:
    """Derive physical Energy retaliation from one eligible source print."""

    records = [
        row for row in copy_resolution.damage_records
        if row.event == body_event and row.target_id == damaged_pokemon_id
    ]
    if len(records) != 1:
        raise ValueError("energy backlash needs one unique damage record")

    board = copy_resolution.state.board
    if board is None:
        raise ValueError("reaction source no longer has an in-play board")

    holder = board.get(damaged_pokemon_id)
    card = _source_card(resources, source_print_id)

    texts: list[str] = []
    if card["supertype"] == "Pokémon":
        if holder.name != card["name"]:
            raise ValueError("live Pokémon differs from bound source print")
        if ability_is_enabled:
            texts = [
                " ".join((entry.get("text") or "").split())
                for entry in card.get("abilities") or ()
            ]
        matcher = _ABILITY
    elif card["supertype"] == "Trainer" and "Pokémon Tool" in (
        card.get("subtypes") or ()
    ):
        if source_instance_id is None:
            raise ValueError("Tool backlash requires a materialized source ID")
        matching_tool = [
            entry for entry in holder.attachments
            if entry.card_id == source_instance_id
            and entry.kind is AttachmentKind.TOOL
            and entry.name == card["name"]
        ]
        if len(matching_tool) != 1:
            raise ValueError("Tool print is not bound to the damaged Pokémon")
        if holder.combat.tool_effect_enabled:
            texts = [
                " ".join(text.split()) for text in card.get("rules") or ()
            ]
        matcher = _TOOL
    else:
        raise ValueError("unsupported printed reaction source kind")

    if (
        board.active_id != damaged_pokemon_id
        or records[0].result.final_damage == 0
        or not from_opponents_pokemon
    ):
        return ()

    reactions = []
    for text in texts:
        match = matcher.fullmatch(text)
        if match and match.group("body") in _BODY_TO_KIND:
            reactions.append(
                PrintedEnergyReaction(
                    _BODY_TO_KIND[match.group("body")],
                    source_print_id,
                    source_instance_id,
                )
            )
    return tuple(reactions)


def apply_physical_energy_backlash(
    base: PhysicalCopyReactionResult,
    reaction: PrintedEnergyReaction,
    *,
    energy_instance_id: str | None,
    destination_pokemon_id: str | None = None,
) -> tuple[PhysicalCopyReactionResult, EnergyReactionOutcome]:
    """Resolve one source-authenticated Energy choice on the attacker board.

    A missing Energy or a missing destination Bench for movement means the
    effect cannot move a card. An invalid explicit choice is rejected.
    Special Energy move restrictions need a richer receiving-Pokémon profile,
    so this narrow move effect accepts only Basic Energy.
    """

    board = base.attacker_state.board
    if board is None:
        raise ValueError("cannot move Energy without a physical attacker board")
    attacker = board.get(base.attacking_pokemon_id)

    energy = tuple(
        entry for entry in attacker.attachments
        if entry.kind is AttachmentKind.ENERGY
    )
    if not base.triggered or not energy:
        return base, EnergyReactionOutcome(reaction, False, "no_eligible_damage_or_energy")

    if energy_instance_id is None:
        raise ValueError("an Energy selection is required when Energy is attached")
    selected = [e for e in energy if e.card_id == energy_instance_id]
    if len(selected) != 1:
        raise ValueError("selected Energy was not attached to the attacking Pokémon")
    card = selected[0]

    if reaction.kind is EnergyReactionKind.MOVE_TO_BENCH:
        if not board.bench_ids:
            return base, EnergyReactionOutcome(reaction, False, "no_destination_bench")
        if destination_pokemon_id not in board.bench_ids:
            raise ValueError("move destination must be an actual Benched Pokémon")
        if destination_pokemon_id == attacker.pokemon_id:
            raise ValueError("cannot move an Energy to its existing holder")
        if card.name not in _BASIC_NAMES:
            raise ValueError(
                "Special Energy movement requires receiving-Pokémon restrictions"
            )

        destination = board.get(destination_pokemon_id)
        without = replace(
            attacker,
            attachments=tuple(
                entry for entry in attacker.attachments
                if entry.card_id != energy_instance_id
            ),
        )
        updated = replace(
            destination,
            attachments=destination.attachments + (card,),
        )
        next_board = replace_pokemon(
            replace_pokemon(board, without), updated,
        )
        ledger = attach_instance(
            base.attacker_state.ledger, energy_instance_id,
            destination_pokemon_id,
        )
    else:
        destination = (
            "discard" if reaction.kind is EnergyReactionKind.DISCARD
            else "hand"
        )
        without = replace(
            attacker,
            attachments=tuple(
                entry for entry in attacker.attachments
                if entry.card_id != energy_instance_id
            ),
        )
        next_board = replace_pokemon(board, without)
        ledger = detach_instance(
            base.attacker_state.ledger, energy_instance_id,
            destination,
        )
        ledger = dematerialize(ledger, energy_instance_id)

    next_state = StackBoardMaterialState(ledger, next_board)
    assert_conserved(base.attacker_state.ledger, next_state.ledger)
    return (
        replace(base, attacker_state=next_state),
        EnergyReactionOutcome(
            reaction,
            True,
            "applied",
            energy_instance_id,
            destination_pokemon_id,
        ),
    )
