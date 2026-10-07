from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.build_expanded_legality_baseline import load_json
from tools.search_action_legality import (
    SearchState,
    build_trainer_search_inventory,
    constrained_search_to_bench,
    constrained_search_to_hand,
    public_zone_up_to_retrieval,
)


def card_by_id(resources: Path, card_id: str) -> dict:
    set_id = card_id.split("-")[0]
    for card in load_json(resources / "cards" / "en" / f"{set_id}.json"):
        if card["id"] == card_id:
            return card
    raise AssertionError(card_id)


def main() -> None:
    resources = Path("resources")

    targetless = constrained_search_to_hand(
        SearchState(deck_cards=40, eligible_targets=0), action_class="item"
    )
    assert targetless.legal
    assert targetless.inspected_full_deck
    assert not targetless.target_moved
    assert targetless.next_state.exact_prize_knowledge

    empty_deck = constrained_search_to_hand(
        SearchState(deck_cards=0, eligible_targets=0), action_class="item"
    )
    assert not empty_deck.legal
    assert not empty_deck.inspected_full_deck

    bench_targetless = constrained_search_to_bench(
        SearchState(deck_cards=40, eligible_targets=0, bench_slots=1),
        action_class="item",
    )
    assert bench_targetless.legal
    assert bench_targetless.inspected_full_deck
    assert bench_targetless.next_state.exact_prize_knowledge

    full_bench = constrained_search_to_bench(
        SearchState(deck_cards=40, eligible_targets=3, bench_slots=0),
        action_class="item",
    )
    assert not full_bench.legal
    assert not full_bench.inspected_full_deck
    assert not full_bench.next_state.exact_prize_knowledge

    attack_full_bench = constrained_search_to_bench(
        SearchState(deck_cards=40, eligible_targets=3, bench_slots=0),
        action_class="attack",
    )
    assert attack_full_bench.legal
    assert not attack_full_bench.inspected_full_deck

    attack_empty_deck = constrained_search_to_hand(
        SearchState(deck_cards=0, eligible_targets=0), action_class="attack"
    )
    assert attack_empty_deck.legal
    assert not attack_empty_deck.inspected_full_deck

    assert not public_zone_up_to_retrieval(0, action_class="item")
    assert public_zone_up_to_retrieval(1, action_class="item")
    assert public_zone_up_to_retrieval(0, action_class="attack")

    nest_ball = card_by_id(resources, "sv1-181")
    assert any(
        "Search your deck for a Basic Pokémon and put it onto your Bench" in rule
        for rule in nest_ball["rules"]
    )

    energy_retrieval = card_by_id(resources, "sv1-171")
    assert any(
        "Put up to 2 Basic Energy cards from your discard pile into your hand" in rule
        for rule in energy_retrieval["rules"]
    )

    clavell = card_by_id(resources, "sv2-177")
    assert any("Search your deck for up to 3 Basic Pokémon" in rule for rule in clavell["rules"])

    porygon = card_by_id(resources, "xy7-64")
    data_check = next(attack for attack in porygon["attacks"] if attack["name"] == "Data Check")
    assert data_check["text"] == "Look through your deck. Shuffle your deck afterward."

    inventory = build_trainer_search_inventory(resources)
    assert inventory["distinct_trainer_search_variants"] == 179
    assert inventory["direct_to_bench_variants"] == 17

    print(json.dumps({
        "targetless_nonempty_search": {
            "legal": targetless.legal,
            "inspected_full_deck": targetless.inspected_full_deck,
            "exact_prize_knowledge": targetless.next_state.exact_prize_knowledge,
        },
        "empty_deck_search": {
            "legal": empty_deck.legal,
            "inspected_full_deck": empty_deck.inspected_full_deck,
        },
        "full_bench_direct_search": {
            "trainer_legal": full_bench.legal,
            "attack_legal": attack_full_bench.legal,
            "attack_inspected_full_deck": attack_full_bench.inspected_full_deck,
        },
        "inventory": inventory,
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
