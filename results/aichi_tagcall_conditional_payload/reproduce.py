"""SFT: exact-mass conditioned physical Aichi Bellelba search comparison."""
from __future__ import annotations

import random
from fractions import Fraction
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[2]))

from tools.aichi_post_gnh_prize_reset import DECK
from tools.aichi_tagcall_conditional_payload import (
    sample_conditioned_order, category_weights, sample_stratified, report,
)
from tools.aichi_tagcall_target_availability import exact_tagcall_target_partition


def physical_checks():
    for g_left in (0,1):
        assert category_weights(g_left)
        rng=random.Random(11000+g_left)
        for _ in range(100):
            indices=sample_conditioned_order(rng,g_left)
            opening=[DECK[i] for i in indices[:7]]
            prizes=[DECK[i] for i in indices[7:13]]
            drawn=DECK[indices[13]]
            deck=[DECK[i] for i in indices[14:]]
            assert len(set(indices))==60
            assert "Jirachi" in opening
            assert "Bellelba & Brycen-Man" in deck
            assert "Bellelba & Brycen-Man" not in opening+prizes+[drawn]
            assert "Guzma & Hala" in opening+[drawn]
            assert "Tag Call" in opening+[drawn]
            assert deck.count("Guzma & Hala")==g_left
    print("Physical conditional permutation constraints: PASS")


def main():
    physical_checks()
    weights=exact_tagcall_target_partition()
    assert weights.count_probability(gnh_count=0,bellelba_count=1) == Fraction(74221,1341841280)
    assert weights.count_probability(gnh_count=1,bellelba_count=1) == Fraction(66550477,64945117952)
    x=sample_stratified(zero_g_samples=300,one_g_samples=1_000,seed=20261010)
    for s in x.strata:
        assert s.eligible>0
    for key in x.uplift:
        assert x.uplift[key]>=-1e-12
        assert x.uplift[key]+1e-12 >= x.protected_uplift[key]>=-1e-12
        assert x.payment_premium[key]>=-1e-12
    print(report(x))
    print("ALL TESTS PASSED")


if __name__ == "__main__":
    main()
