"""SFT: exact hidden-Prize policy, checked with independently labeled cards."""
from __future__ import annotations

from fractions import Fraction
from itertools import combinations, product
from math import comb
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
from secret_box_gnh_tool_pipeline import KINDS, counts
from secret_box_k0_payment import evaluate_hidden_prize_payment


def labeled_policy(hand_counts, unknown_counts, *, prizes, keep_item=False, can_support=True):
    hand = tuple((k, i, "h") for k,n in zip(KINDS,hand_counts) for i in range(n))
    unknown = tuple((k, i, "u") for k,n in zip(KINDS,unknown_counts) for i in range(n))
    payments = tuple(combinations((c for c in hand if c[0] != "P"), 3))
    target = {"A", "B", "S", "E", "I"} if keep_item else {"A", "B", "S", "E"}

    def good(cards):
        return target.issubset({c[0] for c in cards})

    def search(deck, categories):
        opts = [(None,) + tuple(c for c in deck if c[0] in category) for category in categories]
        for picks in product(*opts):
            selected = tuple(c for c in picks if c is not None)
            if len(set(selected)) != len(selected):
                continue
            set_selected = set(selected)
            yield selected, tuple(c for c in deck if c not in set_selected)

    def after_payment(held, deck):
        for obtained, rest in search(deck, ({"I"}, {"A","B"}, {"G"}, {"S"})):
            after_box = held + obtained
            if good(after_box):
                return True
            if not can_support:
                continue
            for g in (c for c in after_box if c[0] == "G"):
                after_g = tuple(c for c in after_box if c != g)
                for got, _ in search(rest, ({"S"},)):
                    if good(after_g + got):
                        return True
                for payment in combinations((c for c in after_g if c[0] != "P"), 2):
                    paid = set(payment)
                    for got, _ in search(rest, ({"S"}, {"A","B"}, {"E"})):
                        if good(tuple(c for c in after_g if c not in paid) + got):
                            return True
        return False

    fixed_wins = [0] * len(payments)
    perfect = 0
    for hidden in combinations(unknown, prizes):
        hidden_set = set(hidden)
        deck = tuple(c for c in unknown if c not in hidden_set)
        outcomes = []
        for i, payment in enumerate(payments):
            cost = set(payment)
            succeeds = after_payment(tuple(c for c in hand if c not in cost), deck)
            fixed_wins[i] += succeeds
            outcomes.append(succeeds)
        perfect += any(outcomes)
    denominator = comb(len(unknown), prizes)
    return Fraction(perfect, denominator), Fraction(max(fixed_wins, default=0), denominator)


def main():
    # Box in an eight-card visible hand after the first natural draw.
    # Initially accepted opener contains at least one Basic inside the P group.
    hand = counts(D=2,A=1,G=1,S=1,P=2)
    unknown = counts(D=18,I=1,A=1,B=1,G=1,S=1,E=1,P=28)
    assert 1 + sum(hand) + sum(unknown) == 60
    result = evaluate_hidden_prize_payment(hand, unknown)
    assert result.clairvoyant_success == Fraction(32637, 44744)
    assert result.k0_success == Fraction(1925583, 2908360)
    assert result.information_gap == Fraction(97911, 1454180)
    assert result.prize_worlds == 64
    assert len(result.best_paid_hands) == 3
    print("60-card exact hidden Prize witness")
    print("  clairvoyant:", result.clairvoyant_success, float(result.clairvoyant_success))
    print("  nonanticipating:", result.k0_success, float(result.k0_success))
    print("  gap:", result.information_gap, float(result.information_gap))
    print("  best post-payment holdings:", result.best_paid_hands)

    checked = 0
    for i, s, spare_g in product((0,1), (0,1,2), (0,1)):
        h = counts(D=2,A=1,G=1,S=1,P=1)
        u = counts(D=2,I=i,A=1,B=1,G=spare_g,S=s,E=1,P=2)
        for retain_item, supporter in product((False,True), repeat=2):
            actual = evaluate_hidden_prize_payment(h,u,prize_count=2,
                    retain_item=retain_item,supporter_available=supporter)
            brute = labeled_policy(h,u,prizes=2,keep_item=retain_item,can_support=supporter)
            assert (actual.clairvoyant_success, actual.k0_success) == brute, (
                i,s,spare_g,retain_item,supporter,actual,brute)
            assert actual.clairvoyant_success >= actual.k0_success
            checked += 1
    assert checked == 48
    print("independent labeled-card Prize-policy oracle:",checked,"PASS")
    print("ALL TESTS PASSED")


if __name__ == "__main__":
    main()
