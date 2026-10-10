"""SFT: Bellelba is a physical optional Tag Call payout before G&H."""
from __future__ import annotations

from collections import Counter
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from tools.aichi_post_gnh_prize_reset import Prepared
from tools.aichi_tagcall_payment_reachability import additional_tag_call
from tools.aichi_tagcall_bellelba_payload import (
    GNH, BELLELBA, supplement_with_bellelba, report, simulate,
)


def fixtures():
    original = Prepared(
        Counter({"Tag Call":1,"Guzma":1}),
        Counter({GNH:1,BELLELBA:1,"Artazon":1}),
        "Jirachi", (), True,
    )
    stock_g = additional_tag_call(original)
    stock_gb = supplement_with_bellelba(original)
    assert stock_g is not None and stock_gb is not None
    assert stock_g.hand[GNH] == 1 and stock_g.hand[BELLELBA] == 0
    assert stock_gb.hand[GNH] == stock_gb.hand[BELLELBA] == 1
    assert stock_gb.hand["Tag Call"] == 0
    assert stock_gb.remaining[GNH] == stock_gb.remaining[BELLELBA] == 0
    assert stock_gb.remaining["Artazon"] == 1
    assert original.hand["Tag Call"] == 1
    assert original.remaining[GNH] == original.remaining[BELLELBA] == 1

    single = Prepared(
        Counter({"Tag Call":1}), Counter({BELLELBA:1}), "Jirachi", (), True
    )
    assert additional_tag_call(single) is None
    assert supplement_with_bellelba(single).hand[BELLELBA] == 1

    full = Prepared(
        Counter({"Tag Call":1}), Counter({GNH:2,BELLELBA:1}),
        "Jirachi", (), True,
    )
    assert supplement_with_bellelba(full) is None

    locked = Prepared(
        Counter({"Guzma":1}), Counter({GNH:1,BELLELBA:1}),
        "Jirachi", (), True,
    )
    assert supplement_with_bellelba(locked) is None
    print("Physical named-card conservation fixtures: PASS")


def main():
    fixtures()
    result = simulate(raw_trials=10_000, seed=20261010)
    assert result.accepted >= 7000
    assert result.candidate_bellelba <= result.eligible <= result.accepted
    for key in result.baseline:
        assert result.extended[key] >= result.protected[key] >= result.baseline[key]
    print(report(result))
    print("ALL TESTS PASSED")


if __name__ == "__main__":
    main()
