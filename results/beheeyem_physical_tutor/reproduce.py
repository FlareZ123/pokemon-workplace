"""Reproduce the exact one-physical-tutor Beheeyem recurrence frontier."""
from fractions import Fraction
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
from beheeyem_multi_draw_packet import exact_multi_draw_packet
from beheeyem_physical_tutor import MODES, exact_physical_tutor

samples = []
for B in range(1, 5):
    for T in range(1, 5):
        for mode in MODES:
            previous = Fraction(0)
            for d in range(6):
                first, blind, assisted, ideal = exact_physical_tutor(B, T, d, mode)
                assert (first, blind) == exact_multi_draw_packet(B, T, d)
                assert blind <= assisted <= ideal <= first
                assert assisted >= previous
                previous = assisted
                if (B, T) in ((1, 1), (1, 4), (4, 4)) and d in (1, 3, 5):
                    samples.append({
                        "beheeyem": B, "tae": T, "draws": d, "tutor": mode,
                        "blind_percent": round(float(blind) * 100, 7),
                        "tutored_percent": round(float(assisted) * 100, 7),
                        "ideal_percent": round(float(ideal) * 100, 7),
                    })

for B, T in ((1, 1), (1, 4), (2, 3), (4, 4)):
    for d in (0, 1, 3, 5):
        assert (
            exact_physical_tutor(B, T, d, "ultra_ball")
            == exact_physical_tutor(T, B, d, "guzma_hala")
        )
        assert (
            exact_physical_tutor(B, T, d, "mysterious_treasure")[2]
            >= exact_physical_tutor(B, T, d, "ultra_ball")[2]
        )

assert exact_physical_tutor(4, 4, 1, "computer_search")[2] == Fraction(1633205, 264385836)
assert exact_physical_tutor(1, 1, 1, "computer_search")[2] > 0
assert exact_physical_tutor(1, 1, 1, "computer_search")[1] == 0
for mode in MODES:
    first, blind, assisted, ideal = exact_physical_tutor(4, 4, 48, mode)
    assert first == blind == assisted == ideal

print(json.dumps({"checked": "16 copy-pairs x 4 tutor modes x 6 draw budgets",
                  "examples": samples}, indent=2))
