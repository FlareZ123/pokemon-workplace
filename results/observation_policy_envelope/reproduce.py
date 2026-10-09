"""Finite exhaustive policy enumeration and Pokémon Prize-signal witness."""
from __future__ import annotations
from fractions import Fraction
from itertools import product
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"tools"))
from observation_policy_envelope import BeliefState, observation_policy_envelope
from prize_informed_iono_n_choice import prize_uncertain_choice


def brute(rows):
    labels=tuple(sorted({x.observation for x in rows}))
    actions=tuple(name for name,v in rows[0].payoffs)
    best=None
    for choices in product(actions, repeat=len(labels)):
        assign=dict(zip(labels,choices))
        payoff=sum((row.probability*dict(row.payoffs)[assign[row.observation]]
                    for row in rows),Fraction(0))
        if best is None or payoff>best: best=payoff
    return best


def check_exhaustive():
    beliefs=(Fraction(1,2),Fraction(1,3),Fraction(1,6))
    actions=("A","B","C")
    layouts=(("z","z","z"),("z","z","y"),("z","y","z"),
             ("z","y","y"),("z","y","x"))
    cases=0
    for bits in product((0,1),repeat=9):
        payoffs=tuple(tuple((actions[a],Fraction(bits[3*s+a])) for a in range(3))
                      for s in range(3))
        for obs in layouts:
            states=tuple(BeliefState(str(i),beliefs[i],obs[i],payoffs[i]) for i in range(3))
            result=observation_policy_envelope(states)
            assert result.expected_payoff==brute(states)
            cases+=1
    assert cases==2560
    print("Exhaustive observation-consistent 3-action policy cases:",cases)


def witnesses():
    v=prize_uncertain_choice(deck_size=46,prizes_hidden=6,unknown_outs=10,
        hand_size=5,hand_outs=1,prize_draw_count=6,opponent_hand_size=2)
    def encode(which):
        return tuple(BeliefState(
            str(row.deck_outs),row.prior_probability,
            "K0" if which=="blind" else
            ("K>=9" if row.deck_outs>=9 else "K<=8") if which=="boundary" else str(row.deck_outs),
            (("Iono",row.iono_success),("N",row.n_success)),
        ) for row in v.rows)
    blind=observation_policy_envelope(encode("blind"))
    grouped=observation_policy_envelope(encode("boundary"))
    full=observation_policy_envelope(encode("full"))
    assert blind.expected_payoff==v.before_information
    assert grouped.expected_payoff==v.after_information==full.expected_payoff
    assert blind.chosen_by_observation==(("K0","Iono"),)
    assert grouped.chosen_by_observation==(("K<=8","N"),("K>=9","Iono"))
    assert round(100*float(full.expected_payoff-blind.expected_payoff),6)==0.169011
    print("One-bit K>=9 signal attains exact full-K1 Iono/N decision value")
    triple=tuple(BeliefState(str(i),Fraction(1,3),"K0",
                 tuple((a,Fraction(i==j)) for j,a in enumerate(("A","B","C"))))
                 for i in range(3))
    blind3=observation_policy_envelope(triple)
    full3=observation_policy_envelope(tuple(
        BeliefState(row.state_id,row.probability,row.state_id,row.payoffs)
        for row in triple))
    assert blind3.expected_payoff==Fraction(1,3)
    assert full3.expected_payoff==Fraction(1)
    print("Three-action toy confirms multi-action envelope: 1/3 blind, 1 fully informed")


if __name__=="__main__":
    check_exhaustive()
    witnesses()
