"""Reproduce lossless Special Condition / board-object synchronization."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from board_object_kernel import EnergyAttachment, make_board, make_pokemon  # noqa: E402
from conditioned_board_state import (  # noqa: E402
    ConditionedBoardState,
    evolve,
    lift_legacy_board_as_regular,
    make_conditioned_board,
    retreat,
    switch_active,
)
from special_condition_state import (  # noqa: E402
    ConditionInstance,
    ConditionKind,
    SpecialConditionState,
    apply_condition,
    effective_damage_counters,
)


def severe_poison() -> SpecialConditionState:
    return apply_condition(
        SpecialConditionState(),
        ConditionInstance(
            ConditionKind.POISONED,
            base_damage_counters=4,
            source_label="Galarian Weezing — Severe Poison",
        ),
    )


def main() -> None:
    energy = EnergyAttachment("energy-1", "Lightning Energy", ("L",))
    active = make_pokemon(
        "active",
        "Active Pokémon",
        energy=(energy,),
        special_conditions=("Poisoned",),
    )
    bench = make_pokemon("bench", "Bench Pokémon")
    board = make_board(active, (bench,))

    typed = make_conditioned_board(
        board,
        {
            "active": severe_poison(),
            "bench": SpecialConditionState(),
        },
    )
    assert effective_damage_counters(
        typed.get_conditions("active"), ConditionKind.POISONED
    ) == 4

    stale = ConditionedBoardState(
        board,
        (("active", SpecialConditionState()), ("bench", SpecialConditionState())),
    )
    try:
        stale.validate()
    except ValueError:
        pass
    else:
        raise AssertionError("stale legacy/typed condition state was accepted")

    switched = switch_active(typed, "bench")
    assert switched is not None
    assert not switched.board.get("active").special_conditions
    assert not switched.get_conditions("active").conditions

    retreat_source = make_pokemon(
        "retreat-source",
        "Retreat Source",
        energy=(energy,),
        special_conditions=("Poisoned",),
    )
    retreat_target = make_pokemon("retreat-target", "Retreat Target")
    retreat_board = make_board(retreat_source, (retreat_target,))
    retreat_state = make_conditioned_board(
        retreat_board,
        {
            "retreat-source": severe_poison(),
            "retreat-target": SpecialConditionState(),
        },
    )
    resolved_retreat = retreat(
        retreat_state,
        "retreat-target",
        retreat_cost=1,
        discard_energy_ids=("energy-1",),
    )
    assert resolved_retreat is not None
    after_retreat, discarded = resolved_retreat
    assert discarded == (energy,)
    assert not after_retreat.board.get("retreat-source").special_conditions
    assert not after_retreat.get_conditions("retreat-source").conditions

    evolve_source = make_pokemon(
        "evolving",
        "Basic Form",
        special_conditions=("Poisoned",),
    )
    evolve_board = make_board(evolve_source)
    evolve_state = make_conditioned_board(
        evolve_board,
        {"evolving": severe_poison()},
    )
    evolved = evolve(
        evolve_state,
        "evolving",
        new_card_name="Stage 1 Form",
    )
    assert evolved is not None
    assert not evolved.board.get("evolving").special_conditions
    assert not evolved.get_conditions("evolving").conditions

    lifted = lift_legacy_board_as_regular(board)
    assert effective_damage_counters(
        lifted.get_conditions("active"), ConditionKind.POISONED
    ) == 1

    print("conditioned-board synchronization regressions passed")


if __name__ == "__main__":
    main()
