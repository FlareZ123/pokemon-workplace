"""Exact Prize-take recurrence cross-validation and quantitative census."""
from fractions import Fraction
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
from beheeyem_physical_tutor import MODES
from beheeyem_prize_packet import exact_prize_take
from beheeyem_tutor_timing import exact_deferred_or_rescue

rows = []
checks = 0
for B in range(1, 5):
    for T in range(1, 5):
        for mode in MODES:
            for d in range(4):
                prev = Fraction(0)
                baseline_first, _, _, baseline_both = exact_deferred_or_rescue(
                    B, T, d, mode)
                for r in range(3):
                    first, direct_both, rescue_both, both = exact_prize_take(
                        B, T, d, mode, r)
                    assert first == baseline_first
                    assert 0 <= direct_both <= both <= first
                    assert rescue_both >= 0 and both == direct_both + rescue_both
                    assert prev <= both
                    prev = both
                    if r == 0:
                        assert both == baseline_both
                    checks += 1
                    if (B,T,d) in ((4,4,1),(1,4,1),(4,4,3)):
                        rows.append({
                            "B":B,"TAE":T,"T3_draws":d,"tutor":mode,
                            "Prizes_taken_after_T2":r,
                            "first_percent":round(float(first)*100,7),
                            "direct_both_percent":round(float(direct_both)*100,7),
                            "T2_rescued_both_percent":round(float(rescue_both)*100,7),
                            "all_both_percent":round(float(both)*100,7)})

for B,T in ((1,1),(1,4),(2,3),(4,4)):
    for d in range(4):
        for r in range(3):
            assert (exact_prize_take(B,T,d,"ultra_ball",r) ==
                    exact_prize_take(T,B,d,"guzma_hala",r))

assert exact_prize_take(4,4,1,"computer_search",0)[3] == Fraction(
    12261875,1850700852)
assert exact_prize_take(4,4,1,"computer_search",1)[3] == Fraction(
    59977412074,5327705077695)
assert exact_prize_take(4,4,1,"computer_search",2)[3] == Fraction(
    447419776261,26638525388475)
assert exact_prize_take(1,1,0,"computer_search",0)[3] == 0
assert exact_prize_take(4,4,0,"computer_search",2)[3] > 0

print(json.dumps({"validated_combinations":checks,"selected_rows":rows},indent=2))
