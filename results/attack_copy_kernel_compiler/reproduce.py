from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from attack_copy_kernel import PokemonRef, State, choose_exact, resolve_attack
from attack_copy_kernel_compiler import compile_copy_attacks
from simple_attack_board_semantics import compile_legal_index


def by_print(rows, card_id: str, attack_name: str):
    matches = [
        row for row in rows
        if row.card_id == card_id
        and (
            row.definition.name if row.definition is not None else attack_name
        ) == attack_name
    ]
    if len(matches) != 1:
        raise AssertionError((card_id, attack_name, len(matches)))
    return matches[0]


def main() -> None:
    compiled = compile_copy_attacks(ROOT / "resources")
    lowered = tuple(row for row in compiled if row.definition is not None)
    unsupported = tuple(
        row for row in compiled if row.definition is None
    )

    unsupported_names = {
        row.definition.name
        if row.definition is not None
        else next(
            attack["name"]
            for card in []
            for attack in ()
        )
        for row in ()
    }
    unsupported_pairs = {
        (row.card_id, row.unsupported_outer_condition)
        for row in unsupported
    }
    unsupported_conditions = {
        row.unsupported_outer_condition for row in unsupported
    }
    assert unsupported_conditions == {
        "coin_flip_gate",
        "opponent_prizes_exact_2",
        "actor_hand_empty",
    }

    # Derive unsupported attack names from the card-grounded contract rows.
    unsupported_card_names = {row.card_name for row in unsupported}
    assert {
        "Liepard",
        "Clefairy",
        "Hypno",
        "Nihilego",
        "Thievul",
    }.issubset(unsupported_card_names)
    assert any("Sudowoodo" in name for name in unsupported_card_names)

    haughty = next(
        row for row in lowered
        if row.card_id == "sv10-150"
        and row.definition is not None
        and row.definition.name == "Haughty Order"
    )
    assert haughty.source_class == "opponent_deck_top10"
    assert haughty.definition.copy_selector is not None
    assert haughty.definition.copy_selector.source == "opponent_revealed"
    assert haughty.definition.copy_selector.optional_selection
    assert haughty.definition.pre_event == "reveal_top_10"
    assert haughty.definition.post_event == "shuffle_revealed"

    seek = next(
        row for row in lowered
        if row.card_id == "sv7-58"
        and row.definition is not None
        and row.definition.name == "Seek Inspiration"
    )
    assert seek.definition.copy_selector is not None
    assert seek.definition.copy_selector.source == "own_deck_top"
    assert seek.definition.copy_selector.precommit_source_to == "discard"
    assert seek.definition.copy_selector.require_no_rule_box

    hypnotic = next(
        row for row in lowered
        if row.card_id == "sm10-119"
        and row.definition is not None
        and row.definition.name == "Hypnotic Reign"
    )
    assert hypnotic.definition.copy_selector is not None
    assert hypnotic.definition.copy_selector.source == "opponent_hand"
    assert hypnotic.definition.copy_selector.move_selected_source_to == "discard"
    assert hypnotic.definition.copy_selector.require_non_gx

    copy_anything = next(
        row for row in lowered
        if row.card_id == "det1-17"
        and row.definition is not None
        and row.definition.name == "Copy Anything"
    )
    assert copy_anything.definition.copy_selector is not None
    assert copy_anything.definition.copy_selector.source == "opponent_in_play"
    assert copy_anything.definition.copy_selector.require_selected_energy

    mimed = next(
        row for row in lowered
        if row.definition is not None
        and row.definition.name == "Mimed Games"
    )
    assert mimed.definition.copy_selector is not None
    assert mimed.definition.copy_selector.chooser == "opponent"

    apex = next(
        row for row in lowered
        if row.card_id == "swsh12-136"
        and row.definition is not None
        and row.definition.name == "Apex Dragon"
    )
    assert apex.definition.copy_selector is not None
    assert apex.definition.copy_selector.source == "own_discard"
    assert apex.definition.copy_selector.required_type == "Dragon"

    trickster = next(
        row for row in lowered
        if row.definition is not None
        and row.definition.name == "Trickster-GX"
    )
    assert trickster.definition.is_gx

    attacks_index = compile_legal_index(ROOT / "resources")
    phantom = next(
        row for row in attacks_index["sv6-130"]
        if row.attack_name == "Phantom Dive"
    )
    phantom_def = phantom.to_leaf_attack_def()
    attacks = {
        haughty.definition.attack_id: haughty.definition,
        phantom_def.attack_id: phantom_def,
    }
    result = resolve_attack(
        actor_player="P1",
        actor_card_id="p1-persian",
        declared_attack_id=haughty.definition.attack_id,
        attacks=attacks,
        state=State(
            pokemon=(
                PokemonRef(
                    "p2-dragapult-revealed",
                    "Dragapult ex",
                    "P2",
                    "revealed",
                    attacks=(phantom_def.attack_id,),
                ),
            )
        ),
        choose=choose_exact((phantom_def.attack_id,)),
    )
    assert result.state.events == (
        "reveal_top_10",
        phantom.event_label,
        "shuffle_revealed",
    )

    print(
        {
            "copy_print_rows": len(compiled),
            "lowered_print_rows": len(lowered),
            "unsupported_print_rows": len(unsupported),
            "unsupported_conditions": sorted(
                condition for condition in unsupported_conditions
                if condition is not None
            ),
            "haughty_events": result.state.events,
        }
    )


if __name__ == "__main__":
    main()
