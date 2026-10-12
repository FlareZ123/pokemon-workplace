"""Exact prize-aware Trainers' Mail -> Battle VIP Pass for Aichi Mew Genesect.

Source-limited goal: first-turn Mew V with two/three Genesect V from held
Basics, held Battle VIP Passes, and held Trainers' Mail finding extra Passes.
This omits Ball searches, Genesect draws, and every non-VIP Mail target.
"""

from __future__ import annotations

import json
from fractions import Fraction
from functools import lru_cache
from itertools import combinations
from math import comb
from pathlib import Path

from results.mew_genesect_vip_opening.reproduce import (
    category_counts,
    exact as vip_only_exact,
)


def counts(vip: int) -> tuple[int, ...]:
    """Mew V, Genesect V, other Basic, VIP, Trainers' Mail, other cards."""
    assert vip in (3, 4)
    return 4, 4, 3, vip, 3, 46 - vip


def vectors(total: int, limits: tuple[int, ...]):
    if not limits:
        if total == 0:
            yield ()
        return
    for n in range(min(total, limits[0]) + 1):
        for tail in vectors(total - n, limits[1:]):
            yield (n, *tail)


@lru_cache(maxsize=None)
def mail_hit_distribution(
    deck_size: int, vip_left: int, mails: int, look_size: int,
) -> tuple[Fraction, ...]:
    """Distribution of fetched VIPs for sequential top-k Mail plays.

    Mail cannot select another Mail. A miss shuffles the inspected cards back
    into the deck. A successful selection removes exactly one VIP card, and
    the rest of the deck is randomized before the next Mail inspection.
    """
    assert 0 <= vip_left <= deck_size and mails >= 0
    if mails == 0:
        return (Fraction(1),)
    look = min(look_size, deck_size)
    hit = (
        1 - Fraction(comb(deck_size - vip_left, look), comb(deck_size, look))
        if look else Fraction(0)
    )
    miss_branch = mail_hit_distribution(
        deck_size, vip_left, mails - 1, look_size
    )
    hit_branch = (
        mail_hit_distribution(deck_size - 1, vip_left - 1, mails - 1, look_size)
        if vip_left else ()
    )
    result = [Fraction(0)] * (mails + 1)
    for fetched, probability in enumerate(miss_branch):
        result[fetched] += (1 - hit) * probability
    for fetched, probability in enumerate(hit_branch):
        result[fetched + 1] += hit * probability
    assert sum(result) == 1
    return tuple(result)


def success_probability(
    seen: tuple[int, ...],
    prized_mew: int,
    prized_genesect: int,
    prized_vip: int,
    total: tuple[int, ...],
    goal: int,
    deck_size: int,
    look_size: int,
    allow_mail: bool,
) -> Fraction:
    mew, genesect, _, held_vip, held_mail, _ = seen
    need_mew = max(0, 1 - mew)
    need_genesect = max(0, goal - genesect)
    missing = need_mew + need_genesect
    if (
        total[0] - mew - prized_mew < need_mew
        or total[1] - genesect - prized_genesect < need_genesect
    ):
        return Fraction(0)

    vip_in_deck = total[3] - held_vip - prized_vip
    probabilities = mail_hit_distribution(
        deck_size, vip_in_deck, held_mail if allow_mail else 0, look_size
    )
    return sum(
        (
            probability
            for extra_vip, probability in enumerate(probabilities)
            if missing <= 2 * (held_vip + extra_vip)
        ),
        Fraction(0),
    )


def exact_counts(
    cards: tuple[int, ...],
    goal: int,
    *,
    hand_size: int,
    prize_size: int,
    look_size: int,
    allow_mail: bool = True,
) -> Fraction:
    total_cards = sum(cards)
    exposed = hand_size + 1
    deck_size = total_cards - exposed - prize_size
    assert len(cards) == 6 and deck_size >= 0 and goal >= 1
    favorable = Fraction(0)
    valid_worlds = 0
    for seen in vectors(exposed, cards):
        visible_basics = sum(seen[:3])
        if visible_basics == 0:
            continue
        weight_visible = exposed if visible_basics >= 2 else hand_size
        for count, held in zip(cards, seen):
            weight_visible *= comb(count, held)
        remaining = tuple(c - v for c, v in zip(cards, seen))
        remainder_other = total_cards - exposed - sum(
            remaining[index] for index in (0, 1, 3)
        )
        for pm in range(min(remaining[0], prize_size) + 1):
            for pg in range(min(remaining[1], prize_size - pm) + 1):
                for pv in range(min(remaining[3], prize_size - pm - pg) + 1):
                    po = prize_size - pm - pg - pv
                    if po > remainder_other:
                        continue
                    weight = (
                        weight_visible
                        * comb(remaining[0], pm)
                        * comb(remaining[1], pg)
                        * comb(remaining[3], pv)
                        * comb(remainder_other, po)
                    )
                    probability = success_probability(
                        seen, pm, pg, pv, cards, goal,
                        deck_size, look_size, allow_mail,
                    )
                    valid_worlds += weight
                    favorable += weight * probability

    denominator = (
        exposed * comb(total_cards, exposed)
        * comb(total_cards - exposed, prize_size)
    )
    assert Fraction(valid_worlds, denominator) == 1 - Fraction(
        comb(total_cards - sum(cards[:3]), hand_size),
        comb(total_cards, hand_size),
    )
    return favorable / valid_worlds


def exact(vip: int, goal: int, *, allow_mail: bool = True) -> Fraction:
    assert goal in (2, 3)
    return exact_counts(
        counts(vip), goal, hand_size=7, prize_size=6,
        look_size=4, allow_mail=allow_mail,
    )


def physical_toy_oracle(
    cards: tuple[int, ...], goal: int,
    *, hand_size: int = 3, prize_size: int = 2, look_size: int = 2,
) -> tuple[Fraction, int]:
    """Independent enumeration of labeled physical opening/Prize/Mail worlds."""
    deck = tuple(category for category, n in enumerate(cards) for _ in range(n))
    ids = tuple(range(len(deck)))
    successes = Fraction(0)
    valid_worlds = 0
    for hand in combinations(ids, hand_size):
        if not any(deck[i] < 3 for i in hand):
            continue
        remaining = tuple(i for i in ids if i not in hand)
        for prizes in combinations(remaining, prize_size):
            available_to_draw = tuple(i for i in remaining if i not in prizes)
            for first_draw in available_to_draw:
                unprized_deck = tuple(
                    i for i in available_to_draw if i != first_draw
                )
                visible = (*hand, first_draw)
                mew = sum(deck[i] == 0 for i in visible)
                genesect = sum(deck[i] == 1 for i in visible)
                held_vip = sum(deck[i] == 3 for i in visible)
                held_mail = sum(deck[i] == 4 for i in visible)
                missing_mew = max(0, 1 - mew)
                missing_genesect = max(0, goal - genesect)
                missing = missing_mew + missing_genesect
                targets_live = (
                    sum(deck[i] == 0 for i in unprized_deck) >= missing_mew
                    and sum(deck[i] == 1 for i in unprized_deck)
                    >= missing_genesect
                )

                @lru_cache(maxsize=None)
                def traverse(
                    current_deck: tuple[int, ...], mails: int, vip_held: int
                ) -> Fraction:
                    if mails == 0:
                        return Fraction(
                            targets_live and missing <= 2 * vip_held
                        )
                    possible = tuple(
                        combinations(
                            current_deck, min(look_size, len(current_deck))
                        )
                    )
                    outcome = Fraction(0)
                    for looked_at in possible:
                        selected = next(
                            (i for i in looked_at if deck[i] == 3), None
                        )
                        next_deck = (
                            current_deck if selected is None
                            else tuple(i for i in current_deck if i != selected)
                        )
                        outcome += traverse(
                            next_deck, mails - 1, vip_held + (selected is not None)
                        )
                    return outcome / len(possible)

                successes += traverse(unprized_deck, held_mail, held_vip)
                valid_worlds += 1
    return successes / valid_worlds, valid_worlds


def verify_printed_mail_text() -> None:
    root = Path(__file__).resolve().parents[2]
    records = json.loads(
        (root / "resources" / "cards" / "en" / "xy6.json").read_text(
            encoding="utf-8"
        )
    )
    card = next(c for c in records if c["id"] == "xy6-92")
    assert card["name"] == "Trainers' Mail"
    assert card["subtypes"] == ["Item"]
    assert "top 4 cards" in card["rules"][0]
    assert "(except Trainers' Mail)" in card["rules"][0]


def self_test() -> None:
    verify_printed_mail_text()
    toy = (1, 2, 1, 2, 2, 2)
    for goal in (1, 2):
        analytical = exact_counts(
            toy, goal, hand_size=3, prize_size=2, look_size=2
        )
        physical, worlds = physical_toy_oracle(toy, goal)
        assert worlds == 10500
        assert analytical == physical, (goal, analytical, physical)
        print(
            f"Physical {goal}-Genesect toy with multiple Mail: "
            f"{worlds} legal worlds match exact rational probability"
        )
    for goal in (2, 3):
        for vip in (3, 4):
            without_mail = exact(vip, goal, allow_mail=False)
            source_only = vip_only_exact(
                category_counts(vip), goal, vip_use_limit=None
            )["combined"]
            assert without_mail == source_only
            with_mail = exact(vip, goal)
            assert with_mail > without_mail
            print(
                f"Mew + {goal} Genesect, {vip} VIP: "
                f"held-VIP={float(without_mail):.9%}, "
                f"plus naturally held Mail={float(with_mail):.9%}, "
                f"gain={float(with_mail-without_mail)*100:.9f} pp"
            )


if __name__ == "__main__":
    self_test()
