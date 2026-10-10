"""Covert Flight protects damage but cannot suppress copied Timeless-GX turn effect.

The canonical attack-copy and turn-schedule kernels execute attack identities
and the turn-boundary effect. Damage protection is checked separately against
the exact Covert Flight and Timeless print texts, not falsely represented as a
full damage engine.
"""

from __future__ import annotations

from dataclasses import replace
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from attack_copy_kernel import (  # noqa: E402
    AttackDef, CopySelector, PokemonRef, State,
    TurnBoundaryEffect, choose_exact, resolve_attack
)
from attack_copy_turn_boundary_bridge import close_declared_attack  # noqa: E402
from canonical_turn_sequence_owner import (  # noqa: E402
    TurnScheduleState, advance_turn
)
from turn_action_budget import TurnActionBudget  # noqa: E402
from unified_state_kernel import make_state  # noqa: E402


APEX = "apex"
TIMELESS = "timeless"
COVERT = "covert"
COPYCAT = "copycat"


def card(set_id: str, ident: str) -> dict:
    rows = json.loads(
        (ROOT / "resources" / "cards" / "en" / f"{set_id}.json")
        .read_text(encoding="utf-8")
    )
    return next(row for row in rows if row["id"] == ident)


def advance_after(schedule, budget_current, budget_other, resolution):
    closed = close_declared_attack(schedule, budget_current, resolution)
    assert closed is not None
    result = advance_turn(closed[0], closed[1], budget_other)
    assert result is not None
    return result


def main() -> None:
    drago = card("swsh12", "swsh12-136")
    noivern = card("sv2", "sv2-153")
    mimikyu = card("sm2", "sm2-58")
    dialga = card("sm5", "sm5-100")

    covert = next(a for a in noivern["attacks"] if a["name"] == "Covert Flight")
    timeless = next(a for a in dialga["attacks"] if a["name"] == "Timeless-GX")
    copycat = next(a for a in mimikyu["attacks"] if a["name"] == "Copycat")

    assert drago["types"] == ["Dragon"]
    assert noivern["types"] == ["Dragon"]
    assert "prevent all damage done to this Pokémon by attacks from Basic Pokémon" in covert["text"]
    assert noivern["subtypes"] == ["Stage 1", "ex"]
    assert "Basic" in mimikyu["subtypes"]
    assert copycat["cost"] == ["Psychic", "Colorless"]
    assert int(timeless["damage"]) == 150
    assert "Take another turn after this one" in timeless["text"]

    fixture = json.loads(
        (ROOT / "results" / "regidrago_budew_promotion_baselines"
         / "aichi9_counts.json").read_text(encoding="utf-8")
    )
    assert sum(r["noivern_ex_sv2_153"] for r in fixture["decklists"]) == 7

    attacks = {
        APEX: AttackDef(
            APEX, "Apex Dragon",
            copy_selector=CopySelector(
                source="own_discard", required_type="Dragon"
            )
        ),
        TIMELESS: AttackDef(
            TIMELESS, "Timeless-GX", is_gx=True,
            turn_boundary_effect=TurnBoundaryEffect(
                take_another_turn=True, skip_pokemon_checkup=True
            )
        ),
        COVERT: AttackDef(COVERT, "Covert Flight"),
        COPYCAT: AttackDef(
            COPYCAT, "Copycat",
            copy_selector=CopySelector(
                source="opponent_last_attack", require_non_gx=True
            ),
        ),
    }
    game = State(pokemon=(
        PokemonRef("regidrago", "Regidrago VSTAR", "P1", "active",
                   types=("Dragon",), attacks=(APEX,)),
        PokemonRef("noivern", "Noivern ex", "P1", "discard",
                   types=("Dragon",), attacks=(COVERT,)),
        PokemonRef("dialga1", "Dialga-GX", "P1", "discard",
                   types=("Dragon",), attacks=(TIMELESS,)),
        PokemonRef("mimikyu", "Mimikyu", "P2", "active",
                   types=("Psychic",), attacks=(COPYCAT,)),
        PokemonRef("dialga2", "Dialga-GX", "P2", "discard",
                   types=("Dragon",), attacks=(TIMELESS,)),
    ))
    sched = TurnScheduleState("P1", "P2")
    p1 = make_state({}, turn_budget=TurnActionBudget())
    p2 = make_state({}, turn_budget=TurnActionBudget())

    first = resolve_attack(
        actor_player="P1", actor_card_id="regidrago",
        declared_attack_id=APEX, attacks=attacks, state=game,
        choose=choose_exact((TIMELESS,))
    )
    first_advance = advance_after(sched, p1, p2, first)
    assert first_advance.same_player_continues

    second = resolve_attack(
        actor_player="P1", actor_card_id="regidrago",
        declared_attack_id=APEX, attacks=attacks,
        state=replace(first.state, pending_turn_boundary=None),
        choose=choose_exact((COVERT,))
    )
    assert second.body_chain == (APEX, COVERT)
    assert second.state.last_attack_for("P1") == APEX
    next_advance = advance_after(
        first_advance.schedule, first_advance.current_state,
        first_advance.other_state, second
    )
    assert next_advance.schedule.current_player == "P2"

    response = resolve_attack(
        actor_player="P2", actor_card_id="mimikyu",
        declared_attack_id=COPYCAT, attacks=attacks,
        state=second.state,
        choose=choose_exact((APEX, TIMELESS))
    )
    assert response.body_chain == (COPYCAT, APEX, TIMELESS)
    assert response.state.gx_used_by == frozenset({"P1", "P2"})
    assert response.state.pending_turn_boundary is not None
    assert response.state.pending_turn_boundary.take_another_turn

    # Printed Covert Flight protects P1's Regidrago from attack *damage*
    # caused by Basic Mimikyu. This independent conditional damage check
    # does not cancel a non-damage extra-turn effect on the attacking player.
    source_is_basic = "Basic" in mimikyu["subtypes"]
    prevent_damage = source_is_basic and second.body_chain == (APEX, COVERT)
    delivered_to_regidrago = 0 if prevent_damage else int(timeless["damage"])
    assert delivered_to_regidrago == 0

    response_advance = advance_after(
        next_advance.schedule, next_advance.current_state,
        next_advance.other_state, response
    )
    assert response_advance.same_player_continues
    assert response_advance.schedule.current_player == "P2"
    assert not response_advance.pokemon_checkup_occurs

    print(json.dumps({
        "aichi_lists_with_noivern_ex": 7,
        "regidrago_declared_on_cover_turn": second.state.last_attack_for("P1"),
        "mimikyu_copycat_nested_attack": list(response.body_chain),
        "timeless_printed_attack_damage": int(timeless["damage"]),
        "covert_prevented_damage_to_regidrago": delivered_to_regidrago,
        "mimikyu_still_gains_bonus_turn": response_advance.same_player_continues,
    }, indent=2))


if __name__ == "__main__":
    main()
