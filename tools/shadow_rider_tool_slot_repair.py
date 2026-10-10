"""Bounded Tool-slot repair preceding Shadow Rider's post-Trifrost recovery.

Pre-actions represent playing Field Blower, a Stadium, and/or Star Alchemy from
an attached Forest Seal Stone. The parent recovery planner handles Tulip,
attachments, promotion and attack readiness. Item lock only prevents Field
Blower; playing Pokémon Tools or Stadiums is governed separately.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, replace

from shadow_rider_post_trifrost_recovery import (
    RecoveryScenario, find_recovery
)


@dataclass(frozen=True)
class ToolConflictScenario:
    recovery: RecoveryScenario = RecoveryScenario()
    incumbent_tool: str = "Forest Seal Stone"
    jamming_tower_live: bool = False
    field_blower_in_hand: bool = False
    field_blower_in_deck: bool = False
    forest_star_alchemy_unused: bool = True
    replacement_stadium_in_hand: str | None = None
    stadium_play_unused: bool = True
    other_tool_lock: bool = False

    def __post_init__(self) -> None:
        if self.incumbent_tool not in {"None", "Forest Seal Stone", "Other"}:
            raise ValueError("invalid incumbent Tool")
        if self.replacement_stadium_in_hand not in {
            None, "Dimension Valley", "Sky Field"
        }:
            raise ValueError("unsupported replacement Stadium")


@dataclass(frozen=True)
class PrepState:
    tool: str
    jam: bool
    blower_hand: bool
    blower_deck: bool
    star_used: bool
    stadium_hand: str | None
    stadium_used: bool
    valley_live: bool


def _prep_transitions(s: PrepState, c: ToolConflictScenario):
    if (s.tool == "Forest Seal Stone" and not s.jam
            and not c.other_tool_lock and not s.star_used and s.blower_deck):
        yield "Forest Seal Stone Star Alchemy: search Field Blower", replace(
            s, blower_deck=False, blower_hand=True, star_used=True
        )

    if (s.blower_hand and c.recovery.item_play_enabled
            and (s.tool != "None" or s.jam)):
        labels = []
        if s.tool != "None":
            labels.append("incumbent Tool")
        if s.jam:
            labels.append("Jamming Tower")
        yield "Field Blower: discard " + " and ".join(labels), replace(
            s, tool="None", jam=False, blower_hand=False
        )

    if s.stadium_hand is not None and not s.stadium_used:
        if not (s.stadium_hand == "Dimension Valley" and s.valley_live):
            label = "Play " + s.stadium_hand
            if s.jam:
                label += " to replace Jamming Tower"
            yield label, replace(
                s, jam=False, stadium_hand=None, stadium_used=True,
                valley_live=(s.stadium_hand == "Dimension Valley")
            )


def find_tool_slot_recovery(
    c: ToolConflictScenario,
) -> tuple[str, ...] | None:
    """Find any valid prep + recovery sequence with minimum total actions."""
    start = PrepState(
        tool=c.incumbent_tool, jam=c.jamming_tower_live,
        blower_hand=c.field_blower_in_hand,
        blower_deck=c.field_blower_in_deck,
        star_used=not c.forest_star_alchemy_unused,
        stadium_hand=c.replacement_stadium_in_hand,
        stadium_used=not c.stadium_play_unused,
        valley_live=c.recovery.dimension_valley
    )
    seen = {start}
    pending = deque([(start, ())])
    successes = []
    while pending:
        state, prefix = pending.popleft()
        updated_recovery = replace(
            c.recovery,
            active_tool_free=(state.tool == "None"),
            float_effect_enabled=(
                c.recovery.float_effect_enabled
                and not state.jam and not c.other_tool_lock
            ),
            dimension_valley=state.valley_live
        )
        witness = find_recovery(updated_recovery)
        if witness is not None:
            successes.append(prefix + witness.actions)
        for action, successor in _prep_transitions(state, c):
            if successor not in seen:
                seen.add(successor)
                pending.append((successor, prefix + (action,)))
    if not successes:
        return None
    return min(successes, key=lambda actions: (len(actions), actions))
