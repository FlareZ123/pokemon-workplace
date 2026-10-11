"""Exact finite deck discard geometry, including density counterexample."""
import json
from fractions import Fraction
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"tools"))
from discard_target_hit_probability import (
    hit_probability,discard_hit_change
)


def run():
    checked=0
    density_down_but_hit_up=0
    for N in range(2,23):
        for K in range(1,N):
            for m in range(1,min(5,N-1)+1):
                for t in range(max(0,m-(N-K)),min(K,m)+1):
                    for n in range(1,min(N-m,6)+1):
                        d=discard_hit_change(N,K,n,m,t)
                        if d["density_nondecrease_is_sufficient"]:
                            assert d["difference"]>=0
                        if t==0:
                            assert d["difference"]>=0
                        if d["density_decreased_but_hit_improved"]:
                            density_down_but_hit_up+=1
                        checked+=1
    witness=discard_hit_change(7,2,3,3,1)
    assert witness["target_density_after"]==Fraction(1,4)
    assert witness["target_density_before"]==Fraction(2,7)
    assert witness["before"]==Fraction(5,7)
    assert witness["after"]==Fraction(3,4)
    assert witness["density_decreased_but_hit_improved"]

    illustrative=[]
    for quota in (4,6):
        for t in range(4):
            d=discard_hit_change(53,4,quota,3,t)
            illustrative.append({
                "draw_quota":quota,"discarded_targets":t,
                "baseline_hit_percent":round(100*float(d["before"]),8),
                "after_hit_percent":round(100*float(d["after"]),8),
                "signed_change_pp":round(100*float(d["difference"]),8)
            })
    assert hit_probability(53,4,6)==discard_hit_change(53,4,6,0,0)["before"]
    return {
        "finite_configurations_checked":checked,
        "density_decreased_yet_hit_probability_increased":density_down_but_hit_up,
        "witness":{
            "N":7,"K":2,"m":3,"discarded_targets":1,"draws":3,
            "density_before":"2/7","density_after":"1/4",
            "hit_before":"5/7","hit_after":"3/4"
        },
        "opponent_X_redraw_scenario":illustrative
    }


if __name__=="__main__":
    print(json.dumps(run(),indent=2))
