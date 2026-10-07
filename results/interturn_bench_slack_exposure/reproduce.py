from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from interturn_bench_slack_exposure import build_result


def main() -> None:
    s = build_result()["scenarios"]
    assert s["preload_then_collapsed"]["forced_discards"] == 0
    assert s["preload_then_collapsed"]["slack_before"] == 1
    assert s["preload_then_collapsed"]["slack_after"] == 0
    assert not s["preload_then_collapsed"]["objective_survives"]
    assert s["immediate_entry_then_collapsed"]["discarded"] == ["core D"]
    assert s["immediate_entry_then_collapsed"]["objective_survives"]
    assert s["preload_then_parallel"]["discarded"] == ["core D"]
    assert not s["preload_then_parallel"]["objective_survives"]
    assert s["immediate_entry_then_parallel"]["discarded"] == ["core D", "core C"]
    assert s["immediate_entry_then_parallel"]["objective_survives"]
    assert s["low_value_entry_then_collapsed"]["discarded"] == ["required entrant"]
    assert not s["low_value_entry_then_collapsed"]["objective_survives"]
    print("interturn_bench_slack_exposure regression passed")


if __name__ == "__main__":
    main()
