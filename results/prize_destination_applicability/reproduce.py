"""Reproduce KO-boundary applicability for Prize destination replacements."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from board_object_kernel import ToolAttachment, knock_out, make_board, make_pokemon
from prize_destination_applicability import derive_knockout_prize_overrides
from prize_destination_overrides import decide_prize_destination


def effect_names(rows):
    return tuple(row.effect_id.split(":", 1)[0] for row in rows)


def main() -> None:
    smoke = ToolAttachment("smoke-1", "Billowing Smoke", "swsh3-158")
    victim = make_pokemon("victim", "Victim", tool=smoke)
    barbaracle = make_pokemon(
        "barbaracle",
        "Barbaracle",
        print_id="swsh11-107",
    )
    board = make_board(victim, (barbaracle,))

    ko = knock_out(board, "victim", promote_object_id="barbaracle")
    assert ko is not None
    after, removed = ko
    assert after is not None
    rows = derive_knockout_prize_overrides(
        after,
        removed,
        knocked_out_by_opponent_attack_damage=True,
    )
    assert effect_names(rows) == ("Billowing Smoke", "Lost Block")
    decision = decide_prize_destination(rows)
    assert decision.requires_choice
    assert decision.candidate_zones == ("discard", "lost_zone")

    barbaracle_with_smoke = make_pokemon(
        "barbaracle",
        "Barbaracle",
        print_id="swsh11-107",
        tool=smoke,
    )
    backup = make_pokemon("backup", "Backup")
    own_ko_board = make_board(barbaracle_with_smoke, (backup,))
    own_ko = knock_out(
        own_ko_board,
        "barbaracle",
        promote_object_id="backup",
    )
    assert own_ko is not None
    own_after, own_removed = own_ko
    assert own_after is not None
    own_rows = derive_knockout_prize_overrides(
        own_after,
        own_removed,
        knocked_out_by_opponent_attack_damage=True,
    )
    assert effect_names(own_rows) == ("Billowing Smoke",)
    assert decide_prize_destination(own_rows).destination_zone == "discard"

    suppressed = make_pokemon(
        "barbaracle",
        "Barbaracle",
        print_id="swsh11-107",
        abilities_enabled=False,
    )
    suppressed_board = make_board(victim, (suppressed,))
    suppressed_ko = knock_out(
        suppressed_board,
        "victim",
        promote_object_id="barbaracle",
    )
    assert suppressed_ko is not None
    suppressed_after, suppressed_removed = suppressed_ko
    assert suppressed_after is not None
    suppressed_rows = derive_knockout_prize_overrides(
        suppressed_after,
        suppressed_removed,
        knocked_out_by_opponent_attack_damage=True,
    )
    assert effect_names(suppressed_rows) == ("Billowing Smoke",)

    blanked_victim = make_pokemon(
        "victim",
        "Victim",
        tool=smoke,
        tool_effect_enabled=False,
    )
    blanked_board = make_board(blanked_victim, (barbaracle,))
    blanked_ko = knock_out(
        blanked_board,
        "victim",
        promote_object_id="barbaracle",
    )
    assert blanked_ko is not None
    blanked_after, blanked_removed = blanked_ko
    assert blanked_after is not None
    blanked_rows = derive_knockout_prize_overrides(
        blanked_after,
        blanked_removed,
        knocked_out_by_opponent_attack_damage=True,
    )
    assert effect_names(blanked_rows) == ("Lost Block",)

    effect_ko_rows = derive_knockout_prize_overrides(
        after,
        removed,
        knocked_out_by_opponent_attack_damage=False,
    )
    assert effect_names(effect_ko_rows) == ("Lost Block",)

    print("Prize destination applicability regressions passed")


if __name__ == "__main__":
    main()
