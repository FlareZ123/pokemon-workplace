"""Gothitelle can put Grand Tree from discard into play and activate it."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
for location in (ROOT, ROOT / "tools"):
    if str(location) not in sys.path:
        sys.path.insert(0, str(location))

from tools.board_position_state import BoardPokemon, PokemonCard, make_state
from tools.effect_evolution_timing import build_profiles
from tools.stadium_entry_channels import StadiumCopy, StadiumEntryState
from tools.teleport_grand_tree_bridge import (
    TeleportGrandTreeState,
    activate_teleported_grand_tree,
    teleport_grand_tree_from_discard,
)
from turn_action_budget import TurnAction, TurnActionBudget


def board(owner: str):
    base = BoardPokemon(
        f"{owner}-object",
        (PokemonCard(f"{owner}-basic", "Bulbasaur"),),
        retreat_cost=1,
        evolution_eligible=True,
    )
    return make_state(
        (base,), active_id=f"{owner}-object", evolution_allowed=True,
    )


def main():
    profiles = [
        p for p in build_profiles(ROOT / "resources") if p.card_id == "sv7-136"
    ]
    assert len(profiles) == 1
    grand_tree = profiles[0]
    assert grand_tree.source_channel == "stadium"

    previous = StadiumCopy("stadium-old", "Brooklet Hill")
    target = StadiumCopy("ace-spec-grand-tree", "Grand Tree")
    spent_budget = TurnActionBudget(stadium_plays_used=1)
    entry = StadiumEntryState(
        budget=spent_budget,
        discard=(target,),
        in_play=previous,
        teleport_room_sources=frozenset({"goth-object"}),
    )
    original = TeleportGrandTreeState(entry)
    assert original.effect_view().in_play is not None
    assert original.effect_view().in_play.card.name == "Brooklet Hill"

    placed = teleport_grand_tree_from_discard(
        original,
        gothitelle_source_id="goth-object",
        grand_tree_copy_id=target.copy_id,
    )
    assert placed is not None
    assert placed.entry.in_play == target
    assert placed.entry.discard == (previous,)
    assert placed.entry.budget.stadium_plays_used == 1
    assert placed.entry.teleport_room_used == {"goth-object"}
    assert placed.effect_view().in_play is not None
    assert placed.effect_view().in_play.instance_id == "ace-spec-grand-tree@1"
    assert not placed.used_effect_instances

    first = activate_teleported_grand_tree(
        placed,
        grand_tree,
        board("first"),
        "first-object",
        PokemonCard("first-ivysaur", "Ivysaur", "Bulbasaur"),
        stage1_retreat_cost=2,
        went_first=True,
    )
    assert first is not None
    assert first.state.entry.in_play == target
    assert first.state.entry.budget == spent_budget
    assert first.state.used_effect_instances == {"ace-spec-grand-tree@1"}
    assert first.board.get("first-object").name == "Ivysaur"

    # No second activation of that same in-play instance this turn.
    assert activate_teleported_grand_tree(
        first.state,
        grand_tree,
        board("second"),
        "second-object",
        PokemonCard("second-ivysaur", "Ivysaur", "Bulbasaur"),
        stage1_retreat_cost=2,
        went_first=True,
    ) is None

    # Teleport Room's own once-per-source limit is independent from the
    # Stadium's voluntary effect-use limit.
    assert teleport_grand_tree_from_discard(
        placed,
        gothitelle_source_id="goth-object",
        grand_tree_copy_id=target.copy_id,
    ) is None

    # An illegal evolution must not use the effect and cannot mutate source.
    mismatched = activate_teleported_grand_tree(
        placed,
        grand_tree,
        board("bad"),
        "bad-object",
        PokemonCard("bad-wartortle", "Wartortle", "Squirtle"),
        stage1_retreat_cost=2,
        went_first=True,
    )
    assert mismatched is None
    assert not placed.used_effect_instances
    assert placed.entry.in_play == target

    # The effect cannot be started after turn end, even if the projected
    # source-use instance has not been consumed.
    ended = placed.entry.budget.consume(TurnAction.END_TURN)
    assert ended is not None
    ended_bridge = replace(placed, entry=replace(placed.entry, budget=ended))
    assert activate_teleported_grand_tree(
        ended_bridge,
        grand_tree,
        board("ended"),
        "ended-object",
        PokemonCard("ended-ivysaur", "Ivysaur", "Bulbasaur"),
        stage1_retreat_cost=2,
        went_first=True,
    ) is None

    # Never construct a Stadium source from a nonexistent discard target.
    assert teleport_grand_tree_from_discard(
        original,
        gothitelle_source_id="goth-object",
        grand_tree_copy_id="nonexistent",
    ) is None

    print("Teleport Room -> Grand Tree source bridge regressions passed")


if __name__ == "__main__":
    main()
