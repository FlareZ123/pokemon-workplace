"""Exact Ultra Ball paid K1 access and pre/post Item-lock window tests."""
from fractions import Fraction
from math import comb
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"tools"))
from beheeyem_prelock_k1_search import (
    search_window_probabilities,missed_under_item_lock
)
from beheeyem_physical_tutor import choose


def independent_two_stage(k):
    """Enumerate Basic-valid opening seven, then k extra physical cards."""
    B,U,F,O=12,4,32,12
    valid=comb(60,7)-comb(48,7)
    total=pay=Fraction()
    for b in range(8):
        for u in range(5):
            for f in range(8):
                o=7-b-u-f
                hw=(choose(B,b)*choose(U,u)*
                    choose(F,f)*choose(O,o))
                if not hw or b==0:
                    continue
                remaining=(B-b,U-u,F-f,O-o)
                for db in range(k+1):
                    for du in range(k-db+1):
                        for df in range(k-db-du+1):
                            do=k-db-du-df
                            dw=(choose(remaining[0],db)*
                                choose(remaining[1],du)*
                                choose(remaining[2],df)*
                                choose(remaining[3],do))
                            if not dw:
                                continue
                            weight=Fraction(hw*dw,valid*comb(53,k))
                            total+=weight
                            if u+du>=1 and f+df>=2:
                                pay+=weight
    assert total==1
    return pay


def run():
    for k in (0,2,4):
        direct=search_window_probabilities(k)["paid_search_feasible"]
        assert direct==independent_two_stage(k)
    rows=[]
    for pre in range(6):
        for locked in range(6):
            z=missed_under_item_lock(pre,locked)
            assert 0<=z["K1_before_lock"]<=z["K1_if_items_remained_playable"]
            assert z["extra_supply_denied_by_lock"]>=0
            if locked==0:
                assert z["extra_supply_denied_by_lock"]==0
            if pre in (0,2,4) and locked in (0,2,4):
                rows.append({
                    "early_deck_draws":pre,
                    "draws_under_future_item_lock":locked,
                    "K1_feasible_prelock_percent":round(
                        100*float(z["K1_before_lock"]),8
                    ),
                    "counterfactual_feasible_percent":round(
                        100*float(z["K1_if_items_remained_playable"]),8
                    ),
                    "extra_source_supply_blocked_percent":round(
                        100*float(z["extra_supply_denied_by_lock"]),8
                    )
                })
    for prize in range(3):
        prev=Fraction()
        for k in range(6):
            data=search_window_probabilities(k,prize)
            assert data["seen_U"]>=data["paid_search_feasible"]>=prev
            prev=data["paid_search_feasible"]
    return {"two_stage_exact_checks":3,"window_combinations_checked":36,
            "rows":rows}


if __name__=="__main__":
    print(json.dumps(run(),indent=2))
