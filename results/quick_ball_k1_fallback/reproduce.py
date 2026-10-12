"""SFT: Search-deck-information Quick Ball fallback against labeled cards."""
from __future__ import annotations

from math import isclose
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

from quick_ball_pre_draw_option import opening_option_probability
from results.quick_ball_pre_draw_option.reproduce import oracle


def main() -> None:
    toys = (
        dict(n=11, p=2, h=4, s=1, a=1, c=2, g=1, q=2, d=2),
        dict(n=12, p=2, h=4, s=2, a=1, c=2, g=2, q=2, d=1),
    )
    for toy in toys:
        exact = opening_option_probability(
            toy["n"], toy["p"], opening_hand_size=toy["h"],
            other_starters=toy["s"], attacker_starter_copies=toy["a"],
            critical_nonstarter=toy["c"], rescue_nonstarter=toy["g"],
            quick_ball_copies=toy["q"], disposable_nonstarter=toy["d"],
            allow_search_fallback=True,
        )
        physical = oracle(**toy, allow_search_fallback=True)
        computed = (
            exact.wait_joint, exact.eager_attacker_joint,
            exact.eager_rescue_joint,
        )
        assert all(
            isclose(a, b, abs_tol=5e-12)
            for a, b in zip(computed, physical)
        ), (toy, computed, physical)
        print("Physical K1 oracle passed:", toy, physical)

    print("Disposable | K0 rescue eager | K1 rescue eager | K1 gain pp")
    for disposable in (4, 8, 12, 16, 20, 24):
        deck = dict(
            other_starters=10, attacker_starter_copies=1,
            critical_nonstarter=4, rescue_nonstarter=2,
            quick_ball_copies=4, disposable_nonstarter=disposable,
        )
        k0 = opening_option_probability(60, 6, **deck)
        k1 = opening_option_probability(
            60, 6, allow_search_fallback=True, **deck
        )
        assert isclose(k0.wait_joint, k1.wait_joint, abs_tol=1e-12)
        assert isclose(
            k0.eager_attacker_joint, k1.eager_attacker_joint,
            abs_tol=1e-12,
        )
        assert k1.eager_rescue_joint >= k0.eager_rescue_joint
        if disposable == 12:
            assert isclose(
                100 * (
                    k1.eager_rescue_joint - k0.eager_rescue_joint
                ), 0.061518918131808764, abs_tol=2e-10
            )
        print(
            disposable,
            f"{100*k0.eager_rescue_joint:.6f}%",
            f"{100*k1.eager_rescue_joint:.6f}%",
            f"{100*(k1.eager_rescue_joint-k0.eager_rescue_joint):.6f}",
        )


if __name__ == "__main__":
    main()
