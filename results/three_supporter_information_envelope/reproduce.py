"""Exact generic envelope and physical small-deck Prize/redraw regression."""
from __future__ import annotations

from fractions import Fraction
from itertools import combinations, product
from math import comb
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from binary_choice_information_gap import binary_choice_information_gap
from multi_action_information_envelope import action_information_envelope
from prize_three_supporter_choice import (
    paid_search_three_supporter_choice, three_supporter_choice,
)


def independent_draw_hit(cards: tuple[int, ...], outs: set[int], d: int) -> Fraction:
    samples = combinations(cards, min(d, len(cards)))
    hits = sum(bool(set(sample) & outs) for sample in samples)
    return Fraction(hits, comb(len(cards), min(d, len(cards))))


def brute_three_supporters(D: int, P: int, U: int, H: int, R: int,
                           d: int, Q: int):
    unknown = tuple(range(D+P))
    outs = set(unknown[:U])
    hand = tuple(range(D+P, D+P+H))
    hand_outs = set(hand[:R])
    totals = [Fraction(), Fraction(), Fraction()]
    best = Fraction()
    cnt = 0
    for prizes in combinations(unknown, P):
        deck = tuple(i for i in unknown if i not in prizes)
        k_outs = outs.intersection(deck)
        if not H+Q:
            iono = Fraction(0)
        elif d <= D:
            iono = independent_draw_hit(deck, k_outs, d)
        elif k_outs:
            iono = Fraction(1)
        else:
            iono = independent_draw_hit(hand, hand_outs, d-D)
        n = independent_draw_hit(deck+hand, k_outs|hand_outs, d)
        research = independent_draw_hit(deck, k_outs, 7)
        payoffs = (iono, n, research)
        for i, a in enumerate(payoffs):
            totals[i] += a
        best += max(payoffs)
        cnt += 1
    return tuple(x/cnt for x in totals), best/cnt


def test_envelopes():
    checks = 0
    vals = (Fraction(-1), Fraction(0), Fraction(1))
    for weight_num in range(5):
        w = Fraction(weight_num, 4)
        for a in product(vals, repeat=6):
            rows = ((w, dict(zip(("a", "b", "c"), a[:3]))),
                    (1-w, dict(zip(("a", "b", "c"), a[3:]))))
            model = action_information_envelope(rows)
            means = {name: sum((mass * state[name] for mass, state in rows), Fraction())
                     for name in ("a", "b", "c")}
            fixed = max(means.values())
            informed = sum((mass*max(payoff.values()) for mass,payoff in rows), Fraction())
            assert (model.best_fixed_value, model.observed_value,
                    model.information_value) == (fixed, informed, informed-fixed)
            assert model.pairwise_lower_bound <= model.information_value <= model.sum_upper_bound
            binary = action_information_envelope(
                (mass, {"a": p["a"], "b": p["b"]}) for mass, p in rows
            )
            old = binary_choice_information_gap(
                (mass, p["a"], p["b"]) for mass, p in rows
            )
            assert binary.information_value == old.information_gain
            assert binary.pairwise_lower_bound == binary.sum_upper_bound
            checks += 1
    for bad in ([], [(Fraction(1), {})], [(Fraction(1,2), {"a":1})],
                [(Fraction(1), {"a":1}), (Fraction(0), {"b":2})]):
        try:
            action_information_envelope(bad)
        except ValueError:
            pass
        else:
            raise AssertionError(f"accepted invalid distribution: {bad}")
    return checks


def test_card_small():
    checks = 0
    for D in range(1,5):
        for P in range(1,4):
            for U in range(D+P+1):
                for H in range(4):
                    for R in range(H+1):
                        for d in range(1,P+1):
                            for Q in (0,1):
                                if not H+Q:
                                    continue
                                r = three_supporter_choice(
                                    deck_size=D, prizes_hidden=P, unknown_outs=U,
                                    hand_size=H, hand_outs=R, prize_draw_count=d,
                                    opponent_hand_size=Q)
                                fixed, observed = brute_three_supporters(D,P,U,H,R,d,Q)
                                assert tuple(x[1] for x in r.envelope.fixed_payoffs)==fixed, (D,P,U,H,R,d,Q)
                                assert r.envelope.observed_value==observed,(D,P,U,H,R,d,Q)
                                checks += 1
    return checks


def pct(x: Fraction) -> str:
    return f"{float(100*x):.6f}%"


def witness():
    p = dict(deck_size=46, prizes_hidden=6, hand_size=5, hand_outs=1,
             prize_draw_count=6, opponent_hand_size=2)
    rich = three_supporter_choice(**p, unknown_outs=10)
    assert round(float(rich.envelope.best_fixed_value)*100,6)==79.834498
    assert rich.envelope.information_value == 0
    pair = binary_choice_information_gap((prior,i,n) for _,prior,i,n,_ in rich.rows)
    assert round(float(pair.information_gain)*100,6)==0.169011
    print("U10 H5 R1: binary Iono/N K1 gain",pct(pair.information_gain),
          "three Supporters K1 gain",pct(rich.envelope.information_value),
          "best fixed Professor Research",pct(rich.envelope.best_fixed_value))

    low = three_supporter_choice(**{**p,"hand_size":8,"unknown_outs":3})
    assert round(float(low.envelope.information_value)*100,6)==0.719670
    pair_low = binary_choice_information_gap((prior,i,n) for _,prior,i,n,_ in low.rows)
    assert pair_low.information_gain == 0
    assert low.envelope.optimal_after_observation==("N","N","N","Professor's Research")
    print("U3 H8 R1: binary K1 gain",pct(pair_low.information_gain),
          "three Supporters K1 gain",pct(low.envelope.information_value),
          "K0",pct(low.envelope.best_fixed_value),
          "K1",pct(low.envelope.observed_value))

    kwargs={**p,"hand_size":8,"unknown_outs":3}
    base, paid, mat, information, total = paid_search_three_supporter_choice(
        **kwargs, payment_count=2, payment_outs=0)
    assert base.envelope.information_value > paid.envelope.information_value > 0
    assert round(float(mat)*100,6)==0.987185
    assert round(float(information)*100,6)==0.050017
    assert round(float(total)*100,6)==1.037202
    print("U3 H8 R1 non-out payment2: material",pct(mat),
          "post-payment K1",pct(information),"net",pct(total))
    _, useful_paid, mat2, info2, total2 = paid_search_three_supporter_choice(
        **kwargs, payment_count=2, payment_outs=1)
    assert mat2==info2==total2==0
    assert useful_paid.envelope.information_value==0


if __name__ == "__main__":
    print("3-action exact/2-action compatibility cases:",test_envelopes())
    print("Independent physical Prize/deck/hand enumeration cases:",test_card_small())
    witness()
