from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from attack_copy_kernel import (
    AttackDef,
    CopySelector,
    MissingCopyChooser,
    PokemonRef,
    State,
    choose_exact,
    resolve_attack,
)

RECALL = "charizard:recall"
MIMED = "mime-jr:mimed-games"
NIGHT = "n-zoroark:night-joker"
A = "endpoint:a"
B = "endpoint:b"

ATTACKS = {
    RECALL: AttackDef(
        RECALL,
        "Recall",
        copy_selector=CopySelector("self_previous_evolution"),
    ),
    MIMED: AttackDef(
        MIMED,
        "Mimed Games",
        copy_selector=CopySelector(
            "opponent_in_play",
            chooser="opponent",
        ),
    ),
    NIGHT: AttackDef(
        NIGHT,
        "Night Joker",
        copy_selector=CopySelector(
            "own_bench",
            required_name_prefix="N's ",
        ),
    ),
    A: AttackDef(A, "Endpoint A", effect_label="A"),
    B: AttackDef(B, "Endpoint B", effect_label="B"),
}


def test_previous_evolution_attacks_live_on_actor_history() -> None:
    state = State(
        pokemon=(
            PokemonRef(
                "p1-charizard",
                "Charizard",
                "P1",
                "active",
                attacks=(RECALL,),
                previous_evolution_attacks=(A, B),
            ),
        )
    )
    result = resolve_attack(
        actor_player="P1",
        actor_card_id="p1-charizard",
        declared_attack_id=RECALL,
        attacks=ATTACKS,
        state=state,
        choose=choose_exact((B,)),
    )
    assert result.body_chain == (RECALL, B)
    assert result.state.events == ("B",)


def test_opponent_choice_uses_separate_policy() -> None:
    state = State(
        pokemon=(
            PokemonRef(
                "p2-a",
                "Opponent A",
                "P2",
                "active",
                attacks=(A,),
            ),
            PokemonRef(
                "p2-b",
                "Opponent B",
                "P2",
                "bench",
                attacks=(B,),
            ),
        )
    )
    try:
        resolve_attack(
            actor_player="P1",
            actor_card_id="p1-mime-jr",
            declared_attack_id=MIMED,
            attacks=ATTACKS,
            state=state,
            choose=choose_exact((A,)),
        )
    except MissingCopyChooser:
        pass
    else:
        raise AssertionError("opponent-owned copy choice defaulted to the actor")

    result = resolve_attack(
        actor_player="P1",
        actor_card_id="p1-mime-jr",
        declared_attack_id=MIMED,
        attacks=ATTACKS,
        state=state,
        choose=choose_exact((A,)),
        choose_opponent=choose_exact((B,)),
    )
    assert result.body_chain == (MIMED, B)
    assert result.state.events == ("B",)


def test_named_bench_filter_excludes_other_pokemon() -> None:
    state = State(
        pokemon=(
            PokemonRef(
                "p1-n",
                "N's Reshiram",
                "P1",
                "bench",
                attacks=(A,),
            ),
            PokemonRef(
                "p1-other",
                "Reshiram",
                "P1",
                "bench",
                attacks=(B,),
            ),
        )
    )
    result = resolve_attack(
        actor_player="P1",
        actor_card_id="p1-n-zoroark",
        declared_attack_id=NIGHT,
        attacks=ATTACKS,
        state=state,
        choose=choose_exact((A,)),
    )
    assert result.body_chain == (NIGHT, A)
    assert result.state.events == ("A",)


def main() -> None:
    test_previous_evolution_attacks_live_on_actor_history()
    test_opponent_choice_uses_separate_policy()
    test_named_bench_filter_excludes_other_pokemon()
    print("attack-copy source geometry regression: PASS")


if __name__ == "__main__":
    main()
