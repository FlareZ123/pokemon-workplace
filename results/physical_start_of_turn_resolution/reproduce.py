from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from identity_materialization import IdentityLedger, materialize, move_instance
from multicopy_zone_state import ZoneCountState
from physical_start_of_turn_resolution import resolve_physical_start_of_turn_deck_out
from post_knockout_game_resolution import Outcome


TOP = "class:top"
with_top = IdentityLedger(
    ZoneCountState.from_mapping({
        (TOP, "deck"): 1,
    })
)
with_top = materialize(
    with_top,
    card_class=TOP,
    card_name="Top",
    source_zone="deck",
    instance_id="top-1",
)
with_top = move_instance(with_top, "top-1", "deck_top")

raw_exchangeable_deck = sum(
    count
    for _card_class, zone, count in with_top.exchangeable.counts
    if zone == "deck"
)
assert raw_exchangeable_deck == 0

continue_resolution = resolve_physical_start_of_turn_deck_out(
    player_ids=("A", "B"),
    current_turn_player="A",
    current_turn_player_ledger=with_top,
)
assert continue_resolution.outcome("A") == Outcome.CONTINUE
assert continue_resolution.outcome("B") == Outcome.CONTINUE

empty = IdentityLedger(ZoneCountState.from_mapping({}))
loss_resolution = resolve_physical_start_of_turn_deck_out(
    player_ids=("A", "B"),
    current_turn_player="A",
    current_turn_player_ledger=empty,
)
assert loss_resolution.outcome("A") == Outcome.LOSS
assert loss_resolution.outcome("B") == Outcome.WIN
assert loss_resolution.loss_count("A") == 1
assert loss_resolution.loss_count("B") == 0

print({
    "raw_exchangeable_deck_with_exact_top": raw_exchangeable_deck,
    "exact_top_turn_start_outcome": continue_resolution.outcome("A").value,
    "empty_deck_turn_start_outcome": loss_resolution.outcome("A").value,
    "opponent_outcome_on_deck_loss": loss_resolution.outcome("B").value,
})
