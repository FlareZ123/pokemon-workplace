"""Diagnose and reproduce the Harto connector-order deficit decomposition."""

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

    print("branch", repr(result.observable_branch_mass), repr(sequencing.observable_branch_mass), flush=True)
    print("direct_mass", repr(result.direct_visible_mass), repr(sequencing.direct_visible_mass), flush=True)
    print("baseline_mass", repr(result.direct_baseline_success_mass), repr(sequencing.direct_visible_baseline_mass), flush=True)
    print("gain_pp", repr(result.direct_gain_pp), repr(sequencing.direct_gain * 100), flush=True)
    for bucket in BUCKETS:
        print(
            bucket,
            "mass", repr(result.bucket_mass[bucket]),
            "baseline", repr(result.bucket_baseline_success_mass[bucket]),
            "gain_pp", repr(result.gain_pp(bucket)),
            "share", repr(result.share(bucket)),
            flush=True,
        )


if __name__ == "__main__":
    main()
