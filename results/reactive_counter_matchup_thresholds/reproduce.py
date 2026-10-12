"""Exact-card HP and Prize counterattack threshold tests."""
from pathlib import Path
import json
import sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"tools"))
from reactive_counter_prize_matchups import verify_sources,required_existing_damage,study

def run():
    verify_sources(ROOT/"resources")
    for hp in range(10,401,10):
        for counters in range(31):
            expected=next((prior for prior in range(0,hp+1,10) if prior+10*counters>=hp),hp)
            assert required_existing_damage(hp,counters)==expected
    result=study()
    full=result["cases"]["full_unlocked"]["attackers"]
    assert (full["shadow_rider_champion"]["minimum_preexisting_damage_for_reactive_ko"],
            full["mew_fifth"]["minimum_preexisting_damage_for_reactive_ko"]) == (30,20)
    assert full["regidrago_tenth"]["ko_from_full_hp"]
    assert full["regidrago_tenth"]["prize_exchange_if_both_ko"]==-1
    assert full["mega_absol_eighth"]["prize_exchange_if_both_ko"]==0
    assert result["effect_only"]["damaged_by_attack_reactions_trigger"] is False
    return result

if __name__=="__main__":
    print(json.dumps(run(),indent=2))
