"""Reproduce the BW-onward discard-search Item catalog."""

from __future__ import annotations
from collections import Counter
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from discard_search_item_catalog import (
    distinct_name_payment_pairs,
    scan_discard_search_items,
)


EXPECTED = {
    "Computer Search": (2, "any", False, True),
    "Cram-o-matic": (1, "item", True, False),
    "Earthen Vessel": (1, "any", False, False),
    "Electromagnetic Radar": (2, "any", False, False),
    "Fiery Flint": (2, "any", False, False),
    "Mysterious Treasure": (1, "any", False, False),
    "Quick Ball": (1, "any", False, False),
    "Secret Box": (3, "any", False, True),
    "Techno Radar": (1, "any", False, False),
    "Ultra Ball": (2, "any", False, False),
}


def main() -> None:
    items = scan_discard_search_items(ROOT / "resources")
    actual = {
        item.name: (
            item.discard_cost,
            item.payment_kind,
            item.conditional_search,
            item.ace_spec,
        )
        for item in items
    }
    assert actual == EXPECTED

    deterministic = tuple(
        item for item in items if not item.conditional_search
    )
    assert len(items) == 10
    assert len(deterministic) == 9
    assert Counter(item.discard_cost for item in deterministic) == {
        1: 4,
        2: 4,
        3: 1,
    }

    pairs = distinct_name_payment_pairs(items)
    assert len(pairs) == 70
    assert ("Computer Search", "Secret Box") not in pairs
    assert ("Secret Box", "Computer Search") not in pairs
    assert ("Quick Ball", "Ultra Ball") in pairs
    assert ("Quick Ball", "Computer Search") in pairs

    print("discard-search Item names:", ", ".join(actual))
    print("deterministic candidates:", len(deterministic))
    print("ACE-SPEC-compatible distinct-name payment pairs:", len(pairs))


if __name__ == "__main__":
    main()
