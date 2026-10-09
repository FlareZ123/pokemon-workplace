"""Exact full-payment and K1 information decomposition regression."""
from __future__ import annotations
from fractions import Fraction
from math import comb
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"tools"))
from presearch_iono_n_decomposition import compare_paid_search


def draw_hit(n,k,d):
    take=min(d,n)
    return Fraction(1)-Fraction(comb(n-k,take),comb(n,take)) if n-k>=take else Fraction(1)


def independent(D,P,U,H,R,d,Q):
    total=Fraction(comb(D+P,U))
    i=n=a=Fraction(0)
    for k in range(max(0,U-P),min(D,U)+1):
        weight=Fraction(comb(D,k)*comb(P,U-k),total)
        nval=draw_hit(D+H,k+R,d)
        if H+Q==0:
            ival=Fraction(0)
        elif d<=D:
            ival=draw_hit(D,k,d)
        elif k:
            ival=Fraction(1)
        elif H:
            ival=draw_hit(H,R,d-D)
        else:
            ival=Fraction(0)
        i+=weight*ival
        n+=weight*nval
        a+=weight*max(ival,nval)
    return max(i,n),a


def check():
    n=0
    for D in range(1,5):
        for P in range(3):
            for U in range(D+P+1):
                for H in range(5):
                    for R in range(H+1):
                        for pay in range(H+1):
                            for rp in range(min(pay,R)+1):
                                if pay-rp>H-R: continue
                                for d in range(4):
                                    for Q in (0,1):
                                        z=compare_paid_search(
                                            deck_size=D,prizes_hidden=P,unknown_outs=U,
                                            hand_size=H,hand_outs=R,
                                            prize_draw_count=d,opponent_hand_size=Q,
                                            payment_count=pay,payment_outs=rp)
                                        first,first_adapt=independent(D,P,U,H,R,d,Q)
                                        post,post_adapt=independent(D,P,U,H-pay,R-rp,d,Q)
                                        assert z.baseline.before_information==first
                                        assert z.after_payment.before_information==post
                                        assert z.after_payment.after_information==post_adapt
                                        assert z.thinning_effect==post-first
                                        assert z.information_effect_after_payment==post_adapt-post
                                        assert z.net_effect==post_adapt-first
                                        n+=1
    print("Independent exact small-state decomposition checks:",n)


def witnesses():
    base=dict(deck_size=46,prizes_hidden=6,unknown_outs=10,
              hand_size=5,hand_outs=1,prize_draw_count=6,
              opponent_hand_size=2,payment_count=2)
    nonouts=compare_paid_search(**base,payment_outs=0)
    oneout=compare_paid_search(**base,payment_outs=1)
    assert round(100*float(nonouts.thinning_effect),6)==1.608069
    assert nonouts.information_effect_after_payment==0
    assert round(100*float(nonouts.net_effect),6)==1.608069
    assert oneout.thinning_effect==0 and oneout.information_effect_after_payment==0
    alt=compare_paid_search(deck_size=46,prizes_hidden=6,unknown_outs=6,
        hand_size=10,hand_outs=1,prize_draw_count=6,opponent_hand_size=2,
        payment_count=2,payment_outs=0)
    assert round(100*float(alt.thinning_effect),6)==0.204495
    assert round(100*float(alt.information_effect_after_payment),6)==0.274329
    assert round(100*float(alt.net_effect),6)==0.478824
    print("D46/H5 sample: nonout pay +1.608069 pp thinning, zero additional K1 info")
    print("D46/H10 sample: +0.204495 pp thinning, +0.274329 pp K1 info")
    print("Paying an out can erase immediate gain entirely in first sample")


if __name__=="__main__":
    check()
    witnesses()
