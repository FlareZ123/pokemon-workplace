"""Cross-validate K1 hidden-state N/Iono divergence against aggregate engines."""
from fractions import Fraction
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
from beheeyem_physical_tutor import MODES
from beheeyem_reset_state_value import exact_state_reset
from beheeyem_supporter_reset import exact_supporter_reset

checks = 0
rows = []
for B in range(1,5):
    for T in range(1,5):
        for mode in MODES:
            for d in range(6):
                for r in range(3):
                    x = exact_state_reset(B,T,d,mode,r)
                    (first,n,iono,n_better,iono_better,tie,
                     gain_n,gain_iono,states,witness_n,witness_iono) = x
                    assert first == exact_supporter_reset(
                        B,T,d,mode,r,"N")[0]
                    assert n == exact_supporter_reset(
                        B,T,d,mode,r,"N")[3]
                    assert iono == exact_supporter_reset(
                        B,T,d,mode,r,"Iono")[3]
                    assert n < iono
                    assert n_better > 0 and iono_better > 0
                    assert first == n_better+iono_better+tie
                    assert n-iono == gain_n-gain_iono
                    assert states > 0
                    assert witness_n[0] > 0 and witness_iono[0] > 0
                    checks += 1
                    if (B,T,d,mode) in (
                        (4,4,1,"computer_search"),
                        (1,4,1,"mysterious_treasure")
                    ):
                        rows.append({
                            "B":B,"TAE":T,"draws":d,"tutor":mode,
                            "Prizes_awarded":r,
                            "N_percent":round(float(n)*100,7),
                            "Iono_percent":round(float(iono)*100,7),
                            "N_favoured_percent_of_first_states":round(
                                float(n_better/first)*100,7),
                            "Iono_favoured_percent_of_first_states":round(
                                float(iono_better/first)*100,7),
                            "reachable_K1_count_states":states,
                        })

x = exact_state_reset(4,4,1,"computer_search",1)
assert x[3] == Fraction(89498641,1988691705)
assert x[6] == Fraction(175095561600308533,203851137945135681000)
assert x[7] == Fraction(19667562004183,7594065715481245)
assert x[8] == 346
assert x[9][1] == (1,4,1,0)
assert x[9][2] == (0,0,0,6)
assert x[10][1] == (1,1,0,4)
assert x[10][2] == (0,0,0,6)

print(json.dumps({"validated_states_and_aggregate_scenarios":checks,
                  "rows":rows},indent=2))
