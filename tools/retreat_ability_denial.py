"""Resolve represented continuous Ability-based opponent Retreat prohibitions.

The target is the caller's Active Pokemon. Attack-applied temporary locks are
already tracked on that Pokemon by the board-object kernel.
"""

from __future__ import annotations

from board_object_kernel import BoardState
from garbotoxin_suppression import stealthy_hood_protects_from_opponent

_ACTIVE_SOURCE_PRINTS = frozenset({
    ("bw8-101", "Snorlax"),       # Block
    ("pgo-55", "Snorlax"),        # Block
    ("sm35-47", "Spiritomb"),    # Cursed Whirlpool
    ("sv3pt5-139", "Omastar"),   # Primordial Tentacles
    ("swsh3-91", "Flygon"),      # Labyrinth of Sand
})
_SPECIAL_CONDITION_SOURCE = ("sm12-11", "Cradily")  # Swaying Strangle
_POISON_SOURCE_PRINTS = frozenset({
    ("xy2-71", "Dragalge"),
    ("xyp-XY10", "Dragalge"),
})


def opposing_retreat_denial_source_ids(
    own_board: BoardState,
    opponent_board: BoardState,
) -> tuple[str, ...]:
    """Return opponent source IDs currently forbidding ordinary Retreat.

    Ability activation/suppression is represented upstream by the
    abilities_enabled flag. Both boards must represent the current
    Active positions and Special Conditions.
    """
    own_active = own_board.get(own_board.active_id)
    if stealthy_hood_protects_from_opponent(own_active):
        return ()

    conditions = own_active.special_conditions
    blocking_sources: list[str] = []

    for source in opponent_board.objects:
        if not source.abilities_enabled:
            continue
        key = (source.print_id, source.card_name)
        if key in _ACTIVE_SOURCE_PRINTS:
            if source.object_id == opponent_board.active_id:
                blocking_sources.append(source.object_id)
        elif key == _SPECIAL_CONDITION_SOURCE:
            if conditions:
                blocking_sources.append(source.object_id)
        elif key in _POISON_SOURCE_PRINTS:
            if "Poisoned" in conditions:
                blocking_sources.append(source.object_id)

    return tuple(sorted(blocking_sources))
