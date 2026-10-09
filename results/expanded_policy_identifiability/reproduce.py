"""Scale-dependent print-policy identifiability for a 52-card unknown pool."""

from fractions import Fraction
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from expanded_policy_identifiability import ExpandedPolicyBelief
from expanded_singleton_reveal_hypergeometric import (
    closed_form_reveal_probabilities,
)

toy = closed_form_reveal_probabilities(6, 2)
realistic = closed_form_reveal_probabilities(52, 6)

small = ExpandedPolicyBelief(Fraction(1, 2), toy)
assert small.print_probability("X") == Fraction(1, 2)
assert small.print_probability("Y") == Fraction(1, 2)
assert small.x_action_threshold() == Fraction(5, 6)
assert small.updated_by_print("X").forward_prior == Fraction(1, 2)
assert small.updated_by_print("Y").forward_prior == Fraction(1, 2)
assert small.a_prized_posterior("X") == Fraction(5, 14)
assert small.a_prized_posterior("Y") == Fraction(5, 14)

large = ExpandedPolicyBelief(Fraction(1, 2), realistic)
assert realistic.probability_x_given_success == Fraction(1, 5)
assert large.print_probability("X") == Fraction(1, 2)
assert large.print_probability("Y") == Fraction(1, 2)
assert large.a_prized_posterior("X") == Fraction(11, 95)
assert large.a_prized_posterior("Y") == Fraction(11, 95)
assert large.print_information_value() == 0
assert large.x_action_threshold() == Fraction(74, 75)
assert large.updated_by_print("X").forward_prior == Fraction(1, 5)
assert large.updated_by_print("Y").forward_prior == Fraction(4, 5)

# If the player consistently uses the forward policy, Y is four times as
# likely as X. Multiple independent successful searches with Y printed
# raise the observer's confidence, even without knowing historical Prizes.
current = large
for count in range(1, 6):
    current = current.updated_by_print("Y")
    assert current.forward_prior == Fraction(4**count, 4**count + 1)
    if count <= 3:
        assert current.forward_prior < Fraction(74, 75)
        assert current.print_information_value() == 0
    else:
        assert current.forward_prior > Fraction(74, 75)
        assert current.print_information_value() > 0

after_three = ExpandedPolicyBelief(Fraction(64, 65), realistic)
after_four = ExpandedPolicyBelief(Fraction(256, 257), realistic)
assert after_three.print_information_value() == 0
assert after_four.print_information_value() == Fraction(182, 24415)
assert after_four.zero_one_accuracy(reveal_print=False) == Fraction(84, 95)
assert after_four.zero_one_accuracy(reveal_print=True) == (
    Fraction(84, 95) + Fraction(182, 24415)
)

# Symmetric other side: four consecutive old-print reveals favor reverse
# policy with the same predictive decision gain after swapping print labels.
reverse = large
for _ in range(4):
    reverse = reverse.updated_by_print("X")
assert reverse.forward_prior == Fraction(1, 257)
assert reverse.print_information_value() == after_four.print_information_value()

# Formula-driven model also reproduces the 6-card threshold as special case,
# and zero or nonzero information as priors vary throughout both pool sizes.
for model in (toy, realistic):
    for i in range(101):
        alpha = Fraction(i, 100)
        posterior = ExpandedPolicyBelief(alpha, model)
        assert posterior.print_probability("X") + (
            posterior.print_probability("Y")
        ) == 1
        if alpha == Fraction(1, 2):
            assert posterior.a_prized_posterior("X") == (
                model.a_prized_given_success
            )
        assert posterior.print_information_value() >= 0

try:
    ExpandedPolicyBelief(Fraction(3, 2), realistic)
except ValueError as exc:
    assert "prior" in str(exc)
else:
    raise AssertionError("out-of-range policy prior must fail")

try:
    large.updated_by_print("Z")
except ValueError as exc:
    assert "print" in str(exc)
else:
    raise AssertionError("unknown print label must fail")

print("six-card policies unidentifiable from print frequency (1/2 each)")
print("52-card forward choice rates: X=1/5 and Y=4/5")
print("unlabeled Y choices update forward odds x4 each independent game")
print("exact action threshold=74/75; crossed after 4 Y observations")
print("future correct-response gain after fourth Y = 182/24415")
