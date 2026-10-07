from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from attack_copy_kernel import (
    AttackDef,
    CopySelector,
    PokemonRef,
    State,
    choose_exact,
    resolve_attack,
)

HAUGHTY = "persian:haughty-order"
HYPNOTIC = "malamar:hypnotic-reign"
ENDPOINT = "target:endpoint"

ATTACKS = {
    HAUGHTY: AttackDef(
        HAUGHTY,
        "Haughty Order",
        copy_selector=CopySelector(
            "opponent_revealed",
            optional_selection=True,
        ),
        pre_event="reveal_top_10",
        post_event="shuffle_revealed",
    ),
    HYPNOTIC: AttackDef(
        HYPNOTIC,
        "Hypnotic Reign",
        copy_selector=CopySelector(
            "opponent_hand",
            require_non_gx=True,
            move_selected_source_to="discard",
            optional_selection=True,
        ),
        pre_event="reveal_hand",
    ),
    ENDPOINT: AttackDef(ENDPOINT, "Endpoint", effect_label="endpoint"),
}


def test_haughty_can_decline_with_eligible_target() -> None:
    state = State(
        pokemon=(
            PokemonRef(
                "p2-revealed",
                "Revealed Pokémon",
                "P2",
                "revealed",
                attacks=(ENDPOINT,),
            ),
        )
    )
    result = resolve_attack(
        actor_player="P1",
        actor_card_id="p1-persian",
        declared_attack_id=HAUGHTY,
        attacks=ATTACKS,
        state=state,
        choose=choose_exact((None,)),
    )
    assert result.body_chain == (HAUGHTY,)
    assert result.state.events == ("reveal_top_10", "shuffle_revealed")
    assert result.trace[0].selected_attack_id is None
    assert result.trace[0].selected_body_executed is False
    assert result.state.last_attack_for("P1") == HAUGHTY


def test_haughty_no_target_still_runs_cleanup() -> None:
    result = resolve_attack(
        actor_player="P1",
        actor_card_id="p1-persian",
        declared_attack_id=HAUGHTY,
        attacks=ATTACKS,
        state=State(pokemon=()),
        choose=choose_exact(()),
    )
    assert result.body_chain == (HAUGHTY,)
    assert result.state.events == ("reveal_top_10", "shuffle_revealed")
    assert result.trace[0].selected_body_executed is False


def test_hypnotic_decline_preserves_hand_source() -> None:
    state = State(
        pokemon=(
            PokemonRef(
                "p2-hand",
                "Hand Pokémon",
                "P2",
                "hand",
                attacks=(ENDPOINT,),
            ),
        )
    )
    result = resolve_attack(
        actor_player="P1",
        actor_card_id="p1-malamar",
        declared_attack_id=HYPNOTIC,
        attacks=ATTACKS,
        state=state,
        choose=choose_exact((None,)),
    )
    assert result.body_chain == (HYPNOTIC,)
    assert result.state.events == ("reveal_hand",)
    assert {p.card_id: p.zone for p in result.state.pokemon} == {
        "p2-hand": "hand"
    }


def main() -> None:
    test_haughty_can_decline_with_eligible_target()
    test_haughty_no_target_still_runs_cleanup()
    test_hypnotic_decline_preserves_hand_source()
    print("attack-copy optional selection regression: PASS")


if __name__ == "__main__":
    main()
