"""Regress printed lock scopes and exact ACE SPEC collision in a real Aichi 60."""
from __future__ import annotations
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"tools"))
from reactive_counter_stack_frontier import Stack
from reactive_counter_lock_profiles import LockProfile, study, verify_prints, verify_reference_ace_spec

def run() -> dict:
    verify_prints(ROOT/"resources")
    manifest=json.loads((ROOT/"results"/"competitive_deck_baselines"/"absol_garbodor_kobayashi_2026.json").read_text(encoding="utf-8"))
    verify_reference_ace_spec(ROOT/"resources",manifest)
    full=Stack(4,4,"deluxe")
    assert LockProfile().counters(full)==29
    assert LockProfile(path_to_peak=True).counters(full)==24
    assert LockProfile(wobbuffet=True).counters(full)==20
    assert LockProfile(garbotoxin=True).counters(full)==20
    assert LockProfile(jamming_tower=True).counters(full)==17
    assert LockProfile(path_to_peak=True,jamming_tower=True).counters(full)==12
    assert LockProfile(garbotoxin=True,jamming_tower=True).counters(full)==8
    assert LockProfile(garbotoxin=True,path_to_peak=True).counters(full)==20
    assert LockProfile().counters(Stack(0,0,"deluxe"))==17
    assert LockProfile(garbotoxin=True).counters(Stack(0,0,"deluxe"))==12
    assert LockProfile(path_to_peak=True).counters(Stack(0,0,"deluxe"))==12

    for gate in (LockProfile(), LockProfile(path_to_peak=True),
                 LockProfile(garbotoxin=True), LockProfile(wobbuffet=True),
                 LockProfile(jamming_tower=True), LockProfile(garbotoxin=True,jamming_tower=True)):
        for spiritomb in range(5):
            for spiky in range(5):
                for tool in ("none","punk","deluxe"):
                    active=(not gate.path_to_peak and not gate.garbotoxin and not gate.wobbuffet)
                    aura=(not gate.garbotoxin and not gate.wobbuffet)
                    expected=(5 if active else 0)+(spiritomb if aura else 0)+2*spiky
                    expected+=(0 if gate.jamming_tower else {"none":0,"punk":4,"deluxe":12}[tool])
                    assert gate.counters(Stack(spiritomb,spiky,tool))==expected

    return study()

if __name__=="__main__":
    print(json.dumps(run(),indent=2))
