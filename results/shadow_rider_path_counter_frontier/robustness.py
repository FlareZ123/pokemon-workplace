"""Exhaustive 15-way two-lock counter mixtures in four flexible deck slots.

Invoke python -m results.shadow_rider_path_counter_frontier.robustness
"""
from __future__ import annotations

from datetime import date
from fractions import Fraction
from pathlib import Path

from results.competitive_deck_baselines.shadow_rider_reproduce import PRINT_IDS
from results.shadow_rider_path_counter_frontier.reproduce import (
    IDS, counts, exact, variant,
)
from tools.deck_legality_proof import adjudicate_deck
from tools.deck_validator import DeckEntry

EXPECTED: dict[tuple[int, int], Fraction] = {
    (0, 0): Fraction(0),
    (1, 0): Fraction(44567700223329, 2257639345561600),
    (0, 1): Fraction(322511728541791, 17512056590028000),
    (2, 0): Fraction(28650171952739, 1150527743411200),
    (1, 1): Fraction(32802078670643, 1250861185002000),
    (0, 2): Fraction(672249515574867, 26812136893622080),
    (3, 0): Fraction(44567700223329, 2257639345561600),
    (2, 1): Fraction(358266483267023, 17512056590028000),
    (1, 2): Fraction(71296280958075, 3412453786460992),
    (0, 3): Fraction(3853081569076989, 190973999943588680),
    (4, 0): Fraction(18385984845499, 741662512281600),
    (3, 1): Fraction(10403699807629, 408614653767320),
    (2, 2): Fraction(1393169570653647, 53624273787244160),
    (1, 3): Fraction(10031601599252619, 381947999887177360),
    (0, 4): Fraction(745666483493, 29231388473952),
}


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    ids = {**PRINT_IDS, **IDS}
    assert len(EXPECTED) == 15
    for pair, expected in EXPECTED.items():
        c, f = pair
        deck = variant(c, f)
        proof = adjudicate_deck(
            [DeckEntry(ids[name], count) for name, count in deck.items()],
            root / "resources", as_of=date(2026, 10, 12))
        assert proof.construction.valid, (pair, proof.construction.issues)
        assert proof.disposition == "eligible_snapshot", (pair, proof.disposition)
        assert all(p.eligibility == "eligible" for p in proof.print_proofs)
        got = exact(counts(c, f))
        assert got == expected, (pair, got, expected)
        print(f"C={c} F={f} Path access={float(got):.9%}")
    by_total = {}
    for total in range(5):
        options = [(v, pair) for pair, v in EXPECTED.items() if sum(pair) == total]
        best, pair = max(options, key=lambda value_pair: value_pair[0])
        by_total[total] = (best, pair)
        print(f"Best with exactly {total} swaps: C={pair[0]}, F={pair[1]} "
              f"success={float(best):.9%}")
    assert [by_total[i][1] for i in range(5)] == [
        (0, 0), (1, 0), (1, 1), (1, 2), (1, 3)
    ]
    assert by_total[3][0] < by_total[2][0]
    assert by_total[4][0] > by_total[2][0]
    increment = by_total[4][0] - by_total[2][0]
    assert 0 < increment < Fraction(1, 10000)
    print("PASS: 15 conservative legal complete decks and nonmonotone frontier")


if __name__ == "__main__":
    main()
