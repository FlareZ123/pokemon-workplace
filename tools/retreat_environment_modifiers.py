"""Derive positional Ability and Stadium Retreat Cost effects from board state.

Exact-print, narrow semantic island. Unmodeled sources remain external.
"""

from __future__ import annotations

from board_object_kernel import BoardState
from retreat_cost_semantics import RetreatCostModifier


_GALAR_MINE = "swsh2-160"
_BIG_NET_ARIADOS = "sv6-5"
_CARRY_AND_CLIMB_SNEASLER = "swsh10-93"
_EVOLUTION_TAGS = frozenset({"Stage1", "Stage 1", "Stage2", "Stage 2", "Evolution"})


def derive_environment_retreat_modifiers(
    own_board: BoardState,
    opponent_board: BoardState,
    *,
    stadium_print_id: str | None = None,
    stadium_effect_enabled: bool = True,
) -> tuple[RetreatCostModifier, ...]:
    """Return modifiers to the OWN Active Pokemon's Retreat Cost.

    Stadium print is the currently active Stadium (if any). Ability-enabled
    flags are already-resolved source suppression, not inferred here.
    """
    modifiers: list[RetreatCostModifier] = []
    active = own_board.get(own_board.active_id)

    if stadium_print_id == _GALAR_MINE and stadium_effect_enabled:
        modifiers.append(RetreatCostModifier("stadium:Galar Mine", delta=2))

    if active.tags & _EVOLUTION_TAGS:
        for source in opponent_board.objects:
            if (
                source.print_id == _BIG_NET_ARIADOS
                and source.card_name == "Ariados"
                and source.abilities_enabled
            ):
                modifiers.append(
                    RetreatCostModifier(f"{source.object_id}:Big Net", delta=1)
                )

    for source in own_board.objects:
        if (
            source.object_id in own_board.bench_ids
            and source.print_id == _CARRY_AND_CLIMB_SNEASLER
            and source.card_name == "Hisuian Sneasler"
            and source.abilities_enabled
        ):
            modifiers.append(
                RetreatCostModifier(f"{source.object_id}:Carry and Climb", delta=-2)
            )

    return tuple(modifiers)
