"""Two full English-print adaptations of 2026 Aichi sixth-place Quad Thorns."""
from __future__ import annotations
from collections import Counter
from datetime import date
from fractions import Fraction
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from tools.deck_legality_proof import adjudicate_deck
from tools.deck_validator import DeckEntry,load_all_card_records
from tools.iron_thorns_quad_opening import grouped_opening_access, independent_labeled_oracle

BASE=Path(__file__).resolve().parent
JP_ONLY={"Palace Book","Palace Belt","Player's Ceremony"}

def read(name):
    return json.loads((BASE/name).read_text(encoding="utf-8"))

def card(resources,pid):
    setid=pid.rsplit("-",1)[0]
    raw=json.loads((resources/"cards"/"en"/(setid+".json")).read_text(encoding="utf-8"))
    return next(c for c in raw if c["id"]==pid)

def verify() -> dict:
    resources=ROOT/"resources"
    records=load_all_card_records(resources)
    source=read("jp_original_names.json")
    assert (source["source"]["date"],source["source"]["place"],source["source"]["player"])==("2026-05-10",6,"Kazuma Kashi")
    original={r["name"]:r["quantity"] for r in source["cards"]}
    assert sum(original.values())==60 and len(original)==35
    assert {r["name"] for r in source["cards"] if r["print_id"] is None}==JP_ONLY
    assert all(name not in {c.name for c in records.values()} for name in JP_ONLY)
    original_core={n:q for n,q in original.items() if n not in JP_ONLY}
    assert sum(original_core.values())==57
    assert {n:q for n,q in original.items() if n in JP_ONLY}==dict.fromkeys(JP_ONLY,1)
    assert original["Iron Thorns ex"]==4
    assert original["Megaton Blower"]==1
    assert (original["Thunder Mountain ◇"],original["Wondrous Labyrinth ◇"])==(1,1)
    thorns=card(resources,"sv6-77")
    assert "Initialization"==thorns["abilities"][0]["name"]
    assert "no Abilities, except for Future Pokémon" in thorns["abilities"][0]["text"]
    assert thorns["attacks"][0]["cost"]==["Lightning","Colorless","Colorless"]
    assert "Search your deck for a Stadium card" in card(resources,"sm12-193")["rules"][0]
    assert "Pokémon Tool card and a Special Energy card" in " ".join(card(resources,"sm12-193")["rules"])
    assert "up to 2 TAG TEAM cards" in card(resources,"sm12-206")["rules"][0]
    assert "attacks of Lightning Pokémon" in card(resources,"sm8-191")["rules"][0]
    assert "Double Colorless Energy provides" in card(resources,"sm1-136")["rules"][0]
    assert "Your turn ends" in card(resources,"swsh5-122")["rules"][0]
    assert "until he or she has 7 cards" in card(resources,"bwp-BW28")["rules"][0]
    assert "draw 2 cards" in card(resources,"sv6-158")["rules"][0]
    assert "+50 HP" in card(resources,"sv2-173")["rules"][0]
    outputs=[]
    specs=[("mail_helmet",{"Trainers' Mail":1,"Tropical Beach":1,"Lucky Helmet":1}),
           ("camping_charm",{"Camping Gear":1,"Tropical Beach":1,"Bravery Charm":1})]
    for filename,delta in specs:
        deck=read(filename+".json")
        actual={r["name"]:r["quantity"] for r in deck["cards"]}
        expected=original_core.copy()
        for name,qty in delta.items():expected[name]=expected.get(name,0)+qty
        assert actual==expected,filename
        assert sum(actual.values())==60 and len(deck["cards"])==33
        categories=Counter()
        basics=0
        entries=[]
        for row in deck["cards"]:
            printed=records[row["print_id"]]
            assert printed.name==row["name"] and printed.supertype==row["category"]
            assert printed.effective_status=="Legal"
            categories[row["category"]]+=row["quantity"]
            basics+=row["quantity"]*int(printed.is_basic_pokemon)
            entries.append(DeckEntry(row["print_id"],row["quantity"]))
        assert categories=={"Pokémon":4,"Trainer":48,"Energy":8}
        assert basics==4
        checked=adjudicate_deck(entries,resources,as_of=date(2026,10,12))
        assert checked.construction.valid,checked.construction.issues
        assert checked.disposition=="eligible_snapshot",[(p.card_id,p.reason) for p in checked.print_proofs if p.eligibility!="eligible"]
        assert all(p.eligibility=="eligible" for p in checked.print_proofs)
        outputs.append({"name":filename,"cards":60,"unique_prints":len(entries),"basic_pokemon":basics,"construction":checked.disposition})
    grouped=grouped_opening_access()
    assert grouped==independent_labeled_oracle()
    assert grouped["valid_seven"]==Fraction(38962,97527)
    assert grouped["gh_route_cond_valid"]==Fraction(4378700663,15059942898)
    assert grouped["direct_dce_thunder_cond_valid"]==Fraction(3429,372680)
    return {"published_jp_source":60,"japanese_only_cards":sorted(JP_ONLY),
            "international_adaptations":outputs,
            "opening_physical_access":{k:format(float(v),".12g") for k,v in grouped.items()}}

if __name__=="__main__":
    print(json.dumps(verify(),indent=2))
