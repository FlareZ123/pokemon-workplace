from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from attack_copy_controlled_execution import (
    UnresolvedCopiedBodyControl,
    copied_body_gate_policy,
)
from attack_copy_kernel import AttackDef, PokemonRef, State, choose_exact, resolve_attack
from attack_copy_kernel_compiler import compile_copy_attacks

LEAF = "test:leaf"
LEAF_DEF = AttackDef(LEAF, "Leaf", effect_label="leaf_effect")


def row_by_name(rows, name: str, guarded: bool):
    for row in rows:
        definition = row.guarded_definition if guarded else row.definition
        if definition is not None and definition.name == name:
            return row
    raise AssertionError(name)


def main() -> None:
    rows = compile_copy_attacks(ROOT / "resources")
    outer = row_by_name(rows, "Genome Hacking", False)
    nightcap = row_by_name(rows, "Nightcap", True)
    assist = row_by_name(rows, "Assist", True)
    assert outer.definition is not None
    assert nightcap.guarded_definition is not None
    assert assist.guarded_definition is not None

    outer_id = outer.definition.attack_id
    nightcap_id = nightcap.guarded_definition.attack_id
    state = State(
        pokemon=(
            PokemonRef(
                "p2-active",
                "Nihilego",
                "P2",
                "active",
                attacks=(nightcap_id,),
            ),
            PokemonRef(
                "p2-bench",
                "Leaf Source",
                "P2",
                "bench",
                attacks=(LEAF,),
            ),
        )
    )
    attacks = {
        outer_id: outer.definition,
        nightcap_id: nightcap.guarded_definition,
        LEAF: LEAF_DEF,
    }

    blocked = resolve_attack(
        actor_player="P1",
        actor_card_id="p1-mew",
        declared_attack_id=outer_id,
        attacks=attacks,
        state=state,
        choose=choose_exact((nightcap_id,)),
        copied_body_gate=copied_body_gate_policy(
            rows,
            opponent_prizes_remaining=3,
        ),
    )
    assert blocked.body_chain == (outer_id, nightcap_id)
    assert blocked.state.events == ()
    assert blocked.state.last_attack_for("P1") == outer_id
    assert blocked.trace[0].selected_attack_id == nightcap_id
    assert blocked.trace[1].body_execution_gate_passed is False

    live = resolve_attack(
        actor_player="P1",
        actor_card_id="p1-mew",
        declared_attack_id=outer_id,
        attacks=attacks,
        state=state,
        choose=choose_exact((nightcap_id, LEAF)),
        copied_body_gate=copied_body_gate_policy(
            rows,
            opponent_prizes_remaining=2,
        ),
    )
    assert live.body_chain == (outer_id, nightcap_id, LEAF)
    assert live.state.events == ("leaf_effect",)

    assist_id = assist.guarded_definition.attack_id
    coin_state = State(
        pokemon=(
            PokemonRef(
                "p2-active",
                "Outer Target",
                "P2",
                "active",
                attacks=(assist_id,),
            ),
            PokemonRef(
                "p1-bench",
                "Leaf Source",
                "P1",
                "bench",
                attacks=(LEAF,),
            ),
        )
    )
    coin_attacks = {
        outer_id: outer.definition,
        assist_id: assist.guarded_definition,
        LEAF: LEAF_DEF,
    }

    try:
        resolve_attack(
            actor_player="P1",
            actor_card_id="p1-mew",
            declared_attack_id=outer_id,
            attacks=coin_attacks,
            state=coin_state,
            choose=choose_exact((assist_id,)),
            copied_body_gate=copied_body_gate_policy(rows),
        )
    except UnresolvedCopiedBodyControl:
        pass
    else:
        raise AssertionError("nested coin gate must require an explicit outcome")

    coin_heads = resolve_attack(
        actor_player="P1",
        actor_card_id="p1-mew",
        declared_attack_id=outer_id,
        attacks=coin_attacks,
        state=coin_state,
        choose=choose_exact((assist_id, LEAF)),
        copied_body_gate=copied_body_gate_policy(
            rows,
            coin_heads_by_attack_id={assist_id: True},
        ),
    )
    assert coin_heads.state.events == ("leaf_effect",)

    print(
        {
            "selected_gated_attack": "Nightcap",
            "false_requirement": "selected_then_body_suppressed",
            "true_requirement": "nested_copy_continues",
            "missing_coin_outcome": "explicitly_unresolved",
        }
    )


if __name__ == "__main__":
    main()
