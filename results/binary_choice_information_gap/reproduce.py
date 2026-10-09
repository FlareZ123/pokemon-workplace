"""Independent exhaustive binary-choice information-gap identity check."""
from __future__ import annotations

from fractions import Fraction
from itertools import product
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"tools"))
from binary_choice_information_gap import binary_choice_information_gap
from prize_informed_iono_n_choice import prize_uncertain_choice


def independent(states):
    expected_max=sum((w*max(a,b) for w,a,b in states),Fraction(0))
    a=sum((w*a for w,a,b in states),Fraction(0))
    b=sum((w*b for w,a,b in states),Fraction(0))
    return expected_max-max(a,b)


def exhaustive():
    values=(Fraction(0),Fraction(1,3),Fraction(2,3),Fraction(1))
    cases=0
    for den in range(1,6):
        for n in range(den+1):
            weights=(Fraction(n,den),Fraction(den-n,den))
            for payoffs in product(values, repeat=4):
                states=((weights[0],payoffs[0],payoffs[1]),
                        (weights[1],payoffs[2],payoffs[3]))
                g=binary_choice_information_gap(states)
                assert g.information_gain==independent(states)
                if (payoffs[0]-payoffs[1])*(payoffs[2]-payoffs[3])>=0:
                    assert g.information_gain==0
                cases+=1
    assert cases==5120
    print("Generic exact rational two-action models checked:",cases)


def source_witness():
    r=prize_uncertain_choice(deck_size=46,prizes_hidden=6,unknown_outs=10,
        hand_size=5,hand_outs=1,prize_draw_count=6,opponent_hand_size=2)
    states=tuple((v.prior_probability,v.iono_success,v.n_success) for v in r.rows)
    gap=binary_choice_information_gap(states)
    assert gap.information_gain==r.information_gain
    assert round(100*float(gap.expected_advantage),6)==0.026215
    assert round(100*float(gap.expected_absolute_advantage),6)==0.364237
    assert round(100*float(gap.information_gain),6)==0.169011
    later=prize_uncertain_choice(deck_size=46,prizes_hidden=6,unknown_outs=10,
        hand_size=3,hand_outs=1,prize_draw_count=6,opponent_hand_size=2)
    after=binary_choice_information_gap(
        (v.prior_probability,v.iono_success,v.n_success) for v in later.rows)
    assert after.information_gain==0
    assert abs(after.expected_advantage)==after.expected_absolute_advantage
    print("Before payment: 0.364237pp E|delta|, 0.026215pp |E(delta)| => +0.169011pp")
    print("After payment: pointwise dominance, exact zero information choice gain")


if __name__=="__main__":
    exhaustive()
    source_witness()
