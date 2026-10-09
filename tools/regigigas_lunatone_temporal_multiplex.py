"""Temporal multiplexing of two named-Ability engines at five Bench slots.

Use Regigigas Ancient Wisdom while all five named Regi partners are present,
play Giovanni's Exile to discard two undamaged partners, Bench Lunatone and
Solrock, then use their Abilities. All cards in this controlled 60-card
configuration are conserved through the complete action sequence.
"""
from __future__ import annotations

import argparse
import json
import unittest
from dataclasses import dataclass, replace
from pathlib import Path

from batch_zone_exit_conservation import leave_play_batch_before_promotion
from board_position_state import (
    Attachment, AttachmentKind, BoardPokemon, PokemonCard, replace_pokemon,
)
from identity_materialization import (
    IdentityLedger, assert_conserved, attach_instance, materialize, put_in_play_instance,
)
from multicopy_zone_state import ZoneCountState
from regigigas_capacity_window import (
    AncientWisdomState, accelerate_from_discard, ancient_wisdom_guard, fixture,
)
from stack_knockout_conservation import StackBoardMaterialState


@dataclass(frozen=True)
class TimedBoard:
    physical: StackBoardMaterialState
    ancient_used: bool = False
    supporter_used: bool = False
    sun_used: bool = False
    lunar_used: bool = False


def with_ledger(
    physical: StackBoardMaterialState, ledger: IdentityLedger
) -> StackBoardMaterialState:
    result = StackBoardMaterialState(ledger, physical.board)
    assert_conserved(physical.ledger, result.ledger)
    return result


def sample_60() -> tuple[IdentityLedger, TimedBoard]:
    """A legal-copy-count toy composition, not a competitive deck recommendation."""
    _, regi = fixture()
    exchangeable = {
        (card_class, zone): n
        for card_class, zone, n in regi.physical.ledger.exchangeable.counts
    }
    exchangeable.update({
        ("giovanni-exile", "hand"): 1,
        ("lunatone", "hand"): 1,
        ("solrock", "hand"): 1,
        ("fighting-energy", "hand"): 1,
        ("psychic-energy", "discard"): 1,
        ("water-energy", "deck"): 40,
        ("water-energy", "prize"): 6,
    })
    ledger = replace(
        regi.physical.ledger,
        exchangeable=ZoneCountState.from_mapping(exchangeable),
    )
    total = sum(row[2] for row in ledger.exchangeable.counts) + len(ledger.instances)
    assert total == 60
    physical = StackBoardMaterialState(ledger, regi.physical.board)
    return ledger, TimedBoard(physical)


def use_ancient_wisdom(state: TimedBoard) -> TimedBoard | None:
    moved = accelerate_from_discard(
        AncientWisdomState(state.physical, state.ancient_used), count=3
    )
    if moved is None:
        return None
    return replace(state, physical=moved.physical, ancient_used=True)


def use_giovannis_exile(
    state: TimedBoard, discard_ids: tuple[str, ...]
) -> TimedBoard | None:
    board = state.physical.board
    if board is None or state.supporter_used:
        return None
    if state.physical.ledger.exchangeable.count("giovanni-exile", "hand") == 0:
        return None
    if len(discard_ids) != 2 or len(set(discard_ids)) != 2:
        return None
    if not set(discard_ids) <= set(board.bench_ids):
        return None
    if any(board.get(object_id).damage_counters > 0 for object_id in discard_ids):
        return None

    routed = leave_play_batch_before_promotion(
        state.physical, discard_ids,
        pokemon_destination="discard", attachment_destination="discard",
    )
    assert routed is not None
    resolved = routed.state.to_stack_state()
    assert resolved is not None
    ledger = replace(
        resolved.ledger,
        exchangeable=resolved.ledger.exchangeable.move(
            "giovanni-exile", "hand", "discard"
        ),
    )
    return replace(
        state, physical=with_ledger(resolved, ledger), supporter_used=True
    )


def bench_basic_from_hand(
    state: TimedBoard, card_name: str, *,
    card_class: str, object_id: str
) -> TimedBoard | None:
    board = state.physical.board
    if board is None or len(board.bench_ids) >= board.bench_capacity:
        return None
    if any(p.pokemon_id == object_id for p in board.pokemon):
        return None
    if state.physical.ledger.exchangeable.count(card_class, "hand") == 0:
        return None

    instance_id = object_id + "-card"
    ledger = materialize(
        state.physical.ledger,
        card_class=card_class, card_name=card_name,
        source_zone="hand", instance_id=instance_id,
    )
    ledger = put_in_play_instance(ledger, instance_id, object_id)
    bench_pokemon = BoardPokemon(
        object_id, (PokemonCard(instance_id, card_name),),
        retreat_cost=1,
    )
    next_board = replace(board, pokemon=board.pokemon + (bench_pokemon,))
    next_physical = StackBoardMaterialState(ledger, next_board)
    assert_conserved(state.physical.ledger, next_physical.ledger)
    return replace(state, physical=next_physical)


def use_sun_energy(state: TimedBoard) -> TimedBoard | None:
    board = state.physical.board
    if board is None or state.sun_used:
        return None
    if not {"Lunatone", "Solrock"} <= {p.name for p in board.pokemon}:
        return None
    if state.physical.ledger.exchangeable.count("psychic-energy", "discard") == 0:
        return None
    target = board.get("lunatone")
    ledger = materialize(
        state.physical.ledger,
        card_class="psychic-energy", card_name="Psychic Energy",
        source_zone="discard", instance_id="sun-psychic-copy",
    )
    ledger = attach_instance(ledger, "sun-psychic-copy", "lunatone")
    added = Attachment(
        "sun-psychic-copy", "Psychic Energy", AttachmentKind.ENERGY,
        retreat_units=1,
    )
    next_board = replace_pokemon(
        board, replace(target, attachments=target.attachments + (added,))
    )
    physical = StackBoardMaterialState(ledger, next_board)
    assert_conserved(state.physical.ledger, physical.ledger)
    return replace(state, physical=physical, sun_used=True)


def use_lunar_cycle(state: TimedBoard) -> TimedBoard | None:
    board = state.physical.board
    if board is None or state.lunar_used:
        return None
    if not {"Lunatone", "Solrock"} <= {p.name for p in board.pokemon}:
        return None
    zones = state.physical.ledger.exchangeable
    if zones.count("fighting-energy", "hand") == 0:
        return None
    if zones.count("water-energy", "deck") < 3:
        return None
    # In this fixture all deck cards are Basic Water Energy, so the draw is exact.
    zones = zones.move("fighting-energy", "hand", "discard")
    zones = zones.move("water-energy", "deck", "hand", amount=3)
    ledger = replace(state.physical.ledger, exchangeable=zones)
    return replace(
        state, physical=with_ledger(state.physical, ledger), lunar_used=True
    )


def complete_line(*, giovanni_first: bool = False) -> tuple[IdentityLedger, TimedBoard]:
    initial, state = sample_60()
    if giovanni_first:
        after_gio = use_giovannis_exile(state, ("regirock", "regice"))
        assert after_gio is not None
        state = after_gio
        assert use_ancient_wisdom(state) is None
    else:
        accelerated = use_ancient_wisdom(state)
        assert accelerated is not None
        state = accelerated
        after_gio = use_giovannis_exile(state, ("regirock", "regice"))
        assert after_gio is not None
        state = after_gio

    for name in ("Lunatone", "Solrock"):
        entered = bench_basic_from_hand(
            state, name, card_class=name.lower(), object_id=name.lower()
        )
        assert entered is not None
        state = entered
    psychic = use_sun_energy(state)
    assert psychic is not None
    state = psychic
    drawn = use_lunar_cycle(state)
    assert drawn is not None
    state = drawn
    assert_conserved(initial, state.physical.ledger)
    return initial, state


class TemporalMultiplexTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        from bench_named_ability_dependencies import build
        rows = build(Path("resources"))["entries"]
        self_rows = [
            (source, ability, print_id)
            for source, ability, print_id in (
                ("Regigigas", "Ancient Wisdom", "swsh10-130"),
                ("Lunatone", "Lunar Cycle", "me1-74"),
            )
            if not any(
                row["source_name"] == source
                and row["ability"] == ability
                and print_id in row["print_ids"]
                for row in rows
            )
        ]
        if self_rows:
            raise AssertionError(f"Missing legal Ability prints: {self_rows!r}")

    def test_60_card_initial_and_two_named_guards(self) -> None:
        initial, state = sample_60()
        self.assertTrue(ancient_wisdom_guard(state.physical))
        self.assertEqual(initial.exchangeable.count("water-energy", "prize"), 6)
        self.assertEqual(initial.exchangeable.count("water-energy", "deck"), 40)
        self.assertIsNone(use_lunar_cycle(state))
        self.assertIsNone(use_sun_energy(state))

    def test_full_sequencing_executed_without_eight_simultaneous_names(self) -> None:
        initial, result = complete_line()
        board = result.physical.board
        assert board is not None
        self.assertEqual(len(board.bench_ids), 5)
        self.assertFalse(ancient_wisdom_guard(result.physical))
        self.assertEqual(len(board.get("regigigas").attachments), 3)
        self.assertEqual(len(board.get("lunatone").attachments), 1)
        self.assertEqual(result.physical.ledger.exchangeable.count("water-energy", "hand"), 3)
        self.assertEqual(result.physical.ledger.exchangeable.count("fighting-energy", "discard"), 1)
        self.assertEqual(result.physical.ledger.exchangeable.count("giovanni-exile", "discard"), 1)
        self.assertEqual(result.physical.ledger.exchangeable.count("regirock", "discard"), 1)
        self.assertEqual(result.physical.ledger.exchangeable.count("regice", "discard"), 1)
        self.assertTrue(result.ancient_used and result.supporter_used)
        self.assertTrue(result.sun_used and result.lunar_used)
        self.assertEqual(result.physical.ledger.exchangeable.count("water-energy", "prize"), 6)
        assert_conserved(initial, result.physical.ledger)

    def test_giovanni_first_closes_ancient_wisdom_but_later_engine_works(self) -> None:
        _, result = complete_line(giovanni_first=True)
        assert result.physical.board is not None
        self.assertFalse(result.ancient_used)
        self.assertEqual(len(result.physical.board.get("regigigas").attachments), 0)
        self.assertTrue(result.sun_used and result.lunar_used)
        self.assertEqual(result.physical.ledger.exchangeable.count("grass-energy", "discard"), 3)

    def test_supporter_window_and_capacity_constraints(self) -> None:
        _, start = sample_60()
        self.assertIsNone(bench_basic_from_hand(
            start, "Lunatone", card_class="lunatone", object_id="lunatone"
        ))
        first = use_giovannis_exile(start, ("regirock", "regice"))
        assert first is not None
        self.assertIsNone(use_giovannis_exile(first, ("registeel", "regidrago")))
        self.assertIsNone(use_giovannis_exile(start, ("regirock", "regirock")))
        self.assertIsNone(use_giovannis_exile(start, ("regigigas", "regice")))

    def test_dependent_ability_payments_and_once_per_turn(self) -> None:
        _, state = complete_line()
        self.assertIsNone(use_ancient_wisdom(state))
        self.assertIsNone(use_sun_energy(state))
        self.assertIsNone(use_lunar_cycle(state))
        self.assertIsNone(use_giovannis_exile(state, ("registeel", "regieleki")))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        unittest.main(argv=["regigigas_lunatone_temporal_multiplex"], verbosity=2)
    else:
        initial, a = complete_line()
        _, b = complete_line(giovanni_first=True)
        assert a.physical.board is not None and b.physical.board is not None
        print(json.dumps({
            "starting_deck_size": 60,
            "starting_prizes": 6,
            "maximum_bench_capacity": 5,
            "wisdom_then_exile_then_lunar": {
                "regigigas_energy": len(a.physical.board.get("regigigas").attachments),
                "lunatone_energy": len(a.physical.board.get("lunatone").attachments),
                "water_energy_drawn": a.physical.ledger.exchangeable.count("water-energy", "hand"),
            },
            "exile_then_attempt_wisdom_then_lunar": {
                "regigigas_energy": len(b.physical.board.get("regigigas").attachments),
                "lunatone_energy": len(b.physical.board.get("lunatone").attachments),
                "water_energy_drawn": b.physical.ledger.exchangeable.count("water-energy", "hand"),
            },
            "all_physical_cards_conserved": True,
        }, indent=2))
        assert_conserved(initial, a.physical.ledger)


if __name__ == "__main__":
    main()
