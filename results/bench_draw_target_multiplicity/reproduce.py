"""Independent labeled-card enumerator for the multicopy stopping theorem."""
from __future__ import annotations

from fractions import Fraction
from itertools import combinations
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from bench_draw_target_multiplicity import analyze  # noqa: E402


def physical_world(*, target_positions: set[int], hand_size: int,
                   natural_draws: int, prizes: int, deck_cards: int,
                   prize_known: bool) -> tuple[bool, bool, int, int]:
    """Play the two policies with physical cards and check real hand lists."""
    n = natural_draws + prizes + deck_cards
    cards = ["K" if i in target_positions else f"x{i}" for i in range(n)]
    earlier_hand = cards[:natural_draws]
    deck = cards[natural_draws + prizes:]
    assert len(deck) == deck_cards

    def run(staged: bool) -> tuple[bool, int]:
        hand = ["C", "D", *earlier_hand]
        hand.extend(f"h{i}" for i in range(hand_size - len(hand)))
        live = list(deck)
        bench: list[str] = []
        prize_slots = set(range(natural_draws, natural_draws + prizes))
        if "K" in hand or (prize_known and target_positions.issubset(prize_slots)):
            return "K" in hand, len(bench)
        if staged:
            hand.remove("C")
            bench.append("C")
            k = max(0, 6 - len(hand))
            hand.extend(live[:k])
            del live[:k]
        if "K" not in hand:
            hand.remove("D")
            bench.append("D")
            hand.clear()
            hand.extend(live[:6])
        return "K" in hand, len(bench)

    d_success, d_bench = run(False)
    s_success, s_bench = run(True)
    return d_success, s_success, d_bench, s_bench


def validate() -> None:
    for hand_size, deck_cards in ((5, 8), (6, 7), (7, 7)):
        natural_draws, prizes = 1, 2
        n = natural_draws + prizes + deck_cards
        for k in range(1, 5):
            model = analyze(copies=k, hand_size=hand_size, natural_draws=1,
                            prizes=2, deck_cards=deck_cards)
            for known in (False, True):
                values = [physical_world(target_positions=set(indices),
                                         hand_size=hand_size,
                                         natural_draws=natural_draws,
                                         prizes=prizes,
                                         deck_cards=deck_cards,
                                         prize_known=known)
                          for indices in combinations(range(n), k)]
                prob = tuple(Fraction(sum(row[i] for row in values), len(values))
                             for i in range(4))
                assert prob[:2] == (model.dedenne_success, model.staged_success)
                expected_bench = ((model.dedenne_bench_k1, model.staged_bench_k1)
                                  if known else
                                  (model.dedenne_bench_k0, model.staged_bench_k0))
                assert prob[2:] == expected_bench, (k, hand_size, known, prob)

    for k in range(1, 7):
        result = analyze(copies=k)
        assert result.dedenne_success <= result.staged_success
        assert result.extra_bench_k1 <= result.extra_bench_k0
    singleton = analyze(copies=1)
    assert singleton.dedenne_success == Fraction(7, 53)
    assert singleton.staged_success == Fraction(9, 53)
    assert singleton.extra_bench_k0 == Fraction(50, 53)
    assert singleton.extra_bench_k1 == Fraction(44, 53)
    print("Multicopy exact physical oracle passed for three draw widths, four multiplicities, and both knowledge states.")
    print("k | Dedenne | staged | gain | extra K0 Bench | all Prized")
    for k in range(1, 7):
        x = analyze(copies=k)
        print(f"{k} | {float(x.dedenne_success):.6%} | {float(x.staged_success):.6%} | "
              f"{float(x.extra_access):.6%} | {float(x.extra_bench_k0):.6f} | "
              f"{float(x.all_prized):.8%}")


if __name__ == "__main__":
    validate()
