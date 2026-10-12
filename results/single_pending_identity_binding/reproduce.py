"""Single-file physical/observer identity-lifetime regression."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from composite_identity_liveness import collect_composite_identity_references
from identity_liveness import assess_dematerialization, dematerialize_if_safe
from identity_materialization import (
    IdentityLedger,
    assert_conserved,
    materialize,
    move_instance,
)
from multicopy_zone_state import ZoneCountState
from pending_prize_identity_belief import (
    ObserverPendingPrizeBeliefs,
    PendingPrizeJointBelief,
    resolve_single_pending_visibility,
)
from physical_zone_count import physical_zone_count
from prize_pending_take import resolve_next_pending_prize, stage_prize_takes
from single_pending_identity_binding import bind_single_pending_prize_identity
from top_prize_physical_bridge import TopPrizePhysicalState


def rejects(f, needle):
    try:
        f()
    except ValueError as exc:
        assert needle in str(exc), str(exc)
    else:
        raise AssertionError(f"expected error containing {needle!r}")


initial = IdentityLedger(
    ZoneCountState.from_mapping({
        ("class:top", "deck"): 1,
        ("class:a", "prize"): 1,
    })
)
ledger = materialize(
    initial,
    card_class="class:top",
    card_name="Top",
    source_zone="deck",
    instance_id="top",
)
ledger = move_instance(ledger, "top", "deck_top")
ledger = materialize(
    ledger,
    card_class="class:a",
    card_name="A",
    source_zone="prize",
    instance_id="prize-a",
)
physical = TopPrizePhysicalState(
    ledger,
    "top",
    ("prize-a",),
    (False,),
)
staged = stage_prize_takes(physical, positions=(0,))
model = PendingPrizeJointBelief(
    groups=("Top", "A"),
    face_up=(),
    masses=((("Top", (), "A"), 1.0),),
)
beliefs = ObserverPendingPrizeBeliefs(
    (("actor", model), ("opponent", model)),
)
bound = bind_single_pending_prize_identity(staged, beliefs)
assert bound.instance_id == "prize-a"

while_queued = collect_composite_identity_references(
    staged.physical.ledger,
    pending_prize=staged,
    single_pending_beliefs=bound,
)
assert tuple(row.reference_id for row in while_queued) == (
    "deck_top",
    "prize_pending:0",
    "belief:single_prize_pending",
)

physical_resolution = resolve_next_pending_prize(staged)
current = physical_resolution.after
refs_after_hand = collect_composite_identity_references(
    current.physical.ledger,
    pending_prize=current,
    single_pending_beliefs=bound,
)
assert assess_dematerialization(
    current.physical.ledger,
    "prize-a",
    references=refs_after_hand,
).blockers == ("reference:belief:single_prize_pending",)

rejected = False
try:
    dematerialize_if_safe(
        current.physical.ledger,
        "prize-a",
        references=refs_after_hand,
    )
except ValueError:
    rejected = True
assert rejected

resolved_belief = resolve_single_pending_visibility(
    bound.beliefs,
    visible_groups={"actor": "A"},
)
assert resolved_belief.belief_for("actor").top_probability("Top") == 1.0

after_all_owners = collect_composite_identity_references(
    current.physical.ledger,
    pending_prize=current,
)
released = dematerialize_if_safe(
    current.physical.ledger,
    "prize-a",
    references=after_all_owners,
)
assert physical_zone_count(released, "hand") == 1
assert released.exchangeable.count("class:a", "hand") == 1
assert_conserved(initial, released)

rejects(
    lambda: bind_single_pending_prize_identity(current, beliefs),
    "exactly one queued Prize",
)
inconsistent = ObserverPendingPrizeBeliefs((
    ("actor", PendingPrizeJointBelief(
        groups=("Top", "A"),
        face_up=(False,),
        masses=((("Top", ("A",), "A"), 1.0),),
    )),
))
rejects(
    lambda: bind_single_pending_prize_identity(staged, inconsistent),
    "visibility disagrees",
)

print({
    "bound_instance_id": bound.instance_id,
    "hand_identity_protected_until_belief_release": rejected,
    "physically_conserved": initial.totals() == released.totals(),
    "post_release_hand_count": physical_zone_count(released, "hand"),
    "mismatched_visibility_rejected": True,
})
