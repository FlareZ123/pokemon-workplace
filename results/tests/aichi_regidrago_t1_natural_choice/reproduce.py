"""Independent small-deck oracle for the physical opening-seven plus first draw."""
from __future__ import annotations

from fractions import Fraction
from itertools import combinations
from pathlib import Path

from tools.aichi_regidrago_t1_natural_choice import build, exact_natural_choice


def direct(n: int, r: int, b: int, d: int, g: int, f: int) -> tuple[Fraction, ...]:
    cards = ["R"] * r + ["B"] * b + ["D"] * d + ["G"] * g + ["F"] * f
    cards += ["X"] * (n - len(cards))
    counts = [0, 0, 0, 0]
    denominator = 0
    for indices in combinations(range(n), 3):
        opener = [cards[i] for i in indices]
        if "R" not in opener and "B" not in opener:
            continue
        for last in range(n):
            if last in indices:
                continue
            hand = set(opener + [cards[last]])
            grass = "R" in hand and "D" in hand and "G" in hand
            fire = "R" in hand and "D" in hand and "F" in hand
            denominator += 1
            for i, yes in enumerate((grass or fire, grass, fire, grass and fire)):
                counts[i] += int(yes)
    return tuple(Fraction(x, denominator) for x in counts)


def main() -> None:
    checked = 0
    for n in range(4, 10):
        for r in range(1, min(3, n) + 1):
            for b in range(min(2, n-r) + 1):
                for d in range(min(2, n-r-b) + 1):
                    for g in range(min(2, n-r-b-d) + 1):
                        for f in range(min(2, n-r-b-d-g) + 1):
                            result = exact_natural_choice(n, r, b, d, g, f, opener=3)
                            expected = direct(n, r, b, d, g, f)
                            assert tuple(result[k] for k in ("either", "grass", "fire", "both")) == expected
                            checked += 1
    assert checked == 945
    source = build(Path("."))
    assert source["source_access_only"]["both"] == "20692516/1505320575"
    print("PASS: 945 independently enumerated opening/draw cases")
    print(source)


if __name__ == "__main__":
    main()
