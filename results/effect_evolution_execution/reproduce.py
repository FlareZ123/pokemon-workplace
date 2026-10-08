from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
for path in (ROOT, ROOT / "tools"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from tools.board_position_kernel import normal_evolve
from tools.board_position_state import BoardPokemon, PokemonCard, make_state
from tools.effect_evolution_execution import effect_evolve, materialized_effect_evolve
from tools.effect_evolution_timing import build_profiles
from tools.identity_materialization import (
    IdentityLedger,
    materialize,
    put_in_play_instance,
    validate_board_position_stack_bindings,
)
from tools.multicopy_zone_state import ZoneCountState


def profile_by_id(card_id: str):
    rows = [p for p in build_profiles(ROOT / "resources") if p.card_id == card_id]
    assert len(rows) == 1, (card_id, rows)
    return rows[0]


def board_for(
    base_name: str,
    *,
    first_turn: bool,
    entered_this_turn: bool,
):
    base = BoardPokemon(
        "pokemon-a",
        (PokemonCard("base-copy", base_name),),
        retreat_cost=1,
        evolution_eligible=not entered_this_turn,
    )
    return make_state(
        (base,),
        active_id="pokemon-a",
        evolution_allowed=not first_turn,
    )


def execute_profile(card_id: str, state, evolution_card, *, source_available=True):
    profile = profile_by_id(card_id)
    return effect_evolve(
        state,
        "pokemon-a",
        evolution_card,
        new_retreat_cost=2,
        first_turn_policy=profile.timing_policy,
        entry_turn_policy=profile.entry_turn_policy,
        source_available=source_available,
    )


def main() -> None:
    ivysaur = PokemonCard("ivy-copy", "Ivysaur", "Bulbasaur")

    first_turn_bulba = board_for("Bulbasaur", first_turn=True, entered_this_turn=False)
    assert normal_evolve(
        first_turn_bulba,
        "pokemon-a",
        ivysaur,
        new_retreat_cost=2,
    ) is None

    first_turn_eevee = board_for("Eevee", first_turn=True, entered_this_turn=False)
    vaporeon = PokemonCard("vaporeon-copy", "Vaporeon", "Eevee")
    eevee = execute_profile("sm1-101", first_turn_eevee, vaporeon)
    assert eevee is not None
    assert eevee.state.get("pokemon-a").name == "Vaporeon"

    first_turn_bulba = board_for("Bulbasaur", first_turn=True, entered_this_turn=False)
    assert execute_profile(
        "sv5-160",
        first_turn_bulba,
        ivysaur,
        source_available=False,
    ) is None
    assert execute_profile(
        "sv5-160",
        first_turn_bulba,
        ivysaur,
        source_available=True,
    ) is not None

    trevenant = PokemonCard("trevenant-copy", "Trevenant", "Phantump")
    first_turn_phantump = board_for("Phantump", first_turn=True, entered_this_turn=False)
    assert execute_profile("me4-38", first_turn_phantump, trevenant) is None
    fresh_phantump = board_for("Phantump", first_turn=False, entered_this_turn=True)
    assert execute_profile("me4-38", fresh_phantump, trevenant) is not None

    venusaur = PokemonCard("venusaur-copy", "Venusaur", "Bulbasaur")
    assert execute_profile(
        "sv1-191",
        board_for("Bulbasaur", first_turn=True, entered_this_turn=False),
        venusaur,
    ) is None
    assert execute_profile(
        "sv1-191",
        board_for("Bulbasaur", first_turn=False, entered_this_turn=True),
        venusaur,
    ) is None

    initial = IdentityLedger(
        ZoneCountState.from_mapping(
            {
                ("eevee-class", "hand"): 1,
                ("vaporeon-class", "hand"): 1,
            }
        )
    )
    ledger = materialize(
        initial,
        card_class="eevee-class",
        card_name="Eevee",
        source_zone="hand",
        instance_id="base-copy",
    )
    ledger = put_in_play_instance(ledger, "base-copy", "pokemon-a")
    board = board_for("Eevee", first_turn=True, entered_this_turn=False)
    validate_board_position_stack_bindings(ledger, board)

    profile = profile_by_id("sm1-101")
    physical = materialized_effect_evolve(
        ledger,
        board,
        "pokemon-a",
        PokemonCard("vaporeon-copy", "Vaporeon", "Eevee"),
        card_class="vaporeon-class",
        source_zone="hand",
        new_retreat_cost=2,
        first_turn_policy=profile.timing_policy,
        entry_turn_policy=profile.entry_turn_policy,
    )
    assert physical is not None
    validate_board_position_stack_bindings(physical.ledger, physical.board)
    assert [c.card_id for c in physical.board.get("pokemon-a").stack] == [
        "base-copy",
        "vaporeon-copy",
    ]
    assert physical.ledger.totals() == initial.totals()

    mismatch = materialized_effect_evolve(
        ledger,
        board,
        "pokemon-a",
        PokemonCard("vaporeon-copy", "Vaporeon", "Pikachu"),
        card_class="vaporeon-class",
        source_zone="hand",
        new_retreat_cost=2,
        first_turn_policy=profile.timing_policy,
        entry_turn_policy=profile.entry_turn_policy,
    )
    assert mismatch is None
    assert ledger.instance("base-copy").board_object_id == "pokemon-a"
    assert ledger.exchangeable.count("vaporeon-class", "hand") == 1

    print("effect evolution execution regressions passed")


if __name__ == "__main__":
    main()
