"""Regression for multi-unit Retreat Cost payment semantics."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from board_position_kernel import normal_retreat
from board_position_state import (
    Attachment,
    AttachmentKind,
    BoardPokemon,
    PokemonCard,
    make_state,
)


def pivot() -> BoardPokemon:
    return BoardPokemon(
        "pivot",
        (PokemonCard("pivot-card", "Pivot"),),
        0,
    )


def attempt(
    *,
    retreat_cost: int,
    attachments: tuple[Attachment, ...],
    selected_ids: tuple[str, ...],
):
    active = BoardPokemon(
        "active",
        (PokemonCard("active-card", "Test Active"),),
        retreat_cost,
        attachments=attachments,
    )
    state = make_state((active, pivot()), active_id="active")
    return normal_retreat(
        state,
        "pivot",
        discard_energy_ids=selected_ids,
    )


def main() -> None:
    dce_a = Attachment(
        "dce-a",
        "Double Colorless Energy A",
        AttachmentKind.ENERGY,
        2,
    )
    dce_b = Attachment(
        "dce-b",
        "Double Colorless Energy B",
        AttachmentKind.ENERGY,
        2,
    )
    basic_a = Attachment(
        "basic-a",
        "Basic Lightning Energy A",
        AttachmentKind.ENERGY,
        1,
    )
    basic_b = Attachment(
        "basic-b",
        "Basic Lightning Energy B",
        AttachmentKind.ENERGY,
        1,
    )
    basic_c = Attachment(
        "basic-c",
        "Basic Lightning Energy C",
        AttachmentKind.ENERGY,
        1,
    )
    inactive = Attachment(
        "inactive",
        "Conditional Special Energy",
        AttachmentKind.ENERGY,
        0,
    )

    one_dce = attempt(
        retreat_cost=2,
        attachments=(dce_a,),
        selected_ids=("dce-a",),
    )
    assert one_dce is not None
    assert one_dce.discarded_card_ids == ("dce-a",)

    two_dce = attempt(
        retreat_cost=2,
        attachments=(dce_a, dce_b),
        selected_ids=("dce-a", "dce-b"),
    )
    assert two_dce is not None
    assert two_dce.discarded_card_ids == ("dce-a", "dce-b")

    dce_plus_basic = attempt(
        retreat_cost=2,
        attachments=(dce_a, basic_a),
        selected_ids=("dce-a", "basic-a"),
    )
    assert dce_plus_basic is not None

    overfill_one = attempt(
        retreat_cost=1,
        attachments=(dce_a,),
        selected_ids=("dce-a",),
    )
    assert overfill_one is not None

    too_many_cards = attempt(
        retreat_cost=2,
        attachments=(basic_a, basic_b, basic_c),
        selected_ids=("basic-a", "basic-b", "basic-c"),
    )
    assert too_many_cards is None

    zero_provider_extra = attempt(
        retreat_cost=2,
        attachments=(dce_a, inactive),
        selected_ids=("dce-a", "inactive"),
    )
    assert zero_provider_extra is None

    free_retreat = attempt(
        retreat_cost=0,
        attachments=(basic_a,),
        selected_ids=(),
    )
    assert free_retreat is not None

    free_with_discard = attempt(
        retreat_cost=0,
        attachments=(basic_a,),
        selected_ids=("basic-a",),
    )
    assert free_with_discard is None

    print(json.dumps({
        "one_dce_for_cost_2": True,
        "two_dce_for_cost_2": True,
        "dce_plus_basic_for_cost_2": True,
        "one_dce_for_cost_1": True,
        "three_basics_for_cost_2": False,
        "zero_provider_extra_allowed": False,
        "free_retreat_discards_energy": False,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
