"""Exact latent-print Bayes transition under a coarsened public search label."""

from collections import defaultdict
from fractions import Fraction
from itertools import permutations
from math import isclose
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from prize_position_belief import PrizePositionBelief
from prize_slot_visibility import PrizeSlotVisibilityBelief
from revealed_print_information import (
    SearchCard,
    conditional_event_probability,
    enumerate_revealed_search_branches,
)
from revealed_target_coarsening import (
    condition_coarse_revealed_search,
    resolve_coarse_revealed_search_for_observers,
)

POOL = ("A", "Xa", "Xb", "F1", "F2", "F3")
GROUPS = ("A", "Xa", "Xb")
POOL_COUNTS = {"A": 1, "Xa": 1, "Xb": 1}
OBSERVATION = {"Xa": "Pikachu", "Xb": "Pikachu", "PASS": "NO_SEARCH"}


def card_group(instance_id: str) -> str | None:
    return instance_id if instance_id in GROUPS else None


def choose(prizes: frozenset[str], deck: frozenset[str]) -> str | None:
    if "A" in prizes and "Xa" in deck:
        return "Xa"
    if "Xb" in deck:
        return "Xb"
    if "Xa" in deck:
        return "Xa"
    return None


def choose_composition(composition: tuple[int, ...]) -> str:
    a_prized, xa_prized, xb_prized = composition
    if a_prized and not xa_prized:
        return "Xa"
    if not xb_prized:
        return "Xb"
    if not xa_prized:
        return "Xa"
    return "PASS"


ordered_prizes = tuple(permutations(POOL, 2))
assert len(ordered_prizes) == 30
masses = defaultdict(float)
for pair in ordered_prizes:
    masses[tuple(map(card_group, pair))] += 1.0 / len(ordered_prizes)

prior = PrizeSlotVisibilityBelief.all_face_down(
    PrizePositionBelief(
        GROUPS,
        2,
        tuple(sorted(masses.items(), key=lambda x: repr(x[0]))),
    )
)
policy = {
    composition: {choose_composition(composition): 1.0}
    for composition in prior.positions.composition_distribution()
}

beliefs = resolve_coarse_revealed_search_for_observers(
    (("actor", prior), ("opponent", prior)),
    actor_id="actor",
    actor_exact_prize_counts={"A": 1, "Xa": 0, "Xb": 0},
    actor_selected_target_group="Xa",
    target_probability_by_composition=policy,
    public_label_by_target=OBSERVATION,
    observed_public_label="Pikachu",
    pre_search_group_pool_counts=POOL_COUNTS,
    pre_search_pool_size=6,
)
actor = beliefs.belief_for("actor")
opponent = beliefs.belief_for("opponent")


def p_prized(belief, group: str) -> float:
    return sum(
        probability
        for (_top, prizes, _selected), probability in belief.masses
        if group in prizes
    )


def check(actual: float, expected: Fraction) -> None:
    assert isclose(actual, float(expected), rel_tol=0.0, abs_tol=1e-12), (
        actual, expected
    )


check(actor.target_probability("Xa"), Fraction(1))
check(actor.top_probability("A"), Fraction(0))
check(actor.top_probability("Xb"), Fraction(1, 3))
check(p_prized(actor, "A"), Fraction(1))

check(opponent.target_probability("Xa"), Fraction(1, 2))
check(opponent.target_probability("Xb"), Fraction(1, 2))
check(p_prized(opponent, "A"), Fraction(5, 14))
check(opponent.top_probability("A"), Fraction(3, 14))

revealed_xa = opponent.condition_target("Xa")
revealed_xb = opponent.condition_target("Xb")
check(p_prized(revealed_xa, "A"), Fraction(4, 7))
check(p_prized(revealed_xb, "A"), Fraction(1, 7))
check(revealed_xa.top_probability("A"), Fraction(1, 7))
check(revealed_xb.top_probability("A"), Fraction(2, 7))

# The exact enumerated search/top branches are an independent oracle.
exact_cards = tuple(
    SearchCard(card, "Pikachu" if card in {"Xa", "Xb"} else card)
    for card in POOL
)
branches = enumerate_revealed_search_branches(exact_cards, 2, choose)
as_name = lambda branch: branch.selected_name
as_print = lambda branch: branch.selected_print_id
is_a_prized = lambda branch: "A" in branch.ordered_prize_ids
is_a_top = lambda branch: branch.top_print_id == "A"
for observation, label, event, analytic in (
    (as_name, "Pikachu", is_a_prized, p_prized(opponent, "A")),
    (as_name, "Pikachu", is_a_top, opponent.top_probability("A")),
    (as_print, "Xa", is_a_prized, p_prized(revealed_xa, "A")),
    (as_print, "Xb", is_a_prized, p_prized(revealed_xb, "A")),
    (as_print, "Xa", is_a_top, revealed_xa.top_probability("A")),
    (as_print, "Xb", is_a_top, revealed_xb.top_probability("A")),
):
    check(
        analytic,
        conditional_event_probability(
            branches, observation, label, event
        ),
    )

# The actor has seen the deck and must not choose an impossible policy target.
try:
    resolve_coarse_revealed_search_for_observers(
        (("actor", prior), ("opponent", prior)),
        actor_id="actor",
        actor_exact_prize_counts={"A": 1, "Xa": 0, "Xb": 0},
        actor_selected_target_group="Xb",
        target_probability_by_composition=policy,
        public_label_by_target=OBSERVATION,
        observed_public_label="Pikachu",
        pre_search_group_pool_counts=POOL_COUNTS,
        pre_search_pool_size=6,
    )
except ValueError as exc:
    assert "impossible under the policy" in str(exc)
else:
    raise AssertionError("actor may not choose an impossible selected print")

try:
    condition_coarse_revealed_search(
        prior,
        target_probability_by_composition=policy,
        public_label_by_target={"Xa": "Pikachu"},
        observed_public_label="Pikachu",
        pre_search_group_pool_counts=POOL_COUNTS,
        pre_search_pool_size=6,
    )
except ValueError as exc:
    assert "public label" in str(exc)
else:
    raise AssertionError("missing target projection must be rejected")

print("coarsened public-reveal posterior validated against exact oracle")
print("opponent P(A Prized|Pikachu)=5/14; P(top A)=3/14")
print("latent print Xa/Xb probabilities 1/2 each")
print("later Xa reveal: A Prized=4/7 and top A=1/7")
print("later Xb reveal: A Prized=1/7 and top A=2/7")
