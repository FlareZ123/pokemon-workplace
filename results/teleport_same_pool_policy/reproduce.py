"""SFT: same-pool adaptive Quick/Ultra policy with Quick-as-Ultra payment."""
from __future__ import annotations

import json
import sys
from dataclasses import replace
from fractions import Fraction
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"tools"))

from bench_teleport_capacity_bridge import (
    BenchPokemon, bench_capacity, bench_from_hand, sample_state, teleport_room,
)
from discard_cost_witness import DiscardCandidate, DiscardSelection
from multicopy_zone_state import ZoneCountState
from raichu_search_to_crobat_execution import QUICK_BALL_PROFILE, ULTRA_BALL_PROFILE
from search_zone_transition import SearchZoneTarget
from stadium_entry_channels import StadiumCopy
from teleport_discard_payload_line import (
    assert_stadium_projection, mirror_teleport_to_trainer_zones,
)
from teleport_same_pool_policy import (
    SharedPool, example, exhaustive, k0_policy, k0_quick_only, k0_ultra_only,
)
from trainer_search_transaction import (
    TrainerSearchExecutionState, execute_trainer_search_transaction,
)
from typed_search_target_allocator import (
    STAGE_1_POKEMON, TargetGroup, enumerate_typed_target_profiles, make_demand,
)


def pct(value: Fraction)->float:
    return 100.0*float(value)


def check_symbolic()->None:
    for other_payment in (0,1,2):
        spec=SharedPool(
            n=11, prizes=2, seen=4,
            quick=2, ultra=2, sky=2, other_payment=other_payment,
        )
        for evo in (False,True):
            assert k0_policy(spec,evolution_target=evo)==exhaustive(
                spec,evolution_target=evo
            )
            print("PASS: all labeled states match exact same-pool policy",
                  "evolution=",evo,"payment=",other_payment)
    spec=SharedPool(46,6,5,4,4,2,16)
    rows=example()
    assert rows["joint_basic_policy"].goal >= rows["quick_basic_only"].goal
    assert rows["joint_basic_policy"].goal >= rows["ultra_only"].goal
    assert rows["joint_evolution_policy"].goal >= rows["quick_evolution_only"].goal
    assert rows["joint_evolution_policy"].goal >= rows["ultra_only"].goal
    assert rows["joint_basic_policy"].goal > rows["quick_basic_only"].goal
    assert rows["joint_evolution_policy"].goal > rows["ultra_only"].goal
    assert rows["ultra_only"].goal > rows["quick_evolution_only"].goal
    for name,row in rows.items():
        print(f"PASS: {name}: {pct(row.goal):.6f}%")
    print(json.dumps({
        name:{
            "target_deck":str(row.target_searched),
            "target_hand":str(row.target_held),
            "fraction":str(row.goal),
            "percent":round(pct(row.goal),6),
        } for name,row in rows.items()
    },indent=2))
    no_other=SharedPool(46,6,5,4,4,2,0)
    assert k0_ultra_only(no_other).goal==0
    assert k0_quick_only(no_other,evolution_target=True).target_searched==0
    survives=k0_policy(no_other,evolution_target=True)
    assert survives.target_searched>0
    assert survives.goal>0
    print("PASS: Ultra Evolution search survives with Quick as payment and no other fodder:",
          f"{pct(survives.goal):.6f}%")


def check_physical_evolution()->None:
    sky=StadiumCopy("sky-1","Sky Field")
    board=sample_state(
        hand_stadiums=(sky,),
        hand_pokemon=(BenchPokemon("ordinary_basic"),),
        stadium_plays_used=1,
    )
    physical=ZoneCountState.from_mapping({
        ("ultra_ball","hand"):1,
        ("quick_ball","hand"):1,
        ("sky_field","hand"):1,
        ("evolution_target","deck"):1,
        ("ordinary_basic","hand"):1,
        ("collapsed_stadium","stadium_in_play"):1,
    })
    state=TrainerSearchExecutionState(zones=physical,budget=board.stadiums.budget)
    target=SearchZoneTarget(
        "evolution_target",
        TargetGroup("Evolution target",1,frozenset({STAGE_1_POKEMON})),
    )
    demand=make_demand("Stage 1 for established Basic","Pokémon")
    ultra_alloc=enumerate_typed_target_profiles(
        ULTRA_BALL_PROFILE.base_outputs,(target.group,),(demand,)
    )
    action=next(
        row for row in ultra_alloc.actions
        if row.output==(1,) and row.target_cost==(1,)
    )
    quick_alloc=enumerate_typed_target_profiles(
        QUICK_BALL_PROFILE.base_outputs,(target.group,),(demand,)
    )
    assert not quick_alloc.full_demand_feasible
    assert all(row.target_cost!=(1,) for row in quick_alloc.actions)
    paid=execute_trainer_search_transaction(
        state,
        profile=ULTRA_BALL_PROFILE,
        action_card_class="ultra_ball",
        demands=(demand,),
        targets=(target,),
        search_action=action,
        discard_candidates=(
            DiscardCandidate("sky_field"),DiscardCandidate("quick_ball"),
        ),
        discard_selection=DiscardSelection((1,1)),
    )
    assert paid.discard_cost==2
    assert paid.after.zones.count("evolution_target","hand")==1
    assert paid.after.zones.count("sky_field","discard")==1
    assert paid.after.zones.count("quick_ball","discard")==1
    assert paid.after.zones.count("ultra_ball","discard")==1

    # Physical mirror of Sky Field's single exact copy.
    s=board.stadiums
    with_sky_discarded=replace(
        board, stadiums=replace(
            s,
            hand=(),
            discard=s.discard+(sky,),
            budget=paid.after.budget,
        ),
    )
    assert_stadium_projection(with_sky_discarded,paid.after.zones)
    relocated=teleport_room(with_sky_discarded,"goth-1")
    assert len(relocated)==1
    assert relocated[0].stadiums.in_play==sky
    assert bench_capacity(relocated[0])==8
    entrant=bench_from_hand(relocated[0],"ordinary_basic")
    assert entrant is not None
    assert len(entrant.bench)==5
    counted=mirror_teleport_to_trainer_zones(
        with_sky_discarded,relocated[0],paid.after.zones
    )
    counted=counted.move("ordinary_basic","hand","bench")
    assert counted.count("evolution_target","hand")==1
    assert counted.count("sky_field","stadium_in_play")==1
    assert counted.count("quick_ball","discard")==1
    assert all(
        physical.total(c)==counted.total(c)
        for c,_,_ in physical.counts
    )
    print("PASS: Ultra discards Quick+Sky, searches Stage 1, then Teleports Sky")


def main()->None:
    check_symbolic()
    check_physical_evolution()
    print("teleport_same_pool_policy regression: PASS")


if __name__=="__main__":
    main()
