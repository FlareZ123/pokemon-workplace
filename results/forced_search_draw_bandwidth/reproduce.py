from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from search_draw_bandwidth import unrestricted_search_then_draw_to_n


computer_miss = unrestricted_search_then_draw_to_n(
    initial_hand_size=7,
    search_card_from_hand=True,
    discard_cost_from_hand=2,
    specified_count=1,
    deck_size_at_search=49,
    useful_units=0,
    later_hand_plays=1,
    draw_to=6,
)
assert computer_miss.selected_units == 1
assert computer_miss.useful_units == 0
assert computer_miss.forced_filler_units == 1
assert computer_miss.physical_hand_before_draw == 4
assert computer_miss.useful_only_hand_before_draw == 3
assert computer_miss.physical_draws == 2
assert computer_miss.useful_only_draws == 3
assert computer_miss.draw_overstatement == 1

rows = []
for initial in range(4, 11):
    outcome = unrestricted_search_then_draw_to_n(
        initial_hand_size=initial,
        search_card_from_hand=True,
        discard_cost_from_hand=2,
        specified_count=1,
        deck_size_at_search=49,
        useful_units=0,
        later_hand_plays=1,
        draw_to=6,
    )
    rows.append((initial, outcome.physical_draws, outcome.useful_only_draws, outcome.draw_overstatement))

assert rows == [
    (4, 5, 6, 1),
    (5, 4, 5, 1),
    (6, 3, 4, 1),
    (7, 2, 3, 1),
    (8, 1, 2, 1),
    (9, 0, 1, 1),
    (10, 0, 0, 0),
]

useful_hit = unrestricted_search_then_draw_to_n(
    initial_hand_size=7,
    search_card_from_hand=True,
    discard_cost_from_hand=2,
    specified_count=1,
    deck_size_at_search=49,
    useful_units=1,
    later_hand_plays=1,
    draw_to=6,
)
assert useful_hit.draw_overstatement == 0

empty = unrestricted_search_then_draw_to_n(
    initial_hand_size=7,
    search_card_from_hand=True,
    discard_cost_from_hand=2,
    specified_count=1,
    deck_size_at_search=0,
    useful_units=0,
    later_hand_plays=1,
    draw_to=6,
)
assert empty.selected_units == 0
assert empty.draw_overstatement == 0

print("computer_miss", computer_miss)
print("initial_hand_rows", rows)
print("useful_hit", useful_hit)
print("empty_deck", empty)
