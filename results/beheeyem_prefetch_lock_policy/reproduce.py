"""Reproduce K1 prefetch timing with exogenous next-turn tutor lock."""
from fractions import Fraction
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
from beheeyem_physical_tutor import MODES
from beheeyem_tutor_timing import exact_deferred_or_rescue
from beheeyem_prefetch_lock_policy import exact_prefetch_policy

checks = 0
for B in range(1, 5):
    for T in range(1, 5):
        for mode in MODES:
            for d in range(4):
                first0, baseline0, optimal0, uplift0, eligible0, selected0 = exact_prefetch_policy(
                    B, T, d, mode, Fraction(0))
                first1, baseline1, optimal1, uplift1, eligible1, selected1 = exact_prefetch_policy(
                    B, T, d, mode, Fraction(1))
                assert first0 == first1 == exact_deferred_or_rescue(B, T, d, mode)[0]
                assert baseline0 == exact_deferred_or_rescue(B, T, d, mode)[1]
                assert baseline1 <= optimal1 <= optimal0 <= first0
                assert baseline0 <= optimal0 <= first0
                assert uplift0 >= 0 and uplift1 >= 0
                assert eligible0 == eligible1
                assert 0 <= selected0 <= eligible0 and 0 <= selected1 <= eligible1
                if mode == "computer_search":
                    assert uplift0 == 0  # unrestricted reactive tutor weakly dominates
                checks += 1

for d in range(4):
    assert exact_prefetch_policy(4,4,d,"ultra_ball",Fraction(1)) == (
        exact_prefetch_policy(4,4,d,"guzma_hala",Fraction(1))
    )
assert exact_prefetch_policy(4,4,1,"computer_search",Fraction(1))[2] == Fraction(
    9216969361,1639293870060)
assert exact_prefetch_policy(4,4,1,"computer_search",Fraction(1,10))[3] == Fraction(
    2891158,20991745775)
assert exact_prefetch_policy(4,4,2,"ultra_ball",Fraction(0))[3] == Fraction(
    2075953571,81691477857990)

rows = []
for B,T,d,mode in ((4,4,1,"computer_search"),(4,4,2,"ultra_ball"),
                     (1,4,1,"mysterious_treasure"),(4,4,3,"guzma_hala")):
    for q in (Fraction(0),Fraction(1,10),Fraction(1,4),Fraction(1,2),Fraction(1)):
        first, baseline, optimal, uplift, eligible, selected = exact_prefetch_policy(
            B,T,d,mode,q)
        rows.append({
            "B":B,"TAE":T,"draws":d,"tutor":mode,
            "T3_tutor_denial_probability":str(q),
            "baseline_percent":round(float(baseline)*100,7),
            "optimal_percent":round(float(optimal)*100,7),
            "prefetch_uplift_percent_points":round(float(uplift)*100,7),
            "eligible_K1_states":eligible,
            "prefetch_K1_states":selected,
        })

print(json.dumps({"tested_B_T_mode_d_combinations":checks, "rows":rows}, indent=2))
