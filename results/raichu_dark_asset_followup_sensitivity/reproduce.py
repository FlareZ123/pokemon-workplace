"""Sensitivity of bounded Dark Asset continuation to disposable-pool density."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from raichu_dark_asset_followup import dark_asset_followup_snapshot


def main() -> None:
    rows = []
    for total_disposable in (4, 8, 12, 16, 20, 24):
        result = dark_asset_followup_snapshot(
            disposable_nonstarter_copies=total_disposable - 1,
            disposable_starter_copies=1,
            other_starter_copies=13,
        )
        rows.append(
            {
                "disposable_pool": total_disposable,
                "first_order": result.first_order_dark_asset_access,
                "bounded": result.bounded_followup_access,
                "increment": result.incremental_followup_access,
                "quick_gain": result.quick_followup_gain,
                "ultra_gain_after_quick": result.ultra_followup_gain_after_quick,
                "target_prized_bounded": (
                    result.conditional_target_prized_bounded_followup_access
                ),
            }
        )

    expected_increments = {
        4: 0.000036533357378520925,
        8: 0.00042066956413167045,
        12: 0.001325214445078271,
        16: 0.0026551226834795605,
        20: 0.004179337336268296,
        24: 0.005639125220682106,
    }
    assert all(
        later["increment"] >= earlier["increment"] - 1e-12
        for earlier, later in zip(rows, rows[1:])
    )
    for row in rows:
        assert abs(
            row["increment"] - expected_increments[row["disposable_pool"]]
        ) < 3e-12
        row["quick_share_of_increment"] = (
            row["quick_gain"] / row["increment"]
            if row["increment"] > 0.0
            else 0.0
        )
    print(json.dumps(rows, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
