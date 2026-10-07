from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from attack_copy_kernel import (
    AttackDef,
    CopyCycleError,
    CopySelector,
    GXAlreadyUsed,
    IllegalCopyTarget,
    PokemonRef,
    State,
    choose_exact,
    resolve_attack,
)

COPYCAT = "mimikyu:copycat"
APEX = "regidrago:apex-dragon"
TIMELESS = "dialga:timeless-gx"
SHADOW = "marshadow:shadow-imitation"
FOUL = "zoroark:foul-play"
HAUGHTY = "persian:haughty-order"

ATTACKS = {
    COPYCAT: AttackDef(
        COPYCAT,
        "Copycat",
        copy_selector=CopySelector("opponent_last_attack", require_non_gx=True),
    ),
    APEX: AttackDef(
        APEX,
        "Apex Dragon",
        copy_selector=CopySelector("own_discard", required_type="Dragon"),
    ),
    TIMELESS: AttackDef(TIMELESS, "Timeless-GX", is_gx=True, effect_label="extra_turn"),
    SHADOW: AttackDef(
        SHADOW,
        "Shadow Imitation",
        copy_selector=CopySelector("opponent_active", require_non_gx=True),
    ),
    FOUL: AttackDef(
        FOUL,
        "Foul Play",
        copy_selector=CopySelector("opponent_active"),
    ),
    HAUGHTY: AttackDef(
        HAUGHTY,
        "Haughty Order",
        copy_selector=CopySelector("opponent_revealed"),
        pre_event="reveal_top_10",
        post_event="shuffle_revealed",
    ),
}


def base_state() -> State:
    return State(
        pokemon=(
            PokemonRef(
                "p1-dialga",
                "Dialga-GX",
                "P1",
                "discard",
                types=("Dragon",),
                attacks=(TIMELESS,),
            ),
            PokemonRef(
                "p2-dialga",
                "Dialga-GX",
                "P2",
                "discard",
                types=("Dragon",),
                attacks=(TIMELESS,),
            ),
        ),
        last_declared_attack=(("P2", APEX),),
    )


def test_nested_copycat_apex_timeless() -> None:
    result = resolve_attack(
        actor_player="P1",
        actor_card_id="p1-mimikyu",
        declared_attack_id=COPYCAT,
        attacks=ATTACKS,
        state=base_state(),
        choose=choose_exact((APEX, TIMELESS)),
    )
    assert result.declared_attack_id == COPYCAT
    assert result.body_chain == (COPYCAT, APEX, TIMELESS)
    assert [step.declared_attack_id for step in result.trace] == [COPYCAT, COPYCAT, COPYCAT]
    assert result.state.last_attack_for("P1") == COPYCAT
    assert "P1" in result.state.gx_used_by


def test_last_attack_identity_is_outer_attack() -> None:
    state = State(
        pokemon=(
            PokemonRef(
                "p2-dialga",
                "Dialga-GX",
                "P2",
                "discard",
                types=("Dragon",),
                attacks=(TIMELESS,),
            ),
        )
    )
    result = resolve_attack(
        actor_player="P2",
        actor_card_id="p2-regidrago",
        declared_attack_id=APEX,
        attacks=ATTACKS,
        state=state,
        choose=choose_exact((TIMELESS,)),
    )
    assert result.body_chain == (APEX, TIMELESS)
    assert result.state.last_attack_for("P2") == APEX
    assert "P2" in result.state.gx_used_by


def test_apex_uses_current_players_discard() -> None:
    p2_only_attack = "p2-only:dragon-attack"
    attacks = dict(ATTACKS)
    attacks[p2_only_attack] = AttackDef(p2_only_attack, "Opponent-only endpoint")
    state = State(
        pokemon=(
            PokemonRef(
                "p1-dialga",
                "Dialga-GX",
                "P1",
                "discard",
                types=("Dragon",),
                attacks=(TIMELESS,),
            ),
            PokemonRef(
                "p2-dragon",
                "P2 Dragon",
                "P2",
                "discard",
                types=("Dragon",),
                attacks=(p2_only_attack,),
            ),
        ),
        last_declared_attack=(("P2", APEX),),
    )
    try:
        resolve_attack(
            actor_player="P1",
            actor_card_id="p1-mimikyu",
            declared_attack_id=COPYCAT,
            attacks=attacks,
            state=state,
            choose=choose_exact((APEX, p2_only_attack)),
        )
    except IllegalCopyTarget:
        pass
    else:
        raise AssertionError("Apex Dragon incorrectly saw the opponent's discard pile")


def test_gx_resource_applies_to_copied_endpoint() -> None:
    state = State(
        pokemon=base_state().pokemon,
        gx_used_by=frozenset({"P1"}),
        last_declared_attack=(("P2", APEX),),
    )
    try:
        resolve_attack(
            actor_player="P1",
            actor_card_id="p1-mimikyu",
            declared_attack_id=COPYCAT,
            attacks=ATTACKS,
            state=state,
            choose=choose_exact((APEX, TIMELESS)),
        )
    except GXAlreadyUsed:
        pass
    else:
        raise AssertionError("copied Timeless-GX ignored the once-per-game GX resource")


def test_no_progress_reentry_is_detected() -> None:
    state = State(
        pokemon=(
            PokemonRef(
                "discarded-regidrago",
                "Regidrago VSTAR",
                "P1",
                "discard",
                types=("Dragon",),
                attacks=(APEX,),
            ),
        )
    )
    try:
        resolve_attack(
            actor_player="P1",
            actor_card_id="active-regidrago",
            declared_attack_id=APEX,
            attacks=ATTACKS,
            state=state,
            choose=choose_exact((APEX,)),
        )
    except CopyCycleError:
        pass
    else:
        raise AssertionError("no-progress Apex Dragon recursion was not detected")



def test_active_slot_binding_blocks_naive_foul_play_escape() -> None:
    state = State(
        pokemon=(
            PokemonRef(
                "p2-zoroark",
                "Zoroark",
                "P2",
                "active",
                attacks=(FOUL,),
            ),
            PokemonRef(
                "p2-gx-bench",
                "GX Bench Target",
                "P2",
                "bench",
                attacks=(TIMELESS,),
            ),
        )
    )
    try:
        resolve_attack(
            actor_player="P1",
            actor_card_id="p1-marshadow",
            declared_attack_id=SHADOW,
            attacks=ATTACKS,
            state=state,
            choose=choose_exact((FOUL, TIMELESS)),
        )
    except IllegalCopyTarget:
        pass
    else:
        raise AssertionError("nested Foul Play incorrectly escaped the opponent Active slot")


def test_active_slot_binding_still_allows_apex_escape() -> None:
    state = State(
        pokemon=(
            PokemonRef(
                "p2-regidrago",
                "Regidrago VSTAR",
                "P2",
                "active",
                types=("Dragon",),
                attacks=(APEX,),
            ),
            PokemonRef(
                "p1-dialga",
                "Dialga-GX",
                "P1",
                "discard",
                types=("Dragon",),
                attacks=(TIMELESS,),
            ),
        )
    )
    result = resolve_attack(
        actor_player="P1",
        actor_card_id="p1-marshadow",
        declared_attack_id=SHADOW,
        attacks=ATTACKS,
        state=state,
        choose=choose_exact((APEX, TIMELESS)),
    )
    assert result.body_chain == (SHADOW, APEX, TIMELESS)
    assert "P1" in result.state.gx_used_by



def test_copy_body_continuation_resumes_outer_text() -> None:
    state = State(
        pokemon=(
            PokemonRef(
                "p2-revealed-dialga",
                "Dialga-GX",
                "P2",
                "revealed",
                types=("Dragon",),
                attacks=(TIMELESS,),
            ),
        )
    )
    result = resolve_attack(
        actor_player="P1",
        actor_card_id="p1-persian",
        declared_attack_id=HAUGHTY,
        attacks=ATTACKS,
        state=state,
        choose=choose_exact((TIMELESS,)),
    )
    assert result.body_chain == (HAUGHTY, TIMELESS)
    assert result.state.events == ("reveal_top_10", "extra_turn", "shuffle_revealed")
    assert result.state.last_attack_for("P1") == HAUGHTY


def main() -> None:
    test_nested_copycat_apex_timeless()
    test_last_attack_identity_is_outer_attack()
    test_apex_uses_current_players_discard()
    test_gx_resource_applies_to_copied_endpoint()
    test_no_progress_reentry_is_detected()
    test_active_slot_binding_blocks_naive_foul_play_escape()
    test_active_slot_binding_still_allows_apex_escape()
    test_copy_body_continuation_resumes_outer_text()
    print("copy-resolution kernel regressions passed")


if __name__ == "__main__":
    main()
