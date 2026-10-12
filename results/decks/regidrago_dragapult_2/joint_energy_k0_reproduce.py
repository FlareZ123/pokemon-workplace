"""SFT: nonanticipative pre-search Item selection under Energy-weighted utility."""

from __future__ import annotations

from fractions import Fraction
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/"tools"))

from regidrago_joint_launch_k0 import first_action_succeeds as prior_action
from regidrago_joint_launch_k0 import analyze_k0 as prior_k0

from tools.regidrago_joint_launch import Build,analyze as original
from tools.regidrago_joint_energy_k0 import analyze,actions,forced
from tools.regidrago_joint_energy_gate import analyze as three_gate


def main() -> None:
    # Independent previous action engine must agree with each available
    # action for an exhaustive set of toy physical material configurations.
    checked=0
    for rv in (0,1,2):
        for dp in (0,1,2):
            for vip in (0,1,2):
                for qb in (0,1,2):
                    for mt in (0,1,2):
                        for bc in (0,1):
                            hand=(rv,1,dp,vip,qb,mt,bc,0,0)
                            for rv_deck in (0,1,2):
                                for dp_deck in (0,1,2):
                                    for a in actions(hand):
                                        assert forced(a,hand,rv_deck,dp_deck)==prior_action(
                                            a,hand,rv_deck=rv_deck,dp_deck=dp_deck)
                                        checked+=1
    print(f"PASS: {checked} forced first-Item decisions against old independent planner")

    for build in (Build(),Build(dragapult=2,vip=2)):
        triple=three_gate(build)
        k0=analyze(build)
        original_item=original(build)["joint_any"]
        prior=prior_k0(build)
        assert k0.clairvoyant==triple.item_and_natural_energy
        assert k0.k0_first_item==k0.clairvoyant
        assert k0.gap==0
        assert k0.positive_oracle_hands==k0.perfect_universal_hands
        assert k0.positive_oracle_hands>0
        assert original_item==prior["clairvoyant_joint"]==prior["k0_joint"]
        print("PASS:",build.dragapult,"Dragapult; first-Item K0 matches full-information three-way joint")
        print("  visible hand classes",k0.legal_visible_hands,
              "winnable source+Energy hand classes",k0.positive_oracle_hands)

    standard=analyze(Build())
    variant=analyze(Build(dragapult=2,vip=2))
    assert standard.k0_first_item==Fraction(
        43802912931679,1337284321420320)
    assert variant.k0_first_item==Fraction(
        408575428938988601,8458323332983524000)
    assert variant.k0_first_item>standard.k0_first_item
    print("PASS: real 60-card protected D=0 model has zero K0 first-Item information gap")
    print("LIMIT: only first committed search; later search/payout policy adaptive, no match outcome")


if __name__=="__main__":
    main()
