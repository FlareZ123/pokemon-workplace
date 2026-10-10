"""Reproduce exact K1 Prize-pickup versus extra blind draw comparison."""
from fractions import Fraction
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
from beheeyem_physical_tutor import MODES
from beheeyem_prize_packet import exact_prize_take
from beheeyem_prize_vs_draw import compare_known_prizes

checks = 0
for B in range(1,5):
    for T in range(1,5):
        for mode in MODES:
            for d in range(6):
                result = compare_known_prizes(B,T,d,mode)
                (first, one_prize, extra_draw, better, worse, tied, pos, neg,
                 states, winner_states, best_prize, best_deck) = result
                assert first == exact_prize_take(B,T,d,mode,1)[0]
                assert one_prize == exact_prize_take(B,T,d,mode,1)[3]
                assert extra_draw == exact_prize_take(B,T,d+1,mode,0)[3]
                assert first == better+worse+tied
                assert pos-neg == one_prize-extra_draw
                assert 0 <= one_prize <= extra_draw <= first
                assert states >= winner_states >= 0
                checks += 1

for B,T in ((1,1),(1,4),(2,3),(4,4)):
    for d in range(6):
        a = compare_known_prizes(B,T,d,"ultra_ball")
        b = compare_known_prizes(T,B,d,"guzma_hala")
        assert a[:8] == b[:8]

x = compare_known_prizes(4,4,1,"computer_search")
assert x[3] == Fraction(1190398024,12595047465)
assert x[6] == Fraction(419175865,189612714564)
assert x[7] == Fraction(108313660067,35010633367710)
assert (x[8],x[9]) == (346,205)
assert x[10][1] == (1,1,1,3)
assert x[10][2] == (3,3,0,0)
assert x[10][5:] == (Fraction(1),Fraction(31,376))
assert x[11][2] == (0,0,0,6)

rows = []
for B,T,d,mode in ((4,4,1,"computer_search"),(4,4,2,"ultra_ball"),
                     (1,4,1,"mysterious_treasure"),(1,1,1,"computer_search")):
    x = compare_known_prizes(B,T,d,mode)
    rows.append({
        "B":B, "TAE":T, "T3_base_draws":d, "tutor":mode,
        "one_prize_percent":round(float(x[1])*100,7),
        "extra_draw_percent":round(float(x[2])*100,7),
        "prize_better_fraction_of_first_states_percent":round(float(x[3]/x[0])*100,7),
        "prize_better_unconditional_percent":round(float(x[3])*100,7),
        "positive_prize_advantage_pp":round(float(x[6])*100,7),
        "positive_deck_advantage_pp":round(float(x[7])*100,7),
        "reachable_K1_count_states":x[8],
    })

print(json.dumps({"validated_configurations":checks,"rows":rows},indent=2))
