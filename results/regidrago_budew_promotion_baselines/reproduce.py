"""Exact inventory-only baselines for Budew history-cover access.

No game turns, playable discards, search sequencing or switching legality
are simulated here. Counts are authoritative only for the named nine
published Aichi decklists, not for Expanded Regidrago in general.
"""

from __future__ import annotations

from fractions import Fraction
from itertools import combinations
from math import comb
import json
from pathlib import Path

FIXTURE = Path(__file__).with_name("aichi9_counts.json")


def choose(n: int, k: int) -> int:
    return comb(n, k) if 0 <= k <= n else 0


def rates(
    *,
    deck_size: int,
    budew: int,
    search: int,
    switches: int,
    seen: int,
    prizes: int,
) -> tuple[Fraction, Fraction]:
    """Probability of two abstract inventory events.

    Draw `seen` uniformly from the entire deck, then put `prizes`
    uniformly into a disjoint zone from the remainder.

    Direct: seen has a Budew and a switch card.
    Search-assisted: seen has a switch and either a Budew, or a Basic
    Grass search card with >=1 Budew available outside Prize cards.
    No claim is made that these cards are legally playable together.
    """
    assert min(deck_size, budew, search, switches, seen, prizes) >= 0
    assert budew + search + switches <= deck_size
    assert seen + prizes <= deck_size
    other = deck_size - budew - search - switches
    total = choose(deck_size, seen)
    direct = Fraction()
    assisted = Fraction()
    for b in range(budew + 1):
        for q in range(search + 1):
            for s in range(switches + 1):
                o = seen - b - q - s
                ways = (choose(budew, b) * choose(search, q)
                        * choose(switches, s) * choose(other, o))
                if not ways or not s:
                    continue
                weight = Fraction(ways, total)
                if b:
                    direct += weight
                    assisted += weight
                elif q:
                    remaining = deck_size - seen
                    all_prized = Fraction(
                        choose(remaining - budew, prizes - budew),
                        choose(remaining, prizes),
                    )
                    assisted += weight * (1 - all_prized)
    return direct, assisted


def joint_prize_collapse(*, budew: int, heavy_ball: int) -> Fraction:
    """All Budew AND all Hisuian Heavy Ball in six initial Prizes."""
    return Fraction(
        choose(60 - budew - heavy_ball, 6 - budew - heavy_ball),
        choose(60, 6),
    )


def brute_small() -> tuple[Fraction, Fraction]:
    """Independent enumeration over every ordered seen/Prize partition."""
    cards = ("B", "B", "Q", "Q", "S", "S", "O", "O", "O", "O")
    direct = assisted = success = total = 0
    for seen in combinations(range(10), 3):
        remain = tuple(i for i in range(10) if i not in seen)
        seen_types = [cards[i] for i in seen]
        for prize in combinations(remain, 2):
            total += 1
            sw = "S" in seen_types
            got_b = "B" in seen_types
            direct += int(sw and got_b)
            assisted += int(
                sw and (
                    got_b or ("Q" in seen_types and
                              any(cards[i] == "B" for i in remain if i not in prize))
                )
            )
    expected = rates(deck_size=10, budew=2, search=2,
                     switches=2, seen=3, prizes=2)
    actual = Fraction(direct, total), Fraction(assisted, total)
    assert expected == actual, (expected, actual)
    assert direct <= assisted <= total
    return actual


def main() -> None:
    assert brute_small()
    data = json.loads(FIXTURE.read_text(encoding="utf-8"))
    rows = data["decklists"]
    assert len(rows) == 9
    assert [r["place"] for r in rows] == [10, 12, 13, 14, 18, 20, 21, 27, 32]
    assert sum(r["budew"] for r in rows) == 12
    assert sum(r["guzma"] for r in rows) == 19
    assert sum(r["prime_catcher"] for r in rows) == 3
    assert sum(r["hisuian_heavy_ball"] for r in rows) == 10
    assert all(r["latias_ex"] == 1 for r in rows)
    assert all(r["guzma"] >= 2 and r["budew"] >= 1 for r in rows)

    for seen in (7, 12, 18):
        current = []
        for row in rows:
            search = sum(row[k] for k in ("quick_ball", "nest_ball", "net_ball"))
            switches = row["guzma"] + row["prime_catcher"]
            d, a = rates(deck_size=60, budew=row["budew"],
                         search=search, switches=switches, seen=seen, prizes=6)
            assert 0 <= d <= a <= 1
            current.append((d, a))
            print(f"seen={seen} place={row['place']} "
                  f"direct={100 * float(d):.6f}% "
                  f"search-assisted={100 * float(a):.6f}%")
        averages = [sum(r[k] for r in current) / len(current) for k in (0, 1)]
        print(f"seen={seen} nine-list equal-weight mean: "
              f"direct={100 * float(averages[0]):.6f}% "
              f"search-assisted={100 * float(averages[1]):.6f}%")

    for b, target in ((1, Fraction(1, 10)), (2, Fraction(1, 118))):
        assert Fraction(choose(60 - b, 6 - b), choose(60, 6)) == target
    collapses = [
        joint_prize_collapse(
            budew=row["budew"],
            heavy_ball=row["hisuian_heavy_ball"],
        )
        for row in rows
    ]
    assert sum(c == Fraction(1, 118) for c in collapses) == 5
    assert sum(c == Fraction(1, 1711) for c in collapses) == 4
    for row, chance in zip(rows, collapses):
        print(f"place={row['place']} all Budew+Heavy Ball prized = "
              f"{100 * float(chance):.6f}%")
    print(f"equal-weight nine-list joint Prize collapse mean: "
          f"{100 * float(sum(collapses) / len(collapses)):.6f}%")
    print("Exact small-deck oracle and Prize collision checks passed.")


if __name__ == "__main__":
    main()
