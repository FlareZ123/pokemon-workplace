"""SFT: population-weighted Nest-first sequencing under hidden Prize knowledge."""
from __future__ import annotations

from pathlib import Path
from fractions import Fraction
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"tools"))

from secret_box_gnh_tool_pipeline import counts
from secret_box_nest_ball_k0 import nest_ball_opening_mixture
from secret_box_pre_nest_opening_mix import pre_nest_opening_mixture


def main():
    deck=counts(D=20,I=1,A=2,B=1,G=2,S=2,E=1,P=30)
    old=nest_ball_opening_mixture(deck,total_basic_starters=12)
    result=pre_nest_opening_mixture(deck,total_basic_starters=12)
    assert result.considered_state_count==old.visible_states==1241
    assert result.box_first_k0==old.k0_success
    assert result.clairvoyant_upper==old.k1_success
    assert 0<=result.sequencing_gain<=old.k1_success-old.k0_success
    print("Baseline Box-first K0",result.box_first_k0,float(result.box_first_k0))
    print("Choose order in K0",result.best_order_k0,float(result.best_order_k0))
    print("Clairvoyant upper",result.clairvoyant_upper,float(result.clairvoyant_upper))
    print("Order gain",result.sequencing_gain,float(result.sequencing_gain))
    print("Residual K0 gap",result.residual_information_gap,float(result.residual_information_gap))
    print("Nest Ball visible, one Basic",result.pre_nest_eligible_hand_mass,
          float(result.pre_nest_eligible_hand_mass))
    print("Hands with strict order advantage",result.improvement_hand_mass,
          float(result.improvement_hand_mass))
    print("Distinct improved category states",result.improvement_state_count)
    print("Typed visible states",result.considered_state_count)
    print("ALL TESTS PASSED")


if __name__=="__main__":
    main()
