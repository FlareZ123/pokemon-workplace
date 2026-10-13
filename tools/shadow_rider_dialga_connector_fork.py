"""Exact first-draw Dialga discard/search connector states for Aichi Shadow Rider.

Standard-library exact counts. This is an opening availability calculation,
not a simulator, legal-action executor, or match win-rate estimate.
"""

from __future__ import annotations

from collections import Counter
from fractions import Fraction
from itertools import combinations, product
from math import comb


def choose(n: int, k: int) -> int:
    return comb(n, k) if 0 <= k <= n else 0


def grouped_counts(b: int, v: int, t: int, g: int, f: int,
                   hand: int = 7, prizes: int = 6,
                   needed_v: int = 2) -> tuple[dict[str, int], int]:
    """Count distinct opening hands, first draws and Prize subsets.

    There is also one each of D(ialga), M(imikyu) and R(adiant Eternatus).
    M and R must remain in deck after the draw; D must be in hand, and
    another non-Radiant opening Basic B must be able to start Active.
    """
    caps = (b, v, t, g, f)
    names = ("B", "V", "T", "G", "F")
    n = sum(caps) + 3
    denominator = choose(n, hand) * (n - hand) * choose(n - hand - 1, prizes)
    outcome: Counter[str] = Counter()
    for d_in_hand in (True, False):
        other_hand_size = hand - int(d_in_hand)
        choices = [range(min(cap, other_hand_size) + 1) for cap in caps]
        for h in product(*choices):
            if sum(h) != other_hand_size or h[0] < 1:
                continue
            hands = 1
            for cap, count in zip(caps, h):
                hands *= choose(cap, count)
            rem = tuple(cap - count for cap, count in zip(caps, h))
            x_options = names if d_in_hand else ("D",)
            for x_name in x_options:
                x_ind = names.index(x_name) if x_name in names else -1
                x_ways = rem[x_ind] if x_ind >= 0 else 1
                if x_ways == 0:
                    continue
                after_draw = list(rem)
                if x_ind >= 0:
                    after_draw[x_ind] -= 1
                held_t = h[2] + int(x_name == "T")
                held_g = h[3] + int(x_name == "G")
                if held_t == 0:
                    continue
                vmax = after_draw[1]
                non_vmax = sum(after_draw) - vmax
                prize_ways = sum(
                    choose(vmax, pv) * choose(non_vmax, prizes-pv)
                    for pv in range(max(0, vmax - needed_v + 1))
                )
                ways = hands * x_ways * prize_ways
                if not ways:
                    continue
                outcome["fork"] += ways
                outcome["dialga_initial" if d_in_hand else "dialga_draw"] += ways
                outcome["single_treasure" if held_t == 1 else "multiple_treasure"] += ways
                outcome["fog_available" if held_g else "no_fog"] += ways
                if held_t == 1 and not held_g:
                    outcome["single_treasure_no_fog"] += ways
                if held_t == 1 and held_g:
                    outcome["single_treasure_with_fog"] += ways
    return dict(outcome), denominator


def brute_counts(b: int, v: int, t: int, g: int, f: int,
                 hand: int, prizes: int,
                 needed_v: int) -> tuple[dict[str, int], int]:
    """Independent card-labeled enumeration across physical zones."""
    cards = (
        ["D", "M", "R"]
        + ["B" + str(i) for i in range(b)]
        + ["V" + str(i) for i in range(v)]
        + ["T" + str(i) for i in range(t)]
        + ["G" + str(i) for i in range(g)]
        + ["F" + str(i) for i in range(f)]
    )
    outcome: Counter[str] = Counter()
    denominator = 0
    for h in combinations(cards, hand):
        hs = set(h)
        rest = [c for c in cards if c not in hs]
        for draw in rest:
            acquired = hs | {draw}
            remaining = [c for c in rest if c != draw]
            for p in combinations(remaining, prizes):
                denominator += 1
                deck = set(remaining) - set(p)
                if not {"R", "M"} <= deck or "D" not in acquired:
                    continue
                if not any(c.startswith("B") for c in h):
                    continue
                held_t = sum(c.startswith("T") for c in acquired)
                held_g = sum(c.startswith("G") for c in acquired)
                if held_t == 0 or sum(c.startswith("V") for c in deck) < needed_v:
                    continue
                outcome["fork"] += 1
                outcome["dialga_initial" if "D" in hs else "dialga_draw"] += 1
                outcome["single_treasure" if held_t == 1 else "multiple_treasure"] += 1
                outcome["fog_available" if held_g else "no_fog"] += 1
                if held_t == 1 and not held_g:
                    outcome["single_treasure_no_fog"] += 1
                if held_t == 1 and held_g:
                    outcome["single_treasure_with_fog"] += 1
    return dict(outcome), denominator


def validate_toy_worlds() -> None:
    toys = (
        (1, 1, 2, 1, 2, 3, 2, 1),
        (2, 2, 2, 1, 1, 3, 2, 1),
        (3, 2, 2, 2, 2, 4, 2, 1),
    )
    for b, v, t, g, f, h, p, nv in toys:
        exact = grouped_counts(b, v, t, g, f, h, p, nv)
        labeled = brute_counts(b, v, t, g, f, h, p, nv)
        assert exact == labeled, (exact, labeled)
        print("validated physical toy", (b, v, t, g, f, h, p, nv),
              "deals", labeled[1])


def champion_results() -> dict[str, Fraction]:
    outcomes, denominator = grouped_counts(11, 4, 4, 4, 34)
    valid_initial = Fraction(1) - Fraction(choose(47, 7), choose(60, 7))
    assert outcomes["fork"] == outcomes["dialga_initial"] + outcomes["dialga_draw"]
    assert outcomes["fork"] == outcomes["single_treasure"] + outcomes["multiple_treasure"]
    assert outcomes["fork"] == outcomes["fog_available"] + outcomes["no_fog"]
    assert outcomes["single_treasure"] == (
        outcomes["single_treasure_no_fog"]
        + outcomes["single_treasure_with_fog"]
    )
    result = {name: Fraction(count, denominator) / valid_initial
              for name, count in outcomes.items()}
    assert result["fork"] == Fraction(58613434588753, 2525562843410880) / valid_initial
    return result


if __name__ == "__main__":
    validate_toy_worlds()
    for name, p in sorted(champion_results().items()):
        print(f"{name}: {p} ({100*float(p):.9f}% of Basic-valid openings)")
