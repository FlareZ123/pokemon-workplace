"""Reproduce Escape Board's Asleep/Paralyzed Retreat exception."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from board_object_kernel import (
    EnergyAttachment,
    ToolAttachment,
    make_board,
    make_pokemon,
    retreat,
)
from board_position_kernel import normal_retreat
from board_position_state import (
    Attachment,
    AttachmentKind,
    BoardPokemon,
    PokemonCard,
    make_state,
)
from build_expanded_legality_baseline import classify_effective_legality
from lock_state_kernel import PokemonState


def card_text_regression() -> None:
    cards = json.loads(
        (ROOT / "resources" / "cards" / "en" / "sm5.json").read_text(
            encoding="utf-8"
        )
    )
    escape_board = next(card for card in cards if card["id"] == "sm5-122")
    status, _reason = classify_effective_legality(escape_board)
    assert status == "Legal"
    assert any(
        rule == (
            "The Retreat Cost of the Pokémon this card is attached to is "
            "Colorless less, and it can retreat even if it's Asleep or "
            "Paralyzed."
        )
        for rule in escape_board["rules"]
    )


def board_object_regression() -> None:
    tool = ToolAttachment("escape", "Escape Board")
    pivot = make_pokemon("pivot", "Pivot")

    for condition in ("Asleep", "Paralyzed"):
        active = make_pokemon(
            f"active-{condition}",
            "Escape Holder",
            tool=tool,
            special_conditions=(condition,),
        )
        state = make_board(active, (pivot,))
        resolved = retreat(
            state,
            "pivot",
            retreat_cost=0,
            discard_energy_ids=(),
        )
        assert resolved is not None

    energy = EnergyAttachment("energy", "Basic Energy", ("C",))
    blanked = make_pokemon(
        "blanked",
        "Blanked Escape Holder",
        energy=(energy,),
        tool=tool,
        tool_effect_enabled=False,
        special_conditions=("Asleep",),
    )
    assert retreat(
        make_board(blanked, (pivot,)),
        "pivot",
        retreat_cost=1,
        discard_energy_ids=("energy",),
    ) is None

    hard_locked = make_pokemon(
        "hard-locked",
        "Hard Locked Escape Holder",
        tool=tool,
        temporary_retreat_lock=True,
        special_conditions=("Asleep",),
    )
    assert retreat(
        make_board(hard_locked, (pivot,)),
        "pivot",
        retreat_cost=0,
        discard_energy_ids=(),
    ) is None


def board_position_regression() -> None:
    tool = Attachment("escape", "Escape Board", AttachmentKind.TOOL)
    pivot = BoardPokemon(
        "pivot",
        (PokemonCard("pivot-card", "Pivot"),),
        0,
    )

    for condition in ("Asleep", "Paralyzed"):
        active = BoardPokemon(
            f"active-{condition}",
            (PokemonCard(f"card-{condition}", "Escape Holder"),),
            0,
            attachments=(tool,),
            combat=PokemonState(tool_attached=True),
            special_conditions=frozenset({condition}),
        )
        state = make_state((active, pivot), active_id=active.pokemon_id)
        assert normal_retreat(state, "pivot") is not None

    energy = Attachment(
        "energy",
        "Basic Energy",
        AttachmentKind.ENERGY,
        1,
    )
    blanked = BoardPokemon(
        "blanked",
        (PokemonCard("blanked-card", "Blanked Escape Holder"),),
        1,
        attachments=(energy, tool),
        combat=PokemonState(
            tool_attached=True,
            tool_effect_enabled=False,
        ),
        special_conditions=frozenset({"Asleep"}),
    )
    blanked_state = make_state((blanked, pivot), active_id="blanked")
    assert normal_retreat(
        blanked_state,
        "pivot",
        discard_energy_ids=("energy",),
    ) is None


def main() -> None:
    card_text_regression()
    board_object_regression()
    board_position_regression()
    print("Escape Board Retreat exception regression: PASS")


if __name__ == "__main__":
    main()
