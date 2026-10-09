"""Exact policy-prior sensitivity of print observation decision value."""

from fractions import Fraction
from math import isclose
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from latent_search_policy_belief import PolicyHypothesis, enumerate_policy_search_worlds
from observation_policy_envelope import BeliefState, observation_policy_envelope
from revealed_print_information import SearchCard, binary_entropy

OLD = "xy1-42"
NEW = "swsh7-49"
CARDS = tuple(
    SearchCard(identifier, "Pikachu" if identifier in {OLD, NEW} else identifier)
    for identifier in ("A", OLD, NEW, "F1", "F2", "F3")
)


def forward(prizes: frozenset[str], deck: frozenset[str]) -> str | None:
    if "A" in prizes and OLD in deck:
        return OLD
    if NEW in deck:
        return NEW
    return OLD if OLD in deck else None


def reverse(prizes: frozenset[str], deck: frozenset[str]) -> str | None:
    if "A" in prizes and NEW in deck:
        return NEW
    if OLD in deck:
        return OLD
    return NEW if NEW in deck else None


def expect_accuracy(posterior, reveal_print: bool) -> Fraction:
    rows = tuple(
        BeliefState(
            str(index),
            probability,
            world.selected_print_id if reveal_print else world.selected_name,
            (
                ("predict_prized", Fraction("A" in world.ordered_prize_ids)),
                ("predict_unprized", Fraction("A" not in world.ordered_prize_ids)),
            ),
        )
        for index, (world, probability) in enumerate(posterior.masses)
    )
    return observation_policy_envelope(rows).expected_payoff


def exact_gain(alpha: Fraction) -> Fraction:
    """Closed form of the additional correct-prediction probability."""
    return max(
        Fraction(),
        (6 * alpha - 5) / 14,
        (1 - 6 * alpha) / 14,
    )


for index in range(61):
    alpha = Fraction(index, 60)
    joint = enumerate_policy_search_worlds(
        CARDS, 2,
        (
            PolicyHypothesis("forward", alpha, forward),
            PolicyHypothesis("reverse", 1 - alpha, reverse),
        ),
    )
    old = joint.print_reveal(OLD)
    new = joint.print_reveal(NEW)
    p_old = old.probability(lambda world: "A" in world.ordered_prize_ids)
    p_new = new.probability(lambda world: "A" in world.ordered_prize_ids)
    assert p_old == (1 + 3 * alpha) / 7
    assert p_new == (4 - 3 * alpha) / 7
    assert joint.probability(
        lambda world: "A" in world.ordered_prize_ids
    ) == Fraction(5, 14)
    assert joint.probability(
        lambda world: world.selected_print_id == OLD
    ) == Fraction(1, 2)
    assert joint.probability(
        lambda world: world.selected_print_id == NEW
    ) == Fraction(1, 2)

    by_name = expect_accuracy(joint, False)
    by_print = expect_accuracy(joint, True)
    assert by_name == Fraction(9, 14)
    assert by_print - by_name == exact_gain(alpha)
    assert (by_print == by_name) == (
        Fraction(1, 6) <= alpha <= Fraction(5, 6)
    )

# With alpha=3/4, a print disclosure has real Shannon information, but the
# optimal zero-one response never changes and so has exactly zero utility.
alpha = Fraction(3, 4)
worlds = enumerate_policy_search_worlds(
    CARDS, 2,
    (
        PolicyHypothesis("forward", alpha, forward),
        PolicyHypothesis("reverse", 1 - alpha, reverse),
    ),
)
prized = lambda row: "A" in row.ordered_prize_ids
p_old = worlds.print_reveal(OLD).probability(prized)
p_new = worlds.print_reveal(NEW).probability(prized)
mutual_information = (
    binary_entropy(Fraction(5, 14))
    - (binary_entropy(p_old) + binary_entropy(p_new)) / 2
)
assert (p_old, p_new) == (Fraction(13, 28), Fraction(1, 4))
assert isclose(
    mutual_information, 0.03648863666158375,
    rel_tol=0.0, abs_tol=1e-12,
)
assert exact_gain(alpha) == 0

# Tight boundary probes: arbitrarily small movement outside the plateau yields
# positive decision gain, with the exact rational slope from the formula.
for boundary, direction in (
    (Fraction(1, 6), -1),
    (Fraction(5, 6), 1),
):
    epsilon = Fraction(1, 6000)
    inside = boundary - direction * epsilon
    outside = boundary + direction * epsilon
    assert exact_gain(boundary) == 0
    assert exact_gain(inside) == 0
    assert exact_gain(outside) == Fraction(3, 7000)

print("61 rational opponent-policy priors match exact threshold formula")
print("print-observation decision value=0 for 1/6 <= prior <= 5/6")
print("gain outside plateau = max(0,(6a-5)/14,(1-6a)/14)")
print("at prior=3/4: 0.036488636662 bits about A; zero decision gain")
