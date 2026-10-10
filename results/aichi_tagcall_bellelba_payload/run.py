"""Fixed-seed 500k raw accepted-start sample for Bellelba named payload."""
from __future__ import annotations

from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[2]))

from tools.aichi_tagcall_bellelba_payload import report, simulate


def main():
    result = simulate(raw_trials=500_000, seed=20261010)
    assert result.accepted > 425_000
    assert result.candidate_bellelba > 100
    for key in result.baseline:
        assert result.extended[key] >= result.protected[key] >= result.baseline[key]
    max_discard_premium = max(
        (result.extended[key]-result.protected[key] for key in result.baseline),
        default=0.0,
    )
    print("Maximum incremental Bellelba-discard premium:",max_discard_premium)
    assert max_discard_premium < 1e-12
    print(report(result))
    print("ALL TESTS PASSED")


if __name__ == "__main__":
    main()
