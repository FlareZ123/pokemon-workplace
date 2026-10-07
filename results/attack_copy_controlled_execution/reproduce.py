from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from attack_copy_controlled_execution import resolve_declared_compiled_copy_attack
from attack_copy_kernel import AttackDef, PokemonRef, State, choose_exact
from attack_copy_kernel_compiler import compile_copy_attacks


LEAF = "test:leaf"
LEAF_DEF = AttackDef(LEAF, "Leaf", effect_label="leaf_effect")


def compiled_row(rows, card_id: str, attack_name: str):
    matches = [
        row
        for row in rows
        if row.card_id == card_id
        and row.guarded_definition is not None
        and row.guarded_definition.name == attack_name
    ]
    if len(matches) != 1:
        raise AssertionError((card_id, attack_name, len(matches)))
    return matches[0]


def target_state(owner: str = "P2", zone: str = "active") -> State:
    return State(
        pokemon=(
            PokemonRef(
                "target",
                "Target",
                owner,
                zone,
                attacks=(LEAF,),
            ),
        )
    )


def test_skill_thief(rows) -> None:
    skill = compiled_row(rows, "me5-54", "Skill Thief")
    assert skill.definition is None
    assert skill.outer_control is not None
    assert skill.outer_control.stage == "body"

    state = target_state()
    blocked = resolve_declared_compiled_copy_attack(
        skill,
        actor_player="P1",
        actor_card_id="p1-thievul",
        attacks={LEAF: LEAF_DEF},
        state=state,
        choose=choose_exact(()),
        actor_hand_size=1,
    )
    assert blocked.outcome == "resolve_without_copy"
    assert blocked.resolution is not None
    assert blocked.resolution.body_chain == (skill.guarded_definition.attack_id,)
    assert blocked.resolution.state.events == ()
    assert blocked.resolution.state.last_attack_for("P1") == skill.guarded_definition.attack_id

    live = resolve_declared_compiled_copy_attack(
        skill,
        actor_player="P1",
        actor_card_id="p1-thievul",
        attacks={LEAF: LEAF_DEF},
        state=state,
        choose=choose_exact((LEAF,)),
        actor_hand_size=0,
    )
    assert live.outcome == "proceed"
    assert live.resolution is not None
    assert live.resolution.state.events == ("leaf_effect",)


def test_nightcap(rows) -> None:
    nightcap = compiled_row(rows, "sm8-106", "Nightcap")
    assert nightcap.outer_control is not None
    assert nightcap.outer_control.stage == "declaration"

    state = target_state()
    illegal = resolve_declared_compiled_copy_attack(
        nightcap,
        actor_player="P1",
        actor_card_id="p1-nihilego",
        attacks={LEAF: LEAF_DEF},
        state=state,
        choose=choose_exact(()),
        opponent_prizes_remaining=3,
    )
    assert illegal.outcome == "declaration_illegal"
    assert illegal.resolution is None
    assert state.last_attack_for("P1") is None

    live = resolve_declared_compiled_copy_attack(
        nightcap,
        actor_player="P1",
        actor_card_id="p1-nihilego",
        attacks={LEAF: LEAF_DEF},
        state=state,
        choose=choose_exact((LEAF,)),
        opponent_prizes_remaining=2,
    )
    assert live.outcome == "proceed"
    assert live.resolution is not None
    assert live.resolution.state.events == ("leaf_effect",)


def test_assist(rows) -> None:
    assist = compiled_row(rows, "bw7-91", "Assist")
    assert assist.outer_control is not None
    assert assist.outer_control.kind == "coin_heads"

    state = target_state("P1", "bench")
    unresolved = resolve_declared_compiled_copy_attack(
        assist,
        actor_player="P1",
        actor_card_id="p1-liepard",
        attacks={LEAF: LEAF_DEF},
        state=state,
        choose=choose_exact(()),
    )
    assert unresolved.outcome == "random_outcome_required"
    assert unresolved.resolution is None

    tails = resolve_declared_compiled_copy_attack(
        assist,
        actor_player="P1",
        actor_card_id="p1-liepard",
        attacks={LEAF: LEAF_DEF},
        state=state,
        choose=choose_exact(()),
        coin_heads=False,
    )
    assert tails.outcome == "resolve_without_copy"
    assert tails.resolution is not None
    assert tails.resolution.state.events == ()
    assert tails.resolution.state.last_attack_for("P1") == assist.guarded_definition.attack_id

    heads = resolve_declared_compiled_copy_attack(
        assist,
        actor_player="P1",
        actor_card_id="p1-liepard",
        attacks={LEAF: LEAF_DEF},
        state=state,
        choose=choose_exact((LEAF,)),
        coin_heads=True,
    )
    assert heads.outcome == "proceed"
    assert heads.resolution is not None
    assert heads.resolution.state.events == ("leaf_effect",)


def main() -> None:
    rows = compile_copy_attacks(ROOT / "resources")
    assert sum(row.guarded_definition is not None for row in rows) == 7
    assert sum(row.outer_control is not None for row in rows) == 7

    test_skill_thief(rows)
    test_nightcap(rows)
    test_assist(rows)

    print(
        {
            "guarded_print_rows": sum(row.guarded_definition is not None for row in rows),
            "skill_thief_nonempty_hand": "resolve_without_copy",
            "nightcap_wrong_prizes": "declaration_illegal",
            "coin_without_outcome": "random_outcome_required",
        }
    )


if __name__ == "__main__":
    main()
