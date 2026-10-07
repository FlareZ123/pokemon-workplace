from __future__ import annotations

from collections import Counter
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from board_object_kernel import make_board, make_pokemon
from dream_ball_evolution_ability_catalog import (
    ACTIVATION_TRIGGERED,
    ACTIVATION_TURN_ACTION,
    GEOMETRY_ACTIVE,
    GEOMETRY_BENCH,
    GEOMETRY_HAND_BENCH_TRIGGER,
    GEOMETRY_HAND_EVOLVE_TRIGGER,
)
from position_ability_profiles import (
    compile_position_ability_profiles,
    execute_position_ability,
)
from position_effect_profile_compiler import (
    ChoiceAuthority,
    PositionEffectKind,
)


def one(rows, *, card_id: str, ability_name: str):
    matches = tuple(
        row
        for row in rows
        if row.card_id == card_id and row.ability_name == ability_name
    )
    assert len(matches) == 1
    return matches[0]


def main() -> None:
    rows = compile_position_ability_profiles(ROOT / "resources")
    assert len(rows) == 52
    assert len({row.name for row in rows}) == 23
    assert Counter(row.kind for row in rows) == Counter(
        {
            PositionEffectKind.SELF_SWITCH: 22,
            PositionEffectKind.TARGETED_GUST: 17,
            PositionEffectKind.OPPONENT_FORCED_SWITCH: 13,
        }
    )

    keldeo = one(rows, card_id="bw7-49", ability_name="Rush In")
    assert keldeo.kind == PositionEffectKind.SELF_SWITCH
    assert keldeo.self_selection == "source_bench"
    assert keldeo.source_geometry == GEOMETRY_BENCH
    assert keldeo.activation == ACTIVATION_TURN_ACTION

    solgaleo = one(rows, card_id="sm1-89", ability_name="Ultra Road")
    assert solgaleo.kind == PositionEffectKind.SELF_SWITCH
    assert solgaleo.self_selection == "any_bench"
    assert solgaleo.activation == ACTIVATION_TURN_ACTION

    umbreon = one(rows, card_id="swsh7-95", ability_name="Dark Signal")
    assert umbreon.kind == PositionEffectKind.TARGETED_GUST
    assert umbreon.chooser == ChoiceAuthority.ACTOR
    assert umbreon.source_geometry == GEOMETRY_HAND_EVOLVE_TRIGGER
    assert umbreon.activation == ACTIVATION_TRIGGERED

    hariyama = one(rows, card_id="me1-73", ability_name="Heave-Ho Catcher")
    assert hariyama.source_geometry == GEOMETRY_HAND_EVOLVE_TRIGGER
    assert hariyama.activation == ACTIVATION_TRIGGERED

    mabosstiff = one(rows, card_id="sv1-137", ability_name="Intimidating Howl")
    assert mabosstiff.kind == PositionEffectKind.OPPONENT_FORCED_SWITCH
    assert mabosstiff.chooser == ChoiceAuthority.OPPONENT

    salamence = one(rows, card_id="sm7-106", ability_name="Dragon Wind")
    assert salamence.source_geometry == GEOMETRY_ACTIVE

    swellow = one(rows, card_id="xy1-103", ability_name="Drive Off")
    assert swellow.source_geometry == GEOMETRY_HAND_BENCH_TRIGGER

    actor = make_board(
        make_pokemon("actor-active", "Attacker"),
        (
            make_pokemon("keldeo", "Keldeo-EX"),
            make_pokemon("pivot", "Pivot"),
            make_pokemon("umbreon", "Umbreon VMAX"),
        ),
    )
    opponent = make_board(
        make_pokemon("opp-active", "Wall"),
        (
            make_pokemon("opp-a", "Target A"),
            make_pokemon("opp-b", "Target B"),
        ),
    )

    rush_in = execute_position_ability(
        keldeo,
        actor,
        opponent,
        source_object_id="keldeo",
    )
    assert rush_in is not None
    assert rush_in[0].active_id == "keldeo"

    ultra_road = execute_position_ability(
        solgaleo,
        actor,
        opponent,
        source_object_id="actor-active",
        chosen_actor_bench="pivot",
    )
    assert ultra_road is not None
    assert ultra_road[0].active_id == "pivot"

    assert execute_position_ability(
        umbreon,
        actor,
        opponent,
        source_object_id="umbreon",
        chosen_opponent_bench="opp-a",
    ) is None
    dark_signal = execute_position_ability(
        umbreon,
        actor,
        opponent,
        source_object_id="umbreon",
        chosen_opponent_bench="opp-a",
        trigger_satisfied=True,
    )
    assert dark_signal is not None
    assert dark_signal[1].active_id == "opp-a"

    assert execute_position_ability(
        mabosstiff,
        actor,
        opponent,
        source_object_id="actor-active",
        chosen_opponent_bench="opp-b",
        abilities_enabled=False,
    ) is None

    # Active-only source geometry is enforced.
    assert execute_position_ability(
        salamence,
        actor,
        opponent,
        source_object_id="pivot",
        chosen_opponent_bench="opp-a",
    ) is None

    print("position Ability profile regression passed")
    print(f"profiles={len(rows)} names={len({row.name for row in rows})}")
    print(dict(sorted((kind.value, count) for kind, count in Counter(row.kind for row in rows).items())))


if __name__ == "__main__":
    main()
