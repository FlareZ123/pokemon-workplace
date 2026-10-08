"""Cross-validate independent KO effect-component factorization against exact DP."""

from math import factorial
from pathlib import Path
from random import Random
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

from ko_order_component_factorization import (
    effect_dependency_components,
    factorized_ko_order_outcomes,
    lexicographic_interleaving,
)
from ko_order_outcome_space import ko_order_outcomes
from results.tyranitar_double_ko_ordering.reproduce import (
    initial_materialized_state,
    programs_for,
)


def compare(programs, precedences=()):
    base = ko_order_outcomes(programs, precedences=precedences)
    separated = factorized_ko_order_outcomes(
        programs, precedences=precedences
    )
    assert separated == base, (programs, precedences, base, separated)
    return separated


def main():
    assert compare({}) == (ko_order_outcomes({})[0],)
    assert lexicographic_interleaving((("b", "d"), ("a", "c"))) == (
        "a", "b", "c", "d"
    )

    independent = {
        "a": {"x": "hand"},
        "b": {"x": "lost_zone"},
        "c": {"y": "hand"},
    }
    assert effect_dependency_components(independent) == (("a", "b"), ("c",))
    assert [row.order_count for row in compare(independent)] == [3, 3]
    assert effect_dependency_components(
        independent, precedences=(("b", "c"),)
    ) == (("a", "b", "c"),)
    compare(independent, (("b", "c"),))
    compare({"a": {"x": "hand"}, "b": {"x": "hand"}})
    assert effect_dependency_components(
        {"a": {"x": "hand"}, "b": {"x": "hand"}}
    ) == (("a",), ("b",))

    rng = Random(20261008)
    sampled = 0
    factored = 0
    for n in range(1, 8):
        for _ in range(40):
            programs = {
                f"effect-{i}": {
                    f"instance-{j}": rng.choice(
                        ("hand", "discard", "lost_zone")
                    )
                    for j in range(rng.randrange(1, 6))
                    if rng.random() < 0.43
                }
                for i in range(n)
            }
            precedence = tuple(
                (f"effect-{i}", f"effect-{j}")
                for i in range(n)
                for j in range(i + 1, n)
                if rng.random() < 0.18
            )
            compare(programs, precedence)
            sampled += 1
            if len(effect_dependency_components(
                programs, precedences=precedence
            )) > 1:
                factored += 1
    assert sampled == 280
    assert factored > 0

    # Two independent conflicts on the real three-Pokemon defender board.
    initial, pending = initial_materialized_state()
    grouped, per_target = programs_for(pending)
    assert len(effect_dependency_components(grouped)) == 1
    assert len(effect_dependency_components(per_target)) == 2
    for programs in (grouped, per_target):
        results = compare(programs)
        assert len(results) == 4
        assert sum(row.order_count for row in results) == factorial(len(programs))
    assert initial.totals() == pending.state.ledger.totals()

    # Ten independent binary conflict pairs yield 1024 distinct endpoints,
    # and a uniform exact per-endpoint multiplicity of (20)! / 2^10.
    # This path invokes ten independent two-effect DPs, avoiding the
    # 20-effect monolithic subset-state expansion.
    large = {
        key: {f"target-{i}": zone}
        for i in range(10)
        for key, zone in (
            (f"keep-{i}", "hand"),
            (f"lose-{i}", "lost_zone"),
        )
    }
    components = effect_dependency_components(large)
    assert len(components) == 10
    assert all(len(component) == 2 for component in components)
    fast = factorized_ko_order_outcomes(large)
    assert len(fast) == 1 << 10
    assert all(row.order_count == factorial(20) // (1 << 10) for row in fast)
    assert sum(row.order_count for row in fast) == factorial(20)

    for bad_precedence in (
        (("a", "a"),),
        (("a", "unknown"),),
        (("a", "b"), ("b", "a")),
    ):
        try:
            factorized_ko_order_outcomes(
                {"a": {}, "b": {}}, precedences=bad_precedence
            )
        except ValueError:
            pass
        else:
            raise AssertionError("invalid constraint was accepted")

    print(
        f"KO component factorization passed: {sampled} randomized full-DP "
        f"cross-checks, {factored} multi-component inputs, plus real "
        "Tyranitar double KO and 20-effect / 1024-endpoint exact stress case"
    )


if __name__ == "__main__":
    main()
