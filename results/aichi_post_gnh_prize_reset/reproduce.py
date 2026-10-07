from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from aichi_post_gnh_prize_reset import ENDPOINTS, simulate


def main() -> None:
    result = simulate(raw_trials=20_000, seed=20261007)

    assert result.accepted == 17_313
    assert result.gnh_core_ready == 12_322
    assert result.baseline["double_tm"] == 12_170
    assert result.baseline["pidgeot_stage2"] == 10_431
    assert result.baseline["stoutland_stage2"] == 8_577
    assert result.baseline["dual_stage2"] == 7_402
    assert result.baseline["item_lock"] == 6_453

    previous_access = 0
    for copies in range(1, 5):
        assert result.access[copies] > previous_access
        previous_access = result.access[copies]
        for endpoint in ENDPOINTS:
            assert result.rescue[("ticket", endpoint, copies)] <= result.fail_access[(endpoint, copies)]
            assert result.rescue[("rotom", endpoint, copies)] <= result.fail_access[(endpoint, copies)]

    # The larger access regimes are stable enough for a deterministic ordering
    # regression while avoiding an assertion on tiny one-copy differences.
    for copies in (2, 3, 4):
        assert result.rescue[("ticket", "dual_stage2", copies)] >= result.rescue[("rotom", "dual_stage2", copies)]

    assert result.rescue[("ticket", "dual_stage2", 1)] == 259
    assert result.rescue[("ticket", "dual_stage2", 4)] == 897
    assert result.rescue[("rotom", "dual_stage2", 4)] == 843

    print("aichi_post_gnh_prize_reset regression passed")


if __name__ == "__main__":
    main()
