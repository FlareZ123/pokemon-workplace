"""Single-file regression for physically resolved yet belief-live Prize identity."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from composite_identity_liveness import collect_composite_identity_references
from identity_liveness import (
    IdentityReference,
    assess_dematerialization,
    dematerialize_if_safe,
)
from identity_materialization import (
    IdentityLedger,
    assert_conserved,
    materialize,
    move_instance,
)
from multicopy_zone_state import ZoneCountState
from pending_prize_batch_identity_belief import (
    ObserverPendingPrizeBatchBeliefs,
    PendingPrizeBatchJointBelief,
    resolve_pending_instance_visibility,
)
from physical_zone_count import physical_zone_count
from prize_pending_take import resolve_next_pending_prize, stage_prize_takes
from top_prize_physical_bridge import TopPrizePhysicalState


def must_fail(action, fragment):
    try:
        action()
    except ValueError as exc:
        assert fragment in str(exc), str(exc)
    else:
        raise AssertionError(f"expected ValueError containing {fragment!r}")


starting = IdentityLedger(
    ZoneCountState.from_mapping({
        ("class:top", "deck"): 1,
        ("class:a", "prize"): 1,
        ("class:b", "prize"): 1,
    })
)
ledger = starting
for card_class, name, source, instance_id in (
    ("class:top", "Top", "deck", "top"),
    ("class:a", "A", "prize", "prize-a"),
    ("class:b", "B", "prize", "prize-b"),
):
    ledger = materialize(
        ledger,
        card_class=card_class,
        card_name=name,
        source_zone=source,
        instance_id=instance_id,
    )
ledger = move_instance(ledger, "top", "deck_top")
physical = TopPrizePhysicalState(
    ledger,
    "top",
    ("prize-a", "prize-b"),
    (False, False),
)
staged = stage_prize_takes(physical, positions=(1,))

belief = PendingPrizeBatchJointBelief(
    groups=("A", "B", "Top"),
    face_up=(False,),
    pending_count=1,
    masses=((("Top", ("A",), ("B",)), 1.0),),
)
observers = ObserverPendingPrizeBatchBeliefs(
    ("prize-b",),
    (("actor", belief), ("opponent", belief)),
)
effect_hold = IdentityReference(
    "effect:before-hand",
    "prize-b",
    "the effect still names the card taken from Prizes",
)

staged_refs = collect_composite_identity_references(
    staged.physical.ledger,
    top_prize=staged.physical,
    pending_prize=staged,
    pending_beliefs=observers,
    effect_references=(effect_hold,),
)
assert tuple(row.reference_id for row in staged_refs) == (
    "deck_top",
    "prize_slot:0",
    "prize_pending:0",
    "belief:prize_pending:0",
    "effect:before-hand",
)
assert tuple(row.instance_id for row in staged_refs).count("prize-b") == 3
assert assess_dematerialization(
    staged.physical.ledger,
    "prize-b",
    references=staged_refs,
).blockers == (
    "reference:belief:prize_pending:0",
    "reference:effect:before-hand",
    "reference:prize_pending:0",
    "zone:prize_pending",
)

resolved = resolve_next_pending_prize(staged)
assert resolved.after.physical.ledger.instance("prize-b").zone == "hand"
after_physical_refs = collect_composite_identity_references(
    resolved.after.physical.ledger,
    pending_prize=resolved.after,
    pending_beliefs=observers,
)
assert tuple(row.reference_id for row in after_physical_refs) == (
    "deck_top",
    "prize_slot:0",
    "belief:prize_pending:0",
)
must_fail(
    lambda: dematerialize_if_safe(
        resolved.after.physical.ledger,
        "prize-b",
        references=after_physical_refs,
    ),
    "reference:belief:prize_pending:0",
)

after_belief = resolve_pending_instance_visibility(
    observers,
    instance_id="prize-b",
    visible_groups={"actor": "B"},
)
ready_refs = collect_composite_identity_references(
    resolved.after.physical.ledger,
    pending_prize=resolved.after,
    pending_beliefs=after_belief,
)
assert tuple(row.reference_id for row in ready_refs) == (
    "deck_top",
    "prize_slot:0",
)
released = dematerialize_if_safe(
    resolved.after.physical.ledger,
    "prize-b",
    references=ready_refs,
)
assert physical_zone_count(released, "hand") == 1
assert released.exchangeable.count("class:b", "hand") == 1
assert_conserved(starting, released)

must_fail(
    lambda: collect_composite_identity_references(
        resolved.after.physical.ledger,
        pending_prize=staged,
    ),
    "stale or different identity ledger",
)
must_fail(
    lambda: collect_composite_identity_references(
        resolved.after.physical.ledger,
        pending_prize=resolved.after,
        effect_references=(
            IdentityReference("deck_top", "prize-a", "collision"),
        ),
    ),
    "conflicting owners",
)
must_fail(
    lambda: collect_composite_identity_references(
        resolved.after.physical.ledger,
        effect_references=(
            IdentityReference("effect:orphan", "missing", "orphan reference"),
        ),
    ),
    "absent instance",
)

print({
    "staged_prize_references": tuple(row.reference_id for row in staged_refs),
    "physically_resolved_but_belief_live": True,
    "release_after_belief_resolution": True,
    "stale_snapshot_rejected": True,
    "conflicting_owner_rejected": True,
    "orphan_reference_rejected": True,
    "hand_count": physical_zone_count(released, "hand"),
    "total_cards_conserved": released.totals() == starting.totals(),
})
