from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from bench_restore_prize_conditioning import build_result


def main() -> None:
    r = build_result()
    k0 = r["k0"]
    k1 = r["k1_examples"]
    assert k0["zero_slack_expected_fraction"] == "43/207"
    assert k0["one_slack_expected_fraction"] == "12383/32637"
    assert abs(k0["zero_slack_expected_percent"] - 20.77294685990338) < 1e-12
    assert abs(k0["one_slack_expected_percent"] - 37.94160002451206) < 1e-12
    assert k1["one_direct_prized_zero_slack"]["percent"] == 12.5
    assert abs(k1["one_remover_prized_zero_slack"]["percent"] - 23.71794871794872) < 1e-12
    assert k1["one_direct_prized_one_slack"] == k1["one_remover_prized_one_slack"]
    print("bench_restore_prize_conditioning regression passed")


if __name__ == "__main__":
    main()
