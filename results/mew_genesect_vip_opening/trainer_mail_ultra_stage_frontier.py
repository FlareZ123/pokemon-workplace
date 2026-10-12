"""Mew VMAX acquisition by naturally held Trainer's Mail -> Ultra Ball.

Exact initial Basic-valid hand, six Prizes and first draw. A held Trainer's
Mail inspects four deck cards for Ultra Ball; each miss reshuffles the
unchanged deck before another held Mail. An acquired Ultra with two designated
safe discard cards can search an unprized Mew VMAX. This model deliberately
does not let the same Mail simultaneously fetch a VIP Pass for Basic setup.
"""
from __future__ import annotations

import json
from fractions import Fraction
from functools import lru_cache
from itertools import combinations
from math import comb
from pathlib import Path


def vectors(total: int, caps: tuple[int, ...]):
    if not caps:
        if total == 0:
            yield ()
        return
    for n in range(min(total, caps[0]) + 1):
        for tail in vectors(total - n, caps[1:]):
            yield (n, *tail)


def stage_probability(
    size: tuple[int, ...],
    *,
    hand: int,
    prizes: int,
    inspect: int,
) -> tuple[Fraction, Fraction]:
    """Basic / Mew VMAX / Ultra / Mail / D / other named categories."""
    n = sum(size)
    exposed = hand + 1
    n_deck = n - exposed - prizes
    valid = direct = through_mail = Fraction(0)
    for seen in vectors(exposed, size):
        basics, stage, ultra, mails, safe, _ = seen
        if basics == 0:
            continue
        weight_visible = exposed if basics >= 2 else hand
        for count, held in zip(size, seen):
            weight_visible *= comb(count, held)
        left_stage = size[1] - stage
        left_ultra = size[2] - ultra
        left_other = n - exposed - left_stage - left_ultra
        for prized_stage in range(min(prizes, left_stage) + 1):
            for prized_ultra in range(
                min(prizes - prized_stage, left_ultra) + 1
            ):
                p_other = prizes - prized_stage - prized_ultra
                if p_other > left_other:
                    continue
                weight = (
                    weight_visible
                    * comb(left_stage, prized_stage)
                    * comb(left_ultra, prized_ultra)
                    * comb(left_other, p_other)
                )
                valid += weight
                if stage:
                    direct += weight
                    through_mail += weight
                    continue
                if safe < 2 or left_stage <= prized_stage:
                    continue
                if ultra:
                    through_mail += weight
                    continue

                unprized_ultra = left_ultra - prized_ultra
                if mails == 0 or unprized_ultra == 0:
                    continue
                top_count = min(inspect, n_deck)
                miss = Fraction(
                    comb(n_deck - unprized_ultra, top_count),
                    comb(n_deck, top_count),
                )
                # A miss returns and shuffles every inspected card; the
                # one-MIMI source pool remains unchanged on the next try.
                through_mail += weight * (1 - miss ** mails)
    assert Fraction(
        valid,
        exposed * comb(n, exposed) * comb(n - exposed, prizes),
    ) == 1 - Fraction(comb(n - size[0], hand), comb(n, hand))
    return direct / valid, through_mail / valid


def exact(ultra: int, d: int, mail: int = 3):
    size = (11, 3, ultra, mail, d, 60 - 11 - 3 - ultra - mail - d)
    assert size[-1] >= 0
    return stage_probability(size, hand=7, prizes=6, inspect=4)


def physical_toy_oracle(
    categories: tuple[int, ...],
    *,
    hand: int = 3,
    prizes: int = 2,
    inspect: int = 2,
) -> tuple[Fraction, int]:
    deck = tuple(k for k, count in enumerate(categories) for _ in range(count))
    ids = tuple(range(len(deck)))
    wins = Fraction(0)
    worlds = 0
    for opening in combinations(ids, hand):
        if not any(deck[i] == 0 for i in opening):
            continue
        others = tuple(i for i in ids if i not in opening)
        for prize_set in combinations(others, prizes):
            drawable = tuple(i for i in others if i not in prize_set)
            for draw in drawable:
                held = (*opening, draw)
                unprized = tuple(i for i in drawable if i != draw)
                count = lambda category: sum(
                    deck[i] == category for i in held
                )
                worlds += 1
                if count(1):
                    wins += 1
                    continue
                if count(4) < 2 or not any(
                    deck[i] == 1 for i in unprized
                ):
                    continue
                if count(2):
                    wins += 1
                    continue

                @lru_cache(maxsize=None)
                def inspect_mail(
                    current: tuple[int, ...], copies: int
                ) -> Fraction:
                    if copies == 0:
                        return Fraction(0)
                    looks = tuple(
                        combinations(current, min(inspect, len(current)))
                    )
                    good = Fraction(0)
                    for top in looks:
                        if any(deck[i] == 2 for i in top):
                            good += 1
                        else:
                            good += inspect_mail(current, copies - 1)
                    return good / len(looks)

                wins += inspect_mail(unprized, count(3))
    return wins / worlds, worlds


def verify_prints() -> None:
    root = Path(__file__).resolve().parents[2] / "resources" / "cards" / "en"
    for set_id, card_id, expected in (
        ("xy6", "xy6-92", "Trainers' Mail"),
        ("swsh9", "swsh9-150", "Ultra Ball"),
    ):
        records = json.loads(
            (root / f"{set_id}.json").read_text(encoding="utf-8")
        )
        card = next(c for c in records if c["id"] == card_id)
        assert card["name"] == expected
    mail = json.loads(
        (root / "xy6.json").read_text(encoding="utf-8")
    )
    item = next(c for c in mail if c["id"] == "xy6-92")
    assert "except Trainers' Mail" in item["rules"][0]


def self_test() -> None:
    verify_prints()
    for small in (
        (3, 2, 2, 2, 2, 1),
        (3, 2, 1, 2, 2, 2),
        (3, 2, 2, 1, 2, 2),
    ):
        grouped = stage_probability(
            small, hand=3, prizes=2, inspect=2
        )[1]
        physical, worlds = physical_toy_oracle(small)
        assert worlds == 34272 and grouped == physical
        print(f"Mail to Ultra physical {small}: 34272 worlds PASS")

    for d in (0, 4, 6, 12, 20):
        baseline = exact(4, d)
        three = exact(3, d)
        assert baseline[0] == three[0]
        assert baseline[1] >= three[1]
        print(
            f"D={d}: directly held VMAX={float(baseline[0]):.9%}, "
            f"4 Ultra with Mail={float(baseline[1]):.9%}, "
            f"3 Ultra with Mail={float(three[1]):.9%}, "
            f"access loss={float(baseline[1]-three[1])*100:.9f} pp"
        )


if __name__ == "__main__":
    self_test()
