"""SFT for exact Tag Call single-target Bellelba fallback ceiling."""
from __future__ import annotations

from fractions import Fraction
from itertools import combinations
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
from aichi_tagcall_bellelba_ceiling import exact_tagcall_bellelba_fallback


def labeled_oracle(n, opening, draws, prizes, basics, gnh, tagcall):
    pool = (["J"] + ["G"]*gnh + ["T"]*tagcall + ["B"] +
            ["S"]*(basics-1) + ["F"]*(n-basics-gnh-tagcall-1))
    assert len(pool) == n
    indexed = list(enumerate(pool))
    winning = denominator = 0
    for initial in combinations(indexed, opening):
        if not any(x[1] in ("J", "S") for x in initial):
            continue
        initial_ids = {x[0] for x in initial}
        after_initial = [x for x in indexed if x[0] not in initial_ids]
        for future in combinations(after_initial, draws):
            future_ids = {x[0] for x in future}
            exposed = initial + future
            remains = [x for x in after_initial if x[0] not in future_ids]
            for prize_cards in combinations(remains, prizes):
                denominator += 1
                g_held = sum(x[1] == "G" for x in exposed)
                g_prized = sum(x[1] == "G" for x in prize_cards)
                if ("J" in (x[1] for x in initial) and
                    g_held >= 1 and any(x[1] == "T" for x in exposed) and
                    all(x[1] != "B" for x in exposed+prize_cards) and
                    g_held + g_prized == gnh):
                    winning += 1
    return Fraction(winning, denominator)


def main():
    toy = exact_tagcall_bellelba_fallback(
        deck_size=11, opening=4, subsequent_random_draws=1,
        prizes=2, total_basics=3, gnh=2, tagcall=2,
    )
    actual = labeled_oracle(11, 4, 1, 2, 3, 2, 2)
    assert toy.accepted_probability == actual == Fraction(62, 1365)
    print("Small labeled opener/draw/Prize oracle:", actual, "PASS")

    result = exact_tagcall_bellelba_fallback()
    assert result.accepted_probability == Fraction(74221, 1341841280)
    assert (sum((p for _, p in result.by_known_gnh), Fraction(0))
            == result.accepted_probability)
    print("Aichi 60 cards, 14 total Basics including Jirachi")
    print("Accepted opener chance:", result.accepted_opening_probability)
    print("Fallback probability:", result.accepted_probability,
          f"{100*float(result.accepted_probability):.12f}%")
    for known, p in result.by_known_gnh:
        print("Visible G&H:", known, "event:", p,
              f"{100*float(p):.12f}%")
    print("ALL TESTS PASSED")


if __name__ == "__main__":
    main()
