"""Two-turn Quick Ball -> Gothita -> Rare Candy Gothitelle -> Teleport Room.

Bounded deterministic legality witness with a single cross-turn Stadium payload.
The state preserves the exact Sky Field copy across hand/discard/play and
tracks the Stage 2 card separately from its existing Basic Bench stack.
"""
from __future__ import annotations

from dataclasses import dataclass, replace

from bench_teleport_capacity_bridge import (
    BenchPokemon, BenchTeleportState, bench_from_hand, play_stadium, teleport_room,
)
from discard_cost_witness import DiscardCandidate, DiscardSelection
from multicopy_zone_state import ZoneCountState
from raichu_search_to_crobat_execution import QUICK_BALL_PROFILE
from search_zone_transition import SearchZoneTarget
from stadium_entry_channels import StadiumCopy, StadiumEntryState
from teleport_discard_payload_line import assert_stadium_projection
from trainer_search_transaction import TrainerSearchExecutionState, execute_trainer_search_transaction
from turn_action_budget import TurnAction, TurnActionBudget
from typed_search_target_allocator import (
    BASIC_POKEMON, TargetGroup, enumerate_typed_target_profiles, make_demand,
)


SKY=StadiumCopy("sky-1","Sky Field")
COLLAPSED=StadiumCopy("collapsed-1","Collapsed Stadium")
GOTHITA_SLOT="gothita-slot"


@dataclass(frozen=True)
class TwoTurnState:
    board: BenchTeleportState
    trainer: TrainerSearchExecutionState
    turn: int = 1
    gothita_entered_turn: int | None = None
    evolved: bool = False
    stadium_hand_lock: bool = True

    def __post_init__(self)->None:
        if self.board.stadiums.budget!=self.trainer.budget:
            raise ValueError("turn budgets disagree")
        assert_stadium_projection(self.board,self.trainer.zones)


def initial_state(*, sky_in_hand:bool, barrier_shrine:bool=True)->TwoTurnState:
    stadiums=StadiumEntryState(
        budget=TurnActionBudget(),
        hand=(SKY,) if sky_in_hand else (),
    )
    board=BenchTeleportState(
        stadiums=stadiums,
        active=BenchPokemon("attacker"),
        bench=tuple(BenchPokemon(f"core-{i}") for i in range(3)),
        hand_pokemon=(BenchPokemon("entry-a"),BenchPokemon("entry-b")),
    )
    count=ZoneCountState.from_mapping({
        ("quick_ball","hand"):1,
        ("sky_field","hand" if sky_in_hand else "deck"):1,
        ("junk","hand"):1,
        ("gothita","deck"):1,
        ("gothitelle","hand"):1,
        ("rare_candy","hand"):1,
        ("entry-a","hand"):1,
        ("entry-b","hand"):1,
        ("collapsed_stadium","opponent_hand"):1,
    })
    trainer=TrainerSearchExecutionState(zones=count,budget=stadiums.budget)
    return TwoTurnState(board,trainer,stadium_hand_lock=barrier_shrine)


def first_turn_quick_gothita(state:TwoTurnState,*,pay_sky:bool)->TwoTurnState:
    if state.turn!=1 or state.gothita_entered_turn is not None:
        raise ValueError("Quick setup only once on first turn")
    payment="sky_field" if pay_sky else "junk"
    if state.trainer.zones.count(payment,"hand")!=1:
        raise ValueError("requested payment absent")
    target=SearchZoneTarget(
        "gothita",TargetGroup("Gothita",1,frozenset({BASIC_POKEMON}))
    )
    demand=make_demand("Gothita setup","Basic Pokémon")
    actions=enumerate_typed_target_profiles(
        QUICK_BALL_PROFILE.base_outputs,(target.group,),(demand,)
    )
    selected=next(
        row for row in actions.actions
        if row.output==(1,) and row.target_cost==(1,)
    )
    transaction=execute_trainer_search_transaction(
        state.trainer,
        profile=QUICK_BALL_PROFILE,
        action_card_class="quick_ball",
        demands=(demand,),
        targets=(target,),
        search_action=selected,
        discard_candidates=(DiscardCandidate(payment),),
        discard_selection=DiscardSelection((1,)),
    )
    stadiums=state.board.stadiums
    if pay_sky:
        stadiums=replace(
            stadiums,
            hand=tuple(card for card in stadiums.hand if card.copy_id!=SKY.copy_id),
            discard=stadiums.discard+(SKY,),
        )
    stadiums=replace(stadiums,budget=transaction.after.budget)
    updated_board=replace(
        state.board,
        stadiums=stadiums,
        hand_pokemon=state.board.hand_pokemon+(BenchPokemon(GOTHITA_SLOT),),
    )
    next_board=bench_from_hand(updated_board,GOTHITA_SLOT)
    if next_board is None:
        raise ValueError("Gothita has no legal Bench slot")
    next_zones=transaction.after.zones.move("gothita","hand","bench")
    next_trainer=replace(transaction.after,zones=next_zones)
    return replace(
        state,board=next_board,trainer=next_trainer,
        gothita_entered_turn=1,
    )


def next_turn_under_collapsed(
    state:TwoTurnState,*,draw_sky:bool=False
)->TwoTurnState:
    if state.turn!=1 or state.gothita_entered_turn!=1:
        raise ValueError("missing first-turn established Gothita")
    turn_end=state.board.stadiums.budget.consume(TurnAction.END_TURN)
    if turn_end is None:
        raise ValueError("unable to end turn")
    budget=turn_end.next_turn()
    stadiums=replace(
        state.board.stadiums,
        budget=budget,
        in_play=COLLAPSED,
    )
    zones=state.trainer.zones.move(
        "collapsed_stadium","opponent_hand","stadium_in_play"
    )
    if draw_sky:
        if zones.count("sky_field","deck")!=1:
            raise ValueError("Sky Field cannot be drawn from deck")
        zones=zones.move("sky_field","deck","hand")
        stadiums=replace(stadiums,hand=stadiums.hand+(SKY,))
    board=replace(state.board,stadiums=stadiums)
    trainer=replace(state.trainer,zones=zones,budget=budget)
    return replace(state,turn=2,board=board,trainer=trainer)


def evolve_on_turn_two(state:TwoTurnState)->TwoTurnState:
    if state.turn!=2 or state.evolved or state.gothita_entered_turn!=1:
        raise ValueError("Rare Candy cannot evolve newly placed Basic")
    zones=state.trainer.zones
    if zones.count("rare_candy","hand")!=1 or zones.count("gothitelle","hand")!=1:
        raise ValueError("Rare Candy or Gothitelle missing")
    index=next(
        (i for i,p in enumerate(state.board.bench) if p.copy_id==GOTHITA_SLOT),
        None
    )
    if index is None:
        raise ValueError("Gothita stack missing on Bench")
    benched=list(state.board.bench)
    benched[index]=replace(benched[index],teleport_room=True)
    stadiums=replace(
        state.board.stadiums,
        teleport_room_sources=state.board.stadiums.teleport_room_sources|{GOTHITA_SLOT},
    )
    board=replace(state.board,stadiums=stadiums,bench=tuple(benched))
    zones=zones.move("rare_candy","hand","discard").move(
        "gothitelle","hand","bench_evolution"
    )
    return replace(
        state,board=board,trainer=replace(state.trainer,zones=zones),
        evolved=True,
    )


def teleport_to_sky(state:TwoTurnState)->TwoTurnState:
    if state.turn!=2 or not state.evolved:
        raise ValueError("Gothitelle not live")
    successor=teleport_room(state.board,GOTHITA_SLOT)
    if len(successor)!=1 or successor[0].stadiums.in_play!=SKY:
        raise ValueError("Sky Field is not live in discard")
    zones=state.trainer.zones.move(
        "collapsed_stadium","stadium_in_play","discard"
    ).move("sky_field","discard","stadium_in_play")
    return replace(
        state,board=successor[0],
        trainer=replace(state.trainer,zones=zones),
    )


def teleport_without_sky(state:TwoTurnState)->TwoTurnState:
    if not state.evolved:
        raise ValueError("Gothitelle not live")
    successor=teleport_room(state.board,GOTHITA_SLOT)
    if len(successor)!=1 or successor[0].stadiums.in_play is not None:
        raise ValueError("requires removal-only Teleport")
    zones=state.trainer.zones.move(
        "collapsed_stadium","stadium_in_play","discard"
    )
    return replace(
        state,board=successor[0],
        trainer=replace(state.trainer,zones=zones),
    )


def play_sky_from_hand(state:TwoTurnState)->TwoTurnState|None:
    if state.stadium_hand_lock:
        return None
    new_boards=play_stadium(state.board,SKY.copy_id)
    if len(new_boards)!=1:
        return None
    zones=state.trainer.zones.move(
        "sky_field","hand","stadium_in_play"
    ).move("collapsed_stadium","stadium_in_play","discard")
    board=new_boards[0]
    return replace(
        state,board=board,trainer=replace(
            state.trainer,zones=zones,budget=board.stadiums.budget
        )
    )


def enter_both(state:TwoTurnState)->TwoTurnState|None:
    board=state.board
    zones=state.trainer.zones
    for name in ("entry-a","entry-b"):
        board=bench_from_hand(board,name)
        if board is None:
            return None
        zones=zones.move(name,"hand","bench")
    return replace(state,board=board,trainer=replace(state.trainer,zones=zones))
