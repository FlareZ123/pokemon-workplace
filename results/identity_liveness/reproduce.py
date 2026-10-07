from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from identity_liveness import (
    IdentityReference,
    assess_dematerialization,
    dematerialize_if_safe,
)
from identity_materialization import (
    IdentityLedger,
    attach_instance,
    materialize,
    move_instance,
)
from multicopy_zone_state import ZoneCountState
from physical_zone_count import physical_zone_count


X = "class:X"
R = "class:returned-card"
Y = "class:Y"
A = "class:A"
E = "class:energy"

ledger = IdentityLedger(
    ZoneCountState.from_mapping({
        (X, "hand"): 1,
        (R, "hand"): 1,
        (Y, "deck"): 1,
        (A, "prize"): 1,
        (E, "hand"): 1,
    })
)

ledger = materialize(
    ledger,
    card_class=X,
    card_name="X",
    source_zone="hand",
    instance_id="x1",
)
ledger = materialize(
    ledger,
    card_class=R,
    card_name="Returned card",
    source_zone="hand",
    instance_id="r1",
)
ledger = materialize(
    ledger,
    card_class=Y,
    card_name="Y",
    source_zone="deck",
    instance_id="top-y",
)
ledger = move_instance(ledger, "top-y", "deck_top")
ledger = materialize(
    ledger,
    card_class=A,
    card_name="A",
    source_zone="prize",
    instance_id="prize-a",
)
ledger = materialize(
    ledger,
    card_class=E,
    card_name="Energy",
    source_zone="hand",
    instance_id="energy-1",
)
ledger = attach_instance(ledger, "energy-1", "pokemon-1")

effect_reference = IdentityReference(
    "effect:return-target",
    "r1",
    "the enclosing effect still refers to the exact moved card",
)

assert assess_dematerialization(ledger, "x1").safe

held = assess_dematerialization(
    ledger,
    "r1",
    references=(effect_reference,),
)
assert not held.safe
assert held.blockers == ("reference:effect:return-target",)

top = assess_dematerialization(ledger, "top-y")
assert not top.safe
assert top.blockers == ("zone:deck_top",)

prize = assess_dematerialization(ledger, "prize-a")
assert not prize.safe
assert prize.blockers == ("zone:prize",)

attached = assess_dematerialization(ledger, "energy-1")
assert not attached.safe
assert "zone:attached" in attached.blockers
assert "attached_to:pokemon-1" in attached.blockers

totals_before = ledger.totals()
hand_before = physical_zone_count(ledger, "hand")

ledger = dematerialize_if_safe(ledger, "x1")
assert ledger.totals() == totals_before
assert physical_zone_count(ledger, "hand") == hand_before
assert ledger.exchangeable.count(X, "hand") == 1

try:
    dematerialize_if_safe(
        ledger,
        "r1",
        references=(effect_reference,),
    )
except ValueError:
    pass
else:
    raise AssertionError("live reference should block dematerialization")

ledger = dematerialize_if_safe(ledger, "r1")
assert ledger.totals() == totals_before
assert physical_zone_count(ledger, "hand") == hand_before
assert ledger.exchangeable.count(R, "hand") == 1

print({
    "safe_unreferenced_hand_instance": True,
    "held_reference_blockers": held.blockers,
    "deck_top_blockers": top.blockers,
    "prize_blockers": prize.blockers,
    "attached_blockers": attached.blockers,
    "physical_hand_size_preserved": physical_zone_count(ledger, "hand"),
    "copy_totals_preserved": ledger.totals() == totals_before,
})
