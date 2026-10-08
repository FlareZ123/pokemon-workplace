"""Independently verify paired-switch stage ordering and legal print texts.

Run: python -m results.paired_switch_order_catalog.reproduce
"""
from collections import Counter
from itertools import product
from pathlib import Path

from tools.paired_switch_order_catalog import (
    PROGRAMS, compiled_profiles, switch_effects,
)


def independent_effects(name, own_bench, opponent_bench, active_rocket, bench_rocket):
    """Direct manual resolution with separately encoded name cases."""
    if name == "Team Rocket's Giovanni":
        if not (own_bench and active_rocket and bench_rocket):
            return ()
        return ("own", "opponent") if opponent_bench else ("own",)
    if not opponent_bench:
        return ()
    return ("opponent", "own") if own_bench else ("opponent",)


def run():
    root = Path(__file__).resolve().parents[2] / "resources"
    rows = compiled_profiles(root)
    by_name = Counter(row.card_name for row, _ in rows)
    assert by_name == {
        "Prime Catcher": 2, "Cross Switcher": 1, "Guzma": 4,
        "Team Rocket's Giovanni": 4
    }

    for row, program in rows:
        assert row.profile.player_selects_existing_bench
        rules = " ".join(row.effective_text.casefold().split())
        if program.first == "opponent":
            first = (
                "switch in 1 of your opponent's benched"
                if row.card_name == "Prime Catcher"
                else "switch 1 of your opponent's benched"
            )
            last = "switch your active pokémon with"
        else:
            first = "switch your active team rocket's pokémon"
            last = "switch in 1 of your opponent's benched"
        assert -1 < rules.find(first) < rules.find("if you do") < rules.find(last), (
            row.card_id, rules
        )

    compared = 0
    for name, program in PROGRAMS.items():
        for own, opponent, active_rocket, bench_rocket in product(
            (False, True), repeat=4
        ):
            if bench_rocket and not own:
                continue
            actual = switch_effects(program, own, opponent,
                                    active_rocket, bench_rocket)
            expected = independent_effects(name, own, opponent,
                                           active_rocket, bench_rocket)
            assert actual == expected, (name, own, opponent, actual, expected)
            compared += 1

    assert compared == 48
    assert PROGRAMS["Cross Switcher"].copies_together == 2
    assert switch_effects(PROGRAMS["Prime Catcher"], False, True) == (
        "opponent",
    )
    assert switch_effects(
        PROGRAMS["Team Rocket's Giovanni"], False, True
    ) == ()
    assert switch_effects(
        PROGRAMS["Team Rocket's Giovanni"], True, False, True, True
    ) == ("own",)
    assert switch_effects(
        PROGRAMS["Team Rocket's Giovanni"], True, True, True, True
    ) == ("own", "opponent")
    assert switch_effects(PROGRAMS["Prime Catcher"], True, False) == ()
    print("Current-legal paired-switch print counts:", dict(by_name))
    print(f"PASS: {len(rows)} source-text audits, "
          f"{compared} independently compared effect orderings")


if __name__ == "__main__":
    run()
