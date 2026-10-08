"""Real-print, real-lock conditional paired-gust materialized transaction.

Run: python -m results.paired_gust_source_permissions.reproduce
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from tools.card_action_metadata import card_action_metadata_by_id
from tools.identity_materialization import IdentityLedger, CardInstance
from tools.multicopy_zone_state import ZoneCountState
from tools.paired_gust_source_permissions import execute_permissioned_paired_switch
from tools.paired_switch_order_catalog import PROGRAMS
from tools.source_scoped_action_restrictions import (
    build_source_scoped_action_restrictions, restrictions_block_attempt
)
from tools.turn_action_budget import TurnActionBudget
from tools.board_object_kernel import make_pokemon, make_board


PRINTS = {
    "Prime Catcher": "sv5-157",
    "Cross Switcher": "swsh8-230",
    "Guzma": "sm3-115",
    "Team Rocket's Giovanni": "sv10-174",
}
LOCK_SOURCES = {
    "item": "xy7-3",
    "supporter": "bw7-122",
    "ace_spec": "bw11-87",
    "trainer": "sm11-125",
}


def build_pair():
    actor = make_pokemon("a", "Team Rocket's Active",
                         tags=("team_rocket",))
    own_bench = make_pokemon("b", "Team Rocket's Bench",
                            tags=("team_rocket",))
    foe = make_pokemon("oa", "Opponent Active")
    opposing_bench = make_pokemon("ob", "Opponent Bench")
    return make_board(actor, (own_bench,)), make_board(foe, (opposing_bench,))


def hand_ledger(program):
    rows = tuple(sorted(
        (CardInstance(f"s{i+1}", program.name, program.name, "hand")
         for i in range(program.copies_together)),
        key=lambda row: row.instance_id,
    ))
    return IdentityLedger(ZoneCountState(), rows)


def run():
    cards = card_action_metadata_by_id(ROOT / "resources")
    compiled = build_source_scoped_action_restrictions(ROOT / "resources")
    locks = {}
    for dimension, source_id in LOCK_SOURCES.items():
        options = [
            r for r in compiled
            if r.card_id == source_id and dimension in r.dimensions
        ]
        assert len(options) == 1, (dimension, source_id, options)
        locks[dimension] = options[0]

    assert cards[PRINTS["Prime Catcher"]].card_kind == "item"
    assert "ace_spec" in cards[PRINTS["Prime Catcher"]].tags
    assert cards[PRINTS["Cross Switcher"]].card_kind == "item"
    assert "ace_spec" not in cards[PRINTS["Cross Switcher"]].tags
    assert cards[PRINTS["Guzma"]].card_kind == "supporter"
    assert cards[PRINTS["Team Rocket's Giovanni"]].card_kind == "supporter"

    regimes = {
        "none": (),
        "item_lock": (locks["item"],),
        "supporter_lock": (locks["supporter"],),
        "ace_spec_lock": (locks["ace_spec"],),
        "trainer_lock": (locks["trainer"],),
        "item_plus_supporter": (locks["item"], locks["supporter"]),
    }
    expected_allowed = {
        "none": {"Prime Catcher", "Cross Switcher", "Guzma", "Team Rocket's Giovanni"},
        "item_lock": {"Guzma", "Team Rocket's Giovanni"},
        "supporter_lock": {"Prime Catcher", "Cross Switcher"},
        "ace_spec_lock": {"Cross Switcher", "Guzma", "Team Rocket's Giovanni"},
        "trainer_lock": set(),
        "item_plus_supporter": set(),
    }

    checks = successful = 0
    pb, ob = build_pair()
    for regime, active_locks in regimes.items():
        for name, program in PROGRAMS.items():
            metadata = cards[PRINTS[name]]
            output = execute_permissioned_paired_switch(
                hand_ledger(program), pb, ob, TurnActionBudget(),
                program, metadata,
                source_instance_ids=tuple(
                    f"s{i+1}" for i in range(program.copies_together)
                ),
                own_promote_id="b", opponent_promote_id="ob",
                active_restrictions=active_locks,
            )
            permitted = name in expected_allowed[regime]
            # The exact predicate cross-check bypasses the projection adapter.
            blocked_raw = restrictions_block_attempt(
                active_locks, metadata.attempt("hand")
            )
            assert permitted == (not blocked_raw), (regime, name, blocked_raw)
            assert (output is not None) == permitted, (regime, name)
            checks += 1
            if output is not None:
                successful += 1
                assert output.ledger.totals() == hand_ledger(program).totals()
                assert output.board_resolution.player_board.active_id == "b"
                assert output.board_resolution.opponent_board.active_id == "ob"
                assert output.board_resolution.turn_budget.supporter_plays_used == (
                    int(metadata.card_kind == "supporter")
                )
                for i in range(program.copies_together):
                    assert output.ledger.instance(f"s{i+1}").zone == "discard"

    assert checks == 24
    assert successful == 13

    p = PROGRAMS["Prime Catcher"]
    try:
        execute_permissioned_paired_switch(
            hand_ledger(p), pb, ob, TurnActionBudget(), p,
            cards[PRINTS["Guzma"]], source_instance_ids=("s1",),
            own_promote_id="b", opponent_promote_id="ob",
        )
    except ValueError as e:
        assert "metadata" in str(e)
    else:
        raise AssertionError("mismatched exact print metadata should reject")

    # A genuine Supporter cannot play after using another Supporter, even
    # when no active lock source prohibits the class.
    gu = PROGRAMS["Guzma"]
    assert execute_permissioned_paired_switch(
        hand_ledger(gu), pb, ob, TurnActionBudget(supporter_used=True),
        gu, cards[PRINTS["Guzma"]], source_instance_ids=("s1",),
        own_promote_id="b", opponent_promote_id="ob"
    ) is None

    print("Print metadata:",PRINTS)
    print("Restriction sources:",{k:v.card_name for k,v in locks.items()})
    print(f"PASS: {checks} current-print / current-restriction scenarios, "
          f"{successful} authorized physical Trainer transactions")
    print("ACE SPEC prohibition isolates Prime; Item, Supporter, and "
          "Trainer-wide locks separate action classes.")


if __name__ == "__main__":
    run()
