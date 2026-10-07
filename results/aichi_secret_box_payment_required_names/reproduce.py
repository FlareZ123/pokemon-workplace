"""Reproduce required-name audit for Secret Box payment families."""

from aichi_secret_box_payment_required_names import analyze_required_names


def main() -> None:
    result = analyze_required_names(100_000, seed=20261007)
    assert result.incremental_successes == 4_175
    print(f"trials={result.trials}")
    print(f"incremental_successes={result.incremental_successes}")
    print(f"states_with_required_name={result.states_with_required_name}")
    print(f"required_name_counts={dict(result.required_name_counts)}")


if __name__ == "__main__":
    main()
