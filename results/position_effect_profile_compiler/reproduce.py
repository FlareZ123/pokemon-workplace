from __future__ import annotations

from collections import Counter
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from board_object_kernel import make_board, make_pokemon
from position_effect_execution import execute_position_effect
from position_effect_profile_compiler import (
    ChoiceAuthority,
    EffectTargetGeometry,
    PositionEffectKind,
    compile_position_effect_profiles,
)


def one(rows, *, card_id: str, source_name: str | None = None):
    matches = tuple(
        row
        for row in rows
        if row.card_id == card_id
        and (source_name is None or row.source_name == source_name)
    )
    assert len(matches) == 1
    return matches[0]


def main() -> None:
    rows = compile_position_effect_profiles(ROOT / "resources")

    assert len(rows) == 133
    assert len({row.name for row in rows}) == 83
    assert Counter((row.source_kind, row.kind) for row in rows) == Counter(
        {
            ("trainer", PositionEffectKind.SELF_SWITCH): 17,
            ("trainer", PositionEffectKind.OPPONENT_FORCED_SWITCH): 2,
            ("trainer", PositionEffectKind.TARGETED_GUST): 18,
            ("attack", PositionEffectKind.OPPONENT_FORCED_SWITCH): 71,
            ("attack", PositionEffectKind.TARGETED_GUST): 25,
        }
    )

    switch = one(rows, card_id="bw1-104")
    assert switch.kind == PositionEffectKind.SELF_SWITCH
    assert switch.chooser == ChoiceAuthority.ACTOR
    assert switch.effect_target == EffectTargetGeometry.ACTOR_ACTIVE
    assert switch.action_class == "Item"

    repel = one(rows, card_id="me1-126")
    assert repel.kind == PositionEffectKind.OPPONENT_FORCED_SWITCH
    assert repel.chooser == ChoiceAuthority.OPPONENT
    assert repel.effect_target == EffectTargetGeometry.OPPONENT_ACTIVE

    counter_catcher = one(rows, card_id="sm4-91")
    assert counter_catcher.kind == PositionEffectKind.TARGETED_GUST
    assert counter_catcher.chooser == ChoiceAuthority.ACTOR
    assert counter_catcher.effect_target == EffectTargetGeometry.SELECTED_OPPONENT_BENCH
    assert (
        counter_catcher.play_condition
        == "You can play this card only if you have more Prize cards remaining than your opponent."
    )

    bayleef = one(rows, card_id="me1-9", source_name="Push Down")
    clefairy = one(rows, card_id="me3-30", source_name="Follow Me")
    assert bayleef.attack_damage == "50"
    assert clefairy.attack_damage == ""

    assert not any(row.card_id in {"sm12-198", "sm12-231"} for row in rows)

    actor = make_board(
        make_pokemon("actor-active", "Attacker"),
        (make_pokemon("actor-bench", "Pivot"),),
    )
    opponent = make_board(
        make_pokemon("opp-active", "Wall"),
        (
            make_pokemon("opp-bench-a", "Target A"),
            make_pokemon("opp-bench-b", "Target B"),
        ),
    )

    own_switch = execute_position_effect(
        switch,
        actor,
        opponent,
        chosen_object_id="actor-bench",
    )
    assert own_switch is not None
    assert own_switch.actor_board.active_id == "actor-bench"
    assert own_switch.opponent_board == opponent

    forced = execute_position_effect(
        bayleef,
        actor,
        opponent,
        chosen_object_id="opp-bench-a",
    )
    assert forced is not None
    assert forced.chooser == ChoiceAuthority.OPPONENT
    assert forced.targeted_object_id == "opp-active"
    assert forced.opponent_board.active_id == "opp-bench-a"

    assert execute_position_effect(
        bayleef,
        actor,
        opponent,
        chosen_object_id="opp-bench-a",
        blocked_effect_target_ids=frozenset({"opp-active"}),
    ) is None
    assert execute_position_effect(
        bayleef,
        actor,
        opponent,
        chosen_object_id="opp-bench-a",
        blocked_effect_target_ids=frozenset({"opp-bench-a"}),
    ) is not None

    gust = execute_position_effect(
        clefairy,
        actor,
        opponent,
        chosen_object_id="opp-bench-a",
    )
    assert gust is not None
    assert gust.chooser == ChoiceAuthority.ACTOR
    assert gust.targeted_object_id == "opp-bench-a"
    assert gust.opponent_board.active_id == "opp-bench-a"

    assert execute_position_effect(
        clefairy,
        actor,
        opponent,
        chosen_object_id="opp-bench-a",
        blocked_effect_target_ids=frozenset({"opp-bench-a"}),
    ) is None
    assert execute_position_effect(
        clefairy,
        actor,
        opponent,
        chosen_object_id="opp-bench-a",
        blocked_effect_target_ids=frozenset({"opp-active"}),
    ) is not None

    print("position effect compiler/executor regression passed")
    print(f"profiles={len(rows)} unique_names={len({row.name for row in rows})}")
    for key, count in sorted(
        Counter((row.source_kind, row.kind.value) for row in rows).items()
    ):
        print(key, count)


if __name__ == "__main__":
    main()
