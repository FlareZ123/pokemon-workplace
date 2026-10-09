"""SFT: enumerate small hidden Prize worlds and prove K0/K1 Tool-thinning reversal."""
from __future__ import annotations

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from tools.gnh_tool_thinning_information import (
    exact, brute_force, describe, exact_multiple,
    brute_force_multiple, multiple_summary,
    minimum_ticket_to_setup_value_ratio,
)


def main() -> None:
    cases = 0
    for unseen in range(3, 11):
        for prizes in range(0, unseen - 1):
            for sample in range(1, unseen - prizes):
                got = exact(unseen, prizes, sample)
                enumerated = brute_force(unseen, prizes, sample)
                assert got == enumerated, (unseen, prizes, sample, got, enumerated)
                if prizes >= 2:
                    assert got.k0_replace_joint < got.k0_keep_joint
                elif prizes == 0:
                    assert got.k0_replace_joint > got.k0_keep_joint
                else:
                    assert got.k0_replace_joint == got.k0_keep_joint
                assert got.k1_oracle_joint > got.k0_keep_joint
                assert got.k0_replace_setup <= got.k0_keep_setup
                cases += 1
    print(f"PASS: {cases} distinct exact parameter cases match independently enumerated Prizes")
    print("PASS: K0 replacement reverses with 2+ Prizes and K1 premium is positive")
    multiple = 0
    for unseen in range(3, 11):
        for prize_count in range(0, unseen - 1):
            for sample_count in range(1, unseen - prize_count):
                for backups in range(1, unseen):
                    got = exact_multiple(unseen, prize_count, sample_count, backups)
                    oracle = brute_force_multiple(unseen, prize_count, sample_count, backups)
                    assert got == oracle, (unseen, prize_count, sample_count, backups)
                    assert got.k1_adaptive_joint >= got.k0_best_joint
                    multiple += 1
    small = exact_multiple(52, 6, 5, 1)
    original = exact(52, 6, 5)
    assert small.keep_joint == original.k0_keep_joint
    assert small.blindly_replace_joint == original.k0_replace_joint
    assert small.k1_adaptive_joint == original.k1_oracle_joint
    assert exact_multiple(52, 6, 5, 2).blindly_replace_joint > small.keep_joint
    print(f"PASS: {multiple} multiple-backup cases match exhaustive physical Prize enumeration")
    print("PASS: one-backup model conserved; two backups reverse the optimal K0 direction")
    # Additive goal scoring: alpha*setup + beta*(setup AND Ticket).
    # Exact ratios are computed without floating-point approximation.
    from fractions import Fraction
    assert minimum_ticket_to_setup_value_ratio(52, 6, 5, 1) is None
    assert minimum_ticket_to_setup_value_ratio(52, 6, 5, 2) == Fraction(150, 13)
    assert minimum_ticket_to_setup_value_ratio(52, 6, 5, 3) == Fraction(588, 1327)
    assert minimum_ticket_to_setup_value_ratio(52, 6, 5, 4) == Fraction(24, 923)
    for unseen in range(3, 10):
        for prize_count in range(0, unseen - 1):
            for sample_count in range(1, unseen - prize_count):
                for backups in range(1, unseen):
                    v = exact_multiple(unseen, prize_count, sample_count, backups)
                    threshold = minimum_ticket_to_setup_value_ratio(
                        unseen, prize_count, sample_count, backups
                    )
                    delta = v.blindly_replace_joint - v.keep_joint
                    loss = 1 - v.blindly_replace_setup
                    if threshold is None:
                        assert delta <= 0
                    else:
                        assert delta > 0
                        assert delta * threshold == loss
    print("PASS: exact Pareto break-even weights match all 164 original cases and extended grid")
    print(describe(52, 6, 5))
    print(multiple_summary(52, 6, 5, 4))


if __name__ == "__main__":
    main()
