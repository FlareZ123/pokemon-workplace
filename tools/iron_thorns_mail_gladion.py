from __future__ import annotations

import math
from fractions import Fraction
from functools import lru_cache


COUNTS = (4, 2, 2, 1, 1, 1, 3, 39, 7)
OPENING = 7
PRIZES = 6


def allocations(total: int, caps: tuple[int, ...]):
    cur = [0] * len(caps)

    def rec(i: int, left: int):
        if i == len(caps) - 1:
            if 0 <= left <= caps[i]:
                cur[i] = left
                yield tuple(cur)
            return
        for value in range(min(caps[i], left) + 1):
            cur[i] = value
            yield from rec(i + 1, left - value)

    yield from rec(0, total)


def k1_success(g, m, e, l, dg, dm, de) -> bool:
    if m and e:
        return True
    gh = g > 0 or dg > 0
    if not m and not e:
        return gh and dm > 0 and de > 0
    if not m:
        return (gh and dm > 0) or (l > 0 and dm == 0)
    return (gh and de > 0) or (l > 0 and de == 0)


@lru_cache(maxsize=None)
def policy(g, c, m, e, l, r, dg, dc, dm, de, dl, dr, do, dn) -> Fraction:
    if m and e:
        return Fraction(1)

    if c > 0 and dg > 0:
        return Fraction(int(k1_success(g, m, e, l, dg, dm, de)))

    if g > 0:
        return Fraction(int((m > 0 or dm > 0) and (e > 0 or de > 0)))

    if l > 0 and bool(m) != bool(e):
        return Fraction(int(de == 0 if m else dm == 0))

    if r <= 0:
        return Fraction(0)

    deck = (dg, dc, dm, de, dl, dr, do, dn)
    size = sum(deck)
    denominator = math.comb(size, 4)
    total = Fraction(0)

    for reveal in allocations(4, deck):
        ways = math.prod(
            math.comb(deck[i], reveal[i]) for i in range(len(deck))
        )
        rg, rc, rm, _, rl, _, ro, _ = reveal

        if e > 0 and m == 0 and rm:
            args = (g, c, m + 1, e, l, r - 1, dg, dc, dm - 1, de, dl, dr, do, dn)
        elif rc:
            args = (g, c + 1, m, e, l, r - 1, dg, dc - 1, dm, de, dl, dr, do, dn)
        elif rg:
            args = (g + 1, c, m, e, l, r - 1, dg - 1, dc, dm, de, dl, dr, do, dn)
        elif rm:
            args = (g, c, m + 1, e, l, r - 1, dg, dc, dm - 1, de, dl, dr, do, dn)
        elif rl:
            args = (g, c, m, e, l + 1, r - 1, dg, dc, dm, de, dl - 1, dr, do, dn)
        elif ro:
            args = (g, c, m, e, l, r - 1, dg, dc, dm, de, dl, dr, do - 1, dn)
        else:
            args = (g, c, m, e, l, r - 1, dg, dc, dm, de, dl, dr, do, dn)

        total += Fraction(ways, denominator) * policy(*args)

    return total


def exact_probability() -> Fraction:
    total_openings = math.comb(60, OPENING)
    accepted = total_openings - math.comb(56, OPENING)
    denominator = accepted * math.comb(53, PRIZES) * 47
    total = Fraction(0)

    for opening in allocations(OPENING, COUNTS):
        if opening[0] < 1:
            continue
        ow = math.prod(math.comb(COUNTS[i], opening[i]) for i in range(9))
        remaining = tuple(COUNTS[i] - opening[i] for i in range(9))

        for prizes in allocations(PRIZES, remaining):
            pw = math.prod(
                math.comb(remaining[i], prizes[i]) for i in range(9)
            )
            after = tuple(remaining[i] - prizes[i] for i in range(9))

            for draw_i, copies in enumerate(after):
                if not copies:
                    continue
                hand = [opening[i] + int(i == draw_i) for i in range(9)]
                hand[0] -= 1
                deck = [after[i] - int(i == draw_i) for i in range(9)]

                continuation = policy(
                    hand[1], hand[2], hand[3], hand[4], hand[5], hand[6],
                    deck[1], deck[2], deck[3], deck[4], deck[5], deck[6],
                    deck[7], deck[0] + deck[8],
                )
                total += ow * pw * copies * continuation

    return total / denominator
