"""Small evidence-backed catalog of effect-order authority cases."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class OrderAuthorityCase(str, Enum):
    DAMAGED_POKEMON_TRIGGERS = "damaged_pokemon_triggers"
    MULTI_POKEMON_KO_TRIGGERS = "multi_pokemon_ko_triggers"
    ENERGY_ATTACHMENT_TRIGGERS = "energy_attachment_triggers"
    POKEMON_CHECKUP_EFFECTS = "pokemon_checkup_effects"
    END_OF_TURN_EFFECTS = "end_of_turn_effects"
    LOST_CITY_PERSISTENT_CELLS = "lost_city_persistent_cells"


@dataclass(frozen=True)
class OrderAuthorityContext:
    current_turn_player: str
    next_turn_player: str
    affected_pokemon_player: str | None = None
    knocked_out_pokemon_owner: str | None = None

    def __post_init__(self) -> None:
        if not self.current_turn_player:
            raise ValueError("current_turn_player must be non-empty")
        if not self.next_turn_player:
            raise ValueError("next_turn_player must be non-empty")
        if self.current_turn_player == self.next_turn_player:
            raise ValueError("current and next turn players must differ")


def ordering_player(
    case: OrderAuthorityCase,
    context: OrderAuthorityContext,
) -> str | None:
    """Return the evidence-backed chooser for one explicitly scoped case."""

    if case == OrderAuthorityCase.DAMAGED_POKEMON_TRIGGERS:
        return context.affected_pokemon_player

    if case == OrderAuthorityCase.MULTI_POKEMON_KO_TRIGGERS:
        return context.current_turn_player

    if case == OrderAuthorityCase.ENERGY_ATTACHMENT_TRIGGERS:
        return context.current_turn_player

    if case == OrderAuthorityCase.POKEMON_CHECKUP_EFFECTS:
        return context.next_turn_player

    if case == OrderAuthorityCase.END_OF_TURN_EFFECTS:
        return context.current_turn_player

    if case == OrderAuthorityCase.LOST_CITY_PERSISTENT_CELLS:
        return context.knocked_out_pokemon_owner

    raise ValueError(f"unsupported authority case: {case!r}")
