"""SFT: optional extra Tag Call and late-Jirachi Item-access bounds."""
from __future__ import annotations

from collections import Counter
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from tools.aichi_post_gnh_prize_reset import Prepared
from tools.aichi_tagcall_payment_reachability import additional_tag_call
from tools.aichi_tagcall_information_preview import (
    SAFE_OUTPUTS, best_access, paths_for_endpoint, output, simulate,
)
from tools.aichi_repeated_ticket_access import PACKAGES


def main() -> None:
    hand = Counter({
        "Tag Call": 1, "Technical Machine: Evolution": 1,
        "Faba": 1, "Gladion": 1, "Pidgey": 1, "Bunnelby": 1, "Lillipup": 1,
    })
    remaining = Counter({
        "Guzma & Hala": 2, "Jet Energy": 1, "Artazon": 1,
        "Pidgeotto": 1, "Pidgeot ex": 1, "Herdier": 1,
        "Stoutland": 1, "TechSlot1": 1, "Other": 5,
    })
    state = Prepared(hand, remaining, "Jirachi", (), True)
    extra = additional_tag_call(state)
    assert extra is not None
    assert extra.hand["Tag Call"] == 0
    assert extra.hand["Guzma & Hala"] == 2
    assert extra.remaining["Guzma & Hala"] == 0
    base = paths_for_endpoint(state, "dual_stage2", SAFE_OUTPUTS)
    enhanced = paths_for_endpoint(extra, "dual_stage2")
    assert base and enhanced
    assert any(p.paid_with == ("Guzma & Hala", "Guzma & Hala") for p in enhanced)
    assignment = PACKAGES["one_ticket"]
    p_before = best_access(base, assignment, eligible=True)
    p_after = best_access(enhanced, assignment, eligible=True)
    assert 0 <= p_before <= 1 and 0 <= p_after <= 1
    print("PASS: Tag Call retrieves two TAG TEAM Supporters into exact discard pool")

    sample = simulate(raw_trials=2500, seed=20261009)
    assert 0 <= sample.optional_preview_available <= sample.pre_k1_eligible <= sample.eligible
    assert sum(sample.affected_endpoint.values()) >= 0
    for key, value in sample.benefit.items():
        assert value >= -1e-12
        assert sample.preview[key] >= sample.guard[key] - 1e-12
    print("PASS: paired 2,500-start optional-K1-preview monotonicity regression")
    print(output(sample))


if __name__ == "__main__":
    main()
