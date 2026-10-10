"""Independent-seed 65k rare-target sample emphasizing Bellelba-only payments."""
from __future__ import annotations

from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from tools.aichi_tagcall_conditional_payload import report, sample_stratified


def main():
    r=sample_stratified(
        zero_g_samples=50_000,one_g_samples=15_000,seed=20261011
    )
    for s in r.strata:
        assert s.eligible>=0.9*s.samples
    for key in r.uplift:
        assert r.uplift[key]>=-1e-12
        assert r.payment_ci_halfwidth[key]>=0
        assert r.uplift[key]+1e-12>=r.protected_uplift[key]>=-1e-12
    print(report(r))
    print("INDEPENDENT REPLICATION PASSED")


if __name__=="__main__":
    main()
