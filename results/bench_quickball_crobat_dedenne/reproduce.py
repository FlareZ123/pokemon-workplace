"""Physical hand, Quick Ball payment/search, shuffle, and draw comparison."""
from __future__ import annotations

from collections import Counter
from fractions import Fraction
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from bench_quickball_crobat_dedenne import analyze  # noqa: E402


def replay(*, hand_size: int, deck: list[str], k_in_hand: bool,
           qb_staged: bool, prize_known: bool, prior_knowledge: bool = False,
           shuffled_k_rank: int = -1
           ) -> tuple[bool, int, int, int]:
    """Independent literal-card replay (K, QB, D, F, C, inert filler)."""
    hand = ["QB", "D", "F"] + (["K"] if k_in_hand else [])
    hand += [f"h{i}" for i in range(hand_size - len(hand))]
    bench: list[str] = []
    discarded: list[str] = []
    ball_uses = 0
    dede_uses = 0
    live = list(deck)
    initial_cards = Counter(hand + live)

    def finish() -> tuple[bool, int, int, int]:
        assert Counter(hand + live + bench + discarded) == initial_cards
        return "K" in hand, len(bench), ball_uses, dede_uses

    if "K" in hand:
        return finish()
    if qb_staged:
        if prior_knowledge and "K" not in live:
            return finish()
        hand.remove("QB")
        discarded.append("QB")
        hand.remove("F")
        discarded.append("F")
        live.remove("C")
        hand.append("C")
        ball_uses += 1
        if "K" in live:
            assert shuffled_k_rank >= 0
            live.remove("K")
            live.insert(shuffled_k_rank, "K")
        if prize_known and "K" not in live:
            return finish()
        hand.remove("C")
        bench.append("C")
        width = max(0, 6 - len(hand))
        hand.extend(live[:width])
        del live[:width]

    if "K" not in hand:
        hand.remove("D")
        bench.append("D")
        dede_uses += 1
        discarded.extend(hand)
        hand.clear()
        hand.extend(live[:6])
        del live[:6]
    return finish()


def physical_oracle(*, hand_size: int, prizes: int = 6,
                    earlier_draws: int = 1, others_in_deck: int = 45,
                    prize_known: bool = False, prior_knowledge: bool = False):
    n = others_in_deck
    N = prizes + earlier_draws + n
    inert = [f"x{i}" for i in range(n+1)]
    known_live_c = ["C", *inert[1:]]
    early = (True, 0, 0, 0)
    prize_d = replay(hand_size=hand_size, deck=known_live_c,
                     k_in_hand=False, qb_staged=False,
                     prize_known=False)
    prize_s = replay(hand_size=hand_size, deck=known_live_c,
                     k_in_hand=False, qb_staged=True,
                     prize_known=prize_known,
                     prior_knowledge=prior_knowledge)

    baseline = []
    staged = []
    # Conditional on K being among live cards, its original draw rank is
    # uniform across the n+1-card deck. After QB removes C and shuffles,
    # the new rank is independently uniform across the n-card deck.
    for original_rank in range(n + 1):
        live = list(inert)
        live[original_rank] = "K"
        c_rank = (original_rank + 1) % (n + 1)
        live[c_rank] = "C"
        for post_shuffle_rank in range(n):
            baseline.append(replay(hand_size=hand_size, deck=live,
                                   k_in_hand=False, qb_staged=False,
                                   prize_known=False))
            staged.append(replay(hand_size=hand_size, deck=live,
                                 k_in_hand=False, qb_staged=True,
                                 prize_known=prize_known,
                                 prior_knowledge=prior_knowledge,
                                 shuffled_k_rank=post_shuffle_rank))

    def average(index: int, which: str) -> Fraction:
        if which == "d":
            live_avg = Fraction(sum(x[index] for x in baseline), len(baseline))
            return (Fraction(earlier_draws * early[index] + prizes * prize_d[index], N)
                    + Fraction(n, N) * live_avg)
        live_avg = Fraction(sum(x[index] for x in staged), len(staged))
        return (Fraction(earlier_draws * early[index] + prizes * prize_s[index], N)
                + Fraction(n, N) * live_avg)

    return (average(0, "d"), average(0, "s"), average(1, "d"),
            average(1, "s"), average(2, "s"), average(3, "s"))


def validate() -> None:
    for n, prizes in ((8, 2), (11, 2), (45, 6)):
        for h in (4, 5, 6, 7, 8):
            if n < max(0, 8-h) + 6:
                continue
            formula = analyze(hand_size=h, natural_draws=1,
                              prize_count=prizes, other_live_cards=n)
            for known, prior in ((False, False), (True, False), (True, True)):
                result = physical_oracle(hand_size=h, prizes=prizes,
                                         earlier_draws=1,
                                         others_in_deck=n, prize_known=known,
                                         prior_knowledge=prior)
                assert result[0] == formula.dedenne_success
                assert result[1] == formula.qb_staged_success
                assert result[2] == formula.dedenne_bench
                assert result[3] == (formula.qb_staged_k1_bench if known
                                     else formula.qb_staged_k0_bench)
                assert result[4] == (formula.qb_uses_prior_k1 if prior
                                     else formula.qb_uses)
                if known:
                    assert result[5] == formula.qb_staged_k1_dedenne
    x = analyze(hand_size=5)
    assert x.dedenne_success == Fraction(79, 598)
    assert x.qb_staged_success == Fraction(5, 26)
    assert x.access_gain == Fraction(18, 299)
    assert x.qb_uses_prior_k1 == Fraction(45, 52)
    assert x.qb_uses - x.qb_uses_prior_k1 == Fraction(6, 52)
    assert x.qb_staged_k0_bench - x.dedenne_bench == Fraction(12, 13)
    assert x.qb_staged_k1_bench - x.dedenne_bench == Fraction(9, 13)
    print("Physical paid Quick Ball, searched Crobat, shuffle and Dedenne replay matches exact model.")
    print("h | Crobat draw | Dedenne only | paid staged | gain | K1 extra Bench")
    for h in (4, 5, 6, 7, 8):
        x = analyze(hand_size=h)
        print(f"{h} | {x.crobat_draw} | {float(x.dedenne_success):.6%} | "
              f"{float(x.qb_staged_success):.6%} | {float(x.access_gain):.6%} | "
              f"{float(x.qb_staged_k1_bench-x.dedenne_bench):.6f}")


if __name__ == "__main__":
    validate()
