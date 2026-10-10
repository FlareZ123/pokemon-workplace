"""Physical first-turn QB/Crobat/Dedenne access certificate.

Full joint opening, Prize, later-draw and post-Quick-Ball shuffle regression.
"""
from __future__ import annotations

from fractions import Fraction
from itertools import combinations
from math import comb
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from bench_quickball_crobat_incidence import analyze as incidence
from bench_quickball_crobat_dedenne import analyze as continuation


def exact_certificate(*, deck_size: int = 60, opening_size: int = 7,
                      prize_count: int = 6, later_draws: int = 1,
                      quick_balls: int = 4, discardable: int = 4,
                      other_basics: int = 4):
    if later_draws != 1:
        raise ValueError("this certificate supports exactly one normal turn draw")
    hand_size = opening_size - 1 + later_draws
    materials = incidence(deck_size=deck_size, opening_size=opening_size,
                          prize_count=prize_count, later_draws=later_draws,
                          quick_balls=quick_balls, discardable=discardable,
                          other_basics=other_basics)
    c_remaining = deck_size - opening_size - prize_count - later_draws - 1
    cont = continuation(hand_size=hand_size, prize_count=prize_count,
                        natural_draws=later_draws, other_live_cards=c_remaining)
    return materials, cont, materials.material_given_valid * cont.access_gain


def direct_small_deck_oracle(*, deck_size: int = 18, opening_size: int = 4,
                             prize_count: int = 2, later_draws: int = 1,
                             quick_balls: int = 2, discardable: int = 2,
                             other_basics: int = 2):
    """Enumerate physical card positions and QB's independent shuffle."""
    groups = [("D", 1), ("C", 1), ("K", 1), ("Q", quick_balls),
              ("F", discardable), ("O", other_basics)]
    cards = [(kind, i) for kind, total in groups for i in range(total)]
    cards.extend(("X", i) for i in range(deck_size-len(cards)))
    all_openings = comb(deck_size, opening_size)
    accepted = 0
    eligible = 0
    d_expected = Fraction(0)
    staged_expected = Fraction(0)
    per_open = comb(deck_size - opening_size, prize_count) * comb(
        deck_size - opening_size - prize_count, later_draws)
    nlive = deck_size - opening_size - prize_count - later_draws
    a = max(0, 8 - (opening_size - 1 + later_draws))
    assert nlive - 1 >= a + 6

    for op in combinations(cards, opening_size):
        opening_set = set(op)
        present = [kind for kind, _ in op]
        if not any(x in ("D", "C", "O") for x in present):
            continue
        accepted += 1
        if ("D" not in present or "O" not in present or "Q" not in present
                or "F" not in present or "C" in present or "K" in present):
            continue
        after = [c for c in cards if c not in opening_set]
        for p in combinations(after, prize_count):
            pset = set(p)
            afterp = [c for c in after if c not in pset]
            for ds in combinations(afterp, later_draws):
                drawn = set(ds)
                if ("C", 0) in pset or ("C", 0) in drawn:
                    continue
                eligible += 1
                if ("K", 0) in drawn:
                    d_expected += 1
                    staged_expected += 1
                elif ("K", 0) in pset:
                    pass
                else:
                    d_expected += Fraction(sum(i < 6 for i in range(nlive)), nlive)
                    staged_expected += Fraction(sum(i < a+6 for i in range(nlive-1)), nlive-1)

    denominator = accepted * per_open
    return (Fraction(accepted, all_openings),
            Fraction(eligible, denominator),
            d_expected / denominator,
            staged_expected / denominator)


def validate() -> None:
    small = dict(deck_size=18, opening_size=4, prize_count=2,
                 later_draws=1, quick_balls=2, discardable=2,
                 other_basics=2)
    x, continuation_result, delta = exact_certificate(**small)
    physical = direct_small_deck_oracle(**small)
    assert x.valid_open == physical[0]
    assert x.material_given_valid == physical[1]
    assert x.material_given_valid * continuation_result.dedenne_success == physical[2]
    assert x.material_given_valid * continuation_result.qb_staged_success == physical[3]
    assert physical[3]-physical[2] == delta

    m, c, benefit = exact_certificate()
    assert c.hand_size == 7
    assert c.crobat_draw == 1
    assert c.access_gain == Fraction(13, 598)
    assert benefit == Fraction(3395, 30785103)
    print("Independent 18-card labeled opening+Prize+draw+shuffle K-placement oracle passed.")
    print(f"60-card eligible material | accepted opener: {float(m.material_given_valid):.9%}")
    print(f"Conditioned Dedenne success: {float(c.dedenne_success):.9%}")
    print(f"Conditioned QB staged success: {float(c.qb_staged_success):.9%}")
    print(f"Conditioned access gain: {float(c.access_gain):.9%}")
    print(f"Weighted material-path contribution: {float(benefit):.9%}")


if __name__ == "__main__":
    validate()
