"""Derive Retreat Cost modifiers from represented active Pokémon Tools."""

from __future__ import annotations

from dataclasses import dataclass

from board_object_kernel import BoardPokemon, BoardState
from retreat_cost_semantics import RetreatCostModifier, no_retreat_cost


_AIR_BALLOON = frozenset({
    "me1-166", "me2pt5-181", "swsh1-156", "swsh1-213", "zsv10pt5-79",
})
_FLOAT_STONE = frozenset({"bw9-99", "xy8-137"})
_U_TURN_BOARD = frozenset({"sm11-211", "sm11-255"})
_ESCAPE_BOARD = frozenset({"sm5-122", "sm5-122a", "sm5-167"})
_BIG_AIR_BALLOON = frozenset({"sv3pt5-155"})
_FUTURE_BOOSTER = frozenset({"sv4-164", "sv5-149"})
_RESCUE_BOARD = frozenset({"sv5-159", "sv6-225", "sv8pt5-126"})
_GRAVITY_GEMSTONE = frozenset({"sv7-137"})
_SNOW_LEAF_BADGE = frozenset({"swsh7-159"})

RETREAT_MODIFYING_TOOL_PRINT_IDS = frozenset().union(
    _AIR_BALLOON,
    _FLOAT_STONE,
    _U_TURN_BOARD,
    _ESCAPE_BOARD,
    _BIG_AIR_BALLOON,
    _FUTURE_BOOSTER,
    _RESCUE_BOARD,
    _GRAVITY_GEMSTONE,
    _SNOW_LEAF_BADGE,
)


@dataclass(frozen=True)
class UnresolvedToolRetreatCondition:
    instance_id: str
    card_name: str
    condition: str


@dataclass(frozen=True)
class ToolRetreatDerivation:
    modifiers: tuple[RetreatCostModifier, ...]
    unresolved_conditions: tuple[UnresolvedToolRetreatCondition, ...] = ()

    @property
    def exact(self) -> bool:
        return not self.unresolved_conditions


def _active_tool_enabled(pokemon: BoardPokemon) -> bool:
    return (
        pokemon.tool is not None
        and pokemon.pokemon_state.tool_effect_enabled
    )


def _self_tool_modifiers(
    pokemon: BoardPokemon,
    *,
    remaining_hp: int | None,
) -> ToolRetreatDerivation:
    if not _active_tool_enabled(pokemon):
        return ToolRetreatDerivation(())

    tool = pokemon.tool
    assert tool is not None
    print_id = tool.print_id
    if print_id is None:
        return ToolRetreatDerivation(())

    effect_id = f"{tool.instance_id}:{tool.card_name}"
    modifiers: list[RetreatCostModifier] = []
    unresolved: list[UnresolvedToolRetreatCondition] = []

    if print_id in _AIR_BALLOON and tool.card_name == "Air Balloon":
        modifiers.append(RetreatCostModifier(effect_id, delta=-2))
    elif print_id in _FLOAT_STONE and tool.card_name == "Float Stone":
        modifiers.append(no_retreat_cost(effect_id))
    elif print_id in _U_TURN_BOARD and tool.card_name == "U-Turn Board":
        modifiers.append(RetreatCostModifier(effect_id, delta=-1))
    elif print_id in _ESCAPE_BOARD and tool.card_name == "Escape Board":
        modifiers.append(RetreatCostModifier(effect_id, delta=-1))
    elif print_id in _BIG_AIR_BALLOON and tool.card_name == "Big Air Balloon":
        if "Stage2" in pokemon.tags or "Stage 2" in pokemon.tags:
            modifiers.append(no_retreat_cost(effect_id))
    elif (
        print_id in _FUTURE_BOOSTER
        and tool.card_name == "Future Booster Energy Capsule"
    ):
        if "Future" in pokemon.tags:
            modifiers.append(no_retreat_cost(effect_id))
    elif print_id in _RESCUE_BOARD and tool.card_name == "Rescue Board":
        modifiers.append(RetreatCostModifier(effect_id + ":base", delta=-1))
        if remaining_hp is None:
            unresolved.append(
                UnresolvedToolRetreatCondition(
                    tool.instance_id,
                    tool.card_name,
                    "holder remaining HP <= 30",
                )
            )
        elif remaining_hp <= 30:
            modifiers.append(no_retreat_cost(effect_id + ":low-hp"))
    elif print_id in _GRAVITY_GEMSTONE and tool.card_name == "Gravity Gemstone":
        modifiers.append(RetreatCostModifier(effect_id, delta=1))
    elif print_id in _SNOW_LEAF_BADGE and tool.card_name == "Snow Leaf Badge":
        is_v = bool(
            pokemon.tags
            & frozenset({
                "Pokemon V", "Pokémon V",
                "Pokemon VMAX", "Pokémon VMAX",
                "Pokemon VSTAR", "Pokémon VSTAR",
            })
        )
        if is_v and (
            "Leafeon" in pokemon.card_name
            or "Glaceon" in pokemon.card_name
        ):
            modifiers.append(no_retreat_cost(effect_id))

    return ToolRetreatDerivation(tuple(modifiers), tuple(unresolved))


def derive_tool_retreat_modifiers(
    own_board: BoardState,
    opponent_board: BoardState,
    *,
    active_remaining_hp: int | None = None,
) -> ToolRetreatDerivation:
    """Derive active-holder Tool effects that change own Active Retreat Cost."""

    own_active = own_board.get(own_board.active_id)
    own = _self_tool_modifiers(
        own_active,
        remaining_hp=active_remaining_hp,
    )
    modifiers = list(own.modifiers)

    opponent_active = opponent_board.get(opponent_board.active_id)
    if _active_tool_enabled(opponent_active):
        tool = opponent_active.tool
        assert tool is not None
        if (
            tool.print_id in _GRAVITY_GEMSTONE
            and tool.card_name == "Gravity Gemstone"
        ):
            modifiers.append(
                RetreatCostModifier(
                    f"{tool.instance_id}:{tool.card_name}:opposing",
                    delta=1,
                )
            )

    return ToolRetreatDerivation(
        modifiers=tuple(modifiers),
        unresolved_conditions=own.unresolved_conditions,
    )
