"""SFT: exact turn-one Quick Ball search for Gothita before Rare Candy."""
from __future__ import annotations

import json
import sys
from dataclasses import replace
from fractions import Fraction
from itertools import combinations
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"tools"))

from build_expanded_legality_baseline import classify_effective_legality
from gothitelle_quick_ball_first_turn import QuickSetup, exact_quick_setup


def brute(case:QuickSetup)->tuple[Fraction,Fraction]:
    """Independent label-level opener/Prize/first draw/second draw exhaustive."""
    labels=(
        "G"*case.gothita+"T"*case.gothitelle
        +"C"*case.rare_candy+"O"*case.other_basics
        +"Q"*case.quick_ball+"D"*case.approved_discard
    )
    labels+="F"*(case.total-len(labels))
    ids=tuple(range(case.total))
    count=0
    baseline=Fraction(0)
    enriched=Fraction(0)
    for opener in combinations(ids,case.opening):
        opening=set(opener)
        opening_tags={labels[i] for i in opener}
        valid=("G" in opening_tags or "O" in opening_tags)
        rest=tuple(i for i in ids if i not in opening)
        for prize in combinations(rest,case.prizes):
            prize_set=set(prize)
            in_deck=tuple(i for i in rest if i not in prize_set)
            for first in in_deck:
                count+=1
                if not valid:
                    continue
                observed=tuple(opener)+(first,)
                seen={labels[i] for i in observed}
                remaining=tuple(i for i in in_deck if i!=first)
                naturally_ready=("G" in seen)
                if naturally_ready:
                    valid_turn2=tuple(
                        i for i in remaining
                        if "T" in seen or labels[i]=="T"
                        if "C" in seen or labels[i]=="C"
                    )
                    success=Fraction(len(valid_turn2),len(remaining))
                    baseline+=success
                    enriched+=success
                    continue
                if not {"Q","D"}<=seen:
                    continue
                gothita_out=tuple(i for i in remaining if labels[i]=="G")
                if not gothita_out:
                    continue
                # Select a physical Gothita found by restricted search.
                after_search=tuple(
                    i for i in remaining if i!=gothita_out[0]
                )
                wins=sum(
                    ("T" in seen or labels[i]=="T")
                    and ("C" in seen or labels[i]=="C")
                    for i in after_search
                )
                enriched+=Fraction(wins,len(after_search))
    return baseline/count,enriched/count


def pct(x:Fraction)->float:
    return 100.0*float(x)


def main()->None:
    rows=json.loads(
        (ROOT/"resources"/"cards"/"en"/"swsh1.json").read_text(encoding="utf-8")
    )
    q=next(x for x in rows if x["id"]=="swsh1-179")
    text=" ".join(q["rules"])
    assert classify_effective_legality(q)[0]=="Legal"
    assert "discard another card from your hand" in text
    assert "Search your deck for a Basic Pokémon" in text
    print("PASS: Quick Ball exact item/Basic text and paper Expanded legality")

    tiny=QuickSetup(
        total=10,opening=3,prizes=2,
        gothita=2,gothitelle=1,rare_candy=1,
        other_basics=1,quick_ball=1,approved_discard=1,
    )
    analytical=exact_quick_setup(tiny)
    baseline,with_quick=brute(tiny)
    assert baseline==analytical.natural.per_seven_card_attempt
    assert with_quick==analytical.quick_enabled.per_seven_card_attempt
    assert with_quick>baseline
    print("PASS: independently enumerate labeled Gothita search and Prize order", analytical)

    no_prizes=replace(tiny,prizes=0)
    no_prize_results=exact_quick_setup(no_prizes)
    assert brute(no_prizes)==(
        no_prize_results.natural.per_seven_card_attempt,
        no_prize_results.quick_enabled.per_seven_card_attempt,
    )
    assert no_prize_results.natural==analytical.natural
    assert no_prize_results.quick_enabled!=analytical.quick_enabled
    print("PASS: natural-only Prize marginal invariant, search branch Prize-sensitive")

    base=QuickSetup()
    out=exact_quick_setup(base)
    assert out.quick_enabled.per_seven_card_attempt>out.natural.per_seven_card_attempt
    assert out.improvement_conditional_legal>0
    assert exact_quick_setup(replace(base,approved_discard=0)).quick_enabled==out.natural
    assert exact_quick_setup(replace(base,quick_ball=0)).quick_enabled==out.natural
    sparse=exact_quick_setup(replace(base,approved_discard=4))
    dense=exact_quick_setup(replace(base,approved_discard=20))
    assert (
        out.natural.per_seven_card_attempt
        <= sparse.quick_enabled.per_seven_card_attempt
        <= out.quick_enabled.per_seven_card_attempt
        <= dense.quick_enabled.per_seven_card_attempt
    )
    for label,case in (
        ("no_search",replace(base,quick_ball=0)),
        ("payment_4",replace(base,approved_discard=4)),
        ("payment_12",base),
        ("payment_20",replace(base,approved_discard=20)),
    ):
        row=exact_quick_setup(case)
        print(
            f"PASS: {label}: unassisted={pct(row.natural.conditional_valid_opener):.6f}% "
            f"Quick-enabled={pct(row.quick_enabled.conditional_valid_opener):.6f}% "
            f"increment={pct(row.improvement_conditional_legal):.6f} pp"
        )
    print(json.dumps({
        "base":{
            "natural_legal_percent":round(pct(out.natural.conditional_valid_opener),6),
            "quick_enabled_legal_percent":round(pct(out.quick_enabled.conditional_valid_opener),6),
            "gain_percentage_points":round(pct(out.improvement_conditional_legal),6),
        },
        "model":"six random Prize cards, legal opener, one turn-one Quick Ball search only if Gothita missing, paid with a separate approved card, one natural second-turn draw",
    },indent=2))
    print("gothitelle_quick_ball_first_turn regression: PASS")


if __name__=="__main__":
    main()
