"""Reproduce the Aichi Secret Box opaque Pareto frontier."""

from __future__ import annotations

from aichi_secret_box_opaque_pareto import analyze_opaque_pareto


def main() -> None:
    result = analyze_opaque_pareto(
        500_000,
        seed=20261007,
        validation_incremental_states=10_000,
    )

    assert result.trials == 500_000
    assert result.incremental_successes == 20_785
    assert result.missing_frontiers == 0
    assert result.initial_validation_mismatches == 0
    assert result.total_validation_mismatches == 0
    assert sum(
        count for _, count in result.frontier_size_histogram
    ) == 20_785

    print(f"trials={result.trials}")
    print(f"incremental_successes={result.incremental_successes}")
    print(f"missing_frontiers={result.missing_frontiers}")
    print(f"tradeoff_states={result.tradeoff_states}")
    print(f"frontier_size_histogram={dict(result.frontier_size_histogram)}")
    print("frontier_shape_histogram=")
    for frontier, count in result.frontier_shape_histogram:
        print(f"  {frontier}: {count}")
    print(
        "total_penalty_if_minimize_initial="
        f"{dict(result.total_penalty_if_minimize_initial)}"
    )
    print(
        "initial_penalty_if_minimize_total="
        f"{dict(result.initial_penalty_if_minimize_total)}"
    )
    print(f"validation_states={result.validation_states}")
    print(
        "initial_validation_mismatches="
        f"{result.initial_validation_mismatches}"
    )
    print(
        "total_validation_mismatches="
        f"{result.total_validation_mismatches}"
    )


if __name__ == "__main__":
    main()
