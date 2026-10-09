"""Reproduce exact hidden-Prize Item-recycling witnesses."""
from fractions import Fraction

from tools.peonia_timing_policy import compare, optimal, play_peonia


def run():
    cases = (
        # Prize composition, expected optimum; deck is a noninteractive filler tail.
        ("TFFFF", Fraction(4, 5)),
        ("TAFFF", Fraction(19, 20)),
        ("TASFF", Fraction(1)),
        ("TFFFFF", Fraction(2, 3)),
        ("TAFFFF", Fraction(23, 30)),
        ("TASFFF", Fraction(19, 24)),
    )

    for cards, expected in cases:
        optimal.cache_clear()
        play_peonia.cache_clear()
        first, flexible = compare(cards, "F" * 46, arcs=1, shoes=1, filler_in_hand=1)
        assert first == expected, (cards, first, expected)
        assert flexible == expected, (cards, flexible, expected)
        print(f"{cards}: first={first} flexible={flexible} "
              f"P={float(expected):.9%}")

    for cards in ("TFFFF", "TAFFF", "TASFF"):
        optimal.cache_clear()
        play_peonia.cache_clear()
        first, flexible = compare(cards, "F" * 46, 1, 1, 0)
        assert (first, flexible) == (Fraction(4, 5),) * 2
        print(f"{cards} without spare filler: {first}")

    # Peonia remains usable even with an empty deck; Items do not.
    optimal.cache_clear()
    play_peonia.cache_clear()
    assert compare("TFFFF", "", 1, 1, 1) == (Fraction(3, 5),) * 2

    # Independent event derivations for the five-slot pure-filler and
    # single-Prized-Arc cases:
    assert Fraction(3, 5) + Fraction(2, 5) * Fraction(1, 2) == Fraction(4, 5)
    assert 1 - Fraction(1, 10) * Fraction(1, 2) == Fraction(19, 20)
    print("All six full-belief witnesses and independent simple-event checks passed.")


if __name__ == "__main__":
    run()
