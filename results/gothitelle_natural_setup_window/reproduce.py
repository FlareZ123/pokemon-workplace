"""SFT: early Gothitelle/Rare Candy natural-draw access timeline."""
from __future__ import annotations

import json
import sys
from fractions import Fraction
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"tools"))

from build_expanded_legality_baseline import classify_effective_legality
from gothitelle_natural_setup_window import (
    GothitelleSetup, exact_unassisted_turn_two,
    exhaustive_small, legal_opener_probability,
)


def pct(value: Fraction)->float:
    return 100.0*float(value)


def check_card_grounding()->None:
    names={
        "xy3": ("xy3-39","xy3-41"),
        "sv1": ("sv1-191",),
    }
    cards={}
    for set_id,card_ids in names.items():
        rows=json.loads(
            (ROOT/"resources"/"cards"/"en"/f"{set_id}.json")
            .read_text(encoding="utf-8")
        )
        cards.update({
            row["id"]:row for row in rows if row["id"] in card_ids
        })
    assert cards["xy3-39"]["name"]=="Gothita"
    assert "Basic" in cards["xy3-39"]["subtypes"]
    assert cards["xy3-41"]["name"]=="Gothitelle"
    assert "Stage 2" in cards["xy3-41"]["subtypes"]
    assert "Teleport Room" in {
        a["name"] for a in cards["xy3-41"]["abilities"]
    }
    assert cards["sv1-191"]["name"]=="Rare Candy"
    candy=" ".join(cards["sv1-191"]["rules"])
    assert "skipping the Stage 1" in candy
    assert "during your first turn" in candy
    assert "Basic Pokémon that was put into play this turn" in candy
    assert all(
        classify_effective_legality(card)[0]=="Legal"
        for card in cards.values()
    )
    print("PASS: Gothita/Gothitelle/Rare Candy legal, typed and timing grounded")


def main()->None:
    check_card_grounding()

    small=GothitelleSetup(
        total=9,opening=3,prizes=2,
        gothita=2,gothitelle=1,rare_candy=1,other_basics=1,
    )
    brute=exhaustive_small(small)
    exact=exact_unassisted_turn_two(small)
    assert brute==exact
    assert brute.legal_opener==legal_opener_probability(small)
    print("PASS: fully labeled opener->Prize->turn1->turn2 enumeration matches",exact)

    same_no_prizes=GothitelleSetup(
        total=9,opening=3,prizes=0,
        gothita=2,gothitelle=1,rare_candy=1,other_basics=1,
    )
    no_prizes=exact_unassisted_turn_two(same_no_prizes)
    assert no_prizes==exact
    assert exhaustive_small(same_no_prizes)==exact
    print("PASS: random Prize count cancels after marginalization over no-search draws")

    cases={
        "thin":GothitelleSetup(gothita=2,gothitelle=2,rare_candy=2,other_basics=8),
        "example":GothitelleSetup(gothita=3,gothitelle=2,rare_candy=4,other_basics=8),
        "wide":GothitelleSetup(gothita=4,gothitelle=3,rare_candy=4,other_basics=8),
        "thick":GothitelleSetup(gothita=4,gothitelle=4,rare_candy=4,other_basics=8),
        "no_other_basics":GothitelleSetup(gothita=3,gothitelle=2,rare_candy=4,other_basics=0),
    }
    computed={name:exact_unassisted_turn_two(case) for name,case in cases.items()}
    assert (
        computed["thin"].per_seven_card_attempt
        < computed["example"].per_seven_card_attempt
        < computed["wide"].per_seven_card_attempt
        < computed["thick"].per_seven_card_attempt
    )
    assert 0<computed["example"].conditional_valid_opener<1
    assert 0<computed["example"].legal_opener<1
    for name,out in computed.items():
        print(
            f"PASS: {name}: attempt={pct(out.per_seven_card_attempt):.6f}% "
            f"legal_opener={pct(out.legal_opener):.6f}% "
            f"conditional_legal={pct(out.conditional_valid_opener):.6f}%"
        )
    print(json.dumps({
        name:{
            "counts":{
                "gothita":cases[name].gothita,
                "gothitelle":cases[name].gothitelle,
                "rare_candy":cases[name].rare_candy,
                "other_basics":cases[name].other_basics,
            },
            "seven_card_attempt":str(out.per_seven_card_attempt),
            "seven_card_attempt_percent":round(pct(out.per_seven_card_attempt),6),
            "legal_opener_percent":round(pct(out.legal_opener),6),
            "conditional_legal_percent":round(pct(out.conditional_valid_opener),6),
        } for name,out in computed.items()
    },indent=2))
    print("gothitelle_natural_setup_window regression: PASS")


if __name__=="__main__":
    main()
