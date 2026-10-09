"""Conserved choice-based Bench-capacity contraction for stack-bearing boards.

Preserve legal player discard choice, entire Pokémon stacks and attachments,
and explicit discard-zone routing. No Knock Out or Prize-take step occurs.
"""
from __future__ import annotations

import argparse
import json
import unittest
from dataclasses import dataclass, replace
from itertools import combinations

from batch_zone_exit_conservation import leave_play_batch_before_promotion
from board_position_state import (
    AttachmentKind, BoardPokemon, PokemonCard, make_state,
)
from identity_materialization import (
    IdentityLedger, assert_conserved, materialize, put_in_play_instance,
)
from multicopy_zone_state import ZoneCountState
from stack_knockout_conservation import (
    StackBoardMaterialState, attach_from_hand,
)


@dataclass(frozen=True)
class ForcedContraction:
    state: StackBoardMaterialState
    discarded_pokemon_ids: tuple[str, ...]
    discarded_card_ids: tuple[str, ...]
    discarded_attachment_ids: tuple[str, ...]


def contract_with_choice(
    state: StackBoardMaterialState,
    *,
    new_capacity: int,
    discard_pokemon_ids: tuple[str, ...],
) -> ForcedContraction | None:
    """Apply one chosen legal forced-discard set and conserve all physical cards."""
    if state.board is None:
        return None
    board = state.board
    if new_capacity < 0:
        raise ValueError("negative Bench capacity")
    if len(discard_pokemon_ids) != len(set(discard_pokemon_ids)):
        return None
    excess = max(0, len(board.bench_ids) - new_capacity)
    if len(discard_pokemon_ids) != excess:
        return None
    if not set(discard_pokemon_ids) <= set(board.bench_ids):
        return None

    routed = leave_play_batch_before_promotion(
        state,
        discard_pokemon_ids,
        pokemon_destination="discard",
        attachment_destination="discard",
    )
    assert routed is not None
    pending = replace(routed.state, bench_capacity=new_capacity)
    after = pending.to_stack_state()
    assert after is not None
    assert after.board is not None
    assert after.board.active_id == board.active_id
    assert_conserved(state.ledger, after.ledger)
    return ForcedContraction(
        state=after,
        discarded_pokemon_ids=routed.pokemon_ids,
        discarded_card_ids=routed.pokemon_card_ids,
        discarded_attachment_ids=routed.attachment_card_ids,
    )


def enumerate_contractions(
    state: StackBoardMaterialState, new_capacity: int
) -> tuple[ForcedContraction, ...]:
    """Generate all legal physical destinations for a capacity change."""
    if state.board is None:
        return ()
    if new_capacity < 0:
        raise ValueError("negative Bench capacity")
    n = max(0, len(state.board.bench_ids) - new_capacity)
    choices: list[ForcedContraction] = []
    for discards in combinations(state.board.bench_ids, n):
        outcome = contract_with_choice(
            state, new_capacity=new_capacity, discard_pokemon_ids=discards
        )
        assert outcome is not None
        choices.append(outcome)
    return tuple(choices)


def materialized_fixture() -> tuple[IdentityLedger, StackBoardMaterialState]:
    """Six-Pokémon board with an evolved stack, Tool and Energy on one Bench object."""
    cards = {
        ("bidoof", "hand"): 1,
        ("tarountula", "hand"): 1,
        ("spidops", "hand"): 1,
        ("solrock", "hand"): 1,
        ("lunatone", "hand"): 1,
        ("regirock", "hand"): 1,
        ("regice", "hand"): 1,
        ("grass-energy", "hand"): 1,
        ("muscle-band", "hand"): 1,
    }
    initial = IdentityLedger(ZoneCountState.from_mapping(cards))
    names = (
        ("active", "bidoof", "Bidoof"),
        ("pair-a", "tarountula", "Tarountula"),
        ("pair-b", "solrock", "Solrock"),
        ("extra1", "lunatone", "Lunatone"),
        ("extra2", "regirock", "Regirock"),
        ("extra3", "regice", "Regice"),
    )
    ledger = initial
    for pokemon_id, card_class, name in names:
        ledger = materialize(
            ledger, card_class=card_class, card_name=name,
            source_zone="hand", instance_id=f"{pokemon_id}-card",
        )
        ledger = put_in_play_instance(ledger, f"{pokemon_id}-card", pokemon_id)
    ledger = materialize(
        ledger, card_class="spidops", card_name="Spidops",
        source_zone="hand", instance_id="pair-a-evolved",
    )
    ledger = put_in_play_instance(ledger, "pair-a-evolved", "pair-a")

    p = tuple(
        BoardPokemon(
            pokemon_id, (PokemonCard(f"{pokemon_id}-card", name),),
            retreat_cost=1,
        )
        for pokemon_id, _, name in names
    )
    p = tuple(
        replace(
            pokemon, stack=(
                PokemonCard("pair-a-card", "Tarountula"),
                PokemonCard("pair-a-evolved", "Spidops", "Tarountula"),
            )
        ) if pokemon.pokemon_id == "pair-a" else pokemon
        for pokemon in p
    )
    board = make_state(p, active_id="active", bench_capacity=5)
    state = StackBoardMaterialState(ledger, board)
    energy = attach_from_hand(
        state, pokemon_id="pair-a", card_class="grass-energy",
        instance_id="pair-a-energy", card_name="Grass Energy",
        kind=AttachmentKind.ENERGY, retreat_units=1,
    )
    assert energy is not None
    attached = attach_from_hand(
        energy, pokemon_id="pair-a", card_class="muscle-band",
        instance_id="pair-a-tool", card_name="Muscle Band",
        kind=AttachmentKind.TOOL,
    )
    assert attached is not None
    assert_conserved(initial, attached.ledger)
    return initial, attached


class ForcedContractionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.initial, self.state = materialized_fixture()

    def test_five_to_four_choices_and_multicard_discard(self) -> None:
        choices = enumerate_contractions(self.state, 4)
        self.assertEqual(len(choices), 5)
        selected = next(x for x in choices if x.discarded_pokemon_ids == ("pair-a",))
        self.assertEqual(selected.discarded_card_ids, ("pair-a-card", "pair-a-evolved"))
        self.assertEqual(selected.discarded_attachment_ids, ("pair-a-energy", "pair-a-tool"))
        self.assertEqual(selected.state.board.bench_ids, (
            "pair-b", "extra1", "extra2", "extra3"
        ))
        self.assertEqual(selected.state.board.active_id, "active")
        for name in ("tarountula", "spidops", "grass-energy", "muscle-band"):
            self.assertEqual(selected.state.ledger.exchangeable.count(name, "discard"), 1)
        assert_conserved(self.initial, selected.state.ledger)

    def test_direct_three_has_ten_choices(self) -> None:
        choices = enumerate_contractions(self.state, 3)
        self.assertEqual(len(choices), 10)
        for outcome in choices:
            self.assertEqual(len(outcome.discarded_pokemon_ids), 2)
            self.assertEqual(len(outcome.state.board.bench_ids), 3)
            assert_conserved(self.initial, outcome.state.ledger)

    def test_two_stage_contraction_conserves_all_cards(self) -> None:
        first = contract_with_choice(
            self.state, new_capacity=4, discard_pokemon_ids=("extra3",)
        )
        assert first is not None
        second = contract_with_choice(
            first.state, new_capacity=3, discard_pokemon_ids=("pair-a",)
        )
        assert second is not None
        self.assertEqual(second.state.board.bench_ids, ("pair-b", "extra1", "extra2"))
        self.assertEqual(second.state.ledger.exchangeable.count("regice", "discard"), 1)
        self.assertEqual(second.state.ledger.exchangeable.count("spidops", "discard"), 1)
        self.assertEqual(second.state.ledger.exchangeable.count("muscle-band", "discard"), 1)
        assert_conserved(self.initial, second.state.ledger)

    def test_selection_rejects_active_and_wrong_count(self) -> None:
        self.assertIsNone(contract_with_choice(
            self.state, new_capacity=4, discard_pokemon_ids=("active",)
        ))
        self.assertIsNone(contract_with_choice(
            self.state, new_capacity=4, discard_pokemon_ids=()
        ))
        self.assertIsNone(contract_with_choice(
            self.state, new_capacity=4,
            discard_pokemon_ids=("pair-a", "pair-b"),
        ))
        self.assertIsNone(contract_with_choice(
            self.state, new_capacity=4,
            discard_pokemon_ids=("pair-a", "pair-a"),
        ))

    def test_noncontraction_preserves_ledger_and_changes_capacity(self) -> None:
        outcome = contract_with_choice(
            self.state, new_capacity=8, discard_pokemon_ids=()
        )
        assert outcome is not None
        self.assertEqual(outcome.state.ledger, self.state.ledger)
        self.assertEqual(outcome.state.board.bench_capacity, 8)
        self.assertEqual(outcome.state.board.bench_ids, self.state.board.bench_ids)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        unittest.main(argv=["bench_contraction_batch_conservation"], verbosity=2)
    else:
        initial, state = materialized_fixture()
        outcomes = enumerate_contractions(state, 4)
        chosen = next(
            option for option in outcomes
            if option.discarded_pokemon_ids == ("pair-a",)
        )
        print(json.dumps({
            "legal_discard_choices": len(outcomes),
            "capacity_after": chosen.state.board.bench_capacity,
            "discarded_pokemon_objects": chosen.discarded_pokemon_ids,
            "discarded_pokemon_cards": chosen.discarded_card_ids,
            "discarded_attachments": chosen.discarded_attachment_ids,
            "physical_conservation_verified": True,
            "prize_cards_taken": 0,
        }, indent=2))
        assert_conserved(initial, chosen.state.ledger)


if __name__ == "__main__":
    main()
