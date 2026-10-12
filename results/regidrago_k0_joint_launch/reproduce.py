"""Nonanticipative first-search Regidrago check against published oracle."""

from fractions import Fraction
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from regidrago_joint_launch import analyze, candidates
from regidrago_joint_launch_k0 import analyze_k0, first_action_succeeds


def verify():
    for safe in (0, 10):
        builds = candidates(safe)
        for name in ("published", "+Dragapult -VIP"):
            build = builds[name]
            result = analyze_k0(build)
            perfect = analyze(build)["joint_any"]
            assert result["clairvoyant_joint"] == perfect
            assert 0 <= result["k0_joint"] <= perfect
            assert result["information_gap"] == perfect - result["k0_joint"]
            assert sum(
                result[key] for key in result if key.startswith("first_")
            ) <= 1
            print(
                f"D={safe} {name}: K0={100 * float(result['k0_joint']):.9f}%",
                f"full={100 * float(perfect):.9f}%",
                f"gap={100 * float(result['information_gap']):.9f}%",
                flush=True,
            )

    # A first search is a real action with a physical payment; no Quick
    # Ball or Treasure can be played without a DP or authorized safe card.
    h = (0, 1, 0, 0, 1, 1, 0, 0, 5)
    for action in ("qb_dp", "mt_dp", "qb_safe", "mt_safe"):
        try:
            first_action_succeeds(action, h, rv_deck=1, dp_deck=1)
        except ValueError:
            pass
        else:
            raise AssertionError("search without a real discard was accepted")
    print("K0 Regidrago prize-information policy regressions passed")


if __name__ == "__main__":
    verify()
