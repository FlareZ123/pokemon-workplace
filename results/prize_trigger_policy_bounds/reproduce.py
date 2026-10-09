"""Exact rational regression for policy-box Prize-trigger inference."""

from fractions import Fraction
from itertools import product
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from observer_top_prize_beliefs import ObserverTopPrizeBeliefs
from pending_prize_identity_belief import stage_one_pending_prize_for_observers
from prize_top_swap_belief import TopPrizeJointBelief
from prize_trigger_policy_bounds import bound_decline_posterior


WORLDS = (
    ("S", "C", Fraction(2, 5)),
    ("F", "C", Fraction(1, 10)),
    ("S", "O", Fraction(1, 10)),
    ("F", "O", Fraction(2, 5)),
)


def make_belief():
    prior = TopPrizeJointBelief(
        ("S", "F", "C", "O"), (False,),
        tuple(((top, (card,)), float(p)) for top, card, p in WORLDS),
    )
    observers = ObserverTopPrizeBeliefs(
        (("actor", prior), ("opponent", prior)),
    )
    return stage_one_pending_prize_for_observers(
        observers, position=0, visible_groups={"actor": "C"},
    ).belief_for("opponent")


def exact_probability(location, group, c_use, o_use):
    use = {"C": c_use, "O": o_use}
    worlds = [
        (top, card, p * (1 - use[card]))
        for top, card, p in WORLDS
    ]
    denominator = sum(m for _top, _card, m in worlds)
    return sum(
        m for top, card, m in worlds
        if (top if location == "top" else card) == group
    ) / denominator


def close(actual, expected):
    assert abs(actual - float(expected)) < 1e-12, (actual, expected)


def main():
    state = make_belief()
    bounds = {"C": (0.4, 0.8), "O": (0.0, 0.0)}
    chansey = bound_decline_posterior(
        state, use_probability_intervals=bounds,
        target_location="pending", target_group="C",
    )
    top = bound_decline_posterior(
        state, use_probability_intervals=bounds,
        target_location="top", target_group="S",
    )
    close(chansey.lower, Fraction(1, 6))
    close(chansey.upper, Fraction(3, 8))
    close(top.lower, Fraction(3, 10))
    close(top.upper, Fraction(17, 40))
    assert dict(chansey.lower_policy) == {"C": 0.8, "O": 0.0}

    broad = {"C": (0.4, 0.8), "O": (0.0, 0.4)}
    for location, group in (("pending", "C"), ("top", "S")):
        calculated = bound_decline_posterior(
            state, use_probability_intervals=broad,
            target_location=location, target_group=group,
        )
        for a, b in product(range(5), repeat=2):
            c = Fraction(2, 5) + Fraction(a, 10)
            o = Fraction(b, 10)
            actual = float(exact_probability(location, group, c, o))
            assert calculated.lower - 1e-12 <= actual
            assert actual <= calculated.upper + 1e-12

    blocked = bound_decline_posterior(
        state,
        use_probability_intervals={"C": (0.0, 0.0), "O": (0.0, 0.0)},
        target_location="pending", target_group="C",
    )
    close(blocked.lower, Fraction(1, 2))
    close(blocked.upper, Fraction(1, 2))

    invalid = (
        {"C": (1.0, 1.0), "O": (1.0, 1.0)},
        {"C": (0.2, 1.1), "O": (0.0, 0.0)},
        {"C": (0.4, 0.8)},
    )
    for policy in invalid:
        try:
            bound_decline_posterior(
                state, use_probability_intervals=policy,
                target_location="pending", target_group="C",
            )
        except ValueError:
            pass
        else:
            raise AssertionError(f"invalid policy accepted: {policy}")

    print("Policy-interval bounds regressions passed")
    print("P(Chansey|decline) in [1/6,3/8]")
    print("P(top S|decline) in [3/10,17/40]")


if __name__ == "__main__":
    main()
