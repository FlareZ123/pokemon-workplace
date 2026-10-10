"""High-precision fixed-seed conditional search over rare Bellelba target strata."""
from __future__ import annotations

from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[2]))

from tools.aichi_tagcall_conditional_payload import sample_stratified, report


def main():
    result=sample_stratified(
        zero_g_samples=10_000,
        one_g_samples=30_000,
        seed=20261010,
    )
    for s in result.strata:
        assert s.eligible>500
    for key in result.uplift:
        assert result.uplift[key]>=0.0
        assert 0.0<=result.protected_uplift[key]<=result.uplift[key]+1e-12
        assert result.payment_premium[key]>=-1e-12
    print(report(result))
    print("ALL TESTS PASSED")


if __name__=="__main__":
    main()
