"""Cross-check physical Iono, N and Marnie reset semantics over exact grid."""
from fractions import Fraction
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
from beheeyem_physical_tutor import MODES
from beheeyem_iono_prize import exact_iono_after_prizes
from beheeyem_prize_packet import exact_prize_take
from beheeyem_supporter_reset import exact_supporter_reset

checked = 0
rows = []
for B in range(1,5):
    for T in range(1,5):
        for mode in MODES:
            for d in range(6):
                previous_iono = previous_n = None
                marnie_ref = None
                for r in range(3):
                    first, _, _, iono = exact_supporter_reset(B,T,d,mode,r,"Iono")
                    _, _, _, n = exact_supporter_reset(B,T,d,mode,r,"N")
                    first_m, _, _, m = exact_supporter_reset(B,T,d,mode,r,"Marnie")
                    assert first == first_m == exact_prize_take(B,T,d,mode,r)[0]
                    assert iono == exact_iono_after_prizes(B,T,d,mode,r)[3]
                    assert 0 < n <= iono <= first
                    if r:
                        assert iono <= previous_iono
                        assert n <= previous_n
                        assert m == marnie_ref
                    else:
                        marnie_ref = m
                    if r == 2:
                        assert m == iono and n < m
                    else:
                        assert n > m
                    previous_iono, previous_n = iono, n
                    checked += 3
                    if (B,T,mode) in ((4,4,"computer_search"),
                                      (1,4,"mysterious_treasure")) and d in (0,1,3):
                        rows.append({
                            "B":B,"TAE":T,"draws":d,"tutor":mode,
                            "Prizes_taken":r,
                            "opposing_Iono_percent":round(float(iono)*100,7),
                            "opposing_N_percent":round(float(n)*100,7),
                            "opposing_Marnie_percent":round(float(m)*100,7)
                        })

for B,T in ((1,1),(1,4),(2,3),(4,4)):
    for d in range(6):
        for r in range(3):
            for supporter in ("Iono","N","Marnie"):
                assert (
                    exact_supporter_reset(B,T,d,"ultra_ball",r,supporter)
                    == exact_supporter_reset(T,B,d,"guzma_hala",r,supporter)
                )

assert exact_supporter_reset(4,4,1,"computer_search",0,"N")[3] == Fraction(
    7638611316894431,219785593471844400)
assert exact_supporter_reset(4,4,1,"computer_search",1,"N")[3] == Fraction(
    363002884397299877,13709287054789826500)
assert exact_supporter_reset(4,4,1,"computer_search",2,"N")[3] == Fraction(
    141211435051321867,7505428260707268255)

print(json.dumps({"supporter_scenarios_checked":checked,"rows":rows},indent=2))
