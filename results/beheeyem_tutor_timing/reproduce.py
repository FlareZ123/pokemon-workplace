"""Exact validation of tutor timing and physically different T3 deck sizes."""
from fractions import Fraction
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
from beheeyem_physical_tutor import MODES, exact_physical_tutor
from beheeyem_tutor_timing import exact_deferred_or_rescue

rows = []
for B in range(1, 5):
    for T in range(1, 5):
        for mode in MODES:
            prev_second = Fraction(0)
            prev_rescue = Fraction(0)
            prev_first = None
            for d in range(6):
                first, second, rescued_first, rescued_second = exact_deferred_or_rescue(B,T,d,mode)
                direct_first, _, deferred, _ = exact_physical_tutor(B,T,d,mode)
                assert first == direct_first + rescued_first
                assert second >= deferred
                assert first >= second >= 0
                assert first == prev_first if prev_first is not None else True
                assert rescued_first >= rescued_second >= prev_rescue
                assert second >= prev_second
                if d == 0:
                    assert rescued_second == 0
                prev_first, prev_second, prev_rescue = first, second, rescued_second
                if (B,T) in ((1,1),(1,4),(4,4)) and d in (1,3,5):
                    rows.append({"B":B,"TAE":T,"d":d,"tutor":mode,
                        "first_percent":round(float(first)*100,7),
                        "both_percent":round(float(second)*100,7),
                        "T2_rescue_first_percent":round(float(rescued_first)*100,7),
                        "T2_rescue_both_percent":round(float(rescued_second)*100,7)})

for B,T in ((1,1),(1,4),(2,3),(4,4)):
    for d in (0,1,3,5):
        assert (
            exact_deferred_or_rescue(B,T,d,"ultra_ball")
            == exact_deferred_or_rescue(T,B,d,"guzma_hala")
        )
        assert (
            exact_deferred_or_rescue(B,T,d,"mysterious_treasure")[1]
            >= exact_deferred_or_rescue(B,T,d,"ultra_ball")[1]
        )

assert exact_deferred_or_rescue(4,4,1,"computer_search")[1] == Fraction(12261875,1850700852)
assert exact_deferred_or_rescue(1,1,2,"computer_search")[1] == Fraction(9,97888)
for mode in MODES:
    _, _, first_rescue, second_rescue = exact_deferred_or_rescue(4,4,47,mode)
    assert first_rescue == second_rescue

print(json.dumps({"checked":"16 B/T pairs x 4 tutor modes x 6 draw budgets",
                  "rows":rows}, indent=2))
