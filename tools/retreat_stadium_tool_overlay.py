"""Project global Stadium Tool-effect suppression onto physical board state."""

from __future__ import annotations

from dataclasses import dataclass, replace

from board_object_kernel import BoardState


JAMMING_TOWER_PRINT_IDS = frozenset({
    "sv6-153", "sv10-243", "me2pt5-261",
})


@dataclass(frozen=True)
class StadiumToolProjection:
    own_board: BoardState
    opponent_board: BoardState
    suppressed_own_tool_ids: tuple[str, ...] = ()
    suppressed_opponent_tool_ids: tuple[str, ...] = ()


def project_stadium_tool_state(
    own_board: BoardState,
    opponent_board: BoardState,
    *,
    stadium_print_id: str | None,
    stadium_effect_enabled: bool = True,
) -> StadiumToolProjection:
    """Blank current Tool effects under effective exact-print Jamming Tower.

    This is a derived current-state overlay. Attached physical Tool cards
    remain present and can reactivate after the Stadium changes.
    """
    if stadium_print_id not in JAMMING_TOWER_PRINT_IDS or not stadium_effect_enabled:
        return StadiumToolProjection(own_board, opponent_board)

    def apply(board: BoardState) -> tuple[BoardState, tuple[str, ...]]:
        disabled: list[str] = []
        objects = []
        for pokemon in board.objects:
            if pokemon.tool is not None and pokemon.pokemon_state.tool_effect_enabled:
                disabled.append(pokemon.tool.instance_id)
                pokemon = replace(
                    pokemon,
                    pokemon_state=replace(
                        pokemon.pokemon_state, tool_effect_enabled=False,
                    ),
                )
            objects.append(pokemon)
        next_board = replace(board, objects=tuple(objects))
        next_board.validate()
        return next_board, tuple(sorted(disabled))

    own, own_ids = apply(own_board)
    opponent, opponent_ids = apply(opponent_board)
    return StadiumToolProjection(own, opponent, own_ids, opponent_ids)


def restore_persistent_tool_flags(
    baseline: BoardState,
    result_board: BoardState,
) -> BoardState:
    """Remove an ephemeral Stadium overlay after resolving a Retreat action.

    The physical board does not own the current Stadium identity; its Tool
    flags remain the source's baseline for later independent derivations.
    Retreat changes positions and Energy, but preserves attached Tools.
    """
    baseline_flags = {
        pokemon.object_id: pokemon.pokemon_state.tool_effect_enabled
        for pokemon in baseline.objects
    }
    result = replace(
        result_board,
        objects=tuple(
            replace(
                pokemon,
                pokemon_state=replace(
                    pokemon.pokemon_state,
                    tool_effect_enabled=baseline_flags[pokemon.object_id],
                ),
            )
            for pokemon in result_board.objects
        ),
    )
    result.validate()
    return result
