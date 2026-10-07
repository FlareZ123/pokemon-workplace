"""Reproduce the physical deck-search/shuffle top boundary."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from deck_search_shuffle_topology import (
    finish_shuffle_with_sampled_top,
    open_deck_for_search,
    search_deck_card_to_play,
)
from identity_materialization import CardInstance, IdentityLedger, assert_conserved
from multicopy_zone_state import ZoneCountState
from top_prize_physical_bridge import TopPrizePhysicalState


def main() -> None:
    ledger = IdentityLedger(
        ZoneCountState.from_mapping(
            {
                ("A", "deck"): 1,
                ("B", "deck"): 1,
            }
        ),
        (
            CardInstance("prize", "P", "Prize", "prize"),
            CardInstance("top-c", "C", "Former top", "deck_top"),
        ),
    )
    physical = TopPrizePhysicalState(
        ledger,
        "top-c",
        ("prize",),
        (False,),
    )

    opened = open_deck_for_search(physical)
    assert all(row.zone != "deck_top" for row in opened.ledger.instances)
    assert opened.ledger.exchangeable.count("A", "deck") == 1
    assert opened.ledger.exchangeable.count("B", "deck") == 1
    assert opened.ledger.exchangeable.count("C", "deck") == 1
    assert_conserved(physical.ledger, opened.ledger)

    # The former top is now a legal deck-search target. A model that looked
    # only at pre-existing exchangeable deck counts would have missed it.
    searched = search_deck_card_to_play(
        opened,
        card_class="C",
        card_name="Former top",
        instance_id="searched-c",
        board_object_id="bench-c",
    )
    searched_c = searched.ledger.instance("searched-c")
    assert searched_c.zone == "in_play"
    assert searched_c.board_object_id == "bench-c"
    assert searched.ledger.exchangeable.count("C", "deck") == 0
    assert_conserved(physical.ledger, searched.ledger)

    shuffled = finish_shuffle_with_sampled_top(
        searched,
        card_class="A",
        card_name="A",
        instance_id="new-top-a",
    )
    assert shuffled.top_instance_id == "new-top-a"
    assert shuffled.ledger.instance("new-top-a").zone == "deck_top"
    assert shuffled.ledger.exchangeable.count("A", "deck") == 0
    assert shuffled.ledger.exchangeable.count("B", "deck") == 1
    assert shuffled.prize_instance_ids == ("prize",)
    assert_conserved(physical.ledger, shuffled.ledger)

    print("Deck-search/shuffle top topology regressions passed")


if __name__ == "__main__":
    main()
