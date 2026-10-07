from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from deck_search_shuffle_topology import SearchableDeckPhysicalState
from identity_materialization import IdentityLedger, materialize, move_instance
from multicopy_zone_state import ZoneCountState
from physical_deck_projection import physical_deck_size
from physical_zone_count import physical_hand_size
from post_knockout_game_resolution import Outcome
from top_prize_physical_bridge import TopPrizePhysicalState
from turn_start_phase import (
    begin_turn_with_exact_top,
    begin_turn_with_sampled_draw,
)


TOP = "class:top"
exact_ledger = IdentityLedger(
    ZoneCountState.from_mapping({
        (TOP, "deck"): 1,
    })
)
exact_ledger = materialize(
    exact_ledger,
    card_class=TOP,
    card_name="Top",
    source_zone="deck",
    instance_id="top-1",
)
exact_ledger = move_instance(exact_ledger, "top-1", "deck_top")
exact = TopPrizePhysicalState(exact_ledger, "top-1", (), ())

exact_result = begin_turn_with_exact_top(
    exact,
    player_ids=("A", "B"),
    current_turn_player="A",
)
assert exact_result.resolution.outcome("A") == Outcome.CONTINUE
assert exact_result.after_draw is not None
assert exact_result.drawn_instance_id == "top-1"
assert physical_deck_size(exact_result.after_draw.ledger) == 0
assert physical_hand_size(exact_result.after_draw.ledger) == 1

unordered_ledger = IdentityLedger(
    ZoneCountState.from_mapping({
        ("class:A", "deck"): 1,
        ("class:F", "deck"): 1,
    })
)
unordered = SearchableDeckPhysicalState(unordered_ledger, (), ())
unordered_result = begin_turn_with_sampled_draw(
    unordered,
    player_ids=("A", "B"),
    current_turn_player="A",
    card_class="class:A",
    card_name="A",
    instance_id="drawn-a",
)
assert unordered_result.resolution.outcome("A") == Outcome.CONTINUE
assert unordered_result.after_draw is not None
assert unordered_result.drawn_instance_id == "drawn-a"
assert physical_deck_size(unordered_result.after_draw.ledger) == 1

empty = SearchableDeckPhysicalState(
    IdentityLedger(ZoneCountState.from_mapping({})),
    (),
    (),
)
empty_result = begin_turn_with_sampled_draw(
    empty,
    player_ids=("A", "B"),
    current_turn_player="A",
)
assert empty_result.resolution.outcome("A") == Outcome.LOSS
assert empty_result.resolution.outcome("B") == Outcome.WIN
assert empty_result.after_draw is None
assert empty_result.drawn_instance_id is None

print({
    "exact_top_outcome": exact_result.resolution.outcome("A").value,
    "exact_top_drawn": exact_result.drawn_instance_id,
    "unordered_outcome": unordered_result.resolution.outcome("A").value,
    "unordered_drawn": unordered_result.drawn_instance_id,
    "empty_outcome": empty_result.resolution.outcome("A").value,
    "empty_performs_draw": empty_result.drawn_instance_id is not None,
})
