"""Exact T3 draw frontier validation."""
from fractions import Fraction
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
from beheeyem_multi_draw_packet import exact_multi_draw_packet
from beheeyem_recycle_packet_probability import exact_packet_outcomes

rows = []
for b, t in ((1, 1), (1, 4), (2, 2), (3, 3), (4, 4)):
    prev = Fraction(0)
    for draws in range(7):
        first, second = exact_multi_draw_packet(b, t, draws)
        assert first == exact_packet_outcomes(b, t).first_attack
        assert prev <= second <= first
        assert exact_multi_draw_packet(t, b, draws) == (first, second)
        if draws == 1:
            assert second == exact_packet_outcomes(b, t).two_attacks_recycled
        prev = second
        rows.append({"beheeyem": b, "tae": t, "draws": draws,
                     "first_percent": round(float(first)*100, 7),
                     "two_percent": round(float(second)*100, 7)})
assert exact_multi_draw_packet(1, 1, 1)[1] == 0
assert exact_multi_draw_packet(1, 1, 2) == (
    Fraction(5, 532), Fraction(5, 600096))
expected = [0.1232245, 0.3163517, 0.6082673,
            0.9798645, 1.4142591, 1.8966009]
assert [round(float(exact_multi_draw_packet(4, 4, d)[1])*100, 7)
        for d in range(6)] == expected
print(json.dumps({"rows": rows, "prizes": 6}, indent=2))
