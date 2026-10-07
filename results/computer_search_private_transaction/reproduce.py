from collections import defaultdict
from itertools import permutations
from math import isclose
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from computer_search_private_transaction import (
    execute_computer_search_private_transaction,
)
from deck_search_shuffle_topology import SearchableDeckPhysicalState
from discard_cost_witness import DiscardCandidate, DiscardSelection
from identity_materialization import IdentityLedger, materialize
from lock_state_kernel import PlayerChannels
from multicopy_zone_state import ZoneCountState
from prize_position_belief import PrizePositionBelief
from prize_slot_visibility import PrizeSlotVisibilityBelief
from trainer_search_transaction import TrainerSearchExecutionState
from turn_action_budget import TurnActionBudget

CS = "class:computer-search"
D1 = "class:discard-one"
D2 = "class:discard-two"
A = "class:A"
X = "class:X"
Y = "class:Y"
F = "class:F"
CARDS = (("A1", A), ("X1", X), ("Y1", Y), ("F1", F), ("F2", F), ("F3", F))
GROUPS = ("A", "X", "Y")


def group(card_class):
    if card_class == A:
        return "A"
    if card_class == X:
        return "X"
    if card_class == Y:
        return "Y"
    return None


def composition(prizes):
    return tuple(
        sum(group(card_class) == current for _name, card_class in prizes)
        for current in GROUPS
    )


ordered_prizes = tuple(permutations(CARDS, 2))
masses = defaultdict(float)
for prizes in ordered_prizes:
    masses[tuple(group(card_class) for _name, card_class in prizes)] += (
        1.0 / len(ordered_prizes)
    )
prior = PrizeSlotVisibilityBelief.all_face_down(
    PrizePositionBelief(
        GROUPS,
        2,
        tuple(sorted(masses.items(), key=lambda row: repr(row[0]))),
    )
)

policy = {}
for current in {composition(prizes) for prizes in ordered_prizes}:
    a_prized, x_prized, y_prized = current
    filler_prized = 2 - sum(current)
    deck_counts = {
        "A": 1 - a_prized,
        "X": 1 - x_prized,
        "Y": 1 - y_prized,
        None: 3 - filler_prized,
    }
    policy[current] = {
        target: count / 4.0
        for target, count in deck_counts.items()
        if count
    }

ledger = IdentityLedger(
    ZoneCountState.from_mapping({
        (CS, "hand"): 1,
        (D1, "hand"): 1,
        (D2, "hand"): 1,
        (A, "prize"): 1,
        (X, "deck"): 1,
        (Y, "deck"): 1,
        (F, "prize"): 1,
        (F, "deck"): 2,
    })
)
ledger = materialize(
    ledger, card_class=A, card_name="A", source_zone="prize", instance_id="prize-a"
)
ledger = materialize(
    ledger, card_class=F, card_name="F", source_zone="prize", instance_id="prize-f"
)
physical = SearchableDeckPhysicalState(
    ledger, ("prize-a", "prize-f"), (False, False)
)
budget = TurnActionBudget(supporter_plays_used=1, supporter_play_limit=2)
execution = TrainerSearchExecutionState(
    zones=ledger.exchangeable,
    budget=budget,
    channels=PlayerChannels(),
)

transaction = execute_computer_search_private_transaction(
    physical,
    execution,
    (("actor", prior), ("observer", prior)),
    actor_id="actor",
    action_card_class=CS,
    discard_candidates=(DiscardCandidate(D1), DiscardCandidate(D2)),
    discard_selection=DiscardSelection((1, 1)),
    target_probability_by_composition=policy,
    group_by_card_class={A: "A", X: "X", Y: "Y"},
    target_card_class=X,
    target_card_name="X",
    target_instance_id="private-x",
    sampled_top_card_class=Y,
    sampled_top_card_name="Y",
    sampled_top_instance_id="top-y",
)

assert transaction.physical_after_cost.ledger.exchangeable.count(CS, "resolving_trainer") == 1
assert transaction.physical_after_cost.ledger.exchangeable.count(D1, "discard") == 1
assert transaction.physical_after_cost.ledger.exchangeable.count(D2, "discard") == 1
assert transaction.after.zones.count(CS, "discard") == 1
assert transaction.after.zones.count(CS, "resolving_trainer") == 0
assert transaction.physical_after.ledger.instance("private-x").zone == "hand"
assert transaction.physical_after.ledger.instance("top-y").zone == "deck_top"
assert transaction.after.budget == budget
assert transaction.after.channels == execution.channels

actor = transaction.beliefs_after.belief_for("actor")
observer = transaction.beliefs_after.belief_for("observer")
assert isclose(actor.top_probability("Y"), 1.0 / 3.0, abs_tol=1e-12)
assert isclose(observer.top_probability("Y"), 1.0 / 6.0, abs_tol=1e-12)
assert transaction.physical_before.ledger.totals() == transaction.physical_after.ledger.totals()

locked = TrainerSearchExecutionState(
    zones=ledger.exchangeable,
    budget=budget,
    channels=PlayerChannels(item_play=False),
)
try:
    execute_computer_search_private_transaction(
        physical,
        locked,
        (("actor", prior),),
        actor_id="actor",
        action_card_class=CS,
        discard_candidates=(DiscardCandidate(D1), DiscardCandidate(D2)),
        discard_selection=DiscardSelection((1, 1)),
        target_probability_by_composition=policy,
        group_by_card_class={A: "A", X: "X", Y: "Y"},
        target_card_class=X,
        target_card_name="X",
        target_instance_id="locked-x",
        sampled_top_card_class=Y,
        sampled_top_card_name="Y",
        sampled_top_instance_id="locked-y",
    )
except ValueError:
    pass
else:
    raise AssertionError("Item lock must block Computer Search")

try:
    execute_computer_search_private_transaction(
        physical,
        execution,
        (("actor", prior),),
        actor_id="actor",
        action_card_class=CS,
        discard_candidates=(DiscardCandidate(D1), DiscardCandidate(D2)),
        discard_selection=DiscardSelection((1, 0)),
        target_probability_by_composition=policy,
        group_by_card_class={A: "A", X: "X", Y: "Y"},
        target_card_class=X,
        target_card_name="X",
        target_instance_id="bad-cost-x",
        sampled_top_card_class=Y,
        sampled_top_card_name="Y",
        sampled_top_instance_id="bad-cost-y",
    )
except ValueError:
    pass
else:
    raise AssertionError("Computer Search must require exactly two discarded cards")

print("atomic Computer Search private transaction regressions passed")
print("cost: Computer Search resolving + two exact discards")
print("target: private X in hand; exact shuffled top Y")
print("actor top Y=1/3; observer top Y=1/6")
print("Item lock blocks the action; Supporter budget remains unchanged")
print("card-class totals remain conserved")
