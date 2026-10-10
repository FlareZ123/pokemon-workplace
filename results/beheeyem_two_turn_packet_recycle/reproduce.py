"""Reproduce exact two-turn Mysterious Noise packet supply and counterfactual."""
from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
from beheeyem_recycle_packet_probability import exact_packet_outcomes


def main() -> None:
    matrix = []
    for b in range(1, 5):
        for tae in range(1, 5):
            out = exact_packet_outcomes(b, tae)
            symmetric = exact_packet_outcomes(tae, b)
            assert out == symmetric
            assert 0 <= out.two_attacks_discard_counterfactual <= out.two_attacks_recycled <= out.first_attack
            if b == tae == 1:
                assert out.two_attacks_recycled == 0
            if b == 1 and tae > 1:
                assert out.two_attacks_discard_counterfactual == 0
                assert out.two_attacks_recycled > 0
            matrix.append({
                "beheeyem": b,
                "tae": tae,
                "t2_attack_percent": round(float(out.first_attack) * 100, 6),
                "t2_and_t3_recycled_percent": round(float(out.two_attacks_recycled) * 100, 6),
                "t2_and_t3_discard_percent": round(float(out.two_attacks_discard_counterfactual) * 100, 6),
            })

    both_four = exact_packet_outcomes(4, 4)
    assert both_four.first_attack == Fraction(155611, 1296009)
    assert both_four.two_attacks_recycled == Fraction(836389, 264385836)
    assert both_four.two_attacks_discard_counterfactual == Fraction(60091, 22032153)
    print(json.dumps({
        "fixed_ready_board": "two mature Elgyem and one anchor Basic",
        "other_cards_in_T2_hand": 6,
        "prizes": 6,
        "T3_natural_draws": 1,
        "two_attacks_given_T2_attack_percent": round(
            100 * float(both_four.two_attacks_recycled / both_four.first_attack), 6
        ),
        "recycling_gain_relative_percent": round(
            100 * float(
                both_four.two_attacks_recycled /
                both_four.two_attacks_discard_counterfactual - 1
            ), 6
        ),
        "rows": matrix,
    }, indent=2))


if __name__ == "__main__":
    main()
