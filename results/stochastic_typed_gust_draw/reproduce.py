"""Validate exact draw dilution of Boss+Counter vs Boss+Serena tactical gaps.

Run: python -m results.stochastic_typed_gust_draw.reproduce
"""
from fractions import Fraction

from tools.stochastic_gust_draw import expected_attacks as unrestricted_expected
from tools.stochastic_typed_gust_draw import after_draw, expected_attacks


def from_hidden(n, active, bench, source):
    return expected_attacks(active, bench, 0, 0, 1, 1, n - 2, 6, 4, source)


def run():
    cases = 0
    for n in (6, 8, 10, 12, 20):
        # Board A: two three-Prize non-V Bench targets, one-Prize Active.
        # Counter must be drawn first and Boss second to win in two attacks.
        counter_a = from_hidden(n, "N1", ("N3", "N3"), "counter")
        serena_a = from_hidden(n, "N1", ("N3", "N3"), "serena")
        second_boss_a = from_hidden(n, "N1", ("N3", "N3"), "boss")
        assert counter_a == 3 - Fraction(1, n * (n - 1))
        assert serena_a == 3
        assert second_boss_a == 3 - Fraction(2, n * (n - 1))
        cases += 3

        # Board B: natural initial two-Prize KO, later two typed gusts.
        # Serena helps if both special cards occur in first three draws.
        counter_b = from_hidden(n, "N2", ("N1", "N2", "V2"), "counter")
        serena_b = from_hidden(n, "N2", ("N1", "N2", "V2"), "serena")
        assert counter_b == 4
        assert serena_b == 4 - Fraction(6, n * (n - 1))
        cases += 2

    # Cross-check unrestricted source type against the prior independent
    # numeric-only stochastic gust model on two structurally different boards.
    for active, bench in ((1, (1, 3, 3)), (2, (1, 2, 2))):
        n = 10
        typed = expected_attacks(
            "N" + str(active),
            tuple("N" + str(v) for v in bench),
            0, 0, 1, 1, n - 2, 6, 4, "boss"
        )
        original = unrestricted_expected(active, bench, 0, 2, n - 2, 6)
        assert typed == original, (typed, original)
        cases += 1

    # Both gusts already in hand: no access uncertainty, recovering the
    # deterministic inventory result on each reciprocal witness.
    assert after_draw(
        "N1", ("N3", "N3"), 1, 1, 0, 0, 8, 6, 4, "counter"
    ) == 2
    assert after_draw(
        "N1", ("N3", "N3"), 1, 1, 0, 0, 8, 6, 4, "serena"
    ) == 3
    assert after_draw(
        "N2", ("N1", "N2", "V2"), 1, 1, 0, 0, 8, 6, 4, "counter"
    ) == 4
    assert after_draw(
        "N2", ("N1", "N2", "V2"), 1, 1, 0, 0, 8, 6, 4, "serena"
    ) == 3
    cases += 4

    for n in (6, 10, 20):
        print(f"n={n} A(Boss+Counter)={from_hidden(n, 'N1', ('N3','N3'), 'counter')} "
              f"A(Boss+Serena)={from_hidden(n, 'N1', ('N3','N3'), 'serena')} "
              f"B(Boss+Counter)={from_hidden(n, 'N2', ('N1','N2','V2'), 'counter')} "
              f"B(Boss+Serena)={from_hidden(n, 'N2', ('N1','N2','V2'), 'serena')}")
    print(f"PASS: {cases} exact identity and cross-model checks")


if __name__ == "__main__":
    run()
