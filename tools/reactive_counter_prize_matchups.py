"""Bounded reaction HP/Prize thresholds vs selected 2026 Aichi main attackers.

A positive-damage opponent-Pokémon attack, post-step-5 surviving reaction
sources, and unprevented counter placement are preconditions.
"""
from __future__ import annotations
import json
from pathlib import Path
from reactive_counter_stack_frontier import Stack, source_validate
from reactive_counter_lock_profiles import LockProfile, verify_prints
from build_expanded_legality_baseline import classify_effective_legality

ATTACKERS = {
    "shadow_rider_champion": ("swsh6-75", "Shadow Rider Calyrex VMAX", 320, 3),
    "mew_fifth": ("swsh8-114", "Mew VMAX", 310, 3),
    "regidrago_tenth": ("swsh12-136", "Regidrago VSTAR", 280, 2),
    "mega_absol_eighth": ("me1-86", "Mega Absol ex", 280, 3),
}

def _card(resources: Path, print_id: str) -> dict:
    set_id=print_id.split("-",1)[0]
    sets=json.loads((resources/"sets"/"en.json").read_text(encoding="utf-8"))
    assert next(s for s in sets if s["id"]==set_id)["legalities"]["expanded"]=="Legal"
    cards=json.loads((resources/"cards"/"en"/(set_id+".json")).read_text(encoding="utf-8"))
    card=next(c for c in cards if c["id"]==print_id)
    assert classify_effective_legality(card)[0]=="Legal"
    return card

def verify_sources(resources: Path) -> None:
    source_validate(resources)
    verify_prints(resources)
    for role,(print_id,name,hp,prizes) in ATTACKERS.items():
        card=_card(resources,print_id)
        assert card["name"]==name and int(card["hp"])==hp
        assert f"takes {prizes} Prize cards" in " ".join(card.get("rules") or ()), role
    absol=_card(resources,ATTACKERS["mega_absol_eighth"][0])
    period=next(a for a in absol["attacks"] if a["name"]=="Terminal Period")
    assert period["damage"]==""
    assert "has exactly 6 damage counters" in period["text"] and "is Knocked Out" in period["text"]
    assert any(a["name"]=="Claw of Darkness" and a["damage"]=="200" for a in absol["attacks"])
    assert any(a["name"]=="Max Geist" and a["damage"]=="10+" for a in _card(resources,ATTACKERS["shadow_rider_champion"][0])["attacks"])
    assert any(a["name"]=="Apex Dragon" and a["damage"]=="" for a in _card(resources,ATTACKERS["regidrago_tenth"][0])["attacks"])

def required_existing_damage(hp: int, counters: int) -> int:
    return max(0, hp - 10 * counters)

def study() -> dict:
    cases={
        "full_unlocked": (Stack(4,4,"deluxe"),LockProfile()),
        "full_path": (Stack(4,4,"deluxe"),LockProfile(path_to_peak=True)),
        "full_garbotoxin": (Stack(4,4,"deluxe"),LockProfile(garbotoxin=True)),
        "lean_unlocked": (Stack(0,0,"deluxe"),LockProfile()),
    }
    return {
        "cases": {
            key: {
                "counters":lock.counters(stack),
                "attackers": {
                    role: {
                        "hp":hp,
                        "prizes_awarded_if_knocked_out":prizes,
                        "minimum_preexisting_damage_for_reactive_ko":required_existing_damage(hp,lock.counters(stack)),
                        "ko_from_full_hp":required_existing_damage(hp,lock.counters(stack))==0,
                        "prize_exchange_if_both_ko":prizes-3,
                    } for role,(_,_,hp,prizes) in ATTACKERS.items()
                },
            } for key,(stack,lock) in cases.items()
        },
        "effect_only": {
            "source": "Mega Absol ex Terminal Period",
            "requires_exact_six_counters_on_defending_active": True,
            "printed_attack_damage": 0,
            "damaged_by_attack_reactions_trigger": False,
        },
    }
