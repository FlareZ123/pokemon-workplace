from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from deck_search_shuffle_topology import SearchableDeckPhysicalState
from identity_materialization import IdentityLedger, assert_conserved
from multicopy_zone_state import ZoneCountState
from physical_deck_projection import physical_deck_size
from physical_zone_count import physical_hand_size
from turn_start_deck_loss import (
    deck_empty_for_turn_start_loss,
    resolve_sampled_turn_start_draw,
)


A = "class:A"
F = "class:filler"
initial = IdentityLedger(
    ZoneCountState.from_mapping({
        (A, "deck"): 1,
        (F, "deck"): 2,
    })
)
state = SearchableDeckPhysicalState(initial, (), ())

assert physical_deck_size(state.ledger) == 3
draw = resolve_sampled_turn_start_draw(
    state,
    card_class=A,
    card_name="A",
    instance_id="drawn-a",
)
assert draw is not None
assert draw.drawn_instance_id == "drawn-a"
assert draw.after.ledger.instance("drawn-a").zone == "hand"
assert physical_deck_size(draw.after.ledger) == 2
assert physical_hand_size(draw.after.ledger) == 1
assert draw.after.ledger.exchangeable.count(A, "deck") == 0
assert draw.after.ledger.exchangeable.count(F, "deck") == 2
assert_conserved(initial, draw.after.ledger)

empty = SearchableDeckPhysicalState(
    IdentityLedger(ZoneCountState.from_mapping({})),
    (),
    (),
)
assert deck_empty_for_turn_start_loss(empty.ledger)
assert resolve_sampled_turn_start_draw(
    empty,
    card_class=A,
    card_name="A",
    instance_id="impossible",
) is None

try:
    resolve_sampled_turn_start_draw(
        draw.after,
        card_class=A,
        card_name="A",
        instance_id="second-a",
    )
except ValueError:
    pass
else:
    raise AssertionError("sampling an unavailable card class must fail")

print({
    "physical_deck_before": physical_deck_size(state.ledger),
    "drawn_instance": draw.drawn_instance_id,
    "physical_deck_after": physical_deck_size(draw.after.ledger),
    "physical_hand_after": physical_hand_size(draw.after.ledger),
    "empty_deck_returns_no_draw": True,
    "unavailable_sample_rejected": True,
    "copy_totals_preserved": draw.after.ledger.totals() == initial.totals(),
})
