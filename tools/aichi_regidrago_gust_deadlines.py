"""Exact natural-draw gust-source deadlines for published Aichi Regidrago."""
from dataclasses import dataclass
from fractions import Fraction
from math import comb


@dataclass(frozen=True)
class Window:
    supporter: bool = True
    item: bool = True
    behind: bool = False


def choose(n: int, k: int) -> int:
    return comb(n, k) if 0 <= k <= n else 0


def access(basics: int, guzma: int, prime: int, counter: int,
           first: Window, second: Window, total: int = 60,
           hand_size: int = 7, prize_count: int = 6) -> tuple[Fraction, Fraction]:
    """P(legal source held by own turn 1), P(by own turn 2).

    The seven-card hand must contain a Basic; each turn has one natural draw.
    Prize removal is uniformly random and therefore integrates out of these
    marginal first-two-draw probabilities. No searches or hand disruptions.
    """
    assert 0 < basics <= total
    assert min(guzma, prime, counter) >= 0
    assert basics + guzma + prime + counter <= total
    assert 0 < hand_size and hand_size + prize_count + 2 <= total
    source_counts = (guzma, prime, counter)
    filler = total - basics - sum(source_counts)
    capacities = (basics, guzma, prime, counter, filler)
    accepted = choose(total, hand_size) - choose(total - basics, hand_size)
    weights = [Fraction(0), Fraction(0)]
    for hb in range(1, min(basics, hand_size) + 1):
        for hg in range(min(guzma, hand_size - hb) + 1):
            for hp in range(min(prime, hand_size - hb - hg) + 1):
                for hc in range(min(counter, hand_size - hb - hg - hp) + 1):
                    hf = hand_size - hb - hg - hp - hc
                    if not 0 <= hf <= filler:
                        continue
                    hand = (hb, hg, hp, hc, hf)
                    ways = 1
                    for n, h in zip(capacities, hand):
                        ways *= choose(n, h)
                    remaining = tuple(n - h for n, h in zip(capacities, hand))
                    for first_type, first_remaining in enumerate(remaining):
                        if not first_remaining:
                            continue
                        p1 = Fraction(ways * first_remaining, accepted * (total - hand_size))
                        after_first = list(hand)
                        after_first[first_type] += 1
                        hit_first = _enabled(after_first, first)
                        if hit_first:
                            weights[0] += p1
                            weights[1] += p1
                            continue
                        for second_type, second_remaining in enumerate(remaining):
                            available = second_remaining - (first_type == second_type)
                            if not available:
                                continue
                            after_second = after_first.copy()
                            after_second[second_type] += 1
                            if _enabled(after_second, second):
                                weights[1] += p1 * Fraction(available, total - hand_size - 1)
    return tuple(weights)


def _enabled(hand: list[int], window: Window) -> bool:
    return bool((window.supporter and hand[1]) or
                (window.item and (hand[2] or (window.behind and hand[3]))))
