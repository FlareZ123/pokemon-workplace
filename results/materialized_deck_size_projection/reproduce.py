from collections import defaultdict
from itertools import permutations
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from computer_search_private_transaction import execute_computer_search_private_transaction
from deck_search_shuffle_topology import SearchableDeckPhysicalState
from discard_cost_witness import DiscardCandidate, DiscardSelection
from identity_materialization import IdentityLedger, materialize
from lock_state_kernel import PlayerChannels
from multicopy_zone_state import ZoneCountState
from physical_deck_projection import draw_exact_top_to_hand, physical_deck_size
from physical_zone_count import physical_hand_size
from prize_position_belief import PrizePositionBelief
from prize_slot_visibility import PrizeSlotVisibilityBelief
from trainer_search_transaction import TrainerSearchExecutionState

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
    return {A: "A", X: "X", Y: "Y"}.get(card_class)


def composition(prizes):
    return tuple(
        sum(group(card_class) == current for _name, card_class in prizes)
        for current in GROUPS
    )


ordered_prizes = tuple(permutations(CARDS, 2))
masses = defaultdict(float)
for prizes in ordered_prizes:
    masses[tuple(group(card_class) for _name, card_class in prizes)] += 1.0 / len(ordered_prizes)
prior = PrizeSlotVisibilityBelief.all_face_down(
    PrizePositionBelief(GROUPS, 2, tuple(sorted(masses.items(), key=lambda row: repr(row[0]))))
)
policy = {}
for current in {composition(prizes) for prizes in ordered_prizes}:
    a_prized, x_prized, y_prized = current
    filler_prized = 2 - sum(current)
    counts = {
        "A": 1 - a_prized,
        "X": 1 - x_prized,
        "Y": 1 - y_prized,
        None: 3 - filler_prized,
    }
    policy[current] = {target: count / 4.0 for target, count in counts.items() if count}

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
ledger = materialize(ledger, card_class=A, card_name="A", source_zone="prize", instance_id="prize-a")
ledger = materialize(ledger, card_class=F, card_name="F", source_zone="prize", instance_id="prize-f")
physical = SearchableDeckPhysicalState(ledger, ("prize-a", "prize-f"), (False, False))
execution = TrainerSearchExecutionState(zones=ledger.exchangeable, channels=PlayerChannels())

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

before_draw = transaction.physical_after
exchangeable_deck_before = sum(
    count
    for _card, zone, count in before_draw.ledger.exchangeable.counts
    if zone == "deck"
)
assert exchangeable_deck_before == 2
assert physical_deck_size(before_draw.ledger) == 3
assert before_draw.ledger.instance("top-y").zone == "deck_top"

draw = draw_exact_top_to_hand(before_draw)
assert draw.drawn_instance_id == "top-y"
assert draw.after.ledger.instance("top-y").zone == "hand"
assert physical_deck_size(draw.after.ledger) == 2
assert physical_hand_size(draw.after.ledger) == 2

exchangeable_deck_after = sum(
    count
    for _card, zone, count in draw.after.ledger.exchangeable.counts
    if zone == "deck"
)
assert exchangeable_deck_after == 2
assert exchangeable_deck_after == exchangeable_deck_before
assert draw.before.ledger.totals() == draw.after.ledger.totals()

print({
    "exchangeable_deck_before_draw": exchangeable_deck_before,
    "physical_deck_before_draw": physical_deck_size(before_draw.ledger),
    "exchangeable_deck_after_draw": exchangeable_deck_after,
    "physical_deck_after_draw": physical_deck_size(draw.after.ledger),
    "drawn_instance": draw.drawn_instance_id,
    "physical_hand_after_draw": physical_hand_size(draw.after.ledger),
})
