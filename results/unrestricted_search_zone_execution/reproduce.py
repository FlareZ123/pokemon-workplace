from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from multicopy_zone_state import ZoneCountState
from unrestricted_search_zone_execution import (
    PhysicalSelection,
    execute_unrestricted_fixed_search,
)


def expect_value_error(fn) -> None:
    try:
        fn()
    except ValueError:
        return
    raise AssertionError("expected ValueError")


computer = ZoneCountState.from_mapping({
    ("fallback_a", "deck"): 1,
    ("fallback_b", "deck"): 1,
    ("other", "hand"): 3,
})
computer_after = execute_unrestricted_fixed_search(
    computer,
    (PhysicalSelection("fallback_a", 1, 0),),
    specified_count=1,
    destination="hand",
)
assert computer_after.selected_units == 1
assert computer_after.useful_units == 0
assert computer_after.after.count("fallback_a", "deck") == 0
assert computer_after.after.count("fallback_a", "hand") == 1

expect_value_error(lambda: execute_unrestricted_fixed_search(
    computer, (), specified_count=1, destination="hand"
))

mallow = ZoneCountState.from_mapping({
    ("desired", "deck"): 1,
    ("filler", "deck"): 2,
    ("other", "hand"): 4,
})
first = execute_unrestricted_fixed_search(
    mallow,
    (
        PhysicalSelection("desired", 1, 1),
        PhysicalSelection("filler", 1, 0),
    ),
    specified_count=2,
    destination="deck_top",
    top_order=("desired", "filler"),
)
second = execute_unrestricted_fixed_search(
    mallow,
    (
        PhysicalSelection("desired", 1, 1),
        PhysicalSelection("filler", 1, 0),
    ),
    specified_count=2,
    destination="deck_top",
    top_order=("filler", "desired"),
)
assert first.selected_units == 2
assert first.useful_units == 1
assert first.after == second.after
assert first.top_order != second.top_order
assert first.after.count("desired", "deck_top") == 1
assert first.after.count("filler", "deck_top") == 1
assert first.after.count("filler", "deck") == 1

expect_value_error(lambda: execute_unrestricted_fixed_search(
    mallow,
    (PhysicalSelection("desired", 1, 1),),
    specified_count=2,
    destination="deck_top",
    top_order=("desired",),
))

short_deck = ZoneCountState.from_mapping({("only", "deck"): 1})
short_after = execute_unrestricted_fixed_search(
    short_deck,
    (PhysicalSelection("only", 1, 0),),
    specified_count=2,
    destination="hand",
)
assert short_after.selected_units == 1

print({
    "computer_selected": computer_after.selected_units,
    "computer_useful": computer_after.useful_units,
    "mallow_selected": first.selected_units,
    "mallow_useful": first.useful_units,
    "same_zone_counts_different_top_order": first.after == second.after and first.top_order != second.top_order,
    "short_deck_selected": short_after.selected_units,
})
