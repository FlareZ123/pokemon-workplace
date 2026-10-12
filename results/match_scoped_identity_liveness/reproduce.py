"""Two-player identity reference namespace regression."""

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
    assert_conserved,
    materialize,
    move_instance,
)
from match_scoped_identity_liveness import (
    PlayerIdentityOwners,
    collect_match_identity_references,
)
from multicopy_zone_state import ZoneCountState
from top_prize_physical_bridge import TopPrizePhysicalState


def build_player(prefix):
    seed = IdentityLedger(ZoneCountState.from_mapping({
        (f"{prefix}:top", "deck"): 1,
        (f"{prefix}:prize", "prize"): 1,
        (f"{prefix}:held", "hand"): 1,
    }))
    current = seed
    for cls, name, zone, identity in (
        (f"{prefix}:top", "Top", "deck", "top"),
        (f"{prefix}:prize", "Prize", "prize", "prize-one"),
        (f"{prefix}:held", "Held", "hand", "hand-one"),
    ):
        current = materialize(
            current,
            card_class=cls,
            card_name=name,
            source_zone=zone,
            instance_id=identity,
        )
    current = move_instance(current, "top", "deck_top")
    return seed, TopPrizePhysicalState(
        current, "top", ("prize-one",), (False,)
    )


def rejects(fn, fragment):
    try:
        fn()
    except ValueError as exc:
        assert fragment in str(exc), str(exc)
    else:
        raise AssertionError(f"expected ValueError: {fragment}")


seed_a, side_a = build_player("Alice")
seed_b, side_b = build_player("Bob")
effect_a = IdentityReference(
    "effect:held",
    "hand-one",
    "Alice's enclosing effect still requires the exact copy",
)

match = collect_match_identity_references((
    PlayerIdentityOwners(
        "alice", side_a.ledger,
        top_prize=side_a,
        effect_references=(effect_a,),
    ),
    PlayerIdentityOwners(
        "bob", side_b.ledger,
        top_prize=side_b,
    ),
))
assert match.player_ids == ("alice", "bob")
assert tuple(ref.reference_id for ref in match.for_player("alice")) == (
    "deck_top", "prize_slot:0", "effect:held",
)
assert tuple(ref.reference_id for ref in match.for_player("bob")) == (
    "deck_top", "prize_slot:0",
)

# Both ledgers independently own card "top" and reference "deck_top".
for player_id, physical in (("alice", side_a), ("bob", side_b)):
    assert assess_dematerialization(
        physical.ledger,
        "top",
        references=match.for_player(player_id),
    ).blockers == ("reference:deck_top", "zone:deck_top")

# Alice's effect cannot block an unreferenced Bob hand card with the same ID.
assert assess_dematerialization(
    side_a.ledger,
    "hand-one",
    references=match.for_player("alice"),
).blockers == ("reference:effect:held",)
assert assess_dematerialization(
    side_b.ledger,
    "hand-one",
    references=match.for_player("bob"),
).safe
released_b = dematerialize_if_safe(
    side_b.ledger,
    "hand-one",
    references=match.for_player("bob"),
)
assert released_b.exchangeable.count("Bob:held", "hand") == 1
assert_conserved(seed_a, side_a.ledger)
assert_conserved(seed_b, released_b)

# Invalid player and same-player duplicates cannot silently merge ownership.
try:
    match.for_player("charlie")
except KeyError:
    pass
else:
    raise AssertionError("unknown player must raise")
rejects(
    lambda: collect_match_identity_references((
        PlayerIdentityOwners("alice", side_a.ledger, top_prize=side_a),
        PlayerIdentityOwners("alice", side_b.ledger, top_prize=side_b),
    )),
    "distinct",
)
rejects(
    lambda: collect_match_identity_references((
        PlayerIdentityOwners(
            "alice",
            move_instance(side_a.ledger, "hand-one", "discard"),
            top_prize=side_a,
        ),
        PlayerIdentityOwners("bob", side_b.ledger, top_prize=side_b),
    )),
    "stale or different",
)

print({
    "match_player_ids": match.player_ids,
    "alice_reference_ids": tuple(
        row.reference_id for row in match.for_player("alice")
    ),
    "bob_reference_ids": tuple(
        row.reference_id for row in match.for_player("bob")
    ),
    "local_id_collisions_safe": True,
    "cross_player_effect_isolation": True,
    "physical_totals_conserved": True,
})
