"""Physical Beheeyem full-stack self-shuffle and replacement Active witness."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from active_self_shuffle_conservation import shuffle_active_and_attached_into_deck
from board_position_state import (
    AttachmentKind,
    BoardPokemon,
    PokemonCard,
    make_state,
)
from identity_materialization import (
    IdentityLedger,
    assert_conserved,
    materialize,
    put_in_play_instance,
)
from multicopy_zone_state import ZoneCountState
from stack_knockout_conservation import (
    StackBoardMaterialState,
    attach_from_hand,
)


def in_play(
    ledger: IdentityLedger,
    card_class: str,
    card_name: str,
    instance_id: str,
    board_object_id: str,
) -> IdentityLedger:
    ledger = materialize(
        ledger,
        card_class=card_class,
        card_name=card_name,
        source_zone="hand",
        instance_id=instance_id,
    )
    return put_in_play_instance(ledger, instance_id, board_object_id)


def main() -> None:
    initial = IdentityLedger(
        ZoneCountState.from_mapping(
            {
                ("elgyem", "hand"): 2,
                ("beheeyem", "hand"): 1,
                ("lillipup", "hand"): 1,
                ("herdier", "hand"): 1,
                ("stoutland", "hand"): 1,
                ("tae", "hand"): 1,
                ("float-stone", "hand"): 1,
            }
        )
    )
    ledger = initial
    cards = (
        ("elgyem", "Elgyem", "elgyem-a", "attacker"),
        ("beheeyem", "Beheeyem", "beheeyem-a", "attacker"),
        ("lillipup", "Lillipup", "lillipup-a", "anchor"),
        ("herdier", "Herdier", "herdier-a", "anchor"),
        ("stoutland", "Stoutland", "stoutland-a", "anchor"),
        ("elgyem", "Elgyem", "elgyem-b", "backup"),
    )
    for card_class, card_name, instance_id, owner in cards:
        ledger = in_play(ledger, card_class, card_name, instance_id, owner)

    board = make_state(
        (
            BoardPokemon(
                "attacker",
                (
                    PokemonCard("elgyem-a", "Elgyem"),
                    PokemonCard("beheeyem-a", "Beheeyem", "Elgyem"),
                ),
                retreat_cost=2,
            ),
            BoardPokemon(
                "anchor",
                (
                    PokemonCard("lillipup-a", "Lillipup"),
                    PokemonCard("herdier-a", "Herdier", "Lillipup"),
                    PokemonCard("stoutland-a", "Stoutland", "Herdier"),
                ),
                retreat_cost=3,
            ),
            BoardPokemon(
                "backup",
                (PokemonCard("elgyem-b", "Elgyem"),),
                retreat_cost=1,
            ),
        ),
        active_id="attacker",
    )
    state = StackBoardMaterialState(ledger, board)

    after_energy = attach_from_hand(
        state,
        pokemon_id="attacker",
        card_class="tae",
        instance_id="tae-a",
        card_name="Triple Acceleration Energy",
        kind=AttachmentKind.ENERGY,
        retreat_units=3,
    )
    assert after_energy is not None
    after_tool = attach_from_hand(
        after_energy,
        pokemon_id="anchor",
        card_class="float-stone",
        instance_id="float-stone-a",
        card_name="Float Stone",
        kind=AttachmentKind.TOOL,
    )
    assert after_tool is not None
    state = after_tool

    # A choice of an unrelated nonexistent target is not a valid promotion.
    assert shuffle_active_and_attached_into_deck(
        state, promote_id="nonexistent"
    ) is None
    assert shuffle_active_and_attached_into_deck(state) is None

    shuffled = shuffle_active_and_attached_into_deck(
        state, promote_id="anchor"
    )
    assert shuffled is not None and shuffled.board is not None
    assert shuffled.board.active_id == "anchor"
    assert shuffled.board.bench_ids == ("backup",)
    assert shuffled.board.get("anchor").name == "Stoutland"
    assert {row.card_id for row in shuffled.board.get("anchor").attachments} == {
        "float-stone-a"
    }
    assert shuffled.board.get("backup").stack[0].card_id == "elgyem-b"
    assert all(
        shuffled.ledger.exchangeable.count(card_class, "deck") == 1
        for card_class in ("elgyem", "beheeyem", "tae")
    )
    assert shuffled.ledger.exchangeable.count("stoutland", "deck") == 0
    assert shuffled.ledger.exchangeable.count("float-stone", "deck") == 0
    assert all(
        shuffled.ledger.exchangeable.count(card_class, "discard") == 0
        for card_class in ("elgyem", "beheeyem", "tae")
    )
    assert shuffled.ledger.instances == tuple(
        row for row in state.ledger.instances
        if row.instance_id not in {"elgyem-a", "beheeyem-a", "tae-a"}
    )
    assert_conserved(initial, shuffled.ledger)

    # Without a surviving Benched Pokemon, self-shuffling creates a terminal
    # no-Pokemon board, but it still returns the actual physical stack to deck.
    lone_ledger = in_play(
        IdentityLedger(ZoneCountState.from_mapping({("elgyem", "hand"): 1})),
        "elgyem",
        "Elgyem",
        "lone-elgyem",
        "lone",
    )
    lone_state = StackBoardMaterialState(
        lone_ledger,
        make_state(
            (BoardPokemon("lone", (PokemonCard("lone-elgyem", "Elgyem"),), 1),),
            active_id="lone",
        ),
    )
    terminal = shuffle_active_and_attached_into_deck(lone_state)
    assert terminal is not None and terminal.board is None
    assert terminal.ledger.exchangeable.count("elgyem", "deck") == 1
    assert not terminal.ledger.instances
    assert_conserved(lone_ledger, terminal.ledger)

    print(json.dumps({
        "whole_evolution_stack_returns_to_deck": True,
        "triple_acceleration_energy_returns_to_deck": True,
        "anchor_float_stone_remains_attached": True,
        "backup_elgyem_remains_benched": True,
        "stoutland_promoted_active": True,
        "no_knockout_discard_or_prize_award": True,
        "invalid_promotions_rejected": True,
        "lone_active_terminal_board_preserved": True,
        "physical_card_counts_conserved": True,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
