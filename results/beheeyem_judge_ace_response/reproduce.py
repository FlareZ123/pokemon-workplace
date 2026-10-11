"""Exact finite-census regression for Judge and Ace Trainer responses.

All probability comparisons concern Beheeyem/TAE second-packet acquisition,
conditional on an established three-Basic board and exogenous T2 KO reward.
Opposing player is assumed to retain all six original Prize cards.
"""
from fractions import Fraction
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
from beheeyem_physical_tutor import MODES
from beheeyem_supporter_reset import exact_supporter_reset
from beheeyem_prize_packet import exact_prize_take


def validate() -> dict:
    configurations = 0
    route_comparisons = 0
    strict_judge = strict_ace = 0
    rows = []
    for B in range(1, 5):
        for T in range(1, 5):
            for tutor in MODES:
                for d in range(6):
                    for r in range(3):
                        judge = exact_supporter_reset(B, T, d, tutor, r, "Judge")
                        marnie = exact_supporter_reset(B, T, d, tutor, r, "Marnie")
                        n = exact_supporter_reset(B, T, d, tutor, r, "N")
                        assert judge[0] == marnie[0] == n[0]
                        assert judge[0] == exact_prize_take(B, T, d, tutor, r)[0]
                        assert all(j <= m for j, m in zip(judge[1:], marnie[1:]))
                        assert all(j <= nn for j, nn in zip(judge[1:], n[1:]))
                        assert judge[1] + judge[2] == judge[3]
                        if r == 2:
                            assert judge == n  # Both shuffle all, draw 4+d.
                        else:
                            assert n[3] >= judge[3]
                        if judge[3] < marnie[3]:
                            strict_judge += 1

                        if r:
                            ace = exact_supporter_reset(B, T, d, tutor, r, "Ace Trainer")
                            assert ace[0] == judge[0]
                            assert all(a <= j for a, j in zip(ace[1:], judge[1:]))
                            assert ace[1] + ace[2] == ace[3]
                            if ace[3] < judge[3]:
                                strict_ace += 1
                        else:
                            try:
                                exact_supporter_reset(B, T, d, tutor, r, "Ace Trainer")
                                raise AssertionError("Ace Trainer must be illegal at tied Prizes")
                            except ValueError:
                                pass
                        route_comparisons += 2
                        configurations += 1
                        if B == T == 4 and tutor == "computer_search" and d == 1:
                            rows.append({
                                "prizes_awarded": r,
                                "first_packet": round(100 * float(judge[0]), 8),
                                "marnie_joint": round(100 * float(marnie[3]), 8),
                                "judge_joint": round(100 * float(judge[3]), 8),
                                "ace_joint": round(100 * float(ace[3]), 8) if r else None,
                            })

    assert configurations == 1152
    assert route_comparisons == 2304
    assert exact_supporter_reset(4,4,1,"computer_search",0,"Judge")[3] == Fraction(
        324655494653179,17094435047810120
    )
    assert exact_supporter_reset(4,4,1,"computer_search",1,"Judge")[3] == Fraction(
        26586216980570059591,1406572851821436198900
    )
    assert exact_supporter_reset(4,4,1,"computer_search",1,"Ace Trainer")[3] == Fraction(
        11897388470993632,992781515966569875
    )
    assert exact_supporter_reset(4,4,1,"computer_search",2,"Ace Trainer")[3] == Fraction(
        47613920258044054,3992249074844291625
    )
    return {
        "configurations": configurations,
        "direct_or_rescued_route_checks": route_comparisons,
        "configurations_with_strict_judge_gain": strict_judge,
        "eligible_configurations_with_strict_ace_gain": strict_ace,
        "example": rows,
    }


if __name__ == "__main__":
    print(json.dumps(validate(), indent=2))
