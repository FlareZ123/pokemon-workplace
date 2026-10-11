"""Exact opponent no-hand-reset action versus Judge and Ace Trainer.

Reuses two independently developed physical-zone engines: prize_take for
hand preservation, supporter_reset for full-deck shuffle and redraw. The
objective is conditional next Beheeyem+TAE packet access, NOT win probability.
"""
from collections import Counter
from fractions import Fraction
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
from beheeyem_physical_tutor import MODES
from beheeyem_prize_packet import exact_prize_take
from beheeyem_supporter_reset import exact_supporter_reset


def run() -> dict:
    overall = Counter()
    by_prize = Counter()
    by_public_route = Counter()
    examples = []
    for B in range(1, 5):
        for T in range(1, 5):
            for tutor in MODES:
                for d in range(6):
                    for r in range(3):
                        intact = exact_prize_take(B,T,d,tutor,r)
                        response = "Judge" if r == 0 else "Ace Trainer"
                        reset = exact_supporter_reset(B,T,d,tutor,r,response)
                        assert intact[0] == reset[0]
                        assert intact[1]+intact[2] == intact[3]
                        assert reset[1]+reset[2] == reset[3]

                        winner = ("No hand reset" if intact[3]<reset[3]
                                  else "Supporter reset" if intact[3]>reset[3]
                                  else "Tie")
                        overall[winner] += 1
                        by_prize[(r,winner)] += 1
                        for route in (1,2):
                            route_winner = (
                                "No hand reset" if intact[route]<reset[route]
                                else "Supporter reset" if intact[route]>reset[route]
                                else "Tie"
                            )
                            by_public_route[(r,route,route_winner)] += 1

                        if B == T == 4 and tutor == "computer_search" and d == 1:
                            examples.append({
                                "prizes_awarded":r,
                                "hand_preserved_percent":round(float(intact[3])*100,8),
                                "best_eligible_reset":response,
                                "reset_percent":round(float(reset[3])*100,8),
                                "lower_access_action":winner
                            })

    assert sum(overall.values()) == 1152
    assert overall == Counter({"No hand reset":945,"Supporter reset":207})
    assert by_prize == Counter({
        (0,"No hand reset"):384,
        (1,"No hand reset"):374,(1,"Supporter reset"):10,
        (2,"No hand reset"):187,(2,"Supporter reset"):197
    })
    assert by_public_route == Counter({
        (0,1,"No hand reset"):384,
        (0,2,"No hand reset"):384,
        (1,1,"No hand reset"):323,
        (1,1,"Supporter reset"):61,
        (1,2,"No hand reset"):384,
        (2,1,"No hand reset"):99,
        (2,1,"Supporter reset"):285,
        (2,2,"No hand reset"):384
    })

    assert exact_prize_take(4,4,1,"computer_search",1)[3] == Fraction(
        59977412074,5327705077695
    )
    assert exact_prize_take(4,4,1,"computer_search",2)[3] == Fraction(
        447419776261,26638525388475
    )
    return {
        "total_configurations":sum(overall.values()),
        "best_response_counts":dict(overall),
        "by_prize":{f"r={r}, {winner}":n for (r,winner),n in sorted(by_prize.items())},
        "by_public_first_packet_route":{
            f"r={r}, {'direct' if route==1 else 'paid-tutor'}, {winner}":n
            for (r,route,winner),n in sorted(by_public_route.items())
        },
        "worked_example":examples
    }


if __name__ == "__main__":
    print(json.dumps(run(),indent=2))
