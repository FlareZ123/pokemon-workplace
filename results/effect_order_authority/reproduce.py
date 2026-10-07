"""Reproduce the scoped effect-order authority catalog from bundled rules."""

from collections import Counter
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from effect_order_authority import (
    OrderAuthorityCase,
    OrderAuthorityContext,
    ordering_player,
)
from rulebook_order_authority_audit import audit_rulebook


def main() -> None:
    manual = (
        ROOT
        / "resources"
        / "manual"
        / "EN_advanced_manual-2025-transcription-structured.md"
    )
    evidence = audit_rulebook(manual)
    evidence_counts = Counter(row.case for row in evidence)
    assert evidence_counts == {
        "damaged_pokemon_triggers": 1,
        "multi_pokemon_ko_triggers": 1,
        "energy_attachment_triggers": 1,
        "pokemon_checkup_effects": 2,
        "end_of_turn_effects": 1,
    }
    assert {
        (row.case, row.chooser_role)
        for row in evidence
    } == {
        ("damaged_pokemon_triggers", "affected_pokemon_player"),
        ("multi_pokemon_ko_triggers", "current_turn_player"),
        ("energy_attachment_triggers", "current_turn_player"),
        ("pokemon_checkup_effects", "next_turn_player"),
        ("end_of_turn_effects", "current_turn_player"),
    }

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
