"""Exhaustive physical-card and coin oracle for triple Bench triggers."""
from itertools import combinations, product
from fractions import Fraction
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
from bench_double_trigger_access import analyze
from bench_multi_trigger_access import analyze_many

def main():
    cards = "ABCOHHDRRFFF"
    successes = {q: [0, 0, 0, 0] for q in (1, 2, 3)}
    total = 0
    for op in combinations(range(12), 5):
        if not any(cards[i] in "ABCO" for i in op):
            continue
        active = next(i for i in op if cards[i] == "O") if 3 in op else next(i for i in op if cards[i] in "ABC")
        rest = set(range(12)) - set(op)
        for prize in combinations(rest, 1):
            pool = rest - set(prize)
            for drawn in combinations(pool, 2):
                hand = set(op) | set(drawn)
                real = hand - {active}
                deck = pool - set(drawn)
                hs = [cards[i] for i in hand]
                rs = [cards[i] for i in real]
                h, d, r = hs.count("H"), hs.count("D"), hs.count("R")
                reachable = [any(cards[j] == name for j in deck) for name in "ABC"]
                naive = all(name in hs or (h+d > 0 and reachable[i]) for i, name in enumerate("ABC"))
                role = all(name in rs or (h+d > 0 and reachable[i]) for i, name in enumerate("ABC"))
                typed = sum(name not in rs for name in "ABC") <= h and all(name in rs or reachable[i] for i, name in enumerate("ABC"))
                for coins in product((0, 1), repeat=2):
                    total += 1
                    heads = sum(coins[:r])
                    for q in (1, 2, 3):
                        need = 3 - q
                        for i, ok in enumerate((naive and r>=need, role and r>=need, typed and r>=need, typed and heads>=need)):
                            successes[q][i] += ok
    for q in (1, 2, 3):
        x = analyze_many(targets=3, deck_size=12, opening_size=5, prize_count=1, draws=2, other_basics=1, hand_connectors=2, direct_connectors=1, coin_pickups=2, bench_slack=q)
        actual = (x.nominal, x.role_aware, x.typed_one_use, x.stochastic_exact)
        expected = tuple(Fraction(n, total) for n in successes[q])
        assert actual == expected, (q, actual, expected)
        print("q", q, [str(v) for v in actual])
    for c in (dict(draws=1, coin_pickups=2), dict(draws=4, coin_pickups=4), dict(draws=4, coin_pickups=0, bench_slack=2)):
        assert analyze_many(targets=2, **c) == analyze(**c)
    print("PASS", total, "labeled and coin paths")
    for q in (1, 2, 3):
        x = analyze_many(bench_slack=q)
        print(q, *(f"{100*float(v):.6f}%" for v in (x.nominal, x.role_aware, x.typed_one_use, x.stochastic_exact)))

if __name__ == "__main__":
    main()
