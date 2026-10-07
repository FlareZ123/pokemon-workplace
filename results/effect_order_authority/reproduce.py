"""Reproduce the scoped effect-order authority catalog."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from effect_order_authority import (
    OrderAuthorityCase,
    OrderAuthorityContext,
    ordering_player,
)


def main() -> None:
    context = OrderAuthorityContext(
        current_turn_player="A",
        next_turn_player="B",
        affected_pokemon_player="B",
        knocked_out_pokemon_owner="B",
    )

    # Advanced Player's Rulebook v3.4 cases.
    assert ordering_player(
        OrderAuthorityCase.DAMAGED_POKEMON_TRIGGERS,
        context,
    ) == "B"
    assert ordering_player(
        OrderAuthorityCase.MULTI_POKEMON_KO_TRIGGERS,
        context,
    ) == "A"
    assert ordering_player(
        OrderAuthorityCase.ENERGY_ATTACHMENT_TRIGGERS,
        context,
    ) == "A"
    assert ordering_player(
        OrderAuthorityCase.POKEMON_CHECKUP_EFFECTS,
        context,
    ) == "B"
    assert ordering_player(
        OrderAuthorityCase.END_OF_TURN_EFFECTS,
        context,
    ) == "A"

    # Official Trainers Website Lost City + Persistent Cells ruling.
    assert ordering_player(
        OrderAuthorityCase.LOST_CITY_PERSISTENT_CELLS,
        context,
    ) == "B"

    # Required role information stays explicit instead of being guessed.
    missing = OrderAuthorityContext(
        current_turn_player="A",
        next_turn_player="B",
    )
    assert ordering_player(
        OrderAuthorityCase.DAMAGED_POKEMON_TRIGGERS,
        missing,
    ) is None
    assert ordering_player(
        OrderAuthorityCase.LOST_CITY_PERSISTENT_CELLS,
        missing,
    ) is None

    # A single blanket authority cannot reproduce these simultaneous situations
    # when the affected/KO'd Pokemon belongs to the non-turn player.
    assert {
        ordering_player(
            OrderAuthorityCase.MULTI_POKEMON_KO_TRIGGERS,
            context,
        ),
        ordering_player(
            OrderAuthorityCase.LOST_CITY_PERSISTENT_CELLS,
            context,
        ),
    } == {"A", "B"}

    print("Effect-order authority regressions passed")


if __name__ == "__main__":
    main()
