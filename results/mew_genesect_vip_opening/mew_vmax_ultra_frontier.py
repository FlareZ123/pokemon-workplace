"""Mew VMAX access through held cards or a physically payable Ultra Ball.

Separate first-draw Stage-1 acquisition endpoint; later evolution, Basic
setup, shared payment with other searches, opponent lock and match wins are
not modeled. Integrates exact six Prize identities and Basic-valid openers.
"""
from __future__ import annotations

import json
from fractions import Fraction
from itertools import combinations
from math import comb
from pathlib import Path


def vectors(k: int, caps: tuple[int, ...]):
    if not caps:
        if k == 0:
            yield ()
        return
    for n in range(min(k, caps[0]) + 1):
        for tail in vectors(k - n, caps[1:]):
            yield (n, *tail)


def exact(total: int, basics: int, stage: int, ultra: int, d: int,
          hand: int = 7, prize_size: int = 6) -> tuple[Fraction, Fraction]:
    counts = (basics, stage, ultra, d, total - basics - stage - ultra - d)
    assert all(x >= 0 for x in counts)
    exposed = hand + 1
    valid = direct = plus_ultra = 0
    for seen in vectors(exposed, counts):
        b, v, u, safe, _ = seen
        if not b:
            continue
        weight = exposed if b >= 2 else hand
        for n, k in zip(counts, seen):
            weight *= comb(n, k)
        remaining = stage - v
        other = total - exposed - remaining
        for prized_stage in range(min(prize_size, remaining) + 1):
            p_other = prize_size - prized_stage
            if p_other > other:
                continue
            w = weight * comb(remaining, prized_stage) * comb(other, p_other)
            valid += w
            direct += w * (v >= 1)
            plus_ultra += w * (
                v >= 1
                or (u >= 1 and safe >= 2 and remaining > prized_stage)
            )
    denominator = exposed * comb(total, exposed) * comb(total - exposed, prize_size)
    assert Fraction(valid, denominator) == 1 - Fraction(
        comb(total - basics, hand), comb(total, hand)
    )
    return Fraction(direct, valid), Fraction(plus_ultra, valid)


def physical_oracle(total: int, basics: int, stage: int, ultra: int,
                    d: int, hand: int = 3,
                    prizes: int = 2) -> tuple[Fraction, Fraction, int]:
    """Exhaustive labeled-card physical hand/Prize/draw verification."""
    assert total <= 13
    counts = (basics, stage, ultra, d, total - basics - stage - ultra - d)
    deck = tuple(i for i, n in enumerate(counts) for _ in range(n))
    ids = tuple(range(total))
    valid = direct = paid = 0
    for h in combinations(ids, hand):
        if not any(deck[i] == 0 for i in h):
            continue
        rest = tuple(i for i in ids if i not in h)
        for p in combinations(rest, prizes):
            drawable = tuple(i for i in rest if i not in p)
            for draw in drawable:
                seen = (*h, draw)
                v = sum(deck[i] == 1 for i in seen)
                u = sum(deck[i] == 2 for i in seen)
                safe = sum(deck[i] == 3 for i in seen)
                target_live = any(
                    deck[i] == 1 for i in drawable if i != draw
                )
                valid += 1
                direct += v >= 1
                paid += v >= 1 or (
                    u >= 1 and safe >= 2 and target_live
                )
    return Fraction(direct, valid), Fraction(paid, valid), valid


def verify_prints() -> None:
    root = Path(__file__).resolve().parents[2] / "resources" / "cards" / "en"
    for card_id, name, required in (
        ("swsh8-114", "Mew VMAX", ""),
        ("swsh9-150", "Ultra Ball", "Discard 2 other cards"),
    ):
        set_id = card_id.rsplit("-", 1)[0]
        cards = json.loads(
            (root / f"{set_id}.json").read_text(encoding="utf-8")
        )
        found = next(x for x in cards if x["id"] == card_id)
        assert found["name"] == name
        assert required.casefold() in " ".join(found.get("rules", [])).casefold()


def self_test() -> None:
    verify_prints()
    for ultra in (1, 2, 3):
        grouped = exact(12, 3, 2, ultra, 2, hand=3, prize_size=2)
        a, b, cases = physical_oracle(12, 3, 2, ultra, 2)
        assert cases == 34272 and grouped == (a, b)
        print(f"Ultra={ultra}, 34272 physical labeled deals: PASS")
    for d in (0, 4, 6, 12, 20):
        original = exact(60, 11, 3, 4, d)
        reduced = exact(60, 11, 3, 3, d)
        assert original[0] == reduced[0] and original[1] >= reduced[1]
        print(
            f"D={d}: direct={float(original[0]):.9%}, "
            f"4-Ultra={float(original[1]):.9%}, "
            f"3-Ultra={float(reduced[1]):.9%}, "
            f"loss={float(original[1]-reduced[1])*100:.9f} pp"
        )


if __name__ == "__main__":
    self_test()
