"""Concrete source-class counterexamples to naive universal gust targeting."""
from __future__ import annotations

from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from board_object_kernel import ToolAttachment, make_board, make_pokemon
from committed_play_event import PlayKind
from paired_switch_order_catalog import PROGRAMS
from paired_switch_physical_transaction import execute_paired_switch
from trainer_effect_gust_protection import (
    PROFILES, TrainerEffectOrigin, evaluate_bench_gust_protection,
)
from turn_action_budget import TurnActionBudget


ITEM = TrainerEffectOrigin(PlayKind.ITEM, True)
SUPPORTER = TrainerEffectOrigin(PlayKind.SUPPORTER, True)
ATTACK_COPY = TrainerEffectOrigin(PlayKind.SUPPORTER, False)


def target(board, which, origin):
    result = evaluate_bench_gust_protection(board, which, origin)
    assert result is not None
    return result


def main():
    # Every manually coded Ability case has the exact expected source Ability.
    for row in PROFILES.values():
        set_id = row.print_id.split("-")[0]
        raw = json.loads(
            (ROOT / "resources" / "cards" / "en" / f"{set_id}.json").read_text(
                encoding="utf-8",
            )
        )
        printed = next(card for card in raw if card["id"] == row.print_id)
        assert printed["name"] == row.source_name
        ability = next(
            ability for ability in printed["abilities"] if ability["name"] == row.label
        )
        assert "prevent all effects of that card" in ability["text"]
    ponchos = json.loads(
        (ROOT / "resources" / "cards" / "en" / "swsh12.json").read_text(
            encoding="utf-8",
        )
    )
    poncho = next(row for row in ponchos if row["id"] == "swsh12-160")
    assert poncho["name"] == "Leafy Camo Poncho"
    assert "Supporter card" in " ".join(poncho["rules"])

    regular = make_pokemon("t", "Target", tags={"Basic"})
    bench = (regular,)

    # Togekiss Active shields all friendly Pokemon from Item effects only.
    tog = make_pokemon("tog", "Togekiss", print_id="bw8-104", tags={"Stage2"})
    board_tog = make_board(tog, bench)
    assert not target(board_tog, "t", ITEM).allowed
    assert target(board_tog, "t", SUPPORTER).allowed
    assert target(board_tog, "t", ATTACK_COPY).allowed
    assert target(board_tog, "t", ITEM).protectors == ("tog:Bright Veil",)
    moved_tog = make_board(regular, (tog,))
    assert target(moved_tog, "tog", ITEM).allowed
    disabled_tog = make_pokemon(
        "tog", "Togekiss", print_id="bw8-104",
        abilities_enabled=False, tags={"Stage2"},
    )
    assert target(make_board(disabled_tog, bench), "t", ITEM).allowed

    # Diancie Active blocks Supporter gust on Benched Basic, not evolved targets.
    dia = make_pokemon("dia", "Diancie", print_id="swsh10-68", tags={"Basic"})
    basic = make_pokemon("basic", "Basic target", tags={"Basic"})
    evo = make_pokemon("evo", "VSTAR target", tags={"VSTAR", "Stage1"})
    board_dia = make_board(dia, (basic, evo))
    assert not target(board_dia, "basic", SUPPORTER).allowed
    assert target(board_dia, "basic", ITEM).allowed
    assert target(board_dia, "evo", SUPPORTER).allowed
    assert target(make_board(basic, (dia, evo)), "dia", SUPPORTER).allowed

    # Axew / Cetitan protect themselves from Items and Supporters.
    axew = make_pokemon("ax", "Axew", print_id="sm11-154", tags={"Basic"})
    ceti = make_pokemon("ceti", "Cetitan ex", print_id="sv10-65", tags={"Stage1"})
    board_self = make_board(regular, (axew, ceti))
    for name in ("ax", "ceti"):
        assert not target(board_self, name, ITEM).allowed
        assert not target(board_self, name, SUPPORTER).allowed
    assert target(board_self, "ax", ATTACK_COPY).allowed

    # Articuno Active protects only Water Bench Pokemon from Supporters.
    arti = make_pokemon("arti", "Articuno", print_id="sm9-32", tags={"Basic", "Water"})
    water = make_pokemon("water", "Water Bench", tags={"Water", "Basic"})
    fire = make_pokemon("fire", "Fire Bench", tags={"Fire", "Basic"})
    board_arti = make_board(arti, (water, fire))
    assert not target(board_arti, "water", SUPPORTER).allowed
    assert target(board_arti, "fire", SUPPORTER).allowed
    assert target(board_arti, "water", ITEM).allowed

    # Leafy Camo Poncho applies to its holder, requires VSTAR/VMAX and live Tool.
    poncho_tool = ToolAttachment("poncho-1", "Leafy Camo Poncho", "swsh12-160")
    shield = make_pokemon(
        "vmax", "VMAX", tags={"VMAX"},
        tool=poncho_tool,
    )
    board_poncho = make_board(regular, (shield,))
    assert not target(board_poncho, "vmax", SUPPORTER).allowed
    assert target(board_poncho, "vmax", ITEM).allowed
    disabled = make_pokemon(
        "vmax", "VMAX", tags={"VMAX"},
        tool=poncho_tool, tool_effect_enabled=False,
    )
    assert target(make_board(regular, (disabled,)), "vmax", SUPPORTER).allowed

    # Rhyperior Active shields all Pokemon from Supporter effects only.
    rhy = make_pokemon("rhy", "Rhyperior", print_id="sv7-76", tags={"Stage2"})
    assert not target(make_board(rhy, bench), "t", SUPPORTER).allowed
    assert target(make_board(rhy, bench), "t", ITEM).allowed
    assert evaluate_bench_gust_protection(board_tog, "nonexistent", ITEM) is None
    assert evaluate_bench_gust_protection(board_tog, "tog", ITEM) is None

    # The physical paired switch transaction remains mechanically feasible
    # before this separate defender-effect gate is applied.
    own_a = make_pokemon("own-a", "Own Active", tags={"Basic"})
    own_b = make_pokemon("own-b", "Own Bench", tags={"Basic"})
    our_board = make_board(own_a, (own_b,))
    prime = PROGRAMS["Prime Catcher"]
    guzma = PROGRAMS["Guzma"]
    physical_prime = execute_paired_switch(
        our_board, board_tog, TurnActionBudget(), prime,
        opponent_promote_id="t", own_promote_id="own-b",
    )
    physical_guzma = execute_paired_switch(
        our_board, board_tog, TurnActionBudget(), guzma,
        opponent_promote_id="t", own_promote_id="own-b",
    )
    assert physical_prime is not None and physical_guzma is not None
    assert not target(board_tog, "t", ITEM).allowed
    assert target(board_tog, "t", SUPPORTER).allowed

    # The converse source-class trap under Diancie.
    assert not target(board_dia, "basic", SUPPORTER).allowed
    assert target(board_dia, "basic", ITEM).allowed

    print(
        "trainer_effect_gust_protection regression: PASS; "
        "7 real print profiles (6 Pokemon Abilities plus one Tool); "
        "Item/Supporter gust target eligibility crosses by protector"
    )


if __name__ == "__main__":
    main()
