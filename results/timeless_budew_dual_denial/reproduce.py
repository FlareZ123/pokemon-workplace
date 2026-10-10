"""Reproduce compound Regidrago Budew history cover + Item lock effects.

Composes earlier validated temporal history and Shadow Rider coarse payload
routing engines. Counts state-space reachability, not game win probability.
"""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

from shadow_rider_regidrago_counter_als import (  # noqa: E402
    PayloadZone, RoutingResources, find_payload_route
)
from results.regidrago_attack_history_evasion.reproduce import (  # noqa: E402
    cover_with_budew
)


def card(set_id: str, card_id: str) -> dict:
    cards = json.loads(
        (ROOT / "resources" / "cards" / "en" / f"{set_id}.json")
        .read_text(encoding="utf-8")
    )
    return next(row for row in cards if row["id"] == card_id)


def reachable(resources: RoutingResources) -> dict:
    return {
        (m.value, d.value): route.actions
        for m in PayloadZone
        for d in PayloadZone
        if (route := find_payload_route(m, d, resources)) is not None
    }


def main() -> None:
    budew = card("sv8pt5", "sv8pt5-4")
    attack = next(a for a in budew["attacks"] if a["name"] == "Itchy Pollen")
    assert attack["cost"] == ["Free"]
    assert "can't play any Item cards from their hand" in attack["text"]
    assert "opponent's next turn" in attack["text"]

    covered = cover_with_budew()
    assert covered.last_attack_for("P1") == "budew:itchy-pollen"

    open_items = reachable(RoutingResources())
    item_lock = reachable(RoutingResources(item_play=False))
    locked_supporter_reserved = reachable(
        RoutingResources(item_play=False, tulip=0)
    )
    assert len(open_items) == 15
    assert set(open_items) == {
        (m.value, d.value) for m in PayloadZone for d in PayloadZone
    } - {("prize", "prize")}
    assert item_lock == {
        ("hand", "discard"): (),
        ("discard", "discard"): ("Tulip: recover Mimikyu",),
    }
    assert locked_supporter_reserved == {("hand", "discard"): ()}

    print(json.dumps({
        "regidrago_last_attack_after_bonus_budew": covered.last_attack_for("P1"),
        "coarse_payload_pairs": 16,
        "pairs_reachable_items_available": len(open_items),
        "pairs_reachable_budew_item_lock": len(item_lock),
        "pairs_reachable_item_lock_and_guzma_supporter_reserved":
            len(locked_supporter_reserved),
        "item_lock_surviving_routes": [
            {"mimikyu": m, "dialga": d, "actions": list(actions)}
            for (m, d), actions in item_lock.items()
        ],
    }, indent=2))


if __name__ == "__main__":
    main()
