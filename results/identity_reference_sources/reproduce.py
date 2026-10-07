from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from identity_liveness import assess_dematerialization
from identity_materialization import (
    IdentityLedger,
    materialize,
    move_instance,
)
from identity_reference_sources import (
    pending_prize_identity_references,
    top_prize_identity_references,
)
from multicopy_zone_state import ZoneCountState
from prize_pending_take import stage_prize_takes
from top_prize_physical_bridge import TopPrizePhysicalState


TOP = "class:top"
A = "class:A"
B = "class:B"

initial = IdentityLedger(
    ZoneCountState.from_mapping({
        (TOP, "deck"): 1,
        (A, "prize"): 1,
        (B, "prize"): 1,
    })
)
ledger = materialize(
    initial,
    card_class=TOP,
    card_name="Top",
    source_zone="deck",
    instance_id="top-1",
)
ledger = move_instance(ledger, "top-1", "deck_top")
ledger = materialize(
    ledger,
    card_class=A,
    card_name="A",
    source_zone="prize",
    instance_id="prize-a",
)
ledger = materialize(
    ledger,
    card_class=B,
    card_name="B",
    source_zone="prize",
    instance_id="prize-b",
)
physical = TopPrizePhysicalState(
    ledger,
    "top-1",
    ("prize-a", "prize-b"),
    (False, False),
)

refs = top_prize_identity_references(physical)
assert tuple(row.reference_id for row in refs) == (
    "deck_top",
    "prize_slot:0",
    "prize_slot:1",
)

broad_zones = frozenset({"deck_top", "prize", "prize_pending"})
top_assessment = assess_dematerialization(
    physical.ledger,
    "top-1",
    references=refs,
    exchangeable_zones=broad_zones,
)
assert not top_assessment.safe
assert top_assessment.blockers == ("reference:deck_top",)

prize_assessment = assess_dematerialization(
    physical.ledger,
    "prize-a",
    references=refs,
    exchangeable_zones=broad_zones,
)
assert not prize_assessment.safe
assert prize_assessment.blockers == ("reference:prize_slot:0",)

pending = stage_prize_takes(
    physical,
    positions=(1,),
)
pending_refs = pending_prize_identity_references(pending)
assert tuple(row.reference_id for row in pending_refs) == (
    "deck_top",
    "prize_slot:0",
    "prize_pending:0",
)
assert tuple(row.instance_id for row in pending_refs) == (
    "top-1",
    "prize-a",
    "prize-b",
)

pending_assessment = assess_dematerialization(
    pending.physical.ledger,
    "prize-b",
    references=pending_refs,
    exchangeable_zones=broad_zones,
)
assert not pending_assessment.safe
assert pending_assessment.blockers == ("reference:prize_pending:0",)

print({
    "topology_reference_ids": tuple(row.reference_id for row in refs),
    "pending_reference_ids": tuple(row.reference_id for row in pending_refs),
    "top_blocker": top_assessment.blockers,
    "prize_blocker": prize_assessment.blockers,
    "pending_blocker": pending_assessment.blockers,
})
