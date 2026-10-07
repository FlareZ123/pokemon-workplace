"""Reproduce turn-scoped attack provenance and Ω Barrage boundaries."""

from __future__ import annotations

import json
import sys
from dataclasses import replace
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from attack_copy_kernel import (  # noqa: E402
    AttackDef,
    CopySelector,
    IllegalCopyTarget,
    PokemonRef,
    State,
    choose_exact,
    resolve_attack,
)
from build_expanded_legality_baseline import classify_effective_legality  # noqa: E402
from turn_attack_history import (  # noqa: E402
    LossyLastAttackProjectionError,
    TurnAttackHistory,
    advance_turn,
    copy_kernel_last_attack_projection,
    record_attack,
)
from turn_sequence_kernel import (  # noqa: E402
    TurnSequenceState,
    advance_turn as advance_sequence_turn,
    close_turn_voluntarily,
    close_turn_with_attack,
)

COPYCAT = "mimikyu:copycat"
APEX = "regidrago:apex-dragon"
TIMELESS = "dialga:timeless-gx"
BURROW = "bunnelby:burrow"
ROTOTILLER = "bunnelby:rototiller"

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
    TIMELESS: AttackDef(
        TIMELESS,
        "Timeless-GX",
        is_gx=True,
        effect_label="extra_turn",
    ),
}


def load_card(card_id: str) -> dict:
    set_id = card_id.split("-", 1)[0]
    rows = json.loads(
        (ROOT / "resources" / "cards" / "en" / f"{set_id}.json").read_text(
            encoding="utf-8"
        )
    )
    return next(card for card in rows if card["id"] == card_id)


def omega_barrage_prints() -> list[tuple[str, str]]:
    sets = json.loads(
        (ROOT / "resources" / "sets" / "en.json").read_text(encoding="utf-8")
    )
    expanded_sets = {
        row["id"]
        for row in sets
        if (row.get("legalities") or {}).get("expanded") == "Legal"
    }

    matches: list[tuple[str, str]] = []
    for path in sorted((ROOT / "resources" / "cards" / "en").glob("*.json")):
        if path.stem not in expanded_sets:
            continue
        for card in json.loads(path.read_text(encoding="utf-8")):
            status, _ = classify_effective_legality(card)
            if status != "Legal":
                continue
            trait = card.get("ancientTrait") or {}
            if "may attack twice a turn" not in (trait.get("text") or "").lower():
                continue
            matches.append((card["id"], card["name"]))
    return matches


def copy_state() -> State:
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
        )
    )


def assert_card_text_evidence() -> None:
    mimikyu = load_card("smp-SM99")
    copycat = next(row for row in mimikyu["attacks"] if row["name"] == "Copycat")
    assert "during their last turn" in copycat["text"].lower()

    dialga = load_card("sm5-100")
    timeless = next(row for row in dialga["attacks"] if row["name"] == "Timeless-GX")
    assert "Take another turn after this one." in timeless["text"]

    expected = [
        ("xy5-26", "Torchic"),
        ("xy5-69", "Nidoqueen"),
        ("xy5-81", "Medicham"),
        ("xy5-97", "Excadrill"),
        ("xy5-121", "Bunnelby"),
    ]
    assert omega_barrage_prints() == expected

    bunnelby = load_card("xy5-121")
    trait = bunnelby.get("ancientTrait") or {}
    assert trait.get("name") == "Ω Barrage"
    assert "may attack twice a turn" in trait.get("text", "").lower()
    assert [row["name"] for row in bunnelby["attacks"]] == ["Burrow", "Rototiller"]


def assert_blank_extra_turn_clears_stale_attack() -> None:
    p2_attack = resolve_attack(
        actor_player="P2",
        actor_card_id="p2-regidrago",
        declared_attack_id=APEX,
        attacks=ATTACKS,
        state=copy_state(),
        choose=choose_exact((TIMELESS,)),
    )
    assert p2_attack.state.last_attack_for("P2") == APEX

    history = TurnAttackHistory(current_player="P2")
    history = record_attack(history, APEX)

    sequence = TurnSequenceState("P2", "P1")
    p2_end = close_turn_with_attack(
        sequence,
        take_another_turn=True,
        skip_pokemon_checkup=True,
    )
    assert p2_end is not None
    extra = advance_sequence_turn(p2_end)
    assert extra is not None
    assert extra.state.current_player == "P2"

    history = advance_turn(history, next_player=extra.state.current_player)
    assert history.last_turn_attacks_for("P2") == (APEX,)
    assert copy_kernel_last_attack_projection(history) == (("P2", APEX),)

    blank_end = close_turn_voluntarily(extra.state)
    assert blank_end is not None
    to_p1 = advance_sequence_turn(blank_end)
    assert to_p1 is not None
    assert to_p1.state.current_player == "P1"

    history = advance_turn(history, next_player=to_p1.state.current_player)
    assert history.last_turn_attacks_for("P2") == ()
    assert copy_kernel_last_attack_projection(history) == ()

    stale = resolve_attack(
        actor_player="P1",
        actor_card_id="p1-mimikyu",
        declared_attack_id=COPYCAT,
        attacks=ATTACKS,
        state=p2_attack.state,
        choose=choose_exact((APEX, TIMELESS)),
    )
    assert stale.body_chain == (COPYCAT, APEX, TIMELESS)

    corrected_state = replace(
        p2_attack.state,
        last_declared_attack=copy_kernel_last_attack_projection(history),
    )
    try:
        resolve_attack(
            actor_player="P1",
            actor_card_id="p1-mimikyu",
            declared_attack_id=COPYCAT,
            attacks=ATTACKS,
            state=corrected_state,
            choose=choose_exact((APEX, TIMELESS)),
        )
    except IllegalCopyTarget:
        pass
    else:
        raise AssertionError("blank last turn failed to clear stale Copycat provenance")


def assert_other_players_record_survives_extra_turn() -> None:
    history = TurnAttackHistory(current_player="P2")
    history = record_attack(history, APEX)
    history = advance_turn(history, next_player="P1")
    assert history.last_turn_attacks_for("P2") == (APEX,)

    history = record_attack(history, COPYCAT)
    history = advance_turn(history, next_player="P1")
    assert history.last_turn_attacks_for("P2") == (APEX,)
    assert history.last_turn_attacks_for("P1") == (COPYCAT,)


def assert_multi_attack_turn_is_not_scalar() -> None:
    history = TurnAttackHistory(current_player="P2")
    history = record_attack(history, BURROW)
    history = record_attack(history, ROTOTILLER)
    history = advance_turn(history, next_player="P1")

    assert history.last_turn_attacks_for("P2") == (BURROW, ROTOTILLER)
    try:
        copy_kernel_last_attack_projection(history)
    except LossyLastAttackProjectionError:
        pass
    else:
        raise AssertionError("multi-attack turn was silently collapsed to one attack")


def main() -> None:
    assert_card_text_evidence()
    assert_blank_extra_turn_clears_stale_attack()
    assert_other_players_record_survives_extra_turn()
    assert_multi_attack_turn_is_not_scalar()
    print("turn attack provenance regression: PASS")


if __name__ == "__main__":
    main()
