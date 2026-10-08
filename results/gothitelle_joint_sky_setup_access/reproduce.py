"""SFT: exact joint Quick/Sky/Gothita/Candy/Gothitelle two-turn access."""
from __future__ import annotations

import json
import sys
from dataclasses import replace
from fractions import Fraction
from itertools import combinations
from math import comb
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"tools"))

from gothitelle_joint_sky_setup_access import (
    JointLineConfig,JointLineProbability,exact_joint_line,
)
from gothitelle_quick_ball_first_turn import exact_quick_setup


def pct(x:Fraction)->float:
    return 100.0*float(x)


def brute(case:JointLineConfig)->tuple[Fraction,Fraction]:
    """Enumerate labeled opening/Prize/turn1 and all possible turn2 draws."""
    strings=(
        "G"*case.gothita+"T"*case.gothitelle+"C"*case.rare_candy
        +"O"*case.other_basics+"Q"*case.quick_ball
        +"S"*case.sky_field
    )
    labels=strings+"F"*(case.total-len(strings))
    ids=tuple(range(case.total))
    total=0
    natural=Fraction(0)
    fetched=Fraction(0)
    for opening in combinations(ids,case.opening):
        beginning=set(opening)
        initial_tags={labels[i] for i in opening}
        legal="G" in initial_tags or "O" in initial_tags
        others=tuple(i for i in ids if i not in beginning)
        for prizes in combinations(others,case.prizes):
            prize_set=set(prizes)
            next_cards=tuple(i for i in others if i not in prize_set)
            for first in next_cards:
                total+=1
                if not legal:
                    continue
                seen=tuple(opening)+(first,)
                hand={labels[i] for i in seen}
                if not {"Q","S"}<=hand:
                    continue
                rest=tuple(i for i in next_cards if i!=first)
                if "G" in hand:
                    successful=sum(
                        ("T" in hand or labels[i]=="T")
                        and ("C" in hand or labels[i]=="C")
                        for i in rest
                    )
                    natural+=Fraction(successful,len(rest))
                else:
                    candidates=tuple(i for i in rest if labels[i]=="G")
                    if not candidates:
                        continue
                    after_search=tuple(i for i in rest if i!=candidates[0])
                    successful=sum(
                        ("T" in hand or labels[i]=="T")
                        and ("C" in hand or labels[i]=="C")
                        for i in after_search
                    )
                    fetched+=Fraction(successful,len(after_search))
    assert total==(
        comb(case.total,case.opening)
        *comb(case.total-case.opening,case.prizes)
        *(case.total-case.opening-case.prizes)
    )
    return fetched/total,natural/total


def main()->None:
    toy=JointLineConfig(
        total=11,opening=4,prizes=2,gothita=2,gothitelle=1,
        rare_candy=1,other_basics=1,quick_ball=1,sky_field=1,
    )
    direct=brute(toy)
    analytical=exact_joint_line(toy)
    assert direct==(analytical.found_gothita,analytical.gothita_already_seen)
    assert analytical.full_line>0
    print("PASS: full labeled 11-card Prize and two-turn joint witness",analytical)

    zero_prize=replace(toy,prizes=0)
    same=exact_joint_line(zero_prize)
    assert brute(zero_prize)==(same.found_gothita,same.gothita_already_seen)
    print("PASS: exact joint search/no-search branches under alternate Prize count")

    example=JointLineConfig()
    result=exact_joint_line(example)
    baseline=exact_quick_setup(example.with_quick_payment_as_sky())
    assert result.found_gothita==(
        baseline.quick_enabled.per_seven_card_attempt
        -baseline.natural.per_seven_card_attempt
    )
    assert result.full_line>result.found_gothita>0
    assert result.gothita_already_seen>0
    assert result.conditional_on_valid_opener<=1
    assert result.legal_opening==baseline.natural.legal_opener
    print("PASS: found-Gothita branch agrees exactly with independent Quick setup delta")

    no_sky=exact_joint_line(replace(example,sky_field=0))
    no_quick=exact_joint_line(replace(example,quick_ball=0))
    assert no_sky.full_line==0 and no_quick.full_line==0
    assert (
        exact_joint_line(replace(example,sky_field=1)).full_line
        <result.full_line
        <exact_joint_line(replace(example,sky_field=3)).full_line
    )
    print("PASS: card absence and Sky count monotonicity")

    print(
        f"PASS: searched Gothita plus first-turn Sky payment "
        f"{pct(result.found_gothita/result.legal_opening):.6f}% given legal opener"
    )
    print(
        f"PASS: already-observed Gothita plus first-turn Sky payment "
        f"{pct(result.gothita_already_seen/result.legal_opening):.6f}% given legal opener"
    )
    print(
        f"PASS: combined two-turn joint access "
        f"{pct(result.conditional_on_valid_opener):.6f}% given legal opener"
    )
    print(json.dumps({
        "setup":{
            "gothita":example.gothita,
            "gothitelle":example.gothitelle,
            "rare_candy":example.rare_candy,
            "other_basics":example.other_basics,
            "quick_ball":example.quick_ball,
            "sky_field":example.sky_field,
            "total":example.total,
            "opening":example.opening,
            "prizes":example.prizes,
        },
        "fetched_gothita_fraction":str(result.found_gothita),
        "observed_gothita_fraction":str(result.gothita_already_seen),
        "joint_fraction":str(result.full_line),
        "per_seven_card_attempt_percent":round(pct(result.full_line),6),
        "legal_opener_percent":round(pct(result.legal_opening),6),
        "joint_conditional_valid_opener_percent":round(
            pct(result.conditional_on_valid_opener),6
        ),
    },indent=2))
    print("gothitelle_joint_sky_setup_access regression: PASS")


if __name__=="__main__":
    main()
