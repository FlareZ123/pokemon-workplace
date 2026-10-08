"""Reproducer for extra Tag Call as two-card discard-fuel access."""

from __future__ import annotations

from collections import Counter
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from tools.aichi_post_gnh_prize_reset import Prepared
from tools.aichi_gnh_discard_frontier import paid_gnh_states
from tools.aichi_tagcall_payment_reachability import (
    DIMENSIONS, PACKAGES, additional_tag_call, output,
    property_values, protected_names_for_package, simulate,
)


def make_payment_witness():
    # Already chosen/consumed the active-turn G&H. A spare Tag Call and two
    # additional G&H in deck are available; the only other cards in hand
    # are future critical pieces protected by the sensitivity experiment.
    original = Prepared(
        Counter({"Tag Call": 1, "TechSlot1": 1, "Gladion": 1}),
        Counter({"Guzma & Hala": 2, "Technical Machine: Evolution": 1,
                 "Jet Energy": 1, "Artazon": 1}),
        "Jirachi", (), True,
    )
    protected = protected_names_for_package("one_ticket")
    assert len(paid_gnh_states(original, protected)) == 0

    post_tag = additional_tag_call(original)
    assert post_tag is not None
    assert post_tag.hand["Tag Call"] == 0
    assert post_tag.hand["Guzma & Hala"] == 2
    assert post_tag.remaining["Guzma & Hala"] == 0
    assert post_tag.hand["TechSlot1"] == 1
    prepared = paid_gnh_states(post_tag, protected)
    assert len(prepared) == 1
    assert prepared[0].paid_with == ("Guzma & Hala", "Guzma & Hala")
    assert prepared[0].hand["TechSlot1"] == 1
    assert prepared[0].hand["Gladion"] == 1
    assert prepared[0].hand["Technical Machine: Evolution"] == 1

    no_tag = Prepared(Counter({"Gladion": 1}),
                      Counter({"Guzma & Hala": 3}), "Jirachi", (), True)
    assert additional_tag_call(no_tag) is None
    no_gnh = Prepared(Counter({"Tag Call": 1}),
                      Counter({"Artazon": 1}), "Jirachi", (), True)
    assert additional_tag_call(no_gnh) is None


def main():
    make_payment_witness()
    s = simulate(raw_trials=15_000, seed=20261008)
    assert 0 < s.extra_tagcall_available <= s.core <= s.accepted
    for package in PACKAGES:
        for i in range(len(DIMENSIONS)):
            baseline = s.ordinary[(package, i)]
            aided = s.enhanced[(package, i)]
            gained = s.gained[(package, i)]
            assert 0 <= baseline <= aided <= s.core
            assert gained == aided - baseline
    print("PASS: double G&H retrieval pays two-card optional cost without sacrificing protected singletons or Ticket; Monte Carlo monotonicity")
    print(output(s))


if __name__ == "__main__":
    main()
