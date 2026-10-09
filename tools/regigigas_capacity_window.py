"""Regigigas Ancient Wisdom timing versus player-controlled Bench contraction.

An exact card-conservation witness. The ability's named condition and Energy
attachments are implemented for this one known print; external Ability locks,
entry legality, Stadium access and actual metagame frequency are not modeled.
"""
from __future__ import annotations

import argparse
import json
import unittest
from dataclasses import dataclass, replace
from pathlib import Path

from bench_contraction_batch_conservation import contract_with_choice
from bench_named_ability_dependencies import build
from board_position_state import (
    Attachment, AttachmentKind, BoardPokemon, PokemonCard, make_state,
    replace_pokemon,
)
from identity_materialization import (
    IdentityLedger, assert_conserved, attach_instance, materialize,
    put_in_play_instance,
)
from multicopy_zone_state import ZoneCountState
from stack_knockout_conservation import StackBoardMaterialState


REGI_PARTNERS = ("Regirock", "Regice", "Registeel", "Regieleki", "Regidrago")
SOURCE_PRINT_ID = "swsh10-130"


@dataclass(frozen=True)
class AncientWisdomState:
    physical: StackBoardMaterialState
    used_this_turn: bool = False


def ancient_wisdom_guard(physical: StackBoardMaterialState) -> bool:
    board = physical.board
    if board is None:
        return False
    names = {pokemon.name for pokemon in board.pokemon}
    return (
        board.get("regigigas").name == "Regigigas"
        and len(board.bench_ids) <= board.bench_capacity
        and set(REGI_PARTNERS) <= names
    )


def accelerate_from_discard(
    state: AncientWisdomState, *, count: int
) -> AncientWisdomState | None:
    """Use Ancient Wisdom once, attaching 1-3 Basic Grass Energy to Regigigas."""
    if count < 1 or count > 3 or state.used_this_turn:
        return None
    if not ancient_wisdom_guard(state.physical):
        return None
    if state.physical.ledger.exchangeable.count("grass-energy", "discard") < count:
        return None

    old = state.physical
    assert old.board is not None
    target = old.board.get("regigigas")
    ledger = old.ledger
    additions = []
    for i in range(count):
        instance_id = f"wisdom-energy-{i}"
        ledger = materialize(
            ledger,
            card_class="grass-energy",
            card_name="Grass Energy",
            source_zone="discard",
            instance_id=instance_id,
        )
        ledger = attach_instance(ledger, instance_id, "regigigas")
        additions.append(
            Attachment(instance_id, "Grass Energy", AttachmentKind.ENERGY, retreat_units=1)
        )
    board = replace_pokemon(
        old.board,
        replace(target, attachments=target.attachments + tuple(additions)),
    )
    next_physical = StackBoardMaterialState(ledger, board)
    assert_conserved(old.ledger, next_physical.ledger)
    return AncientWisdomState(next_physical, True)


def collapse(
    state: AncientWisdomState, *,
    discard_id: str = "regirock"
) -> AncientWisdomState:
    result = contract_with_choice(
        state.physical, new_capacity=4, discard_pokemon_ids=(discard_id,)
    )
    assert result is not None
    return AncientWisdomState(result.state, state.used_this_turn)


def fixture() -> tuple[IdentityLedger, AncientWisdomState]:
    names = ("Regigigas", *REGI_PARTNERS)
    pool = {
        (name.lower(), "hand"): 1 for name in names
    }
    pool[("grass-energy", "discard")] = 3
    initial = IdentityLedger(ZoneCountState.from_mapping(pool))
    ledger = initial
    pokemon = []
    for name in names:
        pokemon_id = name.lower()
        card_id = pokemon_id + "-card"
        ledger = materialize(
            ledger, card_class=name.lower(), card_name=name,
            source_zone="hand", instance_id=card_id,
        )
        ledger = put_in_play_instance(ledger, card_id, pokemon_id)
        pokemon.append(
            BoardPokemon(
                pokemon_id, (PokemonCard(card_id, name),),
                retreat_cost=1,
            )
        )
    board = make_state(pokemon, active_id="regigigas", bench_capacity=5)
    state = StackBoardMaterialState(ledger, board)
    assert_conserved(initial, state.ledger)
    return initial, AncientWisdomState(state)


class RegigigasCapacityTimingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        rows = build(Path("resources"))["entries"]
        cls.ability = next(
            row for row in rows
            if row["source_name"] == "Regigigas"
            and row["ability"] == "Ancient Wisdom"
            and SOURCE_PRINT_ID in row["print_ids"]
        )

    def test_exact_guard_matches_card_database(self) -> None:
        self.assertEqual(tuple(self.ability["required_names"]), REGI_PARTNERS)
        self.assertEqual(self.ability["minimum_bench_slots"], 5)
        self.assertEqual(self.ability["guard"], "if")
        self.assertEqual(self.ability["location"], "in play")

    def test_ability_before_contraction_preserves_acceleration(self) -> None:
        initial, start = fixture()
        after_ability = accelerate_from_discard(start, count=3)
        assert after_ability is not None
        self.assertEqual(
            len(after_ability.physical.board.get("regigigas").attachments), 3
        )
        contracted = collapse(after_ability)
        self.assertFalse(ancient_wisdom_guard(contracted.physical))
        self.assertEqual(contracted.physical.board.bench_capacity, 4)
        self.assertEqual(
            len(contracted.physical.board.get("regigigas").attachments), 3
        )
        self.assertEqual(
            contracted.physical.ledger.exchangeable.count("grass-energy", "discard"), 0
        )
        self.assertTrue(contracted.used_this_turn)
        assert_conserved(initial, contracted.physical.ledger)

    def test_contraction_before_ability_disables_every_choice(self) -> None:
        initial, start = fixture()
        for name in REGI_PARTNERS:
            with self.subTest(discarded=name):
                early = collapse(start, discard_id=name.lower())
                self.assertFalse(ancient_wisdom_guard(early.physical))
                self.assertIsNone(accelerate_from_discard(early, count=3))
                self.assertEqual(
                    early.physical.ledger.exchangeable.count("grass-energy", "discard"),
                    3,
                )
                self.assertEqual(
                    len(early.physical.board.get("regigigas").attachments), 0
                )
                assert_conserved(initial, early.physical.ledger)

    def test_reexpand_capacity_does_not_restore_lost_partner(self) -> None:
        _, start = fixture()
        lost = collapse(start)
        board = replace(lost.physical.board, bench_capacity=8)
        restored_space = AncientWisdomState(
            StackBoardMaterialState(lost.physical.ledger, board), False
        )
        self.assertFalse(ancient_wisdom_guard(restored_space.physical))
        self.assertIsNone(accelerate_from_discard(restored_space, count=1))

    def test_ability_once_and_discard_payment_bound(self) -> None:
        initial, start = fixture()
        for invalid in (-1, 0, 4):
            self.assertIsNone(accelerate_from_discard(start, count=invalid))
        used = accelerate_from_discard(start, count=2)
        assert used is not None
        self.assertIsNone(accelerate_from_discard(used, count=1))
        self.assertEqual(used.physical.ledger.exchangeable.count("grass-energy", "discard"), 1)
        self.assertEqual(len(used.physical.board.get("regigigas").attachments), 2)
        assert_conserved(initial, used.physical.ledger)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        unittest.main(argv=["regigigas_capacity_window"], verbosity=2)
    else:
        initial, start = fixture()
        before = collapse(accelerate_from_discard(start, count=3))
        after = collapse(start)
        print(json.dumps({
            "correct_print": SOURCE_PRINT_ID,
            "five_named_partner_condition_at_start": ancient_wisdom_guard(start.physical),
            "accelerate_then_collapse_attached_energy": len(
                before.physical.board.get("regigigas").attachments
            ),
            "collapse_then_accelerate_ability_available": (
                ancient_wisdom_guard(after.physical)
            ),
            "collapse_then_accelerate_attached_energy": len(
                after.physical.board.get("regigigas").attachments
            ),
            "after_collapse_named_condition_restorable_without_reentry": False,
        }, indent=2))
        assert_conserved(initial, before.physical.ledger)
        assert_conserved(initial, after.physical.ledger)


if __name__ == "__main__":
    main()
