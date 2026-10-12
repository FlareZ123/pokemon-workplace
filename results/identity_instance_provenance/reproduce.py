"""Single-file test for stale-reference aliasing after instance ID reuse."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from composite_identity_liveness import collect_composite_identity_references
from identity_instance_provenance import (
    IdentityProvenanceState,
    begin_identity_provenance,
    dematerialize_preserving_provenance,
    materialize_unique,
    move_instance_preserving_provenance,
)
from identity_liveness import IdentityReference
from identity_materialization import (
    IdentityLedger,
    assert_conserved,
    dematerialize,
    materialize,
)
from multicopy_zone_state import ZoneCountState


def must_reject(fn, fragment):
    try:
        fn()
    except ValueError as exc:
        assert fragment in str(exc), str(exc)
    else:
        raise AssertionError("expected ValueError")


initial = IdentityLedger(ZoneCountState.from_mapping({
    ("A", "hand"): 1,
    ("B", "hand"): 1,
}))
stale_old_reference = IdentityReference(
    "effect:old-instance", "physical-1", "old released copy of A"
)

# Core ledger permits reuse of an ID after the corresponding card is released.
raw_a = materialize(
    initial, card_class="A", card_name="A",
    source_zone="hand", instance_id="physical-1",
)
raw_released = dematerialize(raw_a, "physical-1")
raw_b_reused = materialize(
    raw_released, card_class="B", card_name="B",
    source_zone="hand", instance_id="physical-1",
)
assert raw_b_reused.instance("physical-1").card_class == "B"
ambiguous = collect_composite_identity_references(
    raw_b_reused,
    effect_references=(stale_old_reference,),
)
assert ambiguous[0].instance_id == "physical-1"

# Closed-path provenance tracks every issued ID, including already released IDs.
state = begin_identity_provenance(initial)
state = materialize_unique(
    state, card_class="A", card_name="A",
    source_zone="hand", instance_id="physical-1",
)
state = move_instance_preserving_provenance(state, "physical-1", "discard")
state = move_instance_preserving_provenance(state, "physical-1", "hand")
state = dematerialize_preserving_provenance(state, "physical-1")
assert "physical-1" in state.ever_issued
assert not state.ledger.instances
must_reject(
    lambda: materialize_unique(
        state, card_class="B", card_name="B",
        source_zone="hand", instance_id="physical-1",
    ),
    "already issued",
)
state = materialize_unique(
    state, card_class="B", card_name="B",
    source_zone="hand", instance_id="physical-2",
)
must_reject(
    lambda: collect_composite_identity_references(
        state.ledger,
        effect_references=(stale_old_reference,),
    ),
    "absent instance",
)
assert state.ever_issued == frozenset({"physical-1", "physical-2"})
assert_conserved(initial, state.ledger)

must_reject(
    lambda: IdentityProvenanceState(state.ledger, frozenset({"physical-1"})),
    "missing from provenance",
)
adopted = begin_identity_provenance(
    state.ledger,
    known_prior_ids=("physical-1",),
)
assert adopted.ever_issued == state.ever_issued
assert initial.totals() == state.ledger.totals()

print({
    "raw_ledger_reuses_released_id": True,
    "untracked_reference_aliases_second_card": True,
    "tracked_reuse_rejected": True,
    "stale_reference_rejected_after_fresh_id": True,
    "totals_conserved": True,
    "issued_ids": sorted(state.ever_issued),
})
