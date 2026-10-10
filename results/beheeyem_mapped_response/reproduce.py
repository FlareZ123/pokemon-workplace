"""Exact Town Map optimal Prize policy under N versus uninterrupted hand."""
from fractions import Fraction
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
from beheeyem_physical_tutor import MODES
from beheeyem_mapped_response import exact_mapping_response
from beheeyem_mapped_prizes import exact_mapped_prizes
from beheeyem_supporter_reset import exact_supporter_reset

checked = positive_N = conflicting = 0
rows = []
for B in range(1,5):
    for T in range(1,5):
        for mode in MODES:
            for d in range(6):
                for r in range(3):
                    x = exact_mapping_response(B,T,d,mode,r)
                    (first,blind_N,optimal_N,uplift_N,
                     optimal_no_reply,N_from_no_reply_policy,
                     surprise_N_regret,conflict_mass,conflict_states,witness) = x
                    assert first == exact_supporter_reset(
                        B,T,d,mode,r,"N")[0]
                    assert blind_N == exact_supporter_reset(
                        B,T,d,mode,r,"N")[3]
                    assert optimal_no_reply == exact_mapped_prizes(
                        B,T,d,mode,r)[2]
                    assert 0 <= blind_N <= optimal_N <= first
                    assert uplift_N == optimal_N-blind_N >= 0
                    assert surprise_N_regret == (
                        optimal_N-N_from_no_reply_policy
                    ) >= 0
                    assert 0 <= conflict_mass <= first
                    if r == 0:
                        assert optimal_N == blind_N
                        assert surprise_N_regret == conflict_mass == 0
                        assert conflict_states == 0
                    if uplift_N:
                        positive_N += 1
                    if conflict_states:
                        conflicting += 1
                        assert surprise_N_regret > 0 and witness is not None
                    checked += 1
                    if (B,T,d,mode) in (
                        (4,4,1,"computer_search"),
                        (4,4,1,"mysterious_treasure"),
                        (1,4,1,"mysterious_treasure")
                    ):
                        rows.append({
                            "B":B,"TAE":T,"draws":d,"tutor":mode,
                            "Prizes_awarded":r,
                            "N_random_percent":round(float(blind_N)*100,7),
                            "N_mapped_percent":round(float(optimal_N)*100,7),
                            "NoReply_mapped_percent":round(
                                float(optimal_no_reply)*100,7),
                            "N_mapped_when_noReply_policy_chosen_percent":round(
                                float(N_from_no_reply_policy)*100,7),
                            "surprise_N_regret_pp":round(
                                float(surprise_N_regret)*100,9),
                            "strictly_conflicting_K1_states":conflict_states
                        })

for B,T in ((1,1),(1,4),(2,3),(4,4)):
    for d in range(6):
        for r in range(3):
            assert (
                exact_mapping_response(B,T,d,"ultra_ball",r)[:9]
                == exact_mapping_response(T,B,d,"guzma_hala",r)[:9]
            )

x = exact_mapping_response(4,4,1,"computer_search",1)
assert x[2] == Fraction(17132875347895276513,586072021592265082875)
assert x[6] == Fraction(100669193678,130673806375086975)
assert x[7] == Fraction(957896,12595047465)
assert x[8] == 12
assert x[9][1] == (1,3,1,1)
assert x[9][2] == (0,1,0,5)
assert x[9][6][0][0] == (0,0,0,1)
assert x[9][7][0][0] == (0,1,0,0)
assert (checked,positive_N,conflicting) == (1152,768,232)

print(json.dumps({
    "configurations":checked,
    "positive_mapped_N_value":positive_N,
    "with_conflicting_N_and_noReply_optimal_Prize_choices":conflicting,
    "rows":rows
},indent=2))
