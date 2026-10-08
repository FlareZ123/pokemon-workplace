"""Run the Aichi Secret Box output-dependency audit."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from aichi_secret_box_output_dependencies import analyze_output_dependencies


def main() -> None:
    result = analyze_output_dependencies(100_000, seed=20261007)

    # Existing exact-name payment-family work identifies the same seeded
    # 100,000-state prefix and 4,175 Secret-Box-only successes.
    if result.incremental_successes != 4_175:
        raise AssertionError(result.incremental_successes)
    if result.full_output_successes - result.baseline_successes != 4_175:
        raise AssertionError(
            (
                result.baseline_successes,
                result.full_output_successes,
            )
        )
    if result.minimum_category_counts[0] != 0:
        raise AssertionError(result.minimum_category_counts)
    if sum(result.minimum_category_counts) != result.incremental_successes:
        raise AssertionError(result.minimum_category_counts)
    if result.mask_success_counts[15] != result.incremental_successes:
        raise AssertionError(result.mask_success_counts[15])
    if result.mask_success_counts[0] != 0:
        raise AssertionError(result.mask_success_counts[0])
    if result.monotonicity_violations != 0:
        raise AssertionError(result.monotonicity_violations)

    print(f"baseline_successes={result.baseline_successes}")
    print(f"full_output_successes={result.full_output_successes}")
    print(f"incremental_successes={result.incremental_successes}")
    print(f"minimum_category_counts={result.minimum_category_counts}")
    print(
        "indispensable_category_counts="
        f"{result.indispensable_category_counts}"
    )
    print(f"singleton_route_count_counts={result.singleton_route_count_counts}")
    print("singleton_signature_counts=")
    for signature, count in enumerate(result.singleton_signature_counts):
        if count:
            print(f"{signature:02d} {result.mask_label(signature):28s} {count}")
    print("mask_success_counts=")
    for mask, count in enumerate(result.mask_success_counts):
        print(f"{mask:02d} {result.mask_label(mask):28s} {count}")
    print("minimal_mask_witness_counts=")
    for mask, count in enumerate(result.minimal_mask_witness_counts):
        if count:
            print(f"{mask:02d} {result.mask_label(mask):28s} {count}")
    print("unique_minimal_mask_counts=")
    for mask, count in enumerate(result.unique_minimal_mask_counts):
        if count:
            print(f"{mask:02d} {result.mask_label(mask):28s} {count}")
    print("All Secret Box output-dependency structural checks passed.")


if __name__ == "__main__":
    main()
