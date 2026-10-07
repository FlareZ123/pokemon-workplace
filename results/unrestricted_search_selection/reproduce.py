from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from unrestricted_search_selection import (
    catalog_unrestricted_fixed_searches,
    enumerate_unrestricted_fixed_selections,
    restricted_fixed_bounds,
    summarize_catalog,
    unrestricted_fixed_bounds,
)


resources = ROOT / "resources"
rows = catalog_unrestricted_fixed_searches(resources)
summary = summarize_catalog(rows)

assert summary == {
    "print_effects": 69,
    "unique_names": 43,
    "source_kind_counts": {"ability": 22, "attack": 27, "trainer_rule": 20},
    "specified_count_counts": {"1": 63, "2": 6},
    "destination_counts": {"hand": 56, "top_deck": 13},
}

by_id = {row.card_id: row for row in rows}
assert by_id["bw7-137"].name == "Computer Search"
assert by_id["bw7-137"].specified_count == 1
assert by_id["sm2-127"].name == "Mallow"
assert by_id["sm2-127"].specified_count == 2
assert by_id["sv8-135"].name == "Dialga"
assert by_id["sv8-135"].specified_count == 2

assert unrestricted_fixed_bounds(specified_count=1, deck_size=49).minimum == 1
assert unrestricted_fixed_bounds(specified_count=1, deck_size=49).maximum == 1
assert unrestricted_fixed_bounds(specified_count=2, deck_size=49).minimum == 2
assert unrestricted_fixed_bounds(specified_count=2, deck_size=1).minimum == 1
assert unrestricted_fixed_bounds(specified_count=2, deck_size=0).minimum == 0

assert restricted_fixed_bounds(specified_count=1, eligible_count=4).minimum == 0
assert restricted_fixed_bounds(specified_count=1, eligible_count=4).maximum == 1

one_card = enumerate_unrestricted_fixed_selections(
    (("desired", 0), ("fallback_a", 1), ("fallback_b", 1)),
    specified_count=1,
)
assert {w.selected_counts for w in one_card} == {(0, 0, 1), (0, 1, 0)}
assert all(w.selected_total == 1 for w in one_card)

two_card = enumerate_unrestricted_fixed_selections(
    (("desired", 1), ("filler", 2)),
    specified_count=2,
)
assert {w.selected_counts for w in two_card} == {(0, 2), (1, 1)}
assert all(w.selected_total == 2 for w in two_card)

print(summary)
print("computer_search_fallback_witnesses", [w.selected_counts for w in one_card])
print("two_card_forced_filler_witnesses", [w.selected_counts for w in two_card])
