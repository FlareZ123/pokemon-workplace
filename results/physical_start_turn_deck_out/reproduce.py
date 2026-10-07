from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from identity_materialization import IdentityLedger, materialize, move_instance
from multicopy_zone_state import ZoneCountState
from physical_deck_projection import draw_exact_top_to_hand, physical_deck_size
from physical_start_turn_deck_out import resolve_physical_start_of_turn_deck_out
from post_knockout_game_resolution import Outcome
from top_prize_physical_bridge import TopPrizePhysicalState

TOP = "class:last-card"

ledger = IdentityLedger(
    ZoneCountState.from_mapping({(TOP, "deck"): 1})
)
ledger = materialize(
    ledger,
    card_class=TOP,
    card_name="Last Card",
    source_zone="deck",
    instance_id="last-top",
)
ledger = move_instance(ledger, "last-top", "deck_top")
physical = TopPrizePhysicalState(ledger, "last-top", (), ())

assert physical_deck_size(physical.ledger) == 1
assert sum(
    count
    for _card, zone, count in physical.ledger.exchangeable.counts
    if zone == "deck"
) == 0

before_draw = resolve_physical_start_of_turn_deck_out(
    player_ids=("P1", "P2"),
    current_turn_player="P1",
    current_turn_player_ledger=physical.ledger,
)
assert before_draw.outcome("P1") == Outcome.CONTINUE
assert before_draw.outcome("P2") == Outcome.CONTINUE

draw = draw_exact_top_to_hand(physical)
assert physical_deck_size(draw.after.ledger) == 0
after_draw_future_turn = resolve_physical_start_of_turn_deck_out(
    player_ids=("P1", "P2"),
    current_turn_player="P1",
    current_turn_player_ledger=draw.after.ledger,
)
assert after_draw_future_turn.outcome("P1") == Outcome.LOSS
assert after_draw_future_turn.outcome("P2") == Outcome.WIN

print({
    "raw_exchangeable_deck_before": 0,
    "physical_deck_before": physical_deck_size(physical.ledger),
    "start_turn_before_draw": before_draw.outcome("P1").value,
    "physical_deck_after_draw": physical_deck_size(draw.after.ledger),
    "future_start_turn_after_empty": after_draw_future_turn.outcome("P1").value,
})
