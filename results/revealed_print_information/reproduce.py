"""Exact reproducible same-name, distinct-print revealed-search witness."""

from collections import Counter
from fractions import Fraction
from itertools import combinations
from math import isclose
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from revealed_print_information import (
    SearchCard,
    conditional_event_probability,
    conditional_information_gain,
    enumerate_revealed_search_branches,
)


OLD_PIKACHU = "xy1-42"
NEW_PIKACHU = "swsh7-49"
CARDS = (
    SearchCard("A", "A"),
    SearchCard(OLD_PIKACHU, "Pikachu"),
    SearchCard(NEW_PIKACHU, "Pikachu"),
    SearchCard("F1", "Filler"),
    SearchCard("F2", "Filler"),
    SearchCard("F3", "Filler"),
)


def policy(prizes: frozenset[str], deck: frozenset[str]) -> str | None:
    if "A" in prizes and OLD_PIKACHU in deck:
        return OLD_PIKACHU
    if NEW_PIKACHU in deck:
        return NEW_PIKACHU
    if OLD_PIKACHU in deck:
        return OLD_PIKACHU
    return None


def check_actual_prints() -> None:
    records = {}
    for card_id, set_id in ((OLD_PIKACHU, "xy1"), (NEW_PIKACHU, "swsh7")):
        contents = json.loads(
            (ROOT / "resources" / "cards" / "en" / f"{set_id}.json")
            .read_text(encoding="utf-8")
        )
        records[card_id] = next(row for row in contents if row["id"] == card_id)

    assert all(card["name"] == "Pikachu" for card in records.values())
    assert all(
        card["legalities"]["expanded"] == "Legal"
        for card in records.values()
    )
    attacks = {
        card_id: tuple(attack["name"] for attack in card["attacks"])
        for card_id, card in records.items()
    }
    assert attacks[OLD_PIKACHU] == ("Nuzzle", "Quick Attack")
    assert attacks[NEW_PIKACHU] == ("Energize", "Electro Ball")


check_actual_prints()
branches = enumerate_revealed_search_branches(CARDS, 2, policy)
counts = Counter(branch.selected_print_id for branch in branches)
assert len(branches) == 84
assert counts == {OLD_PIKACHU: 42, NEW_PIKACHU: 42}

# Independent unordered-Prize enumeration: 15 equally likely worlds.
unordered = tuple(combinations(tuple(card.print_id for card in CARDS), 2))
assert len(unordered) == 15
choice_counts = Counter()
a_prized_by_choice = Counter()
for prize_pair in unordered:
    prize_ids = frozenset(prize_pair)
    deck_ids = frozenset(card.print_id for card in CARDS) - prize_ids
    selected = policy(prize_ids, deck_ids)
    choice_counts[selected] += 1
    if "A" in prize_ids:
        a_prized_by_choice[selected] += 1

assert choice_counts == {OLD_PIKACHU: 7, NEW_PIKACHU: 7, None: 1}
assert a_prized_by_choice[OLD_PIKACHU] == 4
assert a_prized_by_choice[NEW_PIKACHU] == 1
assert sum(a_prized_by_choice.values()) == 5

print_observation = lambda branch: branch.selected_print_id
name_observation = lambda branch: branch.selected_name
a_prized = lambda branch: "A" in branch.ordered_prize_ids
a_top = lambda branch: branch.top_print_id == "A"
exact = lambda observation, seen, event: conditional_event_probability(
    branches, observation, seen, event
)

assert exact(name_observation, "Pikachu", a_prized) == Fraction(5, 14)
assert exact(print_observation, OLD_PIKACHU, a_prized) == Fraction(4, 7)
assert exact(print_observation, NEW_PIKACHU, a_prized) == Fraction(1, 7)
assert exact(name_observation, "Pikachu", a_top) == Fraction(3, 14)
assert exact(print_observation, OLD_PIKACHU, a_top) == Fraction(1, 7)
assert exact(print_observation, NEW_PIKACHU, a_top) == Fraction(2, 7)

information = conditional_information_gain(
    branches, name_observation, "Pikachu", print_observation, a_prized
)
assert isclose(information, 0.1518355013623418, rel_tol=0.0, abs_tol=1e-12)

# Invalid policies and absent observations cannot silently create branches.
try:
    enumerate_revealed_search_branches(
        CARDS, 2, lambda _prizes, _deck: "unavailable"
    )
except ValueError as exc:
    assert "absent from deck" in str(exc)
else:
    raise AssertionError("an absent search target must be rejected")

try:
    exact(print_observation, "missing-print", a_prized)
except ValueError:
    pass
else:
    raise AssertionError("a zero-probability observation must be rejected")

print("84 labeled successful-search/top branches validated")
print("7/15 old print, 7/15 new print, 1/15 no target")
print("P(A Prized | name Pikachu)=5/14")
print("P(A Prized | old print)=4/7; new print=1/7")
print("P(top A | name)=3/14; old print=1/7; new print=2/7")
print(f"Conditional information gained from print identity: {information:.12f} bits")
