"""Exact decision-value difference between a Pikachu name and print reveal."""

from fractions import Fraction
from itertools import product
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from observation_policy_envelope import BeliefState, observation_policy_envelope
from revealed_print_information import SearchCard, enumerate_revealed_search_branches

OLD = "xy1-42"
NEW = "swsh7-49"
CARDS = (
    SearchCard("A", "A"),
    SearchCard(OLD, "Pikachu"),
    SearchCard(NEW, "Pikachu"),
    SearchCard("F1", "Filler"),
    SearchCard("F2", "Filler"),
    SearchCard("F3", "Filler"),
)


def policy(prizes: frozenset[str], deck: frozenset[str]) -> str | None:
    if "A" in prizes and OLD in deck:
        return OLD
    if NEW in deck:
        return NEW
    if OLD in deck:
        return OLD
    return None


branches = enumerate_revealed_search_branches(CARDS, 2, policy)
assert len(branches) == 84


def make_states(
    *,
    reveal_print: bool,
    prized_reward: Fraction = Fraction(1),
) -> tuple[BeliefState, ...]:
    return tuple(
        BeliefState(
            state_id=str(index),
            probability=Fraction(1, len(branches)),
            observation=(
                branch.selected_print_id
                if reveal_print else branch.selected_name
            ),
            payoffs=(
                ("assume_prized", prized_reward if "A" in branch.ordered_prize_ids else Fraction(0)),
                ("assume_unprized", Fraction("A" not in branch.ordered_prize_ids)),
            ),
        )
        for index, branch in enumerate(branches)
    )


def independent_oracle(states: tuple[BeliefState, ...]) -> Fraction:
    """Exhaustively evaluate deterministic observation-consistent responses."""
    observations = tuple(sorted({row.observation for row in states}))
    actions = tuple(action for action, _ in states[0].payoffs)
    best = Fraction(-1)
    for choices in product(actions, repeat=len(observations)):
        selected = dict(zip(observations, choices))
        payoff = sum((
            row.probability * dict(row.payoffs)[selected[row.observation]]
            for row in states
        ), Fraction(0))
        if payoff > best:
            best = payoff
    return best


name = observation_policy_envelope(make_states(reveal_print=False))
printwise = observation_policy_envelope(make_states(reveal_print=True))
assert name.expected_payoff == Fraction(9, 14)
assert printwise.expected_payoff == Fraction(5, 7)
assert printwise.expected_payoff - name.expected_payoff == Fraction(1, 14)
assert name.chosen_by_observation == (("Pikachu", "assume_unprized"),)
assert printwise.chosen_by_observation == (
    (OLD, "assume_prized"),
    (NEW, "assume_unprized"),
)
for reveal in (False, True):
    states = make_states(reveal_print=reveal)
    assert observation_policy_envelope(states).expected_payoff == independent_oracle(states)

# Positive information need not change the best decision for a payoff regime.
# With 1/4 payout for predicting A prized, all posterior probabilities remain
# below the break-even threshold of 4/5.
name_high_cost = observation_policy_envelope(
    make_states(reveal_print=False, prized_reward=Fraction(1, 4))
)
print_high_cost = observation_policy_envelope(
    make_states(reveal_print=True, prized_reward=Fraction(1, 4))
)
assert name_high_cost.expected_payoff == Fraction(9, 14)
assert print_high_cost.expected_payoff == Fraction(9, 14)
assert all(
    action == "assume_unprized"
    for _, action in print_high_cost.chosen_by_observation
)

# With extra reward for a successful prized prediction, the optimal split and
# exact information value change. The blind name observer already selects the
# "prized" action; the print observer uses it only when old Pikachu is seen.
name_double = observation_policy_envelope(
    make_states(reveal_print=False, prized_reward=Fraction(2))
)
print_double = observation_policy_envelope(
    make_states(reveal_print=True, prized_reward=Fraction(2))
)
assert name_double.expected_payoff == Fraction(5, 7)
assert print_double.expected_payoff == Fraction(1)
assert print_double.expected_payoff - name_double.expected_payoff == Fraction(2, 7)

print("equal-payoff correct binary choice: 9/14 by name, 5/7 by print")
print("exact decision value from visible print: 1/14")
print("low utility prized prediction: 0 information decision value")
print("double utility prized prediction: 2/7 information decision value")
print("all cases match independent exhaustive policy enumeration")
