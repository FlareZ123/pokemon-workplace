"""Reproduce the Aichi Secret Box opaque-discard frontier."""

from __future__ import annotations

from aichi_secret_box_opaque_discard_frontier import (
    analyze_incremental_opaque_frontier,
)


def main() -> None:
    result = analyze_incremental_opaque_frontier(
        500_000,
        seed=20261007,
        validation_states=20_000,
    )

    assert result.trials == 500_000
    assert result.baseline_successes == 353_262
    assert result.secret_box_successes == 374_047
    assert result.incremental_successes == 20_785
    assert result.baseline_only_successes == 0
    assert result.validation_mismatches == 0
    assert sum(count for _, count in result.opaque_histogram) == 20_785

    print(f"trials={result.trials}")
    print(f"baseline_successes={result.baseline_successes}")
    print(f"secret_box_successes={result.secret_box_successes}")
    print(f"incremental_successes={result.incremental_successes}")
    print(f"baseline_only_successes={result.baseline_only_successes}")
    print(f"opaque_histogram={dict(result.opaque_histogram)}")
    print(f"validation_states={result.validation_states}")
    print(f"validation_mismatches={result.validation_mismatches}")
    for budget in range(6):
        print(
            f"budget={budget}: "
            f"count={result.successes_with_budget(budget)}, "
            f"gain={result.incremental_probability_with_budget(budget):.6%}, "
            f"survival={result.incremental_survival_share(budget):.6%}"
        )


if __name__ == "__main__":
    main()
