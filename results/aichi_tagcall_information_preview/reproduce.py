"""SFT: optional extra Tag Call and late-Jirachi Item-access bounds."""
from __future__ import annotations

from collections import Counter
from fractions import Fraction
from itertools import combinations
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from tools.aichi_post_gnh_prize_reset import Prepared
from tools.aichi_tagcall_payment_reachability import additional_tag_call
from tools.aichi_tagcall_information_preview import (
    SAFE_OUTPUTS, best_access, paths_for_endpoint, output, simulate,
    exact_natural_triplet_probability,
)
from tools.aichi_repeated_ticket_access import PACKAGES


def verify_triplet_exact() -> int:
    trials = 0
    for n in range(7, 11):
        for h in (2, 3):
            for starters in (1, 2, 3):
                for g in (1, 2):
                    for tag in (1, 2):
                        if 1 + g + tag > n:
                            continue
                        pool = (
                            ("Jirachi",) + ("B",) * (starters - 1)
                            + ("Guzma & Hala",) * g + ("Tag Call",) * tag
                            + ("Other",) * (n - starters - g - tag)
                        )
                        if len(pool) != n:
                            continue
                        accepted = success = 0
                        for opener in combinations(range(n), h):
                            other = tuple(i for i in range(n) if i not in opener)
                            if not any(pool[i] in ("Jirachi", "B") for i in opener):
                                continue
                            for drawn in other:
                                accepted += 1
                                known = opener + (drawn,)
                                success += int(
                                    any(pool[i] == "Jirachi" for i in opener)
                                    and any(pool[i] == "Guzma & Hala" for i in known)
                                    and any(pool[i] == "Tag Call" for i in known)
                                )
                        expected = exact_natural_triplet_probability(
                            n, h, starters, g, tag
                        )
                        assert Fraction(success, accepted) == expected, (
                            n, h, starters, g, tag, expected,
                            Fraction(success, accepted)
                        )
                        trials += 1
    return trials


def main() -> None:
    cases = verify_triplet_exact()
    print(f"PASS: {cases} labeled opening/draw counts match exact Jirachi-connector formula")
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
        assert abs(sample.benefit[key] - sample.material_benefit[key]
                   - sample.guard_relaxation_benefit[key]) < 1e-10
        assert sample.material_only[key] >= sample.guard[key] - 1e-12
        assert sample.preview[key] >= sample.material_only[key] - 1e-12
    print("PASS: paired 2,500-start optional-K1-preview monotonicity regression")
    print(output(sample))


if __name__ == "__main__":
    main()
