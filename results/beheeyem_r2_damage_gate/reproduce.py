"""Card-pool audit: unboosted Beheeyem Mysterious Noise versus 2-Prize HP.

Uses the repository's actual per-set Expanded legality and effective print
legality filter. Baseline card-to-card damage is subject to Resistance.
This checks prints with printed HP <= Mysterious Noise printed base 90.
"""
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from tools.build_expanded_legality_baseline import (
    classify_effective_legality,load_json
)


def run():
    res=ROOT/"resources"
    set_records=load_json(res/"sets"/"en.json")
    legal_sets={
        set_record["id"] for set_record in set_records
        if (set_record.get("legalities") or {}).get("expanded")=="Legal"
    }
    beheeyem=next(
        c for c in load_json(res/"cards"/"en"/"sm11.json")
        if c.get("id")=="sm11-91"
    )
    assert classify_effective_legality(beheeyem)[0]=="Legal"
    assert beheeyem["types"]==["Psychic"]
    mysterious=next(
        attack for attack in beheeyem["attacks"]
        if attack["name"]=="Mysterious Noise"
    )
    damage=int(mysterious["damage"])
    assert damage==90
    low_hp_two_prize=[]
    for path in sorted((res/"cards"/"en").glob("*.json")):
        if path.stem not in legal_sets:
            continue
        for card in load_json(path):
            if card.get("supertype")!="Pokémon":
                continue
            hp=card.get("hp") or ""
            if not hp.isdigit() or int(hp)>damage:
                continue
            if classify_effective_legality(card)[0]!="Legal":
                continue
            rules=card.get("rules") or []
            if not any("2 prize cards" in rule.lower() for rule in rules):
                continue
            resistance=next(
                (int(r["value"].replace("−","-"))
                 for r in (card.get("resistances") or [])
                 if r.get("type")=="Psychic"),
                0
            )
            final=damage+resistance
            low_hp_two_prize.append({
                "id":card["id"],"name":card["name"],
                "printed_hp":int(hp),"psychic_resistance":resistance,
                "unboosted_mysterious_noise_damage":final,
                "knockout_without_prior_damage":final>=int(hp),
                "minimum_prior_damage_for_KO":max(0,int(hp)-final)
            })
    assert [c["id"] for c in low_hp_two_prize]==[
        "bw10-60","bw10-98"
    ]
    assert all(c["minimum_prior_damage_for_KO"]==20
               for c in low_hp_two_prize)
    return {
        "mysterious_noise_card":beheeyem["id"],
        "base_damage":damage,
        "matching_legal_low_HP_two_prize_prints":low_hp_two_prize,
        "observation":(
            "The only <=90 HP legal Expanded 2-Prize prints in this "
            "card snapshot are Jirachi-EX. Its Psychic Resistance -20 "
            "reduces 90 to 70, so unmodified Mysterious Noise cannot "
            "one-hit-KO it from full 90 HP. With 20 prior damage "
            "or equivalent damage modification, the 2-Prize branch "
            "can become physically reachable."
        )
    }


if __name__=="__main__":
    print(json.dumps(run(),indent=2))
