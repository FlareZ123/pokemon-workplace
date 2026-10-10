"""Regression census for Iono's Prize-dependent top-deck redraw."""
from fractions import Fraction
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
from beheeyem_physical_tutor import MODES
from beheeyem_prize_packet import exact_prize_take
from beheeyem_iono_prize import exact_iono_after_prizes

checked = 0
rows = []
for B in range(1,5):
    for T in range(1,5):
        for mode in MODES:
            for d in range(6):
                previous = None
                for r in range(3):
                    first, direct, rescue, both = exact_iono_after_prizes(
                        B,T,d,mode,r)
                    unopposed_first, _, _, unopposed_both = exact_prize_take(
                        B,T,d,mode,r)
                    assert first == unopposed_first
                    assert 0 <= direct <= both <= first
                    assert rescue >= 0 and both == direct+rescue
                    assert both >= unopposed_both
                    if previous is not None:
                        assert both <= previous
                    if d and r:
                        assert both == exact_iono_after_prizes(
                            B,T,d-1,mode,r-1)[3]
                    previous = both
                    checked += 1
                    if (B,T,mode) in (
                        (4,4,"computer_search"),(1,4,"mysterious_treasure")
                    ) and d in (0,1,3):
                        rows.append({
                            "B":B,"TAE":T,"draws":d,"tutor":mode,
                            "Prizes_awarded":r,
                            "unopposed_percent":round(float(unopposed_both)*100,7),
                            "opposing_Iono_percent":round(float(both)*100,7)
                        })

for B,T in ((1,1),(1,4),(2,3),(4,4)):
    for d in range(6):
        for r in range(3):
            assert (
                exact_iono_after_prizes(B,T,d,"ultra_ball",r)
                == exact_iono_after_prizes(T,B,d,"guzma_hala",r)
            )

assert exact_iono_after_prizes(4,4,1,"computer_search",0)[3] == Fraction(
    1286911604767,35010633367710)
assert exact_iono_after_prizes(4,4,1,"computer_search",1)[3] == Fraction(
    1843582711391,65353182286392)
assert exact_iono_after_prizes(4,4,1,"computer_search",2)[3] == Fraction(
    304581295121,15081503604552)

print(json.dumps({"checked_scenarios":checked,"rows":rows},indent=2))
