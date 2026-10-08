"""Validate the card-grounded Harto Raichu draw-engine profiles."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"tools"))

from raichu_draw_engine_profiles import (
    compile_raichu_draw_engine_profiles,
    post_quick_ball_hand_transition,
)


def main() -> None:
    profiles={p.name:p for p in compile_raichu_draw_engine_profiles(ROOT/"resources")}

    assert set(profiles)=={"Crobat V","Dedenne-GX","Squawkabilly ex"}
    assert profiles["Crobat V"].forest_seal_host
    assert not profiles["Dedenne-GX"].forest_seal_host
    assert not profiles["Squawkabilly ex"].forest_seal_host
    assert profiles["Squawkabilly ex"].first_turn_only

    transitions={}
    for name,profile in profiles.items():
        transitions[name]={}
        for source in ("deck","hand","in_play"):
            transitions[name][source]=post_quick_ball_hand_transition(
                profile,engine_source=source
            )

    assert transitions["Crobat V"]["deck"]["cards_drawn"]==1
    assert transitions["Crobat V"]["hand"]["cards_drawn"]==2
    assert transitions["Crobat V"]["in_play"]["cards_drawn"]==0
    assert transitions["Dedenne-GX"]["deck"]["cards_discarded_by_ability"]==5
    assert transitions["Dedenne-GX"]["deck"]["cards_drawn"]==6
    assert transitions["Dedenne-GX"]["hand"]["cards_discarded_by_ability"]==4
    assert transitions["Dedenne-GX"]["in_play"]["ability_status"]=="entry_trigger_unavailable"
    assert transitions["Squawkabilly ex"]["deck"]["cards_discarded_by_ability"]==5
    assert transitions["Squawkabilly ex"]["hand"]["cards_discarded_by_ability"]==4
    assert transitions["Squawkabilly ex"]["in_play"]["cards_discarded_by_ability"]==5
    assert transitions["Squawkabilly ex"]["in_play"]["cards_drawn"]==6

    print(json.dumps({
        "profiles":{
            name:{
                "print_id":p.print_id,
                "ability":p.ability_name,
                "trigger":p.trigger,
                "hand_effect":p.hand_effect,
                "first_turn_only":p.first_turn_only,
                "pokemon_v":p.pokemon_v,
                "forest_seal_host":p.forest_seal_host,
            } for name,p in profiles.items()
        },
        "quick_ball_transitions":transitions,
    },indent=2,sort_keys=True))


if __name__=="__main__":
    main()
