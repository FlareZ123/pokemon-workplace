"""Validate the collapsed exact connector-domination calculation."""

from __future__ import annotations

from math import isclose
from pathlib import Path
from statistics import median
import sys
from time import perf_counter

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from connector_domination import (
    two_channel_connector_access,
    two_channel_connector_access_collapsed,
)


def main() -> None:
    cases = []
    for discard_cost in (0, 1, 2, 3):
        for target_a, target_b, disposable in (
            (1, 1, 5),
            (2, 1, 10),
            (2, 2, 15),
            (3, 2, 20),
            (4, 3, 25),
        ):
            cases.append(
                dict(
                    deck_size=60,
                    prize_count=6,
                    starter_cards=12,
                    target_a_copies=target_a,
                    target_b_copies=target_b,
                    disposable_nonstarters=disposable,
                    discard_cost=discard_cost,
                )
            )

    fields = tuple(
        two_channel_connector_access(**cases[0]).__dataclass_fields__
    )

    max_error = 0.0
    for case in cases:
        explicit = two_channel_connector_access(**case)
        collapsed = two_channel_connector_access_collapsed(**case)
        for field in fields:
            error = abs(getattr(explicit, field) - getattr(collapsed, field))
            max_error = max(max_error, error)
            if not isclose(
                getattr(explicit, field),
                getattr(collapsed, field),
                rel_tol=0.0,
                abs_tol=1e-12,
            ):
                raise AssertionError(
                    f"{case} field={field}: "
                    f"{getattr(explicit, field)!r} != "
                    f"{getattr(collapsed, field)!r}"
                )

    baseline = cases[3]
    explicit_times = []
    collapsed_times = []
    for _ in range(5):
        start = perf_counter()
        two_channel_connector_access(**baseline)
        explicit_times.append(perf_counter() - start)

    for _ in range(50):
        start = perf_counter()
        two_channel_connector_access_collapsed(**baseline)
        collapsed_times.append(perf_counter() - start)

    explicit_median = median(explicit_times)
    collapsed_median = median(collapsed_times)

    print(f"Cases checked: {len(cases)}")
    print(f"Maximum absolute difference: {max_error:.3e}")
    print(f"Explicit Prize enumeration median: {explicit_median:.6f}s")
    print(f"Collapsed calculation median: {collapsed_median:.6f}s")
    print(
        "Observed local speed ratio: "
        f"{explicit_median / collapsed_median:.1f}x"
    )
    print("All collapsed exact-calculation checks passed.")


if __name__ == "__main__":
    main()
