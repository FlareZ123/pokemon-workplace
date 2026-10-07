"""Regression for the Aichi Prize-Supporter information result."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from aichi_prize_supporter_information import simulate

result = simulate(100_000, seed=20261007)

expected = {
    "baseline": 70_709,
    "gladion_state_aware": 71_006,
    "peonia_blind": 70_938,
    "both_state_aware": 71_212,
    "gladion_tag_k1": 70_721,
    "gladion_tag_or_fan_k1": 70_776,
    "gladion_added_via_stellar": 13,
}
for field, value in expected.items():
    actual = getattr(result, field)
    if actual != value:
        raise AssertionError(f"{field}: {actual} != {value}")

expected_recovered = {
    "Technical Machine: Evolution": 124,
    "Jet Energy": 108,
    "Artazon": 28,
    "Bunnelby": 28,
    "Fan Rotom": 9,
}
if result.gladion_added_by_card != expected_recovered:
    raise AssertionError(result.gladion_added_by_card)

print(result)
print("Aichi Prize-Supporter information regression passed")
