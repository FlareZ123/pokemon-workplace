"""Exhaustive independent checks for KO outcome-space dynamic programming."""

from __future__ import annotations

from collections import Counter
from itertools import permutations
from math import factorial
from pathlib import Path
from random import Random
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from ko_order_outcome_space import ko_order_outcomes


def brute(programs, precedences=()):
    ids = tuple(programs)
    result = Counter()
    witness = {}
    universe = tuple(sorted({k for program in programs.values() for k in program}))
    for order in permutations(ids):
        position = {effect: i for i, effect in enumerate(order)}
        if any(position[a] >= position[b] for a, b in precedences):
            continue
        routes = {}
        for effect in order:
            for instance, zone in programs[effect].items():
                routes.setdefault(instance, zone)
        outcome = tuple(
            (instance, routes.get(instance, "discard")) for instance in universe
        )
        result[outcome] += 1
        witness[outcome] = min(witness.get(outcome, order), order)
    return result, witness


def check(programs, precedences=()):
    got = ko_order_outcomes(programs, precedences=precedences)
    expected, witnesses = brute(programs, precedences)
    assert {r.destinations: r.order_count for r in got} == dict(expected)
    assert {r.destinations: r.witness_order for r in got} == witnesses
    assert sum(r.order_count for r in got) == sum(expected.values())
    return got


def main():
    # Abstract programs with the destination geometry of a return effect,
    # a Lost City effect, and selective Energy recovery. Real-world
    # applicability/ordering authority must be established upstream.
    programs = {
        "return": {"pokemon": "hand", "energy": "discard"},
        "lost": {"pokemon": "lost_zone", "energy": "discard"},
        "recover": {"energy": "hand"},
    }
    outcomes = check(programs)
    assert len(outcomes) == 4
    assert sorted(r.order_count for r in outcomes) == [1, 1, 2, 2]
    assert sum(r.order_count for r in outcomes) == factorial(3) == 6
    assert len(check(programs, (("recover", "return"),))) == 3
    assert len(check(programs, (("return", "lost"), ("return", "recover")))) == 1

    # Explicitly discarded attachments preempt later routing to hand.
    assert len(check({"discard": {"e": "discard"}, "hand": {"e": "hand"}})) == 2

    # Structural conflict does not imply multiple outcomes when the
    # externally permitted order is fixed.
    assert len(
        check(
            {"a": {"p": "hand"}, "b": {"p": "lost_zone"}},
            (("a", "b"),),
        )
    ) == 1
    assert check({}, ()) == (ko_order_outcomes({})[0],)

    for bad in [(("a", "a"),), (("a", "unknown"),)]:
        try:
            ko_order_outcomes({"a": {}, "b": {}}, precedences=bad)
        except ValueError:
            pass
        else:
            raise AssertionError("invalid precedence was accepted")
    try:
        ko_order_outcomes(
            {"a": {}, "b": {}},
            precedences=(("a", "b"), ("b", "a")),
        )
    except ValueError:
        pass
    else:
        raise AssertionError("cycle was accepted")

    rng = Random(260810)
    for n in range(1, 6):
        for _ in range(45):
            programs = {
                f"e{i}": {
                    name: rng.choice(("hand", "discard", "lost_zone"))
                    for name in ("p", "e", "tool")
                    if rng.random() < 0.64
                }
                for i in range(n)
            }
            constraints = tuple(
                (f"e{i}", f"e{j}")
                for i in range(n)
                for j in range(i + 1, n)
                if rng.random() < 0.2
            )
            check(programs, constraints)

    # Ten disjoint effects: 10! distinct orders, one physical outcome.
    redundant = {f"e{i}": {f"c{i}": "hand"} for i in range(10)}
    collapsed = ko_order_outcomes(redundant)
    assert len(collapsed) == 1
    assert collapsed[0].order_count == factorial(10)
    print("KO outcome-space regression passed: 225 randomized brute-force cases and 10! compression")
    for row in outcomes:
        print(f"{row.destinations}: {row.order_count}/6 orders; witness {row.witness_order}")


if __name__ == "__main__":
    main()
