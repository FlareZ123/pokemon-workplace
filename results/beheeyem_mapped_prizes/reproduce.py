"""Regression for face-up optimally chosen Prize cards versus blind awards."""
from fractions import Fraction
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
from beheeyem_physical_tutor import MODES
from beheeyem_mapped_prizes import exact_mapped_prizes
from beheeyem_prize_packet import exact_prize_take

checks = improved_scenarios = 0
rows = []
for B in range(1,5):
    for T in range(1,5):
        for mode in MODES:
            for d in range(6):
                previous = Fraction(0)
                for r in range(3):
                    first,blind,mapped,uplift,mass,states,witness = exact_mapped_prizes(
                        B,T,d,mode,r)
                    assert first == exact_prize_take(B,T,d,mode,r)[0]
                    assert blind == exact_prize_take(B,T,d,mode,r)[3]
                    assert 0 <= blind <= mapped <= first
                    assert uplift == mapped-blind >= 0
                    assert mapped >= previous
                    assert 0 <= mass <= first
                    if r == 0:
                        assert mapped == blind and uplift == mass == 0
                    if uplift:
                        assert states > 0 and witness[0] > 0
                        improved_scenarios += 1
                    previous = mapped
                    checks += 1
                    if (B,T,d,mode) in (
                        (4,4,1,"computer_search"),
                        (4,4,1,"mysterious_treasure"),
                        (1,4,1,"mysterious_treasure"),
                    ):
                        rows.append({
                            "B":B,"TAE":T,"draws":d,"tutor":mode,
                            "Prizes_awarded":r,
                            "blind_percent":round(float(blind)*100,7),
                            "optimally_mapped_percent":round(float(mapped)*100,7),
                            "mapping_advantage_pp":round(float(uplift)*100,7),
                            "improvable_K1_state_mass_percent":round(
                                float(mass/first)*100,7)
                        })

for B,T in ((1,1),(1,4),(2,3),(4,4)):
    for d in range(6):
        for r in range(3):
            assert (
                exact_mapped_prizes(B,T,d,"ultra_ball",r)[:6]
                == exact_mapped_prizes(T,B,d,"guzma_hala",r)[:6]
            )

x = exact_mapped_prizes(4,4,1,"computer_search",1)
assert x[2] == Fraction(69292566989,2367868923420)
assert x[3] == Fraction(4039194259,224324424324)
assert x[4] == Fraction(713992960,7557028479)
assert x[5] == 199
assert x[6][1] == (0,2,1,3)
assert x[6][2] == (1,0,0,5)
assert x[6][6] == (1,0,0,0)
assert x[6][7:] == (Fraction(1),Fraction(31,141))
x2 = exact_mapped_prizes(4,4,1,"computer_search",2)
assert x2[2] == Fraction(79067942461,1775901692565)

print(json.dumps({
    "validated_configuration_count":checks,
    "configurations_with_positive_map_advantage":improved_scenarios,
    "selected_rows":rows
},indent=2))
