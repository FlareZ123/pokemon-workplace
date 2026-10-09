"""SFT: exact surplus-payment and K1-informative critical discards.

The independent reference enumerates every physical opening, first
draw, Prize subset, searched Basic identity, and final natural draw.
For a counterfactual K0 commitment, it maximizes the Stage2-versus-
Candy discard expectation only *after aggregating all possible Prize
subsets for a fixed observed opening and first-turn draw*.
For K1, it maximizes separately after each realized Prize subset.
"""
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

from build_expanded_legality_baseline import classify_effective_legality
from gothitelle_k1_discard_choices import (
    DynamicPaymentOdds, exact_dynamic_payment,
)
from gothitelle_paid_adaptive_items import PaidAdaptiveSetup


def exhaustive(case:PaidAdaptiveSetup)->tuple[Fraction,...]:
    labels="".join(
        symbol*count for symbol,count in zip(
            "GTCOQSNVDX",case.categories
        )
    )
    universe=set(range(case.total))
    denominator=(
        comb(case.total,case.opening)
        *comb(case.total-case.opening,case.prizes)
        *(case.total-case.opening-case.prizes)
    )
    baseline=Fraction(0)
    safe=Fraction(0)
    critical_k0=Fraction(0)
    critical_k1=Fraction(0)

    for opener in combinations(range(case.total),case.opening):
        if not any(labels[i]=="O" for i in opener):
            continue
        after_opener=universe-set(opener)
        for first in sorted(after_opener):
            observed=tuple(opener)+(first,)
            counts={
                kind:sum(labels[i]==kind for i in observed)
                for kind in "GTCOQSNVD"
            }
            if not counts["Q"] or not counts["S"]:
                continue
            required_g=int(counts["G"]==0)
            required_o=max(0,4-counts["O"])
            missing=required_g+required_o
            extra_q=max(
                0,missing-(1+counts["N"]+2*counts["V"])
            )
            if extra_q > counts["Q"]-1:
                continue
            other=after_opener-{first}
            safe_payment=(
                counts["D"]
                + counts["S"]-1
                + max(0,counts["G"]-1)
                + max(0,counts["O"]-4)
                + max(0,counts["T"]-1)
                + max(0,counts["C"]-1)
                + counts["Q"]-1-extra_q
            )
            # For K0, commitment happens before seeing any Prize subset.
            # Its expected outcomes for discarding T vs discarding C
            # must be aggregated separately over all possible Prizes.
            k0_discard_t=Fraction(0)
            k0_discard_c=Fraction(0)
            for prizes in combinations(sorted(other),case.prizes):
                deck=other-set(prizes)
                remaining=set(deck)
                for target in (
                    "G"*required_g+"O"*required_o
                ):
                    selected=next(
                        (i for i in remaining if labels[i]==target),
                        None,
                    )
                    if selected is None:
                        break
                    remaining.remove(selected)
                else:
                    if not remaining:
                        continue
                    if extra_q==0 or counts["D"]>=extra_q:
                        winners=sum(
                            (counts["T"]>0 or labels[i]=="T")
                            and (counts["C"]>0 or labels[i]=="C")
                            for i in remaining
                        )
                        baseline+=Fraction(winners,len(remaining))
                    elif safe_payment>=extra_q:
                        winners=sum(
                            (counts["T"]>0 or labels[i]=="T")
                            and (counts["C"]>0 or labels[i]=="C")
                            for i in remaining
                        )
                        safe+=Fraction(winners,len(remaining))
                    elif (
                        safe_payment==extra_q-1
                        and counts["T"]>0 and counts["C"]>0
                    ):
                        stage_outs=sum(
                            labels[i]=="T" for i in remaining
                        )
                        candy_outs=sum(
                            labels[i]=="C" for i in remaining
                        )
                        stage_chance=Fraction(
                            stage_outs,len(remaining)
                        )
                        candy_chance=Fraction(
                            candy_outs,len(remaining)
                        )
                        k0_discard_t+=stage_chance
                        k0_discard_c+=candy_chance
                        critical_k1+=max(
                            stage_chance,candy_chance
                        )
            critical_k0+=max(k0_discard_t,k0_discard_c)

    return tuple(
        value/denominator
        for value in (
            baseline,safe,critical_k0,critical_k1
        )
    )


def check_quick_ball() -> None:
    cards=json.loads(
        (ROOT/"resources"/"cards"/"en"/"swsh1.json")
        .read_text(encoding="utf-8")
    )
    quick=next(card for card in cards if card["id"]=="swsh1-179")
    assert classify_effective_legality(quick)[0]=="Legal"
    assert "discard another card from your hand" in " ".join(
        quick["rules"]
    )
    print("PASS exact one-card Quick Ball discard legality")


def main()->None:
    check_quick_ball()
    cases=(
        PaidAdaptiveSetup(
            total=16,opening=7,prizes=1,gothita=1,gothitelle=2,
            rare_candy=2,other_basics=4,quick_ball=2,
            sky_field=1,nest_ball=0,battle_vip_pass=1,
            approved_discard=0,
        ),
        PaidAdaptiveSetup(
            total=16,opening=7,prizes=1,gothita=1,gothitelle=2,
            rare_candy=2,other_basics=4,quick_ball=2,
            sky_field=2,nest_ball=0,battle_vip_pass=1,
            approved_discard=0,
        ),
    )
    for case in cases:
        got=exact_dynamic_payment(case)
        expected=exhaustive(case)
        actual=(
            got.approved_only,got.safe_surplus_increment,
            got.k0_critical_increment,got.k1_critical_increment,
        )
        assert actual==expected
        assert got.safe_surplus_increment>0
        assert got.k1_critical_increment>got.k0_critical_increment>0
        print("PASS independent complete physical Prize and K0/K1 choices",
              case,actual)

    base=PaidAdaptiveSetup()
    result=exact_dynamic_payment(base)
    assert (
        result.k1_optimal_total
        >result.k0_committed_total
        >result.safe_surplus_total
        >result.approved_only
    )
    no_extra_q=exact_dynamic_payment(replace(base,quick_ball=1))
    assert no_extra_q.safe_surplus_increment==0
    assert no_extra_q.k1_critical_increment==0
    assert no_extra_q.information_gain==0

    print(json.dumps({
        "per_opening_attempt_percent":{
            "approved_only":round(
                100*float(result.approved_only),12
            ),
            "approved_plus_surplus":round(
                100*float(result.safe_surplus_total),12
            ),
            "k0_committed":round(
                100*float(result.k0_committed_total),12
            ),
            "k1_optimal":round(
                100*float(result.k1_optimal_total),12
            ),
            "new_safe_payment_pp":round(
                100*float(result.safe_surplus_increment),12
            ),
            "new_k1_critical_payment_pp":round(
                100*float(result.k1_critical_increment),12
            ),
            "k1_information_value_pp":round(
                100*float(result.information_gain),14
            ),
        }
    },indent=2))
    print("gothitelle_k1_discard_choices regression: PASS")


if __name__=="__main__":
    main()
