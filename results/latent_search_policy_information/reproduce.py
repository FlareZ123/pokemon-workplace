"""Independent exact tests of unknown target-choice policies and hidden Prizes."""

from fractions import Fraction
from itertools import combinations, product
from math import isclose
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from latent_search_policy_belief import (
    PolicyHypothesis,
    enumerate_policy_search_worlds,
)
from observation_policy_envelope import BeliefState, observation_policy_envelope
from revealed_print_information import SearchCard, binary_entropy

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


def forward(prizes: frozenset[str], deck: frozenset[str]) -> str | None:
    if "A" in prizes and OLD in deck:
        return OLD
    if NEW in deck:
        return NEW
    if OLD in deck:
        return OLD
    return None


def reverse(prizes: frozenset[str], deck: frozenset[str]) -> str | None:
    if "A" in prizes and NEW in deck:
        return NEW
    if OLD in deck:
        return OLD
    if NEW in deck:
        return NEW
    return None


policies = (
    PolicyHypothesis("forward", Fraction(1, 2), forward),
    PolicyHypothesis("reverse", Fraction(1, 2), reverse),
)
state = enumerate_policy_search_worlds(CARDS, 2, policies)
assert len(state.masses) == 168
assert all(mass == Fraction(1, 168) for _, mass in state.masses)

a_prized = lambda world: "A" in world.ordered_prize_ids
a_top = lambda world: world.shuffled_top_print_id == "A"
cond_old = state.print_reveal(OLD)
cond_new = state.print_reveal(NEW)
assert state.probability(a_prized) == Fraction(5, 14)
assert state.probability(a_top) == Fraction(3, 14)
assert cond_old.probability(a_prized) == Fraction(5, 14)
assert cond_new.probability(a_prized) == Fraction(5, 14)
assert cond_old.probability(a_top) == Fraction(3, 14)
assert cond_new.probability(a_top) == Fraction(3, 14)
assert state.probability(lambda w: w.policy_name == "forward") == Fraction(1, 2)
assert cond_old.probability(lambda w: w.policy_name == "forward") == Fraction(1, 2)
assert cond_new.probability(lambda w: w.policy_name == "forward") == Fraction(1, 2)

# While either individual disclosure is uninformative about A, their joint
# disclosure has posterior 4/7 or 1/7, depending on which policy selected it.
assert cond_old.policy_reveal("forward").probability(a_prized) == Fraction(4, 7)
assert cond_old.policy_reveal("reverse").probability(a_prized) == Fraction(1, 7)
assert cond_new.policy_reveal("forward").probability(a_prized) == Fraction(1, 7)
assert cond_new.policy_reveal("reverse").probability(a_prized) == Fraction(4, 7)
assert cond_old.condition(a_prized).probability(
    lambda w: w.policy_name == "forward"
) == Fraction(4, 5)

information_from_print_alone = (
    binary_entropy(state.probability(a_prized))
    - sum(
        float(state.probability(lambda w, print_id=print_id: w.selected_print_id == print_id))
        * binary_entropy(state.print_reveal(print_id).probability(a_prized))
        for print_id in (OLD, NEW)
    )
)
information_from_policy_after_print = (
    binary_entropy(state.probability(a_prized))
    - (
        binary_entropy(Fraction(4, 7)) + binary_entropy(Fraction(1, 7))
    ) / 2
)
assert isclose(information_from_print_alone, 0, abs_tol=1e-12)
assert isclose(information_from_policy_after_print, 0.1518355013623418, abs_tol=1e-12)

# Independently reconstruct Prize-world choice counts without sampling top.
for policy in policies:
    counts = {OLD: [0, 0], NEW: [0, 0], None: [0, 0]}
    all_ids = frozenset(card.print_id for card in CARDS)
    for pair in combinations(tuple(all_ids), 2):
        prizes = frozenset(pair)
        selected = policy.choose(prizes, all_ids - prizes)
        counts[selected][0] += 1
        counts[selected][1] += "A" in prizes
    assert counts[None] == [1, 0]
    assert sorted(row[0] for row in counts.values()) == [1, 7, 7]
    assert sorted(row[1] for row in (counts[OLD], counts[NEW])) == [1, 4]


def policy_response_value(channel: str) -> Fraction:
    rows = []
    for index, (world, mass) in enumerate(state.masses):
        if channel == "name":
            label = world.selected_name
        elif channel == "print":
            label = world.selected_print_id
        elif channel == "policy":
            label = world.policy_name
        else:
            label = f"{world.policy_name}:{world.selected_print_id}"
        rows.append(BeliefState(
            str(index),
            mass,
            label,
            (
                ("assume_prized", Fraction(a_prized(world))),
                ("assume_unprized", Fraction(not a_prized(world))),
            ),
        ))
    answer = observation_policy_envelope(rows)
    labels = tuple(sorted({row.observation for row in rows}))
    brute = max(
        (
            sum((
                row.probability
                * dict(row.payoffs)[dict(zip(labels, choice))[row.observation]]
                for row in rows
            ), Fraction())
            for choice in product(("assume_prized", "assume_unprized"), repeat=len(labels))
        )
    )
    assert brute == answer.expected_payoff
    return answer.expected_payoff


assert policy_response_value("name") == Fraction(9, 14)
assert policy_response_value("print") == Fraction(9, 14)
assert policy_response_value("policy") == Fraction(9, 14)
assert policy_response_value("both") == Fraction(5, 7)

# Invalid policy priors and impossible selections are rejected.
try:
    enumerate_policy_search_worlds(
        CARDS, 2,
        (
            PolicyHypothesis("forward", Fraction(1, 4), forward),
            PolicyHypothesis("reverse", Fraction(1, 4), reverse),
        ),
    )
except ValueError as exc:
    assert "priors" in str(exc)
else:
    raise AssertionError("non-normalized policy prior accepted")

try:
    enumerate_policy_search_worlds(
        CARDS, 2,
        (PolicyHypothesis("impossible", Fraction(1), lambda _p, _d: "not-a-card"),),
    )
except ValueError as exc:
    assert "absent from deck" in str(exc)
else:
    raise AssertionError("impossible policy target accepted")

try:
    state.print_reveal("not-a-print")
except ValueError as exc:
    assert "zero probability" in str(exc)
else:
    raise AssertionError("zero likelihood public reveal accepted")

print("168 exact policy/Prize/search/shuffle branches validated")
print("either print alone gives P(A Prized)=5/14 under 50/50 policy mix")
print("joint print plus policy gives 4/7 or 1/7, with delayed information")
print("single-channel prediction value=9/14; combined=5/7")
print("four response channels matched independent exhaustive policies")
