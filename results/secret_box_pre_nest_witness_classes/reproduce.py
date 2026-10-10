"""SFT: enumerate every D20/I2 prior-Nest order advantage hand class."""
from __future__ import annotations

from fractions import Fraction
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))

from secret_box_gnh_tool_pipeline import D, I, KINDS, counts
from secret_box_k0_bench_bootstrap import counted_visible_hands
from secret_box_pre_nest_information import optimal_pre_nest_choice


def advantage_classes(deck, *, basic_count=12, prize_count=6):
    weighted, denominator = counted_visible_hands(deck, basics=basic_count)
    out = []
    eligible_weight = 0
    total_advantage = Fraction(0)
    for (hand, visible_basics), weight in weighted.items():
        if visible_basics != 1 or hand[I] == 0:
            continue
        eligible_weight += weight
        unseen = tuple(total - held for total, held in zip(deck, hand))
        result = optimal_pre_nest_choice(
            hand, unseen, visible_basics=visible_basics,
            unseen_basics=basic_count - visible_basics,
            prizes=prize_count,
        )
        assert result.box_first_k0 <= result.optimal_first_action_success
        assert result.optimal_first_action_success <= result.informational_upper_bound
        contribution = Fraction(weight, denominator) * result.gain_from_nest_first
        total_advantage += contribution
        if contribution:
            assert hand[D] < 3
            out.append((hand, weight, result, contribution))
    out.sort(key=lambda t: t[3], reverse=True)
    return out, Fraction(eligible_weight, denominator), total_advantage, denominator


def main():
    deck = counts(D=20, I=2, A=2, B=1, G=2, S=2, E=1, P=29)
    assert sum(deck) == 59
    classes, eligible_mass, advantage, denominator = advantage_classes(deck)
    assert len(classes) == 4
    assert abs(float(advantage)*100 - 0.0077586397) < 1e-9
    total_beneficial_mass = sum((Fraction(w, denominator) for _, w, _, _ in classes), Fraction(0))
    assert abs(float(total_beneficial_mass)*100 - 0.126349) < 0.000001
    print("D20 / I2 full accepted opening, valid Basic plus one natural draw")
    print("eligible Nest-in-hand, one-Basic mass:", eligible_mass)
    print("beneficial hand mass:", total_beneficial_mass)
    print("aggregate sequencing gain fraction:", advantage)
    print("aggregate sequencing gain pp:", f"{float(advantage)*100:.12f}")
    print("Class count:", len(classes))
    for hand, weight, result, contribution in classes:
        desc = ", ".join(f"{name}{n}" for name, n in zip(KINDS, hand) if n)
        print("\nHAND", desc)
        print("visible-class mass", Fraction(weight, denominator), f"{100*weight/denominator:.9f}%")
        print("Box-first", result.box_first_k0, f"{float(result.box_first_k0):.9%}")
        print("Nest-first", result.nest_first_k0, f"{float(result.nest_first_k0):.9%}")
        print("Conditional gain", result.gain_from_nest_first, f"{float(result.gain_from_nest_first)*100:.9f} pp")
        print("Aggregate contribution", contribution, f"{float(contribution)*100:.12f} pp")
    assert sum((row[3] for row in classes), Fraction(0)) == advantage
    print("\nALL TESTS PASSED")


if __name__ == "__main__":
    main()
