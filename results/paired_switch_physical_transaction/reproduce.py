"""Physical paired-switch execution tests using real board and action kernels.

Run: python -m results.paired_switch_physical_transaction.reproduce
"""
from itertools import product
from pathlib import Path
import sys

# Legacy board_object_kernel imports its sibling modules by bare names.
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))

from tools.board_object_kernel import (
    EnergyAttachment, ToolAttachment, make_board, make_pokemon
)
from tools.paired_switch_order_catalog import PROGRAMS, switch_effects
from tools.paired_switch_physical_transaction import execute_paired_switch
from tools.turn_action_budget import TurnActionBudget


def build_boards(own_bench, other_bench, rocket):
    active = make_pokemon(
        "a", "Active Test", tags=("team_rocket",) if rocket else (),
        energy=(EnergyAttachment("e-a", "Double Colorless Energy", ("C", "C")),),
        tool=ToolAttachment("t-a", "Float Stone"),
        damage_counters=6, special_conditions=("Poisoned",),
        temporary_attack_lock=True,
    )
    ours = [active]
    if own_bench:
        ours.append(make_pokemon(
            "b", "Own Bench", tags=("team_rocket",) if rocket else (),
            energy=(EnergyAttachment("e-b", "Basic Water Energy", ("W",)),),
        ))
    opponent = [
        make_pokemon(
            "oa", "Opposing Active", damage_counters=5,
            special_conditions=("Asleep",),
            energy=(EnergyAttachment("oe-a", "Basic Fire Energy", ("R",)),)
        )
    ]
    if other_bench:
        opponent.append(make_pokemon(
            "ob", "Opposing Bench",
            energy=(EnergyAttachment("oe-b", "Double Colorless Energy", ("C", "C")),),
        ))
    return make_board(ours[0], ours[1:]), make_board(opponent[0], opponent[1:])


def all_attachment_ids(board):
    return sorted(
        [e.instance_id for p in board.objects for e in p.energy]
        + [p.tool.instance_id for p in board.objects if p.tool is not None]
    )


def run():
    checked = 0
    emitted = 0
    for name, program in PROGRAMS.items():
        for own, opposing, rocket, supporter_spent, item_allowed in product(
            (False, True), repeat=5
        ):
            for copies in (0, 1, 2):
                pb, ob = build_boards(own, opposing, rocket)
                budget = TurnActionBudget(supporter_used=supporter_spent)
                outcome = execute_paired_switch(
                    pb, ob, budget, program,
                    opponent_promote_id="ob" if opposing else None,
                    own_promote_id="b" if own else None,
                    copies_available=copies,
                    item_play_allowed=item_allowed,
                )
                source_allowed = copies >= program.copies_together and (
                    (name not in ("Guzma", "Team Rocket's Giovanni") and item_allowed)
                    or (name in ("Guzma", "Team Rocket's Giovanni") and not supporter_spent)
                )
                expected = switch_effects(
                    program, own, opposing, rocket, rocket and own
                )
                valid = source_allowed and bool(expected)
                assert (outcome is not None) == valid, (
                    name, own, opposing, rocket, supporter_spent, item_allowed,
                    copies, expected, outcome
                )
                checked += 1
                if not valid:
                    continue
                emitted += 1
                assert outcome.effect_sequence == expected
                assert outcome.source_copies_spent == program.copies_together
                assert all_attachment_ids(outcome.player_board) == all_attachment_ids(pb)
                assert all_attachment_ids(outcome.opponent_board) == all_attachment_ids(ob)
                assert tuple(sorted(p.object_id for p in outcome.player_board.objects)) == (
                    tuple(sorted(p.object_id for p in pb.objects))
                )
                assert tuple(sorted(p.object_id for p in outcome.opponent_board.objects)) == (
                    tuple(sorted(p.object_id for p in ob.objects))
                )
                assert outcome.turn_budget.supporter_plays_used == (
                    budget.supporter_plays_used
                    + int(name in ("Guzma", "Team Rocket's Giovanni"))
                )
                assert outcome.turn_budget.retreats_used == budget.retreats_used
                if "own" in expected:
                    assert outcome.player_board.active_id == "b"
                    assert outcome.player_board.get("a").damage_counters == 6
                    assert outcome.player_board.get("a").special_conditions == frozenset()
                    assert not outcome.player_board.get("a").pokemon_state.temporary_attack_lock
                else:
                    assert outcome.player_board.active_id == "a"
                    assert outcome.player_board.get("a").special_conditions == {"Poisoned"}
                if "opponent" in expected:
                    assert outcome.opponent_board.active_id == "ob"
                    assert outcome.opponent_board.get("oa").special_conditions == frozenset()
                else:
                    assert outcome.opponent_board.active_id == "oa"

    assert checked == 384
    pb, ob = build_boards(True, True, True)
    for name in ("Prime Catcher", "Cross Switcher", "Guzma", "Team Rocket's Giovanni"):
        p = PROGRAMS[name]
        assert execute_paired_switch(
            pb, ob, TurnActionBudget(), p,
            opponent_promote_id="invalid", own_promote_id="b",
            copies_available=2
        ) is None
        assert execute_paired_switch(
            pb, ob, TurnActionBudget(), p,
            opponent_promote_id="ob", own_promote_id="invalid",
            copies_available=2
        ) is None
    pb_empty, ob_with_bench = build_boards(False, True, True)
    p = PROGRAMS["Prime Catcher"]
    prime = execute_paired_switch(
        pb_empty, ob_with_bench, TurnActionBudget(), p,
        opponent_promote_id="ob", own_promote_id=None
    )
    assert prime and prime.player_board.active_id == "a"
    assert prime.opponent_board.active_id == "ob"
    assert prime.player_board.get("a").special_conditions == {"Poisoned"}

    gio = PROGRAMS["Team Rocket's Giovanni"]
    no_own_bench = execute_paired_switch(
        pb_empty, ob_with_bench, TurnActionBudget(), gio,
        opponent_promote_id="ob", own_promote_id=None,
        copies_available=1
    )
    assert no_own_bench is None

    pb_full, ob_empty = build_boards(True, False, True)
    g = execute_paired_switch(
        pb_full, ob_empty, TurnActionBudget(), gio,
        opponent_promote_id=None, own_promote_id="b"
    )
    assert g and g.effect_sequence == ("own",)
    print(f"PASS: {checked} source/lock/quota/geometry cases, {emitted} "
          "accepted physical transitions, attachment conservation and order")
    print("Prime empty Bench performs opponent-only gust; "
          "Giovanni requires own Team Rocket first, consumes Supporter.")


if __name__ == "__main__":
    run()
