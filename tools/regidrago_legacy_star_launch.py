"""Exact natural-only T1 Regidrago V+Guzma -> T2 VSTAR Legacy Star access.

The event is a structural availability certificate, not a legal move planner:
it presumes the T1 Regidrago V remains in play, a bench target exists for
Guzma, and Legacy Star is unspent and not Ability-locked on own T2.
"""
from fractions import Fraction
from math import comb


def choose(n: int, k: int) -> int:
    return comb(n, k) if 0 <= k <= n else 0


def launch(other_basics: int = 11, regidrago_v: int = 4,
           vstar: int = 3, guzma: int = 2, total: int = 60,
           hand_size: int = 7, prize_count: int = 6) -> Fraction:
    """P(T1 naturally hold Regidrago V+Guzma; T2 naturally hold VSTAR).

    Conditions on at least one Basic in initial seven. Includes first
    natural draw before T1 decisions and next natural draw before T2.
    Prize selection is uniformly random and integrated out exactly.
    """
    counts = (other_basics, regidrago_v, vstar, guzma,
              total - other_basics - regidrago_v - vstar - guzma)
    assert min(counts) >= 0 and regidrago_v > 0 and other_basics >= 0
    assert total >= hand_size + prize_count + 2
    accepted = (choose(total, hand_size) -
                choose(total - other_basics - regidrago_v, hand_size))
    hit = Fraction(0)
    for ho in range(min(other_basics, hand_size) + 1):
        for hv in range(min(regidrago_v, hand_size - ho) + 1):
            if not (ho or hv):
                continue
            for hs in range(min(vstar, hand_size - ho - hv) + 1):
                for hg in range(min(guzma, hand_size - ho - hv - hs) + 1):
                    hf = hand_size - ho - hv - hs - hg
                    if not 0 <= hf <= counts[-1]:
                        continue
                    hand = (ho, hv, hs, hg, hf)
                    ways = 1
                    for n, h in zip(counts, hand):
                        ways *= choose(n, h)
                    remaining = tuple(n - h for n, h in zip(counts, hand))
                    for first_type, first_available in enumerate(remaining):
                        if not first_available:
                            continue
                        t1 = list(hand)
                        t1[first_type] += 1
                        if not t1[1] or not t1[3]:
                            continue
                        probability = Fraction(
                            ways * first_available,
                            accepted * (total - hand_size))
                        for second_type, second_available in enumerate(remaining):
                            available = second_available - (first_type == second_type)
                            if not available:
                                continue
                            if t1[2] or second_type == 2:
                                hit += probability * Fraction(
                                    available, total - hand_size - 1)
    return hit
