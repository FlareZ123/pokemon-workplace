"""Reproduce the conservative Prize-effect transition catalog."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from prize_effect_catalog import build_catalog, rows_for_card

RESOURCES = ROOT / "resources"


def atoms_for(rows, card_id: str) -> set[str]:
    output: set[str] = set()
    for row in rows_for_card(rows, card_id):
        output.update(row.atoms)
    if not output:
        raise AssertionError(f"no compiled Prize atoms for {card_id}")
    return output


def require(rows, card_id: str, expected: set[str]) -> None:
    actual = atoms_for(rows, card_id)
    assert expected <= actual, (card_id, expected, actual)


def main() -> None:
    rows = build_catalog(RESOURCES)
    assert rows

    require(
        rows,
        "sm4-95",
        {
            "inspect_own_prize",
            "prize_to_hand",
            "hand_to_prize",
            "shuffle_prizes",
        },
    )
    require(
        rows,
        "swsh10-146",
        {
            "inspect_own_prize",
            "prize_to_hand",
            "hand_to_prize",
            "shuffle_prizes",
        },
    )
    require(
        rows,
        "swsh6-149",
        {"prize_to_hand", "hand_to_prize"},
    )
    require(
        rows,
        "sv9-156",
        {"prize_to_deck", "deck_to_prize", "shuffle_prizes"},
    )
    require(
        rows,
        "sm1-131",
        {"prize_to_deck", "deck_to_prize", "shuffle_prizes"},
    )
    require(
        rows,
        "sm8-52",
        {"prize_to_discard", "prize_to_attached"},
    )
    require(
        rows,
        "swsh7-165",
        {"before_hand_prize_trigger"},
    )
    require(
        rows,
        "sv3pt5-113",
        {"before_hand_prize_trigger", "take_extra_prize"},
    )
    require(
        rows,
        "sm7-97",
        {"before_hand_prize_trigger", "take_extra_prize"},
    )
    require(
        rows,
        "swsh11-152",
        {"swap_prize_topdeck", "prize_to_deck", "deck_to_prize"},
    )
    require(
        rows,
        "sv10-172",
        {
            "face_up_opponent_prize",
            "swap_prize_hand",
            "prize_to_hand",
            "hand_to_prize",
        },
    )
    require(
        rows,
        "sm11-160",
        {"discard_to_prize"},
    )
    require(
        rows,
        "swsh11-107",
        {"taken_prize_to_lost_zone"},
    )
    require(
        rows,
        "swsh3-158",
        {"taken_prize_to_discard"},
    )
    require(
        rows,
        "bw7-136",
        {"face_up_own_prize"},
    )
    require(
        rows,
        "sm8-107",
        {"inspect_own_prize"},
    )
    require(
        rows,
        "sm3-103",
        {"inspect_opponent_prize"},
    )
    require(
        rows,
        "sm10-163",
        {"prize_to_hand", "deck_to_prize"},
    )
    require(
        rows,
        "me1-120",
        {"take_prize"},
    )
    require(
        rows,
        "sm5-129",
        {"take_prize"},
    )

    # Banned overlays and explicit tournament exclusions must not leak into the
    # legal catalog.
    compiled_ids = {row.card_id for row in rows}
    assert "swsh7-83" not in compiled_ids
    assert "xy12-112" not in compiled_ids

    all_atoms = {atom for row in rows for atom in row.atoms}
    required_atoms = {
        "inspect_own_prize",
        "inspect_opponent_prize",
        "face_up_own_prize",
        "face_up_opponent_prize",
        "prize_to_hand",
        "hand_to_prize",
        "deck_to_prize",
        "prize_to_deck",
        "discard_to_prize",
        "prize_to_discard",
        "prize_to_attached",
        "swap_prize_topdeck",
        "swap_prize_hand",
        "shuffle_prizes",
        "take_prize",
        "take_extra_prize",
        "taken_prize_to_lost_zone",
        "taken_prize_to_discard",
        "before_hand_prize_trigger",
    }
    assert required_atoms <= all_atoms

    print(
        "Prize effect catalog regressions passed:",
        len(rows),
        "compiled effect rows;",
        len(all_atoms),
        "transition atoms",
    )


if __name__ == "__main__":
    main()
