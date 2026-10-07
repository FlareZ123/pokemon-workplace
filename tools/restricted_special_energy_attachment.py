"""Revalidate holder-restricted Special Energy attachments after state changes."""

from __future__ import annotations

from dataclasses import dataclass, replace

from board_object_kernel import BoardState, EnergyAttachment
from energy_board_conservation import ATTACHED, DISCARD, EnergyBoardState


@dataclass(frozen=True, order=True)
class RestrictedSpecialEnergyRule:
    print_id: str
    card_name: str
    required_tag: str


_RULE_ROWS = (
    ("dc1-33", "Double Aqua Energy", "Team Aqua"),
    ("dc1-34", "Double Magma Energy", "Team Magma"),
    ("me2pt5-217", "Team Rocket's Energy", "Team Rocket's"),
    ("sm10-190", "Triple Acceleration Energy", "Evolution"),
    ("sm10-234", "Triple Acceleration Energy", "Evolution"),
    ("sv10-182", "Team Rocket's Energy", "Team Rocket's"),
    ("swsh5-140", "Rapid Strike Energy", "Rapid Strike"),
    ("swsh5-141", "Single Strike Energy", "Single Strike"),
    ("swsh5-182", "Rapid Strike Energy", "Rapid Strike"),
    ("swsh5-183", "Single Strike Energy", "Single Strike"),
    ("swsh6-157", "Impact Energy", "Single Strike"),
    ("swsh6-159", "Spiral Energy", "Rapid Strike"),
    ("swsh8-244", "Fusion Strike Energy", "Fusion Strike"),
    ("xy10-115", "Strong Energy", "Fighting"),
    ("xy3-103", "Herbal Energy", "Grass"),
    ("xy3-104", "Strong Energy", "Fighting"),
    ("xy4-112", "Mystery Energy", "Psychic"),
    ("xy5-143", "Shield Energy", "Metal"),
    ("xy5-144", "Wonder Energy", "Fairy"),
    ("xy6-97", "Double Dragon Energy", "Dragon"),
    ("xy7-82", "Dangerous Energy", "Darkness"),
    ("xy7-83", "Flash Energy", "Lightning"),
    ("xy8-151", "Burning Energy", "Fire"),
    ("xy9-113", "Splash Energy", "Water"),
)

RESTRICTED_SPECIAL_ENERGY_RULES = tuple(
    RestrictedSpecialEnergyRule(*row)
    for row in _RULE_ROWS
)
_RULE_BY_PRINT = {
    rule.print_id: rule
    for rule in RESTRICTED_SPECIAL_ENERGY_RULES
}
_EVOLUTION_TAGS = frozenset({"Stage1", "Stage 1", "Stage2", "Stage 2", "Evolution"})


@dataclass(frozen=True)
class RestrictedEnergyDiscard:
    instance_id: str
    print_id: str
    card_name: str
    holder_id: str
    required_tag: str


@dataclass(frozen=True)
class RestrictedEnergyRevalidationResult:
    state: EnergyBoardState
    discarded: tuple[RestrictedEnergyDiscard, ...] = ()


def _holder_satisfies(required_tag: str, holder_tags: frozenset[str]) -> bool:
    if required_tag == "Evolution":
        return bool(holder_tags & _EVOLUTION_TAGS)
    return required_tag in holder_tags


def attachment_rule(
    energy: EnergyAttachment,
) -> RestrictedSpecialEnergyRule | None:
    if energy.print_id is None:
        return None
    rule = _RULE_BY_PRINT.get(energy.print_id)
    if rule is None or energy.card_name != rule.card_name:
        return None
    return rule


def revalidate_restricted_special_energy(
    state: EnergyBoardState,
) -> RestrictedEnergyRevalidationResult:
    """Discard exact restricted Special Energy whose current holder is illegal.

    This is a post-mutation normalization step. Physical Energy identity remains
    materialized while attached. If its exact-print restriction no longer
    accepts the holder, the card is removed from that board object, the attached
    zone count moves to discard, and the materialized instance index is removed.
    """

    zones = state.zones
    instance_classes = dict(state.instance_classes)
    discarded: list[RestrictedEnergyDiscard] = []
    next_objects = []

    for pokemon in state.board.objects:
        kept: list[EnergyAttachment] = []
        for energy in pokemon.energy:
            rule = attachment_rule(energy)
            if rule is None or _holder_satisfies(rule.required_tag, pokemon.tags):
                kept.append(energy)
                continue

            card_class = instance_classes.pop(energy.instance_id)
            zones = zones.move(card_class, ATTACHED, DISCARD)
            discarded.append(
                RestrictedEnergyDiscard(
                    instance_id=energy.instance_id,
                    print_id=rule.print_id,
                    card_name=rule.card_name,
                    holder_id=pokemon.object_id,
                    required_tag=rule.required_tag,
                )
            )

        next_objects.append(replace(pokemon, energy=tuple(kept)))

    if not discarded:
        return RestrictedEnergyRevalidationResult(state)

    board = replace(state.board, objects=tuple(next_objects))
    board.validate()
    next_state = EnergyBoardState(
        zones=zones,
        board=board,
        instance_classes=tuple(sorted(instance_classes.items())),
    )
    return RestrictedEnergyRevalidationResult(
        state=next_state,
        discarded=tuple(discarded),
    )
