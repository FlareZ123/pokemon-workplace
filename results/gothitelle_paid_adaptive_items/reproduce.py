"""SFT: paid second Quick Ball within the adaptive Nest/VIP model."""
from __future__ import annotations

import json
import sys
from dataclasses import replace
from fractions import Fraction
from itertools import combinations
from math import comb
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"tools"))

from gothitelle_adaptive_item_mix import (
    AdaptiveItemSetup, exact_adaptive_item_access,
)
from gothitelle_paid_adaptive_items import (
    MODES, PaidAdaptiveSetup, exact_paid_adaptive_access,
)


def exhaustive(case: PaidAdaptiveSetup) -> dict[str,tuple[Fraction,...]]:
    labels = "".join(
        kind*count
        for kind,count in zip("GTCOQSNVDX",case.categories)
    )
    universe=set(range(case.total))
    denominator = (
        comb(case.total,case.opening)
        * comb(case.total-case.opening,case.prizes)
        * (case.total-case.opening-case.prizes)
    )
    rows = {
        mode:[Fraction(0) for _ in range(5)]
        for mode in MODES
    }
    for opener in combinations(range(case.total),case.opening):
        if not any(labels[i]=="O" for i in opener):
            continue
        outside=universe-set(opener)
        for prizes in combinations(sorted(outside),case.prizes):
            deck=outside-set(prizes)
            for first in deck:
                observed=tuple(opener)+(first,)
                names={labels[i] for i in observed}
                if not {"Q","S"}<=names:
                    continue
                need_g=int("G" not in names)
                need_o=max(0,4-sum(labels[i]=="O" for i in observed))
                total_missing=need_g+need_o
                if total_missing>4:
                    continue
                remaining=deck-{first}
                # Physical searched copies must be present outside Prize.
                valid=True
                for kind in "G"*need_g+"O"*need_o:
                    found=next(
                        (i for i in remaining if labels[i]==kind),
                        None,
                    )
                    if found is None:
                        valid=False
                        break
                    remaining.remove(found)
                if not valid:
                    continue
                wins=sum(
                    ("T" in names or labels[i]=="T")
                    and ("C" in names or labels[i]=="C")
                    for i in remaining
                )
                if wins==0:
                    continue
                q=sum(labels[i]=="Q" for i in observed)
                d=sum(labels[i]=="D" for i in observed)
                n=sum(labels[i]=="N" for i in observed)
                v=sum(labels[i]=="V" for i in observed)
                extra=min(q-1,d)
                budgets={
                    "one_quick":1,
                    "paid_quick":1+extra,
                    "free_item_mix":1+n+2*v,
                    "adaptive_all":1+extra+n+2*v,
                }
                for mode,capacity in budgets.items():
                    if total_missing<=capacity:
                        rows[mode][total_missing] += Fraction(
                            wins,len(remaining)
                        )
    return {
        k:tuple(value/denominator for value in values)
        for k,values in rows.items()
    }


def main() -> None:
    cases=(
        PaidAdaptiveSetup(
            total=13,opening=6,prizes=1,gothita=1,
            gothitelle=1,rare_candy=1,other_basics=4,
            quick_ball=2,sky_field=1,nest_ball=1,
            battle_vip_pass=1,approved_discard=1,
        ),
        PaidAdaptiveSetup(
            total=14,opening=6,prizes=2,gothita=2,
            gothitelle=1,rare_candy=1,other_basics=4,
            quick_ball=2,sky_field=1,nest_ball=1,
            battle_vip_pass=1,approved_discard=1,
        ),
    )
    for case in cases+(replace(cases[0],prizes=0),):
        actual=exact_paid_adaptive_access(case)
        assert actual.by_policy==exhaustive(case)
        print("PASS independently enumerated copy-level Prize/payment policy",case)

    base=PaidAdaptiveSetup()
    out=exact_paid_adaptive_access(base)
    old=exact_adaptive_item_access(AdaptiveItemSetup())
    assert out.probability("one_quick")==old.probability("quick_only")
    assert out.probability("free_item_mix")==old.probability("adaptive")
    assert out.probability("paid_quick")>out.probability("one_quick")
    assert out.probability("adaptive_all")>out.probability("free_item_mix")
    assert out.paid_quick_gain_with_free_items>out.paid_quick_gain_alone
    assert out.paid_quick_interaction>0

    no_discard=exact_paid_adaptive_access(
        replace(base,approved_discard=0)
    )
    assert no_discard.probability("paid_quick")==out.probability("one_quick")
    assert no_discard.probability("adaptive_all")==out.probability("free_item_mix")
    assert exact_paid_adaptive_access(
        replace(base,quick_ball=1)
    ).paid_quick_gain_with_free_items==0

    sweep=[
        exact_paid_adaptive_access(replace(base,approved_discard=d))
        for d in (0,4,8,12,16,20)
    ]
    gains=[row.paid_quick_gain_with_free_items for row in sweep]
    assert all(gains[i]<gains[i+1] for i in range(len(gains)-1))
    assert all(
        gains[i+2]-2*gains[i+1]+gains[i]
        == gains[2]-2*gains[1]+gains[0]<0
        for i in range(1,len(gains)-2)
    )
    print(json.dumps({
        "policy_percent":{
            mode:round(100*float(out.probability(mode)),12)
            for mode in MODES
        },
        "paid_quick_gain_alone_pp":round(
            100*float(out.paid_quick_gain_alone),12
        ),
        "paid_quick_gain_with_items_pp":round(
            100*float(out.paid_quick_gain_with_free_items),12
        ),
        "positive_interaction_pp":round(
            100*float(out.paid_quick_interaction),12
        ),
        "gain_by_approved_discard_count_pp":{
            str(d):round(100*float(row.paid_quick_gain_with_free_items),12)
            for d,row in zip((0,4,8,12,16,20),sweep)
        },
    },indent=2))
    print("gothitelle_paid_adaptive_items regression: PASS")


if __name__=="__main__":
    main()
