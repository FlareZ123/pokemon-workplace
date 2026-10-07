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
from attack_copy_turn_boundary_bridge import close_declared_attack
from canonical_turn_sequence_owner import TurnScheduleState, advance_turn
from turn_action_budget import TurnActionBudget
from unified_state_kernel import make_state

COPY_ANYTHING = "ditto:copy-anything"
FOUL = "zoroark:foul-play"
ENDPOINT = "target:typed-attack"

ATTACKS = {
    COPY_ANYTHING: AttackDef(
        COPY_ANYTHING,
        "Copy Anything",
        copy_selector=CopySelector(
            "opponent_in_play",
            require_selected_energy=True,
        ),
    ),
    FOUL: AttackDef(
        FOUL,
        "Foul Play",
        copy_selector=CopySelector("opponent_in_play"),
    ),
    ENDPOINT: AttackDef(
        ENDPOINT,
        "Typed Endpoint",
        energy_cost=("R", "C", "C"),
        effect_label="endpoint_executed",
    ),
}


def state_for_actor(*energy_units: frozenset[str]) -> State:
    return State(
        pokemon=(
            PokemonRef(
                "p1-copying",
                "Copying Pokémon",
                "P1",
                "active",
                attacks=(COPY_ANYTHING, FOUL),
                attached_energy_units=tuple(energy_units),
            ),
            PokemonRef(
                "p2-target",
                "Target Pokémon",
                "P2",
                "active",
                attacks=(ENDPOINT,),
            ),
        )
    )


def test_insufficient_energy_suppresses_only_selected_body() -> None:
    resolution = resolve_attack(
        actor_player="P1",
        actor_card_id="p1-copying",
        declared_attack_id=COPY_ANYTHING,
        attacks=ATTACKS,
        state=state_for_actor(frozenset({"R"}), frozenset({"C"})),
        choose=choose_exact((ENDPOINT,)),
    )
    assert resolution.body_chain == (COPY_ANYTHING,)
    assert resolution.state.events == ()
    assert resolution.state.last_attack_for("P1") == COPY_ANYTHING
    assert len(resolution.trace) == 1
    assert resolution.trace[0].selected_attack_id == ENDPOINT
    assert resolution.trace[0].selected_body_executed is False

    schedule = TurnScheduleState("P1", "P2")
    p1 = make_state({}, turn_budget=TurnActionBudget())
    p2 = make_state({}, turn_budget=TurnActionBudget())
    closed = close_declared_attack(schedule, p1, resolution)
    assert closed is not None
    closed_schedule, p1_closed = closed
    advanced = advance_turn(closed_schedule, p1_closed, p2)
    assert advanced is not None
    assert advanced.schedule.current_player == "P2"
    assert advanced.pokemon_checkup_occurs


def test_sufficient_energy_executes_selected_body() -> None:
    resolution = resolve_attack(
        actor_player="P1",
        actor_card_id="p1-copying",
        declared_attack_id=COPY_ANYTHING,
        attacks=ATTACKS,
        state=state_for_actor(
            frozenset({"R"}),
            frozenset({"C"}),
            frozenset({"C"}),
        ),
        choose=choose_exact((ENDPOINT,)),
    )
    assert resolution.body_chain == (COPY_ANYTHING, ENDPOINT)
    assert resolution.state.events == ("endpoint_executed",)
    assert resolution.trace[0].selected_body_executed is True


def test_generic_c18_copy_ignores_selected_attack_cost() -> None:
    resolution = resolve_attack(
        actor_player="P1",
        actor_card_id="p1-copying",
        declared_attack_id=FOUL,
        attacks=ATTACKS,
        state=state_for_actor(),
        choose=choose_exact((ENDPOINT,)),
    )
    assert resolution.body_chain == (FOUL, ENDPOINT)
    assert resolution.state.events == ("endpoint_executed",)


def main() -> None:
    test_insufficient_energy_suppresses_only_selected_body()
    test_sufficient_energy_executes_selected_body()
    test_generic_c18_copy_ignores_selected_attack_cost()
    print("attack-copy selected-energy gate regression: PASS")


if __name__ == "__main__":
    main()
