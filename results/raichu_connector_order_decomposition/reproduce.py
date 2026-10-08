"""Reproduce the Harto connector-order deficit decomposition."""

from __future__ import annotations
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from raichu_connector_order_decomposition import (
    BUCKETS,
    connector_order_decomposition,
)
from raichu_visible_connector_sequencing import (
    visible_connector_sequencing_snapshot,
)


def main() -> None:
    result = connector_order_decomposition()
    sequencing = visible_connector_sequencing_snapshot()

    assert abs(
        result.observable_branch_mass
        - sequencing.observable_branch_mass
    ) < 1e-12
    assert abs(
        result.direct_visible_mass
        - sequencing.direct_visible_mass
    ) < 1e-12
    assert abs(
        result.direct_baseline_success_mass
        - sequencing.direct_visible_baseline_mass
    ) < 1e-12
    assert abs(
        result.direct_gain_pp
        - sequencing.direct_gain * 100
    ) < 1e-12
    assert abs(
        sum(result.share(bucket) for bucket in BUCKETS) - 1.0
    ) < 1e-12

    print(f"direct_gain_pp={result.direct_gain_pp:.12f}")
    for bucket in BUCKETS:
        print(
            f"{bucket} "
            f"gain_pp={result.gain_pp(bucket):.12f} "
            f"share={result.share(bucket):.12%}"
        )


if __name__ == "__main__":
    main()
