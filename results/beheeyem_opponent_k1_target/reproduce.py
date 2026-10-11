"""Check exact K1 Prize-state response policies."""

from pathlib import Path
from fractions import Fraction
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
from beheeyem_opponent_k1_target import prize_x_posterior, own_x_after_reset_k1, evaluate_k1_own_target_policy
from beheeyem_opponent_self_target import own_target_after_reset, evaluate_own_target_policy

for s in range(3):
    for held in range(5):
        assert sum(prize_x_posterior(held, s, z) for z in range(5)) == 1
        for quota in (3, 4, 6):
            assert own_target_after_reset(held, s, quota) == sum(prize_x_posterior(held, s, z) * own_x_after_reset_k1(z, s, quota) for z in range(5))

for r, q in ((0,6), (1,6), (1,5), (2,6), (2,5), (2,4)):
    for weight in (0, 1, 10, 100, 1000000):
        for visible in (False, True):
            k1 = evaluate_k1_own_target_policy(4, 4, 1, "computer_search", r, q, Fraction(weight), visible)
            k0 = evaluate_own_target_policy(4, 4, 1, "computer_search", r, q, Fraction(weight), visible)
            assert k1["k1_utility_gain"] >= 0
            if weight == 0:
                assert k1["own_target_ready"] >= k0["own_target_ready"]
            if weight == 1000000:
                assert k1["beheeyem_joint_packet"] == k0["beheeyem_joint_packet"]
            print(f"r={r} q={q} weight={weight} route={visible}: X K0={100*float(k0['own_target_ready']):.6f}% K1={100*float(k1['own_target_ready']):.6f}%; packet K0={100*float(k0['beheeyem_joint_packet']):.6f}% K1={100*float(k1['beheeyem_joint_packet']):.6f}%; gain={float(k1['k1_utility_gain']):.9f}")

print("K1 validation passed: 60 scenario policies")
