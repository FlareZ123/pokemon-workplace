"""Exact policy learning across independent searches and later Prize evidence."""

from fractions import Fraction
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from latent_search_policy_belief import (
    PolicyHypothesis,
    enumerate_policy_search_worlds,
)
from observation_policy_envelope import BeliefState, observation_policy_envelope
from revealed_print_information import SearchCard
from search_policy_session_learning import (
    PolicyLearningPosterior,
    SearchObservation,
    policy_search_likelihoods,
)

OLD = "xy1-42"
NEW = "swsh7-49"
CARDS = tuple(
    SearchCard(card_id, "Pikachu" if card_id in {OLD, NEW} else card_id)
    for card_id in ("A", OLD, NEW, "F1", "F2", "F3")
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


policies = (
    PolicyHypothesis("forward", Fraction(1, 2), forward),
    PolicyHypothesis("reverse", Fraction(1, 2), reverse),
)
likelihoods = policy_search_likelihoods(CARDS, 2, policies)
initial = PolicyLearningPosterior((
    ("forward", Fraction(1, 2)),
    ("reverse", Fraction(1, 2)),
))
old_only = SearchObservation(OLD, "A")
old_and_prized = SearchObservation(OLD, "A", True)
old_and_unprized = SearchObservation(OLD, "A", False)

# Print choices alone have identical likelihoods under these two policies.
state = initial
for _ in range(50):
    state = state.update(old_only, likelihoods)
assert state == initial

# When the past game reveals whether A was Prized, it identifies behavior.
once = initial.update(old_and_prized, likelihoods)
assert once.probability("forward") == Fraction(4, 5)
twice = once.update(old_and_prized, likelihoods)
assert twice.probability("forward") == Fraction(16, 17)
assert initial.update(old_and_unprized, likelihoods).probability(
    "forward"
) == Fraction(1, 3)

# An old-print observation in a *future* game crosses the equal-payoff
# response threshold only after two earlier aligned labeled examples.
def future_decision(prior: PolicyLearningPosterior) -> tuple[Fraction, Fraction]:
    mix = enumerate_policy_search_worlds(
        CARDS, 2,
        tuple(
            PolicyHypothesis(
                candidate.name,
                prior.probability(candidate.name),
                candidate.choose,
            )
            for candidate in policies
        ),
    )
    name_rows = []
    print_rows = []
    for i, (world, probability) in enumerate(mix.masses):
        payoffs = (
            ("predict_prized", Fraction("A" in world.ordered_prize_ids)),
            ("predict_unprized", Fraction("A" not in world.ordered_prize_ids)),
        )
        name_rows.append(BeliefState(str(i), probability, "Pikachu", payoffs))
        print_rows.append(BeliefState(
            str(i), probability, world.selected_print_id, payoffs
        ))
    return (
        observation_policy_envelope(name_rows).expected_payoff,
        observation_policy_envelope(print_rows).expected_payoff,
    )


assert future_decision(initial) == (Fraction(9, 14), Fraction(9, 14))
assert future_decision(once) == (Fraction(9, 14), Fraction(9, 14))
assert future_decision(twice) == (
    Fraction(9, 14),
    Fraction(9, 14) + Fraction(11, 238),
)

# Reveal the print first and learn that same game's Prize status later:
# the old print is already counted; only the *conditional* Prize likelihood
# may be applied. Verify the sequential update matches observing both at once.
print_then_labeled = (
    initial.update(old_only, likelihoods)
    .update_deferred_prize_status(old_only, True, likelihoods)
)
assert print_then_labeled == once

# Asymmetric control: print selection itself has informative likelihood.
def prefer_old(_prizes: frozenset[str], deck: frozenset[str]) -> str | None:
    return OLD if OLD in deck else NEW if NEW in deck else None


def prefer_new(_prizes: frozenset[str], deck: frozenset[str]) -> str | None:
    return NEW if NEW in deck else OLD if OLD in deck else None


asymmetric_policies = (
    PolicyHypothesis("prefer_old", Fraction(1, 2), prefer_old),
    PolicyHypothesis("prefer_new", Fraction(1, 2), prefer_new),
)
asymmetric_likelihoods = policy_search_likelihoods(
    CARDS, 2, asymmetric_policies
)
asymmetric_start = PolicyLearningPosterior((
    ("prefer_old", Fraction(1, 2)),
    ("prefer_new", Fraction(1, 2)),
))
asymmetric_after_print = asymmetric_start.update(
    old_only, asymmetric_likelihoods
)
assert asymmetric_after_print.probability("prefer_old") == Fraction(5, 7)
asymmetric_complete = asymmetric_start.update(
    old_and_prized, asymmetric_likelihoods
)
assert asymmetric_complete.probability("prefer_old") == Fraction(4, 5)
assert asymmetric_after_print.update_deferred_prize_status(
    old_only, True, asymmetric_likelihoods
) == asymmetric_complete
# Naively applying the entire event again double counts the known print.
assert asymmetric_after_print.update(
    old_and_prized, asymmetric_likelihoods
).probability("prefer_old") == Fraction(10, 11)

try:
    asymmetric_after_print.update_deferred_prize_status(
        old_and_prized, True, asymmetric_likelihoods
    )
except ValueError as exc:
    assert "already included" in str(exc)
else:
    raise AssertionError("duplicated Prize observation should be rejected")

print("50 print-only observations leave symmetric search-policy prior at 1/2")
print("one labeled game gives P(forward)=4/5; two give 16/17")
print("future print response gain crosses zero to 11/238 after second label")
print("asymmetric print-first + deferred Prize label equals one-shot 4/5")
print("naive double-counting produces incorrect 10/11 posterior")
