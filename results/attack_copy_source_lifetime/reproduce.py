from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from attack_copy_kernel import (
    AmbiguousCopySource,
    AttackDef,
    CopySelector,
    IllegalCopyTarget,
    PokemonRef,
    State,
    choose_exact,
    choose_source_exact,
    resolve_attack,
)

HYPNOTIC = "malamar:hypnotic-reign"
SEEK = "slowking:seek-inspiration"
ENDPOINT = "source:endpoint"
GX_ENDPOINT = "source:gx-endpoint"

ATTACKS = {
    HYPNOTIC: AttackDef(
        HYPNOTIC,
        "Hypnotic Reign",
        copy_selector=CopySelector(
            "opponent_hand",
            require_non_gx=True,
            move_selected_source_to="discard",
        ),
    ),
    SEEK: AttackDef(
        SEEK,
        "Seek Inspiration",
        copy_selector=CopySelector(
            "own_deck_top",
            require_no_rule_box=True,
            move_selected_source_to="discard",
        ),
    ),
    ENDPOINT: AttackDef(
        ENDPOINT,
        "Endpoint",
        effect_label="endpoint_body",
    ),
    GX_ENDPOINT: AttackDef(
        GX_ENDPOINT,
        "Endpoint-GX",
        is_gx=True,
        effect_label="gx_body",
    ),
}


def zones(state: State) -> dict[str, str]:
    return {card.card_id: card.zone for card in state.pokemon}


def test_duplicate_hypnotic_sources_require_physical_choice() -> None:
    state = State(
        pokemon=(
            PokemonRef("p2-copy-a", "Source A", "P2", "hand", attacks=(ENDPOINT,)),
            PokemonRef("p2-copy-b", "Source B", "P2", "hand", attacks=(ENDPOINT,)),
        )
    )
    try:
        resolve_attack(
            actor_player="P1",
            actor_card_id="p1-malamar",
            declared_attack_id=HYPNOTIC,
            attacks=ATTACKS,
            state=state,
            choose=choose_exact((ENDPOINT,)),
        )
    except AmbiguousCopySource:
        pass
    else:
        raise AssertionError("duplicate source instances were silently collapsed")

    result = resolve_attack(
        actor_player="P1",
        actor_card_id="p1-malamar",
        declared_attack_id=HYPNOTIC,
        attacks=ATTACKS,
        state=state,
        choose=choose_exact((ENDPOINT,)),
        choose_source=choose_source_exact(("p2-copy-b",)),
    )
    assert result.body_chain == (HYPNOTIC, ENDPOINT)
    assert result.state.events == ("endpoint_body",)
    assert zones(result.state) == {
        "p2-copy-a": "hand",
        "p2-copy-b": "discard",
    }


def test_hypnotic_non_gx_filter_applies_before_source_commit() -> None:
    state = State(
        pokemon=(
            PokemonRef("p2-gx", "GX Source", "P2", "hand", attacks=(GX_ENDPOINT,)),
        )
    )
    try:
        resolve_attack(
            actor_player="P1",
            actor_card_id="p1-malamar",
            declared_attack_id=HYPNOTIC,
            attacks=ATTACKS,
            state=state,
            choose=choose_exact((GX_ENDPOINT,)),
        )
    except IllegalCopyTarget:
        pass
    else:
        raise AssertionError("Hypnotic Reign accepted a GX endpoint")
    assert zones(state) == {"p2-gx": "hand"}


def test_seek_moves_selected_top_card_before_body_completes() -> None:
    state = State(
        pokemon=(
            PokemonRef(
                "p1-top",
                "Top Pokémon",
                "P1",
                "deck_top",
                attacks=(ENDPOINT,),
                has_rule_box=False,
            ),
        )
    )
    result = resolve_attack(
        actor_player="P1",
        actor_card_id="p1-slowking",
        declared_attack_id=SEEK,
        attacks=ATTACKS,
        state=state,
        choose=choose_exact((ENDPOINT,)),
    )
    assert result.body_chain == (SEEK, ENDPOINT)
    assert result.state.events == ("endpoint_body",)
    assert zones(result.state) == {"p1-top": "discard"}


def test_seek_rule_box_filter_blocks_before_movement() -> None:
    state = State(
        pokemon=(
            PokemonRef(
                "p1-top-rulebox",
                "Rule Box Pokémon",
                "P1",
                "deck_top",
                attacks=(ENDPOINT,),
                has_rule_box=True,
            ),
        )
    )
    try:
        resolve_attack(
            actor_player="P1",
            actor_card_id="p1-slowking",
            declared_attack_id=SEEK,
            attacks=ATTACKS,
            state=state,
            choose=choose_exact((ENDPOINT,)),
        )
    except IllegalCopyTarget:
        pass
    else:
        raise AssertionError("Seek Inspiration accepted a Rule Box source")
    assert zones(state) == {"p1-top-rulebox": "deck_top"}


def main() -> None:
    test_duplicate_hypnotic_sources_require_physical_choice()
    test_hypnotic_non_gx_filter_applies_before_source_commit()
    test_seek_moves_selected_top_card_before_body_completes()
    test_seek_rule_box_filter_blocks_before_movement()
    print("attack-copy source lifetime regression: PASS")


if __name__ == "__main__":
    main()
