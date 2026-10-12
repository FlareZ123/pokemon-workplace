"""Regression for scoped, reference-gated, lifetime-safe match release."""

from dataclasses import replace
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from identity_instance_provenance import (
    begin_identity_provenance,
    materialize_unique,
)
from identity_liveness import IdentityReference
from identity_materialization import (
    IdentityLedger, assert_conserved, materialize, move_instance,
)
from match_identity_release import MatchIdentityReleaseState, release_match_identity
from match_scoped_identity_liveness import PlayerIdentityOwners
from multicopy_zone_state import ZoneCountState
from top_prize_physical_bridge import TopPrizePhysicalState


def make_side(prefix):
    original = IdentityLedger(ZoneCountState.from_mapping({
        (f"{prefix}:top", "deck"): 1,
        (f"{prefix}:prize", "prize"): 1,
        (f"{prefix}:hand", "hand"): 1,
    }))
    ledger = original
    for kind, zone, instance_id in (
        ("top", "deck", "top"),
        ("prize", "prize", "prize"),
        ("hand", "hand", "held"),
    ):
        ledger = materialize(
            ledger,
            card_class=f"{prefix}:{kind}",
            card_name=kind,
            source_zone=zone,
            instance_id=instance_id,
        )
    ledger = move_instance(ledger, "top", "deck_top")
    topology = TopPrizePhysicalState(ledger, "top", ("prize",), (False,))
    return original, topology


def must_reject(action, fragment):
    try:
        action()
    except ValueError as exc:
        assert fragment in str(exc), str(exc)
    else:
        raise AssertionError(f"expected error containing {fragment}")


seed_a, physical_a = make_side("A")
seed_b, physical_b = make_side("B")
hold = IdentityReference(
    "effect:A", "held", "A's effect refers to its exact hand instance"
)
owner_a = PlayerIdentityOwners(
    "A", physical_a.ledger, top_prize=physical_a,
    effect_references=(hold,),
)
owner_b = PlayerIdentityOwners(
    "B", physical_b.ledger, top_prize=physical_b,
)
state = MatchIdentityReleaseState((
    (owner_a, begin_identity_provenance(owner_a.ledger)),
    (owner_b, begin_identity_provenance(owner_b.ledger)),
))

must_reject(
    lambda: release_match_identity(state, player_id="A", instance_id="held"),
    "reference:effect:A",
)
assert state.owner_for("A").ledger.instance("held").zone == "hand"

released_b = release_match_identity(
    state, player_id="B", instance_id="held",
)
assert released_b.owner_for("B").ledger.exchangeable.count("B:hand", "hand") == 1
assert released_b.owner_for("B").top_prize.ledger == released_b.owner_for("B").ledger
assert released_b.provenance_for("B").ever_issued == frozenset({
    "top", "prize", "held",
})
assert released_b.owner_for("A") == owner_a

must_reject(
    lambda: materialize_unique(
        released_b.provenance_for("B"),
        card_class="B:hand", card_name="hand",
        source_zone="hand", instance_id="held",
    ),
    "already issued",
)

# The effect owner is explicitly removed after its external effect has ended.
a_after_effect = replace(
    released_b.owner_for("A"), effect_references=(),
)
released_once = replace(
    released_b,
    players=(
        (a_after_effect, released_b.provenance_for("A")),
        (released_b.owner_for("B"), released_b.provenance_for("B")),
    ),
)
both_released = release_match_identity(
    released_once, player_id="A", instance_id="held",
)
assert both_released.owner_for("A").ledger.exchangeable.count("A:hand", "hand") == 1
assert both_released.owner_for("A").top_prize.ledger == both_released.owner_for("A").ledger
assert_conserved(seed_a, both_released.owner_for("A").ledger)
assert_conserved(seed_b, both_released.owner_for("B").ledger)

must_reject(
    lambda: MatchIdentityReleaseState((
        (owner_a, released_b.provenance_for("B")),
        (owner_b, begin_identity_provenance(owner_b.ledger)),
    )),
    "provenance ledger mismatch",
)
try:
    release_match_identity(state, player_id="C", instance_id="held")
except KeyError:
    pass
else:
    raise AssertionError("unknown player must be rejected")

print({
    "cross_player_isolated_release": True,
    "live_effect_blocks_atomic_release": True,
    "provenance_prevents_id_reuse": True,
    "topology_ledger_rebound_after_release": True,
    "independent_player_totals_conserved": True,
})
