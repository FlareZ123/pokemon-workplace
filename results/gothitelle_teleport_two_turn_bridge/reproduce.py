"""SFT: a single turn-one Quick Ball pays Sky Field and bootstraps turn-two Teleport."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"tools"))

from bench_teleport_capacity_bridge import bench_capacity, bench_from_hand
from build_expanded_legality_baseline import classify_effective_legality
from gothitelle_teleport_two_turn_bridge import (
    SKY, COLLAPSED, initial_state,
    first_turn_quick_gothita, next_turn_under_collapsed,
    evolve_on_turn_two, teleport_to_sky, teleport_without_sky,
    play_sky_from_hand, enter_both,
)


def cards_text()->None:
    needed={
        "xy3":("xy3-39","xy3-41"),
        "xy5":("xy5-20","xy5-21"),
        "xy6":("xy6-89",),
        "swsh1":("swsh1-179",),
        "swsh9":("swsh9-137",),
        "sv1":("sv1-191",),
    }
    cards={}
    for set_id,ids in needed.items():
        rows=json.loads(
            (ROOT/"resources"/"cards"/"en"/f"{set_id}.json")
            .read_text(encoding="utf-8")
        )
        cards.update({card["id"]:card for card in rows if card["id"] in ids})
    assert len(cards)==8
    assert all(classify_effective_legality(c)[0]=="Legal" for c in cards.values())
    assert cards["xy3-39"]["name"]=="Gothita"
    assert cards["xy3-41"]["name"]=="Gothitelle"
    assert "Stage 2" in cards["xy3-41"]["subtypes"]
    assert "Teleport Room" in {a["name"] for a in cards["xy3-41"]["abilities"]}
    assert cards["xy5-20"]["name"]=="Vulpix"
    assert "Basic" in cards["xy5-20"]["subtypes"]
    shrine=next(a for a in cards["xy5-21"]["abilities"] if a["name"]=="Barrier Shrine")
    assert "can't play any Stadium cards from his or her hand" in shrine["text"]
    assert "discard another card from your hand" in " ".join(cards["swsh1-179"]["rules"])
    assert "Basic Pokémon" in " ".join(cards["swsh1-179"]["rules"])
    assert "skipping the Stage 1" in " ".join(cards["sv1-191"]["rules"])
    assert "Basic Pokémon that was put into play this turn" in " ".join(cards["sv1-191"]["rules"])
    print("PASS: eight legal prints and opponent evolution timing/lock grounded")


def conserved(initial,following)->None:
    base=initial.trainer.zones
    final=following.trainer.zones
    for name,_,_ in base.counts:
        assert base.total(name)==final.total(name),name
    assert following.board.stadiums.budget==following.trainer.budget
    print("PASS: all represented card-class counts and budgets conserved")


def positive()->None:
    opening=initial_state(sky_in_hand=True)
    assert opening.turn==1
    assert opening.board.stadiums.in_play==COLLAPSED
    assert len(opening.board.bench)==3
    assert bench_capacity(opening.board)==4
    assert play_sky_from_hand(opening) is not None  # Opponent Ninetales cannot evolve on its first turn

    q=first_turn_quick_gothita(opening,pay_sky=True)
    assert q.trainer.zones.count("quick_ball","discard")==1
    assert q.trainer.zones.count("sky_field","discard")==1
    assert q.trainer.zones.count("gothita","bench")==1
    assert q.board.stadiums.discard==(SKY,)
    assert len(q.board.bench)==4
    assert not q.board.stadiums.teleport_room_sources
    assert q.gothita_entered_turn==1

    # Evolution timing: the first-turn Basic cannot Rare Candy on that turn.
    try:
        evolve_on_turn_two(q)
    except ValueError as exc:
        assert "Rare Candy" in str(exc)
    else:
        raise AssertionError("Stage2 illegal first-turn evolution accepted")

    t2=next_turn_under_collapsed(q)
    assert t2.turn==2
    assert t2.board.stadiums.budget.stadium_plays_used==0
    assert t2.board.stadiums.in_play==COLLAPSED
    evolved=evolve_on_turn_two(t2)
    assert evolved.trainer.zones.count("rare_candy","discard")==1
    assert evolved.trainer.zones.count("gothitelle","bench_evolution")==1
    assert evolved.trainer.zones.count("gothita","bench")==1
    assert evolved.board.stadiums.teleport_room_sources==frozenset({"gothita-slot"})
    assert bench_capacity(evolved.board)==4

    teleported=teleport_to_sky(evolved)
    assert teleported.board.stadiums.in_play==SKY
    assert teleported.trainer.zones.count("collapsed_stadium","discard")==1
    assert teleported.trainer.zones.count("sky_field","stadium_in_play")==1
    assert teleported.board.stadiums.budget.stadium_plays_used==0
    assert teleported.board.stadiums.teleport_room_used==frozenset({"gothita-slot"})
    assert bench_capacity(teleported.board)==8
    entered=enter_both(teleported)
    assert entered is not None and len(entered.board.bench)==6
    assert entered.trainer.zones.count("entry-a","bench")==1
    assert entered.trainer.zones.count("entry-b","bench")==1
    conserved(opening,entered)
    print("PASS: first-turn Quick Sky payment -> Gothita -> second-turn Candy Gothitelle -> Sky Field -> both entrants")


def negative_late_sky()->None:
    opening=initial_state(sky_in_hand=False)
    quick=first_turn_quick_gothita(opening,pay_sky=False)
    assert quick.trainer.zones.count("junk","discard")==1
    assert not quick.board.stadiums.discard
    t2=next_turn_under_collapsed(quick,draw_sky=True)
    assert t2.trainer.zones.count("sky_field","hand")==1
    evolved=evolve_on_turn_two(t2)
    assert play_sky_from_hand(evolved) is None  # Opposing Barrier Shrine lock
    removed=teleport_without_sky(evolved)
    assert removed.board.stadiums.in_play is None
    assert bench_capacity(removed.board)==5
    assert enter_both(removed) is None
    first=bench_from_hand(removed.board,"entry-a")
    assert first is not None and len(first.bench)==5
    assert bench_from_hand(first,"entry-b") is None
    conserved(opening,removed)
    print("PASS: delayed Sky Field draw cannot use exhausted Quick Ball payment under Barrier Shrine")


def negative_wrong_payment()->None:
    opening=initial_state(sky_in_hand=True,barrier_shrine=True)
    q=first_turn_quick_gothita(opening,pay_sky=False)
    t2=next_turn_under_collapsed(q)
    evolved=evolve_on_turn_two(t2)
    assert play_sky_from_hand(evolved) is None
    removed=teleport_without_sky(evolved)
    assert bench_capacity(removed.board)==5
    assert enter_both(removed) is None
    conserved(opening,removed)
    print("PASS: discarding junk rather than early Sky leaves only one newly available slot")


def alternative_unlocked()->None:
    opening=initial_state(sky_in_hand=True)
    q=first_turn_quick_gothita(opening,pay_sky=False)
    t2=next_turn_under_collapsed(q,opponent_establishes_shrine=False)
    evolved=evolve_on_turn_two(t2)
    direct=play_sky_from_hand(evolved)
    assert direct is not None
    assert direct.board.stadiums.in_play==SKY
    assert direct.board.stadiums.budget.stadium_plays_used==1
    assert direct.board.stadiums.teleport_room_used==frozenset()
    final=enter_both(direct)
    assert final is not None
    conserved(opening,final)
    print("PASS: without Stadium-from-hand lock, direct Sky Field is a valid alternative")


def main()->None:
    cards_text()
    positive()
    negative_late_sky()
    negative_wrong_payment()
    alternative_unlocked()
    print("gothitelle_teleport_two_turn_bridge regression: PASS")


if __name__=="__main__":
    main()
