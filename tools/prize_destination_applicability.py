"""Derive Prize-destination replacements across a Knock Out boundary.

Lost Block is continuous and must survive until Prize taking. Billowing Smoke is
captured from the Knocked Out holder when its Tool effect was live at the KO
trigger. This module derives applicable replacement programs and leaves final
ordering to prize_destination_overrides.
"""

from __future__ import annotations

from board_object_kernel import BoardPokemon, BoardState
from prize_destination_overrides import PrizeDestinationOverride

LOST_BLOCK_PRINT_IDS = frozenset({"swsh11-107"})
BILLOWING_SMOKE_PRINT_IDS = frozenset({"swsh3-158"})


def derive_knockout_prize_overrides(
    defender_after_ko: BoardState | None,
    knocked_out: BoardPokemon,
    *,
    knocked_out_by_opponent_attack_damage: bool,
) -> tuple[PrizeDestinationOverride, ...]:
    """Return destination replacements applicable to this opponent Prize award."""

    rows: list[PrizeDestinationOverride] = []

    if defender_after_ko is not None:
        for pokemon in defender_after_ko.objects:
            if (
                pokemon.print_id in LOST_BLOCK_PRINT_IDS
                and pokemon.abilities_enabled
            ):
                rows.append(
                    PrizeDestinationOverride(
                        f"Lost Block:{pokemon.object_id}",
                        "lost_zone",
                    )
                )

    tool = knocked_out.tool
    if (
        knocked_out_by_opponent_attack_damage
        and tool is not None
        and tool.print_id in BILLOWING_SMOKE_PRINT_IDS
        and knocked_out.pokemon_state.tool_effect_enabled
    ):
        rows.append(
            PrizeDestinationOverride(
                f"Billowing Smoke:{tool.instance_id}",
                "discard",
            )
        )

    return tuple(sorted(rows))
