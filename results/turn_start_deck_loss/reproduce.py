from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from identity_materialization import (
    IdentityLedger,
    assert_conserved,
    materialize,
    move_instance,
)
from multicopy_zone_state import ZoneCountState
from physical_deck_projection import physical_deck_size
from turn_start_deck_loss import (
    deck_empty_for_turn_start_loss,
    resolve_exact_top_turn_start_draw,
)
from top_prize_physical_bridge import TopPrizePhysicalState


Y = "class:Y"
initial = IdentityLedger(
    ZoneCountState.from_mapping({
        (Y, "deck"): 1,
    })
)
ledger = materialize(
    initial,
    card_class=Y,
    card_name="Y",
    source_zone="deck",
    instance_id="top-y",
)
ledger = move_instance(ledger, "top-y", "deck_top")
physical = TopPrizePhysicalState(
    ledger,
    "top-y",
    (),
    (),
)

exchangeable_deck_count = sum(
    count
    for _card_class, zone, count in physical.ledger.exchangeable.counts
    if zone == "deck"
)
assert exchangeable_deck_count == 0
assert physical_deck_size(physical.ledger) == 1
assert not deck_empty_for_turn_start_loss(physical.ledger)

turn_start = resolve_exact_top_turn_start_draw(physical)
assert turn_start is not None
after = turn_start.after
assert after.ledger.instance("top-y").zone == "hand"
assert physical_deck_size(after.ledger) == 0
assert deck_empty_for_turn_start_loss(after.ledger)
assert_conserved(initial, after.ledger)

empty = IdentityLedger(ZoneCountState.from_mapping({}))
assert deck_empty_for_turn_start_loss(empty)

print({
    "exchangeable_deck_count_before_draw": exchangeable_deck_count,
    "physical_deck_size_before_draw": physical_deck_size(physical.ledger),
    "turn_start_loss_before_draw": deck_empty_for_turn_start_loss(physical.ledger),
    "drawn_instance": turn_start.draw.drawn_instance_id,
    "physical_deck_size_after_draw": physical_deck_size(after.ledger),
    "deck_empty_after_draw": deck_empty_for_turn_start_loss(after.ledger),
    "copy_totals_preserved": after.ledger.totals() == initial.totals(),
})
