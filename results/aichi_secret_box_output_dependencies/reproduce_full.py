"""Full 500,000-state Secret Box output-dependency audit."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from aichi_secret_box_output_dependencies import analyze_output_dependencies


def main() -> None:
    result = analyze_output_dependencies(500_000, seed=20261007)

    if result.incremental_successes != 20_785:
        raise AssertionError(result.incremental_successes)
    if result.full_output_successes - result.baseline_successes != 20_785:
        raise AssertionError(
            (result.baseline_successes, result.full_output_successes)
        )
    if result.mask_success_counts[15] != result.incremental_successes:
        raise AssertionError(result.mask_success_counts[15])
    if result.mask_success_counts[0] != 0:
        raise AssertionError(result.mask_success_counts[0])
    if sum(result.minimum_category_counts) != result.incremental_successes:
        raise AssertionError(result.minimum_category_counts)
    if result.monotonicity_violations != 0:
        raise AssertionError(result.monotonicity_violations)

    expected = {
        "baseline_successes": 353_262,
        "full_output_successes": 374_047,
        "minimum_category_counts": (0, 20_785, 0, 0, 0),
        "item_failure_tag_call_deck_counts": (2, 0, 0, 0, 0),
        "supporter_failure_gnh_deck_counts": (0, 0, 5, 24, 53),
        "indispensable_category_counts": (0, 0, 2, 0),
        "singleton_route_count_counts": (0, 44, 17_849, 2_888, 4),
        "singleton_signature_counts": (
            0, 42, 0, 40,
            2, 17_809, 0, 2_269,
            0, 0, 0, 0,
            0, 619, 0, 4,
        ),
        "mask_success_counts": (
            0, 20_783, 2_313, 20_783,
            20_703, 20_785, 20_785, 20_785,
            623, 20_783, 4_849, 20_783,
            20_745, 20_785, 20_785, 20_785,
        ),
        "minimal_mask_witness_counts": (
            0, 20_783, 2_313, 0,
            20_703, 0, 0, 0,
            623, 0, 0, 0,
            0, 0, 0, 0,
        ),
        "unique_minimal_mask_counts": (
            0, 42, 0, 0,
            2, 0, 0, 0,
            0, 0, 0, 0,
            0, 0, 0, 0,
        ),
    }
    for field, value in expected.items():
        actual = getattr(result, field)
        if actual != value:
            raise AssertionError(f"{field}: {actual!r} != {value!r}")

    print(f"baseline_successes={result.baseline_successes}")
    print(f"full_output_successes={result.full_output_successes}")
    print(f"incremental_successes={result.incremental_successes}")
    print(f"minimum_category_counts={result.minimum_category_counts}")
    print(
        "item_failure_tag_call_deck_counts="
        f"{result.item_failure_tag_call_deck_counts}"
    )
    print(
        "supporter_failure_gnh_deck_counts="
        f"{result.supporter_failure_gnh_deck_counts}"
    )
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


if __name__ == "__main__":
    main()
