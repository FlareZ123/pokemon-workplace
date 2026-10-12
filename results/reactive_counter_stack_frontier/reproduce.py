"""Source-verified exhaustive static reaction-stack regression."""
from __future__ import annotations
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from reactive_counter_stack_frontier import Stack, pareto, source_validate, study

def run() -> dict:
    source_validate(ROOT / "resources")
    assert Stack(4, 4, "deluxe").counters() == 29
    assert Stack(4, 4, "punk").counters() == 21
    assert Stack(4, 4, "deluxe").earliest_outlaw_leg_turn() == 6
    assert Stack(4, 4, "deluxe").counters(abilities=False) == 20
    assert Stack(4, 4, "deluxe").counters(tools=False) == 17
    assert Stack(4, 4, "deluxe").counters(abilities=False, tools=False) == 8
    assert {(s.spiritomb, s.spiky) for s in pareto(28, "deluxe")} == {(3, 4)}
    assert {(s.spiritomb, s.spiky) for s in pareto(29, "deluxe")} == {(4, 4)}
    assert not pareto(30, "deluxe")
    assert not pareto(22, "punk")
    for tool in ("none", "punk", "deluxe"):
        for threshold in range(31):
            result = pareto(threshold, tool)
            feasible = [
                (b, e) for b in range(5) for e in range(5)
                if Stack(b, e, tool).counters() >= threshold
            ]
            expected = {
                (b, e) for b, e in feasible
                if not any((x <= b and y <= e) and (x, y) != (b, e)
                           for x, y in feasible)
            }
            assert {(s.spiritomb, s.spiky) for s in result} == expected, (tool, threshold)
    return study()

if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
