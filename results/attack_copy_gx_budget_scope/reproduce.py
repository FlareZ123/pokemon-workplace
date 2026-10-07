from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from attack_copy_kernel import (
    AttackDef,
    CopySelector,
    GXAlreadyUsed,
    PokemonRef,
    State,
    choose_exact,
    resolve_attack,
)

FOUL = "zoroark:foul-play"
TRICKSTER = "zoroark-gx:trickster-gx"
TIMELESS = "dialga-gx:timeless-gx"

ATTACKS = {
    FOUL: AttackDef(
        FOUL,
        "Foul Play",
        copy_selector=CopySelector("opponent_active"),
    ),
    TRICKSTER: AttackDef(
        TRICKSTER,
        "Trickster-GX",
        is_gx=True,
        copy_selector=CopySelector("opponent_in_play"),
    ),
    TIMELESS: AttackDef(
        TIMELESS,
        "Timeless-GX",
        is_gx=True,
        effect_label="extra_turn",
    ),
}


def opponent_dialga_state(*, gx_used: bool = False) -> State:
    return State(
        pokemon=(
            PokemonRef(
                "p2-dialga",
                "Dialga-GX",
                "P2",
                "active",
                types=("Dragon",),
                attacks=(TIMELESS,),
            ),
        ),
        gx_used_by=frozenset({"P1"}) if gx_used else frozenset(),
    )


def test_non_gx_copy_consumes_one_gx_use() -> None:
    result = resolve_attack(
        actor_player="P1",
        actor_card_id="p1-zoroark",
        declared_attack_id=FOUL,
        attacks=ATTACKS,
        state=opponent_dialga_state(),
        choose=choose_exact((TIMELESS,)),
    )
    assert result.body_chain == (FOUL, TIMELESS)
    assert result.state.gx_used_by == frozenset({"P1"})


def test_non_gx_copy_cannot_reuse_spent_gx_channel() -> None:
    try:
        resolve_attack(
            actor_player="P1",
            actor_card_id="p1-zoroark",
            declared_attack_id=FOUL,
            attacks=ATTACKS,
            state=opponent_dialga_state(gx_used=True),
            choose=choose_exact((TIMELESS,)),
        )
    except GXAlreadyUsed:
        pass
    else:
        raise AssertionError("copied GX attack was allowed after the GX channel was spent")


def test_gx_copy_attack_can_copy_gx_body_without_double_charge() -> None:
    result = resolve_attack(
        actor_player="P1",
        actor_card_id="p1-zoroark-gx",
        declared_attack_id=TRICKSTER,
        attacks=ATTACKS,
        state=opponent_dialga_state(),
        choose=choose_exact((TIMELESS,)),
    )
    assert result.body_chain == (TRICKSTER, TIMELESS)
    assert result.state.gx_used_by == frozenset({"P1"})


def test_gx_copy_attack_cannot_start_after_gx_channel_spent() -> None:
    try:
        resolve_attack(
            actor_player="P1",
            actor_card_id="p1-zoroark-gx",
            declared_attack_id=TRICKSTER,
            attacks=ATTACKS,
            state=opponent_dialga_state(gx_used=True),
            choose=choose_exact((TIMELESS,)),
        )
    except GXAlreadyUsed:
        pass
    else:
        raise AssertionError("Trickster-GX was allowed after the GX channel was spent")


def main() -> None:
    test_non_gx_copy_consumes_one_gx_use()
    test_non_gx_copy_cannot_reuse_spent_gx_channel()
    test_gx_copy_attack_can_copy_gx_body_without_double_charge()
    test_gx_copy_attack_cannot_start_after_gx_channel_spent()
    print("attack-copy GX budget scope regression: PASS")


if __name__ == "__main__":
    main()
