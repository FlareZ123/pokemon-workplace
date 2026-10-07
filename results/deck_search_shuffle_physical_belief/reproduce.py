from collections import defaultdict
from itertools import permutations
from math import isclose
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from deck_search_shuffle_physical_belief import (
    resolve_physical_full_search_shuffle,
)
from deck_search_shuffle_topology import SearchableDeckPhysicalState
from identity_materialization import IdentityLedger, materialize
from multicopy_zone_state import ZoneCountState
from prize_position_belief import PrizePositionBelief
from prize_slot_visibility import PrizeSlotVisibilityBelief
from top_prize_physical_bridge import (
    actual_joint_groups,
    belief_truth_probability,
)

A = "class:A"
B = "class:B"
F = "class:F"
CARDS = (("A1", A), ("B1", B), ("B2", B), ("F1", F), ("F2", F))
GROUPS = ("A", "B")


def group(card_class):
    if card_class == A:
        return "A"
    if card_class == B:
        return "B"
    return None


masses = defaultdict(float)
denominator = len(CARDS) * (len(CARDS) - 1)
for first, second in permutations(CARDS, 2):
    masses[(group(first[1]), group(second[1]))] += 1.0 / denominator

prior = PrizeSlotVisibilityBelief.all_face_down(
    PrizePositionBelief(
        GROUPS,
        2,
        tuple(sorted(masses.items(), key=lambda row: repr(row[0]))),
    )
)

ledger = IdentityLedger(
    ZoneCountState.from_mapping({
        (A, "prize"): 1,
        (B, "deck"): 2,
        (F, "prize"): 1,
        (F, "deck"): 1,
    })
)
ledger = materialize(
    ledger,
    card_class=A,
    card_name="A",
    source_zone="prize",
    instance_id="prize-a",
)
ledger = materialize(
    ledger,
    card_class=F,
    card_name="F",
    source_zone="prize",
    instance_id="prize-f",
)
physical = SearchableDeckPhysicalState(
    ledger,
    ("prize-a", "prize-f"),
    (False, False),
)

transition = resolve_physical_full_search_shuffle(
    physical,
    (("actor", prior), ("observer", prior)),
    actor_id="actor",
    group_by_card_class={A: "A", B: "B"},
    sampled_top_card_class=B,
    sampled_top_card_name="B",
    sampled_top_instance_id="top-b",
)

assert transition.actor_exact_prize_counts == (("A", 1), ("B", 0))
assert transition.group_pool_counts == (("A", 1), ("B", 2))
assert transition.pool_size == 5
assert transition.physical_after.top_instance_id == "top-b"
assert transition.physical_after.ledger.instance("top-b").zone == "deck_top"

actor = transition.beliefs_after.belief_for("actor")
observer = transition.beliefs_after.belief_for("observer")
assert isclose(actor.top_probability("A"), 0.0, abs_tol=1e-12)
assert isclose(actor.top_probability("B"), 2.0 / 3.0, abs_tol=1e-12)
assert isclose(observer.top_probability("B"), 2.0 / 5.0, abs_tol=1e-12)

top_group, prize_groups = actual_joint_groups(
    transition.physical_after,
    {A: "A", B: "B"},
)
assert top_group == "B"
assert prize_groups == ("A", None)
for belief in (actor, observer):
    assert belief_truth_probability(
        belief,
        top_group=top_group,
        prize_groups=prize_groups,
    ) > 0.0

before_totals = transition.physical_before.ledger.totals()
after_totals = transition.physical_after.ledger.totals()
assert before_totals == after_totals

try:
    resolve_physical_full_search_shuffle(
        physical,
        (("actor", prior),),
        actor_id="actor",
        group_by_card_class={A: "A", B: "B"},
        sampled_top_card_class=A,
        sampled_top_card_name="A",
        sampled_top_instance_id="impossible-top-a",
    )
except ValueError:
    pass
else:
    raise AssertionError("Prized singleton A cannot be sampled from deck")

print("physical search-shuffle belief bridge regressions passed")
print("exact physical truth: top=B, prizes=(A, filler)")
print("actor K1 and observer K0 both retain positive support on truth")
print("card totals remain conserved across top materialization")
