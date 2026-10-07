"""Reproduce exact Secret Box payment-family statistics."""

from __future__ import annotations

from aichi_secret_box_payment_families import analyze_payment_families


def main() -> None:
    result = analyze_payment_families(100_000, seed=20261007)

    assert result.trials == 100_000
    assert result.incremental_successes == 4_175
    assert result.missing_families == 0
    assert result.family_size_total == 80_912
    assert result.family_size_min == 4
    assert result.family_size_max == 70
    assert result.singleton_floor_histogram == (
        (0, 3_577),
        (1, 498),
        (2, 90),
        (3, 10),
    )
    assert result.singleton_free_states == 3_577
    assert result.any_forced_singleton_states == 0
    assert result.forced_singleton_counts == ()
    assert result.protection_cut_histogram == (
        (1, 1),
        (2, 120),
        (3, 1_008),
        (4, 2_752),
        (5, 294),
    )

    print(f"trials={result.trials}")
    print(f"incremental_successes={result.incremental_successes}")
    print(f"missing_families={result.missing_families}")
    print(f"family_size_total={result.family_size_total}")
    print(f"family_size_min={result.family_size_min}")
    print(f"family_size_max={result.family_size_max}")
    print(f"family_size_histogram={dict(result.family_size_histogram)}")
    print(f"singleton_floor_histogram={dict(result.singleton_floor_histogram)}")
    print(f"singleton_free_states={result.singleton_free_states}")
    print(f"any_forced_singleton_states={result.any_forced_singleton_states}")
    print(f"forced_singleton_counts={dict(result.forced_singleton_counts)}")
    print(f"protection_cut_histogram={dict(result.protection_cut_histogram)}")


if __name__ == "__main__":
    main()
