from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from identity_liveness import assess_dematerialization, dematerialize_if_safe
from identity_materialization import IdentityLedger, materialize
from identity_reference_sources import pending_prize_belief_identity_references
from multicopy_zone_state import ZoneCountState
from pending_prize_batch_identity_belief import (
    ObserverPendingPrizeBatchBeliefs,
    PendingPrizeBatchJointBelief,
    project_completed_batch,
    resolve_pending_instance_visibility,
)


A = "class:A"

ledger = IdentityLedger(
    ZoneCountState.from_mapping({
        (A, "hand"): 1,
    })
)
ledger = materialize(
    ledger,
    card_class=A,
    card_name="A",
    source_zone="hand",
    instance_id="pending-a",
)

belief = PendingPrizeBatchJointBelief(
    groups=("A",),
    face_up=(),
    pending_count=1,
    masses=(
        (("A", (), ("A",)), 1.0),
    ),
)
observer_beliefs = ObserverPendingPrizeBatchBeliefs(
    ("pending-a",),
    (
        ("actor", belief),
        ("observer", belief),
    ),
)

refs = pending_prize_belief_identity_references(observer_beliefs)
assert tuple(row.reference_id for row in refs) == (
    "belief:prize_pending:0",
)

assessment = assess_dematerialization(
    ledger,
    "pending-a",
    references=refs,
)
assert not assessment.safe
assert assessment.blockers == ("reference:belief:prize_pending:0",)

resolved_beliefs = resolve_pending_instance_visibility(
    observer_beliefs,
    instance_id="pending-a",
    visible_groups={"actor": "A"},
)
assert resolved_beliefs.pending_instance_ids == ()
projected = project_completed_batch(resolved_beliefs)
assert projected.belief_for("actor").top_probability("A") == 1.0

released = dematerialize_if_safe(
    ledger,
    "pending-a",
    references=pending_prize_belief_identity_references(resolved_beliefs),
)
assert released.exchangeable.count(A, "hand") == 1
assert released.instances == ()
assert released.totals() == ledger.totals()

print({
    "blocked_while_belief_keys_instance": assessment.blockers,
    "belief_pending_ids_after_resolution": resolved_beliefs.pending_instance_ids,
    "released_after_belief_projection": True,
    "copy_totals_preserved": released.totals() == ledger.totals(),
})
