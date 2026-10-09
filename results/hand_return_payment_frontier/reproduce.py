"""Exhaustive labeled regression for multi-out hand-return payment frontier."""
from __future__ import annotations

from fractions import Fraction
from itertools import combinations
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from hand_return_payment_frontier import shuffle_return_payment_delta, hit_probability


def brute(pool: tuple[str, ...], targets: frozenset[str], draws: int) -> Fraction:
    d = min(draws, len(pool))
    groups = list(combinations(pool, d))
    return Fraction(sum(any(x in targets for x in sample) for sample in groups), len(groups))


def exhaustive_check() -> int:
    count = 0
    for n in range(1, 5):
        for h in range(4):
            for k in range(n + 1):
                for r in range(h + 1):
                    deck = tuple(f"d{i}" for i in range(n))
                    hand = tuple(f"h{i}" for i in range(h))
                    targets = frozenset(deck[:k] + hand[:r])
                    for p in range(h + 1):
                        for pr in range(min(r, p) + 1):
                            if p - pr > h - r:
                                continue
                            payment = hand[:pr] + hand[r:r + (p - pr)]
                            remaining = deck + tuple(x for x in hand if x not in payment)
                            for d in range(n + h + 2):
                                b, a, delta = shuffle_return_payment_delta(
                                    deck_size=n, hand_size=h, deck_outs=k,
                                    hand_outs=r, draws=d, payment_count=p,
                                    payment_outs=pr)
                                eb = brute(deck + hand, targets, d)
                                ea = brute(remaining, targets, d)
                                assert (b, a, delta) == (eb, ea, ea - eb), (n, h, k, r, p, pr, d)
                                if pr == 0:
                                    assert delta >= 0
                                if pr == p:
                                    assert delta <= 0
                                count += 1
    return count


def main() -> None:
    cases = exhaustive_check()
    assert hit_probability(51, 4, 6) == Fraction(961, 2380)
    args = dict(deck_size=46, hand_size=5, deck_outs=7,
                hand_outs=1, draws=6, payment_count=2)
    prior, after0, delta0 = shuffle_return_payment_delta(**args, payment_outs=0)
    _, after1, delta1 = shuffle_return_payment_delta(**args, payment_outs=1)
    assert delta0 > 0 and delta1 < 0 and after0 > prior > after1
    assert round(100 * float(delta0), 6) == 1.697171
    assert round(100 * float(delta1), 6) == -3.661867
    for total_outs in range(1, 47):
        _, _, delta = shuffle_return_payment_delta(
            deck_size=46, hand_size=5, deck_outs=total_outs - 1,
            hand_outs=1, draws=6, payment_count=2, payment_outs=1)
        if total_outs <= 24:
            assert delta < 0, (total_outs, delta)
        if 25 <= total_outs <= 45:
            assert delta > 0, (total_outs, delta)
        if total_outs == 46:
            assert delta == 0
    print(f"Exhaustively checked {cases} small-state cases")
    print(f"Eight outs and two no-out payments: {100 * float(delta0):+.6f} percentage points")
    print(f"Eight outs and one-out payment: {100 * float(delta1):+.6f} percentage points")
    print("One-out payment sign boundary: 25 total outs for N=46 H=5 P=2 d=6")


if __name__ == "__main__":
    main()
