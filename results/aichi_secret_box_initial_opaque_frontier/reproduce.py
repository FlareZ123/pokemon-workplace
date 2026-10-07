"""Reproduce the initial Secret Box opaque-discard frontier."""

from __future__ import annotations

from aichi_secret_box_initial_opaque_frontier import (
    analyze_initial_opaque_frontier,
)


def main() -> None:
    result = analyze_initial_opaque_frontier(500_000, seed=20261007)

    assert result.trials == 500_000
    assert result.incremental_successes == 20_785
    assert result.missing_cost_witnesses == 0
    assert result.histogram == (
        (0, 570),
        (1, 4_598),
        (2, 9_592),
        (3, 6_025),
    )
    assert [result.successes_with_budget(budget) for budget in range(4)] == [
        570,
        5_168,
        14_760,
        20_785,
    ]

    print(f"trials={result.trials}")
    print(f"incremental_successes={result.incremental_successes}")
    print(f"histogram={dict(result.histogram)}")
    print(f"missing_cost_witnesses={result.missing_cost_witnesses}")
    for budget in range(4):
        print(
            f"budget={budget}: "
            f"count={result.successes_with_budget(budget)}, "
            f"survival={result.survival_share(budget):.6%}"
        )


if __name__ == "__main__":
    main()
