"""Reproduce the Regidrago attack-history evasion result."""

from __future__ import annotations

from dataclasses import replace
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from attack_copy_kernel import (  # noqa: E402
    AttackDef,
    CopySelector,
    IllegalCopyTarget,
    PokemonRef,
    State,
    TurnBoundaryEffect,
    choose_exact,
    resolve_attack,
)
from attack_copy_turn_boundary_bridge import close_declared_attack  # noqa: E402
from build_expanded_legality_baseline import classify_effective_legality  # noqa: E402
from canonical_turn_sequence_owner import TurnScheduleState, advance_turn  # noqa: E402
from turn_action_budget import TurnActionBudget  # noqa: E402
from unified_state_kernel import make_state  # noqa: E402

APEX = "regidrago:apex-dragon"
TIMELESS = "dialga:timeless-gx"
ITCHY = "budew:itchy-pollen"
RETRIBUTION = "koraidon:retribution-strike"
TRIFROST = "kyurem:trifrost"
COPYCAT = "mimikyu:copycat"

ATTACKS = {
    APEX: AttackDef(
        APEX,
        "Apex Dragon",
        copy_selector=CopySelector(
            source="own_discard",
            required_type="Dragon",
        ),
    ),
    TIMELESS: AttackDef(
        TIMELESS,
        "Timeless-GX",
        is_gx=True,
        turn_boundary_effect=TurnBoundaryEffect(
            take_another_turn=True,
            skip_pokemon_checkup=True,
        ),
    ),
    ITCHY: AttackDef(ITCHY, "Itchy Pollen"),
    RETRIBUTION: AttackDef(
        RETRIBUTION,
        "Retribution Strike",
        energy_cost=("Colorless", "Colorless"),
    ),
    TRIFROST: AttackDef(TRIFROST, "Trifrost"),
    COPYCAT: AttackDef(
        COPYCAT,
        "Copycat",
        copy_selector=CopySelector(
            source="opponent_last_attack",
            require_non_gx=True,
        ),
    ),
}


def card(set_id: str, card_id: str) -> dict:
    rows = json.loads(
        (ROOT / "resources" / "cards" / "en" / f"{set_id}.json").read_text(
            encoding="utf-8"
        )
    )
    return next(row for row in rows if row["id"] == card_id)


def attack(card_row: dict, name: str) -> dict:
    return next(row for row in card_row["attacks"] if row["name"] == name)


def legal(card_row: dict) -> None:
    assert classify_effective_legality(card_row)[0] == "Legal"


def aichi_fixture() -> dict:
    return json.loads(
        (
            ROOT
            / "results"
            / "regidrago_attack_history_evasion"
            / "aichi_2026_published_regidrago.json"
        ).read_text(encoding="utf-8")
    )


def with_active(state: State, owner: str, card_id: str) -> State:
    return replace(
        state,
        pokemon=tuple(
            replace(
                pokemon,
                zone=(
                    "active"
                    if pokemon.card_id == card_id
                    else (
                        "bench"
                        if pokemon.owner == owner
                        and pokemon.zone == "active"
                        else pokemon.zone
                    )
                ),
            )
            for pokemon in state.pokemon
        ),
    )


def clear_consumed_boundary(state: State) -> State:
    return replace(state, pending_turn_boundary=None)


def initial_copy_state() -> State:
    return State(
        pokemon=(
            PokemonRef(
                "p1-regidrago",
                "Regidrago VSTAR",
                "P1",
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
            PokemonRef(
                "p1-kyurem",
                "Kyurem",
                "P1",
                "discard",
                types=("Dragon",),
                attacks=(TRIFROST,),
            ),
            PokemonRef(
                "p1-budew",
                "Budew",
                "P1",
                "bench",
                types=("Grass",),
                attacks=(ITCHY,),
            ),
            PokemonRef(
                "p1-koraidon",
                "Koraidon ex",
                "P1",
                "bench",
                types=("Dragon",),
                attacks=(RETRIBUTION,),
                attached_energy_units=(
                    frozenset(
                        {
                            "Grass",
                            "Fire",
                            "Water",
                            "Lightning",
                            "Psychic",
                            "Fighting",
                            "Darkness",
                            "Metal",
                            "Fairy",
                            "Colorless",
                        }
                    ),
                    frozenset(
                        {
                            "Grass",
                            "Fire",
                            "Water",
                            "Lightning",
                            "Psychic",
                            "Fighting",
                            "Darkness",
                            "Metal",
                            "Fairy",
                            "Colorless",
                        }
                    ),
                ),
            ),
            PokemonRef(
                "p2-mimikyu",
                "Mimikyu",
                "P2",
                "active",
                types=("Psychic",),
                attacks=(COPYCAT,),
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


def first_apex_timeless() -> tuple[State, object, object]:
    resolution = resolve_attack(
        actor_player="P1",
        actor_card_id="p1-regidrago",
        declared_attack_id=APEX,
        attacks=ATTACKS,
        state=initial_copy_state(),
        choose=choose_exact((TIMELESS,)),
    )
    assert resolution.body_chain == (APEX, TIMELESS)
    assert resolution.state.last_attack_for("P1") == APEX
    assert resolution.state.gx_used_by == frozenset({"P1"})

    schedule = TurnScheduleState("P1", "P2")
    p1 = make_state({}, turn_budget=TurnActionBudget())
    p2 = make_state({}, turn_budget=TurnActionBudget())
    closed = close_declared_attack(schedule, p1, resolution)
    assert closed is not None
    closed_schedule, p1_closed = closed
    advanced = advance_turn(closed_schedule, p1_closed, p2)
    assert advanced is not None
    assert advanced.same_player_continues
    assert advanced.schedule.current_player == "P1"
    assert not advanced.pokemon_checkup_occurs

    return clear_consumed_boundary(resolution.state), advanced, p2


def cover_with_budew() -> State:
    state, advanced, p2 = first_apex_timeless()
    state = with_active(state, "P1", "p1-budew")
    cover = resolve_attack(
        actor_player="P1",
        actor_card_id="p1-budew",
        declared_attack_id=ITCHY,
        attacks=ATTACKS,
        state=state,
        choose=choose_exact(()),
    )
    assert cover.state.last_attack_for("P1") == ITCHY

    closed = close_declared_attack(
        advanced.schedule,
        advanced.current_state,
        cover,
    )
    assert closed is not None
    closed_schedule, p1_closed = closed
    handed = advance_turn(closed_schedule, p1_closed, p2)
    assert handed is not None
    assert not handed.same_player_continues
    assert handed.schedule.current_player == "P2"

    copied = resolve_attack(
        actor_player="P2",
        actor_card_id="p2-mimikyu",
        declared_attack_id=COPYCAT,
        attacks=ATTACKS,
        state=cover.state,
        choose=choose_exact((ITCHY,)),
    )
    assert copied.body_chain == (COPYCAT, ITCHY)

    try:
        resolve_attack(
            actor_player="P2",
            actor_card_id="p2-mimikyu",
            declared_attack_id=COPYCAT,
            attacks=ATTACKS,
            state=cover.state,
            choose=choose_exact((APEX, TIMELESS)),
        )
    except IllegalCopyTarget:
        pass
    else:
        raise AssertionError("Apex Dragon should no longer be Copycat-eligible")

    return cover.state


def cover_with_koraidon() -> State:
    state, advanced, p2 = first_apex_timeless()
    state = with_active(state, "P1", "p1-koraidon")
    cover = resolve_attack(
        actor_player="P1",
        actor_card_id="p1-koraidon",
        declared_attack_id=RETRIBUTION,
        attacks=ATTACKS,
        state=state,
        choose=choose_exact(()),
    )
    assert cover.state.last_attack_for("P1") == RETRIBUTION

    closed = close_declared_attack(
        advanced.schedule,
        advanced.current_state,
        cover,
    )
    assert closed is not None
    closed_schedule, p1_closed = closed
    handed = advance_turn(closed_schedule, p1_closed, p2)
    assert handed is not None
    assert handed.schedule.current_player == "P2"

    copied = resolve_attack(
        actor_player="P2",
        actor_card_id="p2-mimikyu",
        declared_attack_id=COPYCAT,
        attacks=ATTACKS,
        state=cover.state,
        choose=choose_exact((RETRIBUTION,)),
    )
    assert copied.body_chain == (COPYCAT, RETRIBUTION)
    return cover.state


def repeat_apex_exposes_counter() -> State:
    state, advanced, p2 = first_apex_timeless()
    second_apex = resolve_attack(
        actor_player="P1",
        actor_card_id="p1-regidrago",
        declared_attack_id=APEX,
        attacks=ATTACKS,
        state=state,
        choose=choose_exact((TRIFROST,)),
    )
    assert second_apex.body_chain == (APEX, TRIFROST)
    assert second_apex.state.last_attack_for("P1") == APEX

    closed = close_declared_attack(
        advanced.schedule,
        advanced.current_state,
        second_apex,
    )
    assert closed is not None
    closed_schedule, p1_closed = closed
    handed = advance_turn(closed_schedule, p1_closed, p2)
    assert handed is not None
    assert handed.schedule.current_player == "P2"

    mimikyu = resolve_attack(
        actor_player="P2",
        actor_card_id="p2-mimikyu",
        declared_attack_id=COPYCAT,
        attacks=ATTACKS,
        state=second_apex.state,
        choose=choose_exact((APEX, TIMELESS)),
    )
    assert mimikyu.body_chain == (COPYCAT, APEX, TIMELESS)
    assert mimikyu.state.gx_used_by == frozenset({"P1", "P2"})
    return second_apex.state


def main() -> None:
    regidrago = card("swsh12", "swsh12-136")
    dialga = card("sm5", "sm5-100")
    mimikyu = card("sm2", "sm2-58")
    budew = card("sv8pt5", "sv8pt5-4")
    koraidon = card("sv5", "sv5-120")
    kyurem = card("sv6pt5", "sv6pt5-47")
    dde = card("xy6", "xy6-97")
    for row in (regidrago, dialga, mimikyu, budew, koraidon, kyurem, dde):
        legal(row)

    assert attack(budew, "Itchy Pollen")["cost"] == ["Free"]
    assert "can't play any Item cards" in attack(
        budew,
        "Itchy Pollen",
    )["text"]
    assert koraidon["types"] == ["Dragon"]
    assert kyurem["types"] == ["Dragon"]
    assert "110 damage to 3" in attack(kyurem, "Trifrost")["text"]
    assert attack(koraidon, "Retribution Strike")["cost"] == [
        "Colorless",
        "Colorless",
    ]
    assert "provides only 2 Energy at a time" in dde["rules"][0]
    assert "only be attached to Dragon Pokémon" in dde["rules"][0]

    fixture = aichi_fixture()
    rows = fixture["decklists"]
    assert len(rows) == 9
    assert all(row["budew"] >= 1 for row in rows)
    assert sum(row["budew"] for row in rows) == 12
    assert sum(row["koraidon_ex_tef120"] for row in rows) == 5
    assert sum(row["double_dragon_energy"] for row in rows) == 34
    assert round(sum(row["budew"] for row in rows) / len(rows), 2) == 1.33
    assert (
        round(
            sum(row["koraidon_ex_tef120"] for row in rows) / len(rows),
            2,
        )
        == 0.56
    )
    assert (
        round(
            sum(row["double_dragon_energy"] for row in rows) / len(rows),
            2,
        )
        == 3.78
    )

    budew_state = cover_with_budew()
    koraidon_state = cover_with_koraidon()
    apex_state = repeat_apex_exposes_counter()

    print(
        json.dumps(
            {
                "published_regidrago_lists": len(rows),
                "lists_with_budew": sum(
                    row["budew"] > 0 for row in rows
                ),
                "total_budew": sum(row["budew"] for row in rows),
                "lists_with_koraidon_ex": sum(
                    row["koraidon_ex_tef120"] > 0 for row in rows
                ),
                "double_dragon_energy_total": sum(
                    row["double_dragon_energy"] for row in rows
                ),
                "history_after_budew_cover": (
                    budew_state.last_attack_for("P1")
                ),
                "history_after_koraidon_cover": (
                    koraidon_state.last_attack_for("P1")
                ),
                "history_after_repeat_apex": (
                    apex_state.last_attack_for("P1")
                ),
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
