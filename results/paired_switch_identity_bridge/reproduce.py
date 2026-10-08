"""Regression for conserving physical Trainer cards through paired switch.

Run: python -m results.paired_switch_identity_bridge.reproduce
"""
from dataclasses import replace
from itertools import product
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))

from tools.board_object_kernel import (
    EnergyAttachment, ToolAttachment, make_board, make_pokemon
)
from tools.identity_materialization import (
    CardInstance, IdentityLedger, validate_board_attachment_bindings
)
from tools.multicopy_zone_state import ZoneCountState
from tools.paired_switch_identity_bridge import execute_materialized_paired_switch
from tools.paired_switch_order_catalog import PROGRAMS
from tools.turn_action_budget import TurnActionBudget


def board_pair(own_bench, opp_bench, rocket):
    a = make_pokemon(
        "a", "Actor", tags=("team_rocket",) if rocket else (),
        energy=(EnergyAttachment("en-a", "Double Colorless Energy", ("C", "C")),),
        tool=ToolAttachment("tl-a", "Float Stone"),
        damage_counters=4, special_conditions=("Poisoned",),
    )
    bench = (
        make_pokemon(
            "b", "Support", tags=("team_rocket",) if rocket else (),
            energy=(EnergyAttachment("en-b", "Basic Water Energy", ("W",)),),
        ),
    ) if own_bench else ()
    oa = make_pokemon("oa", "Enemy", damage_counters=5)
    ob = (make_pokemon("ob", "Enemy Bench"),) if opp_bench else ()
    return make_board(a, bench), make_board(oa, ob)


def identity_ledger(player_board, program, copies, zone="hand"):
    cards = [
        CardInstance("en-a", "DCE", "Double Colorless Energy",
                     "attached", attached_to="a"),
        CardInstance("tl-a", "Float Stone", "Float Stone",
                     "attached", attached_to="a"),
    ]
    if "b" in player_board.bench_ids:
        cards.append(CardInstance("en-b", "Water", "Basic Water Energy",
                                  "attached", attached_to="b"))
    for n in range(copies):
        cards.append(CardInstance(
            "source-" + str(n + 1), program.name, program.name, zone
        ))
    cards = tuple(sorted(cards, key=lambda row: row.instance_id))
    result = IdentityLedger(ZoneCountState(), cards)
    validate_board_attachment_bindings(result, player_board)
    return result


def run():
    attempts = successes = 0
    for name, program in PROGRAMS.items():
        for own, opponent, rocket, supporter_spent, item_allowed in product(
            (False, True), repeat=5
        ):
            for copies in (0, 1, 2):
                own_board, opposing_board = board_pair(own, opponent, rocket)
                before = identity_ledger(own_board, program, copies)
                source_ids = tuple(
                    "source-" + str(i + 1)
                    for i in range(program.copies_together)
                )
                budget = TurnActionBudget(supporter_used=supporter_spent)
                output = execute_materialized_paired_switch(
                    before, own_board, opposing_board, budget, program,
                    source_instance_ids=source_ids,
                    own_promote_id="b" if own else None,
                    opponent_promote_id="ob" if opponent else None,
                    item_play_allowed=item_allowed,
                )
                source_ok = copies >= program.copies_together
                action_ok = (
                    not supporter_spent if name in ("Guzma", "Team Rocket's Giovanni")
                    else item_allowed
                )
                first_ok = (
                    opponent if program.first == "opponent" else (own and rocket)
                )
                expect = source_ok and action_ok and first_ok
                assert (output is not None) == expect, (
                    name, own, opponent, rocket, supporter_spent, item_allowed,
                    copies, output
                )
                attempts += 1
                if output is None:
                    assert before.instance("en-a").zone == "attached"
                    continue
                successes += 1
                assert output.ledger.totals() == before.totals()
                assert output.board_resolution.source_copies_spent == len(source_ids)
                validate_board_attachment_bindings(
                    output.ledger, output.board_resolution.player_board
                )
                for source_id in source_ids:
                    assert before.instance(source_id).zone == "hand"
                    assert output.ledger.instance(source_id).zone == "discard"
                for p in before.instances:
                    if p.instance_id.startswith("source-") and p.instance_id not in source_ids:
                        assert output.ledger.instance(p.instance_id).zone == "hand"
                assert output.board_resolution.turn_budget.supporter_plays_used == (
                    int(supporter_spent)
                    + int(name in ("Guzma", "Team Rocket's Giovanni"))
                )
                assert execute_materialized_paired_switch(
                    output.ledger,
                    output.board_resolution.player_board,
                    output.board_resolution.opponent_board,
                    output.board_resolution.turn_budget,
                    program,
                    source_instance_ids=source_ids,
                    own_promote_id="a",
                    opponent_promote_id="oa",
                ) is None

    assert attempts == 384
    # Duplicate Cross source is never enough to satisfy the required two copies.
    pb, ob = board_pair(True, True, True)
    p = PROGRAMS["Cross Switcher"]
    led = identity_ledger(pb, p, 2)
    assert execute_materialized_paired_switch(
        led, pb, ob, TurnActionBudget(), p,
        source_instance_ids=("source-1", "source-1"),
        opponent_promote_id="ob", own_promote_id="b"
    ) is None
    # Identically named but inaccessible in the deck cannot pay hand cost.
    bad_ledger = identity_ledger(pb, PROGRAMS["Prime Catcher"], 1, "deck")
    assert execute_materialized_paired_switch(
        bad_ledger, pb, ob, TurnActionBudget(),
        PROGRAMS["Prime Catcher"], source_instance_ids=("source-1",),
        opponent_promote_id="ob", own_promote_id="b"
    ) is None
    assert attempts > successes > 0
    print(f"PASS: {attempts} attempted source/board/quota states, "
          f"{successes} exact conserving hand-to-discard transactions")
    print("Duplicate Cross source, non-hand source, and repeated source use rejected.")


if __name__ == "__main__":
    run()
