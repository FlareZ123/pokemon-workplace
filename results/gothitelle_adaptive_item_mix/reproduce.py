"""SFT: same-population adaptive Quick/Nest/Battle VIP Basic search.

The independent exhaustive reference uses physical card IDs for each
opening, Prize subset, first-turn draw, searched Basics, and second
turn draw. It checks each per-policy success mass and exclusive,
overlapping, and combined-only branch independently.
"""
from __future__ import annotations

import json
import sys
from dataclasses import replace
from fractions import Fraction
from itertools import combinations
from math import comb
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/"tools"))

from build_expanded_legality_baseline import classify_effective_legality
from gothitelle_adaptive_item_mix import (
    AdaptiveItemSetup, PARTS, MODES,
    exact_adaptive_item_access,
)
from gothitelle_core_board_joint_access import exact_core_board_access
from gothitelle_dual_use_joint_access import DualUseSetup


def exhaustive(case: AdaptiveItemSetup) -> tuple[
    dict[str,tuple[Fraction,...]],
    dict[str,tuple[Fraction,...]],
]:
    labels = "".join(
        name * count for name,count in zip(
            "GTCOQSNVX",case.categories
        )
    )
    universe = set(range(case.total))
    denominator = (
        comb(case.total,case.opening)
        * comb(case.total-case.opening,case.prizes)
        * (case.total-case.opening-case.prizes)
    )
    outcomes = {
        mode:[Fraction() for _ in range(5)]
        for mode in MODES
    }
    components = {
        name:[Fraction() for _ in range(5)]
        for name in PARTS
    }
    for opener in combinations(range(case.total),case.opening):
        if not any(labels[i]=="O" for i in opener):
            continue  # Ordinary initial Active
        other = universe-set(opener)
        for prizes in combinations(sorted(other),case.prizes):
            deck = other-set(prizes)
            for first in deck:
                seen = tuple(opener)+(first,)
                tags = {labels[i] for i in seen}
                if not {"Q","S"} <= tags:
                    continue
                need_g = int("G" not in tags)
                need_o = max(
                    0,4-sum(labels[i]=="O" for i in seen)
                )
                missing = need_g + need_o
                if missing > 4:
                    continue
                live = deck-{first}
                for target in "G"*need_g+"O"*need_o:
                    chosen = next(
                        (i for i in live if labels[i]==target),
                        None,
                    )
                    if chosen is None:
                        break
                    live.remove(chosen)
                else:
                    num_wins = sum(
                        ("T" in tags or labels[i]=="T")
                        and ("C" in tags or labels[i]=="C")
                        for i in live
                    )
                    if not num_wins:
                        continue
                    n = sum(labels[i]=="N" for i in seen)
                    v = sum(labels[i]=="V" for i in seen)
                    good = {
                        "quick_only":missing<=1,
                        "nest_only":missing<=1+n,
                        "vip_only":missing<=1+2*v,
                        "adaptive":missing<=1+n+2*v,
                    }
                    weight = Fraction(num_wins,len(live))
                    for mode, ok in good.items():
                        if ok:
                            outcomes[mode][missing] += weight
                    if good["quick_only"]:
                        component="base"
                    elif good["nest_only"] and good["vip_only"]:
                        component="shared_extra"
                    elif good["nest_only"]:
                        component="nest_exclusive"
                    elif good["vip_only"]:
                        component="vip_exclusive"
                    elif good["adaptive"]:
                        component="combined_only"
                    else:
                        continue
                    components[component][missing] += weight
    return (
        {
            k:tuple(x/denominator for x in values)
            for k,values in outcomes.items()
        },
        {
            k:tuple(x/denominator for x in values)
            for k,values in components.items()
        },
    )


def check_cards() -> None:
    sources = {
        "swsh1":("swsh1-179",),
        "xy6":("xy6-89",),
        "sv1":("sv1-181",),
        "swsh8":("swsh8-225",),
    }
    cards = {}
    for code, ids in sources.items():
        rows = json.loads(
            (ROOT/"resources"/"cards"/"en"/f"{code}.json")
            .read_text(encoding="utf-8")
        )
        cards.update({
            card["id"]:card for card in rows
            if card["id"] in ids
        })
    assert len(cards)==4
    assert all(
        classify_effective_legality(card)[0]=="Legal"
        for card in cards.values()
    )
    assert "discard another card" in " ".join(
        cards["swsh1-179"]["rules"]
    )
    assert "put it onto your Bench" in " ".join(
        cards["sv1-181"]["rules"]
    )
    vip_text=" ".join(cards["swsh8-225"]["rules"])
    assert "only during your first turn" in vip_text
    assert "up to 2 Basic Pokémon" in vip_text
    assert "put them onto your Bench" in vip_text
    assert cards["xy6-89"]["name"]=="Sky Field"
    print("PASS Quick, Nest, VIP, Sky card texts and Expanded legality")


def main() -> None:
    check_cards()
    cases = (
        AdaptiveItemSetup(
            total=12,opening=6,prizes=1,gothita=1,
            gothitelle=1,rare_candy=1,other_basics=4,
            quick_ball=1,sky_field=1,nest_ball=1,battle_vip_pass=1,
        ),
        AdaptiveItemSetup(
            total=13,opening=6,prizes=2,gothita=2,
            gothitelle=1,rare_candy=1,other_basics=4,
            quick_ball=1,sky_field=1,nest_ball=2,battle_vip_pass=1,
        ),
    )
    for case in cases+(replace(cases[0],prizes=0),):
        analytic=exact_adaptive_item_access(case)
        modes,parts=exhaustive(case)
        assert analytic.per_mode==modes
        assert analytic.decomposition==parts
        print("PASS physical-ID joint search/prizes and disjoint events",case)
    base=AdaptiveItemSetup()
    odds=exact_adaptive_item_access(base)
    q,n,v,j=(
        odds.probability(mode)
        for mode in ("quick_only","nest_only","vip_only","adaptive")
    )
    assert q==exact_core_board_access(DualUseSetup()).per_attempt
    assert q<n<v<j
    assert odds.component("combined_only")>odds.component("shared_extra")
    assert odds.positive_complementarity==j-v-n+q>0
    assert exact_adaptive_item_access(
        replace(base,nest_ball=0)
    ).probability("adaptive")==v
    assert exact_adaptive_item_access(
        replace(base,battle_vip_pass=0)
    ).probability("adaptive")==n
    assert exact_adaptive_item_access(
        replace(base,quick_ball=0)
    ).probability("adaptive")==0
    assert exact_adaptive_item_access(
        replace(base,sky_field=0)
    ).probability("adaptive")==0
    print(json.dumps({
        "percent_by_policy":{
            mode:round(100*float(odds.probability(mode)),12)
            for mode in MODES
        },
        "exact_disjoint_decomposition_percent":{
            part:round(100*float(odds.component(part)),12)
            for part in PARTS
        },
        "positive_complementarity_pp":round(
            100*float(odds.positive_complementarity),12
        ),
        "joint_success_by_missing_basics_percent":{
            str(n):round(100*float(prob),12)
            for n,prob in enumerate(odds.per_mode["adaptive"])
        },
    },indent=2))
    print("gothitelle_adaptive_item_mix regression: PASS")


if __name__=="__main__":
    main()
