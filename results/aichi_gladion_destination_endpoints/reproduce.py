from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from aichi_gladion_destination_endpoints import simulate

result = simulate(20_000, seed=20261007)

expected = {
    "baseline": {
        "core": 14227,
        "pidgeot": 12134,
        "stoutland": 9960,
        "dual": 8584,
        "item": 7492,
        "item_pidgeot": 4829,
        "item_stoutland": 4016,
    },
    "prize_to_hand": {
        "core": 14289,
        "pidgeot": 12176,
        "stoutland": 10002,
        "dual": 8619,
        "item": 7520,
        "item_pidgeot": 4844,
        "item_stoutland": 4032,
    },
    "prize_to_deck": {
        "core": 14227,
        "pidgeot": 12140,
        "stoutland": 9963,
        "dual": 8591,
        "item": 7493,
        "item_pidgeot": 4831,
        "item_stoutland": 4017,
    },
    "either_destination": {
        "core": 14289,
        "pidgeot": 12179,
        "stoutland": 10004,
        "dual": 8623,
        "item": 7521,
        "item_pidgeot": 4846,
        "item_stoutland": 4033,
    },
}
for field, values in expected.items():
    actual = getattr(result, field)
    if actual != values:
        raise AssertionError(f"{field}: {actual} != {values}")

print(result)
print("Aichi Gladion destination endpoint regression passed")
