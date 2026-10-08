"""Independent physical-card oracle and analytical marginals for Tool fan-out."""
from __future__ import annotations

from itertools import combinations, product
from math import comb
from pathlib import Path
from collections import Counter
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
from secret_box_gnh_tool_pipeline import KINDS, counts, feasible, minimum_fodder


def labeled_oracle(hand_counts, deck_counts, *, require_item=False, supporter_available=True):
    """Independent literal identity enumerator, with distinct labels for copies."""
    hand = tuple((k, j, "h") for k, c in zip(KINDS, hand_counts) for j in range(c))
    deck = tuple((k, j, "d") for k, c in zip(KINDS, deck_counts) for j in range(c))
    needed = set(("A", "B", "S", "E", "I") if require_item else ("A", "B", "S", "E"))

    def success(cards):
        return needed <= {c[0] for c in cards}

    def searches(pool, categories):
        options = [(None,) + tuple(c for c in pool if c[0] in category) for category in categories]
        for picks in product(*options):
            selected = tuple(c for c in picks if c is not None)
            if len(set(selected)) != len(selected):
                continue
            chosen = set(selected)
            yield selected, tuple(c for c in pool if c not in chosen)

    for payment in combinations((c for c in hand if c[0] != "P"), 3):
        spent = set(payment)
        held = tuple(c for c in hand if c not in spent)
        for gained, remaining in searches(deck, ({"I"}, {"A", "B"}, {"G"}, {"S"})):
            after_box = held + gained
            if success(after_box):
                return True
            if not supporter_available:
                continue
            for supporter in (c for c in after_box if c[0] == "G"):
                without_supporter = tuple(c for c in after_box if c != supporter)
                for new, _ in searches(remaining, ({"S"},)):
                    if success(without_supporter + new):
                        return True
                for payment2 in combinations((c for c in without_supporter if c[0] != "P"), 2):
                    paid = set(payment2)
                    held2 = tuple(c for c in without_supporter if c not in paid)
                    for new, _ in searches(remaining, ({"S"}, {"A", "B"}, {"E"})):
                        if success(held2 + new):
                            return True
    return False


def opening_disposable_gate(minimum, *, deck_size=60, starters=12, disposable=20, hand_size=7):
    """Exact P(D>=minimum | Box in seven-card hand and at least one Basic)."""
    others = deck_size - 1
    protected = others - starters - disposable
    choose = lambda n, k: comb(n, k) if 0 <= k <= n else 0
    draw = hand_size - 1
    denominator = choose(others, draw) - choose(others - starters, draw)
    numerator = sum(
        choose(starters, s) * choose(disposable, d) * choose(protected, draw - s - d)
        for s in range(1, draw + 1)
        for d in range(minimum, draw - s + 1)
    )
    return numerator / denominator


def main():
    expected = {
        (1, 1, False): 4,
        (1, 2, False): 3,
        (1, 1, True): 5,
        (1, 2, True): 4,
        (0, 1, False): 5,
        (0, 2, False): 4,
        (0, 2, True): None,
        (1, 0, False): None,
    }
    for (items, stadiums, retain_item), answer in expected.items():
        got = minimum_fodder(item_copies=items, stadium_copies=stadiums,
                             require_item=retain_item)
        assert got == answer, ((items, stadiums, retain_item), got, answer)
        print("minimum upfront D:", items, stadiums, retain_item, got)

    assert not feasible(counts(D=5, P=1), counts(I=1, A=1, B=1, G=1, S=2, E=1),
                        supporter_available=False)
    assert feasible(counts(D=2, G=1, P=1),
                    counts(I=1, A=1, B=1, G=1, S=2, E=1))
    assert not feasible(counts(D=2, G=1, P=1),
                        counts(I=1, A=1, B=1, G=0, S=2, E=1))
    print("supporter timing and conditional G&H reacquisition fixtures: PASS")

    checked = 0
    for d in range(1, 5):
        for item, stadium, gnh in product((0, 1), (0, 1, 2), (0, 1)):
            for g_in_hand, a_in_hand, a_in_deck in product((0, 1), repeat=3):
                hand = counts(D=d, G=g_in_hand, A=a_in_hand, P=1)
                deck = counts(I=item, A=a_in_deck, B=1, G=gnh, S=stadium, E=1)
                for keep_item in (False, True):
                    for can_support in (False, True):
                        predicted = feasible(hand, deck, require_item=keep_item,
                                             supporter_available=can_support)
                        actual = labeled_oracle(hand, deck, require_item=keep_item,
                                                 supporter_available=can_support)
                        assert predicted == actual, (hand, deck, keep_item, can_support, predicted, actual)
                        checked += 1
    assert checked == 1536
    print("independent labeled-card comparison:", checked, "PASS")

    want = (0.2668876579801323, 0.06047797165848468, 0.005420994658463613)
    for threshold, answer in zip((3, 4, 5), want):
        got = opening_disposable_gate(threshold)
        assert abs(got - answer) < 1e-12, (threshold, got, answer)
        print(f"conditional P(D>={threshold})={got:.12%}")
    print("ALL TESTS PASSED")


if __name__ == "__main__":
    main()
