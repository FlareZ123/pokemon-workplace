"""Concrete intervening-action counterexample to physical Bench confluence.

Lunatone me1-74's Lunar Cycle: with Solrock in play, discard a Basic
Fighting Energy from hand and draw 3. We intentionally model one
already-authorized Ability resolution, not a whole game's turn scheduler.
"""

from __future__ import annotations

import argparse
import json
import unittest
from dataclasses import replace

from bench_contraction_batch_conservation import (
    contract_with_choice,
    materialized_fixture,
)
from identity_materialization import IdentityLedger, assert_conserved
from multicopy_zone_state import ZoneCountState
from stack_knockout_conservation import StackBoardMaterialState


def print_specific_fixture() -> StackBoardMaterialState:
    """Use actual Lunar Cycle print ID and give the hand a payable cost."""
    _initial, state = materialized_fixture()
    print_ids = {
        "extra1-card": "me1-74",   # Lunar Cycle Lunatone
        "pair-b-card": "pgo-39",   # Solrock in play
    }
    rows = tuple(
        replace(row, card_class=print_ids[row.instance_id])
        if row.instance_id in print_ids else row
        for row in state.ledger.instances
    )
    counts = {
        (card_class, zone): amount
        for card_class, zone, amount in state.ledger.exchangeable.counts
    }
    counts[("basic-fighting-energy", "hand")] = 1
    counts[("non-target-card", "deck")] = 3
    return StackBoardMaterialState(
        IdentityLedger(ZoneCountState.from_mapping(counts), rows),
        state.board,
    )


def use_lunar_cycle_once(state: StackBoardMaterialState) -> StackBoardMaterialState:
    """Resolve the printed conditional effect in a specified legal window.

    Caller guarantees an unused Ability quota and absence of Ability lock.
    The deck has exactly three exchangeable draw cards in this fixture.
    """
    if state.board is None:
        raise ValueError("no playable board")
    in_play_prints = {
        row.card_class for row in state.ledger.instances
        if row.zone == "in_play"
    }
    if "me1-74" not in in_play_prints or "pgo-39" not in in_play_prints:
        raise ValueError("Lunar Cycle condition missing")
    counts = state.ledger.exchangeable
    if counts.count("basic-fighting-energy", "hand") < 1:
        raise ValueError("Lunar Cycle payment missing")
    if counts.count("non-target-card", "deck") < 3:
        raise ValueError("fixture lacks three draw cards")
    counts = counts.move("basic-fighting-energy", "hand", "discard")
    counts = counts.move("non-target-card", "deck", "hand", amount=3)
    next_state = StackBoardMaterialState(
        IdentityLedger(counts, state.ledger.instances), state.board
    )
    assert_conserved(state.ledger, next_state.ledger)
    return next_state


def witness() -> dict[str, object]:
    start = print_specific_fixture()
    # Contract to four while leaving Lunar Cycle and Solrock in play.
    first = contract_with_choice(
        start, new_capacity=4, discard_pokemon_ids=("extra3",)
    )
    assert first is not None
    after_ability = use_lunar_cycle_once(first.state)
    final_staged = contract_with_choice(
        after_ability, new_capacity=3, discard_pokemon_ids=("extra1",)
    )
    assert final_staged is not None

    # The same two Pokémon are discarded in the direct 5 -> 3 path.
    direct = contract_with_choice(
        start, new_capacity=3, discard_pokemon_ids=("extra1", "extra3")
    )
    assert direct is not None
    assert final_staged.state.board == direct.state.board
    assert final_staged.state.ledger.instances == direct.state.ledger.instances
    assert final_staged.state.ledger != direct.state.ledger
    assert_conserved(start.ledger, final_staged.state.ledger)
    assert_conserved(start.ledger, direct.state.ledger)

    # Lunar Cycle is no longer available after the direct contraction.
    unavailable = False
    try:
        use_lunar_cycle_once(direct.state)
    except ValueError:
        unavailable = True
    assert unavailable

    a = final_staged.state.ledger.exchangeable
    b = direct.state.ledger.exchangeable
    assert a.count("basic-fighting-energy", "discard") == 1
    assert b.count("basic-fighting-energy", "hand") == 1
    assert a.count("non-target-card", "hand") == 3
    assert b.count("non-target-card", "deck") == 3
    return {
        "final_bench_ids": final_staged.state.board.bench_ids,
        "same_board": True,
        "same_materialized_instances": True,
        "same_exchangeable_zone_counts": False,
        "staged_fighting_energy_in_discard": a.count(
            "basic-fighting-energy", "discard"
        ),
        "direct_fighting_energy_in_hand": b.count(
            "basic-fighting-energy", "hand"
        ),
        "staged_drawn_cards_in_hand": a.count("non-target-card", "hand"),
        "direct_draw_cards_in_deck": b.count("non-target-card", "deck"),
        "direct_post_contraction_lunar_cycle_available": False,
    }


class IntermediateActionTests(unittest.TestCase):
    def test_action_prevents_confluence(self) -> None:
        result = witness()
        self.assertTrue(result["same_board"])
        self.assertTrue(result["same_materialized_instances"])
        self.assertFalse(result["same_exchangeable_zone_counts"])

    def test_source_and_payment_gates(self) -> None:
        start = print_specific_fixture()
        once = use_lunar_cycle_once(start)
        self.assertEqual(once.ledger.exchangeable.count(
            "basic-fighting-energy", "hand"
        ), 0)
        with self.assertRaises(ValueError):
            use_lunar_cycle_once(once)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    if parser.parse_args().self_test:
        unittest.main(argv=["bench_contraction_intermediate_action"], verbosity=2)
    else:
        print(json.dumps(witness(), indent=2))


if __name__ == "__main__":
    main()
