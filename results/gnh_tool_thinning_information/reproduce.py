"""SFT: enumerate small hidden Prize worlds and prove K0/K1 Tool-thinning reversal."""
from __future__ import annotations

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from tools.gnh_tool_thinning_information import exact, brute_force, describe


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
    print(describe(52, 6, 5))


if __name__ == "__main__":
    main()
