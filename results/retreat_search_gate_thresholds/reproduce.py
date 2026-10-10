"""Typed hand-payment thresholds after an Energy-returning Retreat."""
from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from discard_cost_witness import DiscardCandidate, enumerate_discard_selections
from discard_search_item_catalog import scan_discard_search_items
from multicopy_zone_state import ZoneCountState


def can_pay(cost: int, returned: int, spares: int, *, payment_kind: str) -> bool:
    """Model the exact eligible hand classes, not the raw total hand size."""
    assert returned in (1, 2)
    assert spares >= 0
    mapping = {
        ("played_item", "hand"): 1,
        ("returned_dce", "hand"): 1,
    }
    if returned == 2:
        mapping[("returned_basic", "hand")] = 1
    if spares:
        mapping[("generic_non_item_fodder", "hand")] = spares

    state = ZoneCountState.from_mapping(mapping)
    # Cram-o-matic's other-Item gate cannot be funded by returned Energy or
    # other non-Item fodder, despite all those cards being in hand.
    eligible = (
        (DiscardCandidate("returned_dce"),
         DiscardCandidate("returned_basic"),
         DiscardCandidate("generic_non_item_fodder"))
        if payment_kind == "any" else ()
    )
    possible = enumerate_discard_selections(state, eligible, cost)
    return bool(possible)


def main() -> None:
    items = scan_discard_search_items(ROOT / "resources")
    by_name = {row.name: row for row in items}
    assert len(items) == 10
    assert by_name["Quick Ball"].discard_cost == 1
    assert by_name["Ultra Ball"].discard_cost == 2
    assert by_name["Secret Box"].discard_cost == 3
    assert by_name["Cram-o-matic"].payment_kind == "item"

    unlocked: dict[int, set[str]] = {}
    checked = 0
    for item in items:
        assert item.payment_kind in ("any", "item")
        for spares in range(4):
            smaller = can_pay(
                item.discard_cost, 1, spares, payment_kind=item.payment_kind
            )
            larger = can_pay(
                item.discard_cost, 2, spares, payment_kind=item.payment_kind
            )
            assert not (smaller and not larger), (item.name, spares)
            if item.payment_kind == "any":
                assert smaller == (spares + 1 >= item.discard_cost)
                assert larger == (spares + 2 >= item.discard_cost)
            else:
                assert not smaller and not larger
            if larger and not smaller:
                unlocked.setdefault(spares, set()).add(item.name)
            checked += 1

    assert unlocked == {
        0: {"Computer Search", "Electromagnetic Radar",
            "Fiery Flint", "Ultra Ball"},
        1: {"Secret Box"},
    }, unlocked

    print("Retreat-to-discard-search payment threshold atlas: PASS")
    print({"item_names": len(items), "item_spare_cases": checked,
           "unlocked_with_zero_spares": sorted(unlocked[0]),
           "unlocked_with_one_spare": sorted(unlocked[1])})
    print("Cram-o-matic requires an Item payment; returned Energy is ineligible")


if __name__ == "__main__":
    main()
