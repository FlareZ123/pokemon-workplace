"""Independent exact and exhaustive validation of 60-card-like search signals."""

from fractions import Fraction
from itertools import combinations
from math import comb
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from expanded_singleton_reveal_hypergeometric import (
    closed_form_reveal_probabilities,
    exact_membership_enumeration,
)


def exhaustive(pool_size: int, prizes: int):
    """Enumerate all equally likely physical Prize subsets for small pools."""
    ids = ("A", "X", "Y") + tuple(
        f"F{i}" for i in range(pool_size - 3)
    )
    outcomes = []
    for prize_set in combinations(ids, prizes):
        unavailable = frozenset(prize_set)
        selected = (
            "X" if "A" in unavailable and "X" not in unavailable
            else "Y" if "Y" not in unavailable
            else "X" if "X" not in unavailable
            else None
        )
        outcomes.append(("A" in unavailable, selected))
    assert len(outcomes) == comb(pool_size, prizes)
    accepted = [row for row in outcomes if row[1] is not None]
    selected_x = [row for row in accepted if row[1] == "X"]
    selected_y = [row for row in accepted if row[1] == "Y"]
    event = lambda rows: Fraction(sum(a for a, _ in rows), len(rows))
    return (
        Fraction(len(accepted), len(outcomes)),
        Fraction(len(selected_x), len(accepted)),
        Fraction(len(selected_y), len(accepted)),
        event(accepted),
        event(selected_x),
        event(selected_y),
    )


# Three independent versions: fully labeled small-deck brute force,
# eight physical singleton-Prize membership events, and symbolic formulas.
for u in range(5, 66):
    for p in range(2, u - 1):
        symbolic = closed_form_reveal_probabilities(u, p)
        hypergeom = exact_membership_enumeration(u, p)
        assert symbolic == hypergeom, (u, p, symbolic, hypergeom)
        if u <= 9:
            assert exhaustive(u, p) == (
                symbolic.search_success,
                symbolic.probability_x_given_success,
                symbolic.probability_y_given_success,
                symbolic.a_prized_given_success,
                symbolic.a_prized_given_x,
                symbolic.a_prized_given_y,
            )

# Reproduce the earlier tiny six-card print-reveal signal exactly.
small = closed_form_reveal_probabilities(6, 2)
assert small.search_success == Fraction(14, 15)
assert small.probability_x_given_success == Fraction(1, 2)
assert small.a_prized_given_success == Fraction(5, 14)
assert small.a_prized_given_x == Fraction(4, 7)
assert small.a_prized_given_y == Fraction(1, 7)
assert small.print_information_decision_gain == Fraction(1, 14)

# Opening-like substrate: 60 total, eight cards in hand, 52 unknown
# deck-plus-Prize cards, six hidden Prizes. Three singleton identities are
# assumed in the unknown pool, so their earlier opening-hand probability
# has been conditioned away.
benchmark = closed_form_reveal_probabilities(52, 6)
assert benchmark.search_success == Fraction(437, 442)
assert benchmark.probability_x_given_success == Fraction(1, 5)
assert benchmark.probability_y_given_success == Fraction(4, 5)
assert benchmark.a_prized_given_success == Fraction(11, 95)
assert benchmark.a_prized_given_x == Fraction(10, 19)
assert benchmark.a_prized_given_y == Fraction(1, 76)
assert benchmark.name_only_correct_prediction == Fraction(84, 95)
assert benchmark.print_aware_correct_prediction == Fraction(17, 19)
assert benchmark.print_information_decision_gain == Fraction(1, 95)

for u in range(6, 66):
    for p in range(2, (u - 1) // 2 + 1):
        outcome = closed_form_reveal_probabilities(u, p)
        # The old print is selected more often when A is Prized than
        # when A is available. Its conditional Prize posterior is > 1/2.
        assert outcome.a_prized_given_x == Fraction(u - 2, 2 * u - p - 3)
        assert outcome.a_prized_given_x > Fraction(1, 2)
        assert outcome.a_prized_given_y <= Fraction(1, 2)
        assert outcome.a_prized_given_success <= Fraction(1, 2)
        # Under the equal-reward binary guessing game, only choosing
        # "Prized" after X changes the name-only default response.
        gain = Fraction(
            p * (p - 1) * (u - p),
            (u - 2) * (u * (u - 1) - p * (p - 1)),
        )
        assert outcome.print_information_decision_gain == gain

print("symbolic hypergeometric identities match 1,830+ membership cases")
print("physical Prize subsets independently agree for U <= 9")
print("U=52, P=6: search success=437/442; X reveal rate=1/5")
print("P(A Prized): name=11/95, X=10/19, Y=1/76")
print("binary response accuracy: name=84/95; print=17/19; gain=1/95")
