"""Exact two-turn Guzma -> follow-up gust supply with VS Seeker recovery.

Only natural draws are included. First own turn is going second, with
Supporters available. Turn 2 uses an exogenous lock/Prize condition.
"""
from dataclasses import dataclass
from fractions import Fraction
from math import comb


@dataclass(frozen=True)
class Turn2:
    supporter: bool = True
    item: bool = True
    behind: bool = False


def choose(n: int, k: int) -> int:
    return comb(n, k) if 0 <= k <= n else 0


def chain(basics: int, guzma: int, seekers: int, prime: int, counter: int,
          second: Turn2, total: int = 60, hand_size: int = 7,
          prize_count: int = 6) -> tuple[Fraction, Fraction]:
    """P(Guzma T1), P(Guzma T1 and one legal gust source T2).

    Assumes the first Guzma is played, stays in discard, and can be
    retrieved by VS Seeker. Its Supporter use on T1 does not consume
    the Supporter allowance on T2.
    """
    counts = (basics, guzma, seekers, prime, counter,
              total - basics - guzma - seekers - prime - counter)
    assert min(counts) >= 0 and basics > 0
    assert hand_size + prize_count + 2 <= total
    accepted = choose(total, hand_size) - choose(total - basics, hand_size)
    first_access = second_access = Fraction(0)
    for hb in range(1, min(basics, hand_size) + 1):
        for hg in range(min(guzma, hand_size - hb) + 1):
            for hv in range(min(seekers, hand_size - hb - hg) + 1):
                for hp in range(min(prime, hand_size - hb - hg - hv) + 1):
                    for hc in range(min(counter, hand_size - hb - hg - hv - hp) + 1):
                        hf = hand_size - hb - hg - hv - hp - hc
                        if not 0 <= hf <= counts[-1]:
                            continue
                        hand = (hb, hg, hv, hp, hc, hf)
                        ways = 1
                        for n, h in zip(counts, hand):
                            ways *= choose(n, h)
                        remaining = tuple(n - h for n, h in zip(counts, hand))
                        for a, ra in enumerate(remaining):
                            if not ra:
                                continue
                            after = list(hand)
                            after[a] += 1
                            if not after[1]:
                                continue
                            p = Fraction(ways * ra, accepted * (total - hand_size))
                            first_access += p
                            after[1] -= 1  # Guzma played on T1; now in discard.
                            for b, rb in enumerate(remaining):
                                available = rb - (a == b)
                                if not available:
                                    continue
                                on_t2 = after.copy()
                                on_t2[b] += 1
                                legal_second = (
                                    (second.supporter and
                                     (on_t2[1] or (second.item and on_t2[2]))) or
                                    (second.item and
                                     (on_t2[3] or (second.behind and on_t2[4])))
                                )
                                if legal_second:
                                    second_access += p * Fraction(
                                        available, total - hand_size - 1)
    return first_access, second_access
