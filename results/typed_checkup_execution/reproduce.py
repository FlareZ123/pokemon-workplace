"""Reproduce typed condition payloads through multi-Pokémon Checkup execution."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from checkup_execution_kernel import (  # noqa: E402
    CheckupBoard,
    CheckupPokemon,
    CounterMutation,
    MutationKind,
)
from special_condition_state import (  # noqa: E402
    CHECKUP_CONDITION_BLOCK,
    ConditionInstance,
    ConditionKind,
    ConditionModifier,
    ModifierMode,
    regular_condition,
)
from timed_special_conditions import (  # noqa: E402
    TimedConditionState,
    apply_timed_condition,
)
from typed_checkup_execution import (  # noqa: E402
    CoinOutcomes,
    execute_static_typed_checkup,
)


def load_card(path: str, card_id: str) -> dict[str, object]:
    cards = json.loads((ROOT / path).read_text(encoding="utf-8"))
    return next(card for card in cards if card["id"] == card_id)


def main() -> None:
    weezing = load_card("resources/cards/en/swsh2.json", "swsh2-113")
    toxicroak = load_card("resources/cards/en/swsh1.json", "swsh1-124")
    garganacl = load_card("resources/cards/en/sv2.json", "sv2-123")

    assert next(a["text"] for a in weezing["attacks"] if a["name"] == "Severe Poison") == (
        "Your opponent's Active Pokémon is now Poisoned. Put 4 damage counters "
        "instead of 1 on that Pokémon during Pokémon Checkup."
    )
    assert next(a["text"] for a in toxicroak["abilities"] if a["name"] == "More Poison") == (
        "Put 2 more damage counters on your opponent's Poisoned Pokémon during "
        "Pokémon Checkup."
    )
    assert next(a["text"] for a in garganacl["abilities"] if a["name"] == "Blessed Salt") == (
        "During Pokémon Checkup, heal 20 damage from each of your Pokémon."
    )

    target_conditions = TimedConditionState("A")
    target_conditions = apply_timed_condition(
        target_conditions,
        ConditionInstance(
            ConditionKind.POISONED,
            base_damage_counters=4,
            source_label="Galarian Weezing — Severe Poison",
        ),
        applied_turn_serial=7,
    )
    target_conditions = apply_timed_condition(
        target_conditions,
        regular_condition(ConditionKind.BURNED),
        applied_turn_serial=7,
    )

    board = CheckupBoard(
        (
            CheckupPokemon("target", hp=100, damage_counters=2),
            CheckupPokemon("garganacl", hp=180, damage_counters=0),
        )
    )
    empty = TimedConditionState("A")

    executed = execute_static_typed_checkup(
        board,
        (CHECKUP_CONDITION_BLOCK, "Blessed Salt"),
        condition_states={
            "target": target_conditions,
            "garganacl": empty,
        },
        completed_turn_player="B",
        completed_turn_serial=8,
        coin_outcomes={
            "target": CoinOutcomes(burn_heads=False),
        },
        modifiers={
            "target": (
                ConditionModifier(
                    ConditionKind.POISONED,
                    2,
                    ModifierMode.ADD,
                    "Toxicroak — More Poison",
                ),
            ),
        },
        effect_mutations={
            "Blessed Salt": (
                CounterMutation(
                    "blessed-salt-target",
                    MutationKind.HEAL,
                    ("target", "garganacl"),
                    2,
                ),
            ),
        },
    )

    mutations = executed.condition_block.mutations
    assert [(m.mutation_id, m.amount) for m in mutations] == [
        ("condition:Poisoned:target", 6),
        ("condition:Burned:target", 2),
    ]

    after_conditions = executed.board_execution.snapshots[0]
    assert after_conditions.token == CHECKUP_CONDITION_BLOCK
    assert after_conditions.board.get("target").damage_counters == 10
    assert after_conditions.zero_hp_ids == ("target",)

    final = executed.board_execution.final_board
    assert final.get("target").damage_counters == 8
    assert final.get("target").remaining_hp == 20
    assert executed.board_execution.knocked_out_ids == ()

    next_target = executed.condition_block.conditions_for("target")
    assert next_target.get(ConditionKind.POISONED) is not None
    assert next_target.get(ConditionKind.BURNED) is not None

    print("compiled condition mutations:", [(m.mutation_id, m.amount) for m in mutations])
    print("zero HP after condition block:", after_conditions.zero_hp_ids)
    print("final target damage counters:", final.get("target").damage_counters)
    print("typed Checkup execution regression passed")


if __name__ == "__main__":
    main()
