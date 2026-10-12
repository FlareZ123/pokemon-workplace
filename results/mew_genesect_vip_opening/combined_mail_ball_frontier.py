"""Exact first-turn Mew/Genesect combined paid-Ball -> Mail -> VIP line.

On a Basic-valid opening seven, after six Prizes and one draw, use only
hypothetically discardable D cards to pay naturally held Quick/Ultra Balls.
Search missing Mew/Genesect first, then play held Trainers' Mail for VIPs,
and play all held/fetched VIPs. Computes exact probability of target access.
"""

from __future__ import annotations

from fractions import Fraction
from functools import lru_cache
from itertools import combinations
from math import comb

from results.mew_genesect_vip_opening.paid_ball_frontier import (
    exact as paid_ball_exact,
    paid_capacity,
)
from results.mew_genesect_vip_opening.trainers_mail_vip_bridge import (
    exact as mail_exact,
    mail_hit_distribution,
)


def counts(vip: int, disposable: int) -> tuple[int, ...]:
    """Mew, Genesect, other Basic, VIP, Mail, Quick, Ultra, safe D, other."""
    assert vip in (3, 4) and 0 <= disposable <= 38 - vip
    return 4, 4, 3, vip, 3, 4, 4, disposable, 38 - vip - disposable


def vectors(total: int, limits: tuple[int, ...]):
    if not limits:
        if total == 0:
            yield ()
        return
    for n in range(min(total, limits[0]) + 1):
        for tail in vectors(total - n, limits[1:]):
            yield (n, *tail)


def opening_success(
    seen: tuple[int, ...],
    prized: tuple[int, int, int],
    cards: tuple[int, ...],
    goal: int,
    deck_size: int,
    look_size: int,
    *,
    allow_mail: bool = True,
) -> Fraction:
    """Ball-first policy: physically consume only D; then stochastic Mail.

    Ball searches remove Basic targets from the deck, increase Mail's
    subsequent VIP-hit chance, and conserve each source and payment card.
    Fetching a needed Basic first cannot hurt this binary board-access goal
    while its Ball payment is allowed by the hypothetical DCI policy.
    """
    mew, genesect, _, held_vip, mail, quick, ultra, safe, _ = seen
    prized_mew, prized_genesect, prized_vip = prized
    missing_mew = max(0, 1 - mew)
    missing_genesect = max(0, goal - genesect)
    total_missing = missing_mew + missing_genesect
    if (
        cards[0] - mew - prized_mew < missing_mew
        or cards[1] - genesect - prized_genesect < missing_genesect
    ):
        return Fraction(0)

    balls_used = min(total_missing, paid_capacity(quick, ultra, safe))
    still_missing = total_missing - balls_used
    if still_missing <= 2 * held_vip:
        return Fraction(1)

    # Physical Ball deck searches shuffle before Mail inspects the next k cards.
    vip_in_deck = cards[3] - held_vip - prized_vip
    distribution = mail_hit_distribution(
        deck_size - balls_used,
        vip_in_deck,
        mail if allow_mail else 0,
        look_size,
    )
    return sum(
        (
            probability
            for newly_acquired_vip, probability in enumerate(distribution)
            if still_missing <= 2 * (held_vip + newly_acquired_vip)
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
    n = sum(cards)
    exposed = hand_size + 1
    deck_size = n - exposed - prize_size
    favorable = Fraction(0)
    all_valid = 0
    for seen in vectors(exposed, cards):
        basics = sum(seen[:3])
        if basics == 0:
            continue
        # Of the exposed cards, exactly one arrived after the starting hand.
        visible_weight = exposed if basics >= 2 else hand_size
        for available, held in zip(cards, seen):
            visible_weight *= comb(available, held)
        remaining = tuple(a - h for a, h in zip(cards, seen))
        other = n - exposed - sum(remaining[i] for i in (0, 1, 3))
        for pm in range(min(remaining[0], prize_size) + 1):
            for pg in range(min(remaining[1], prize_size - pm) + 1):
                for pv in range(min(remaining[3], prize_size - pm - pg) + 1):
                    p_other = prize_size - pm - pg - pv
                    if p_other > other:
                        continue
                    weight = (
                        visible_weight
                        * comb(remaining[0], pm)
                        * comb(remaining[1], pg)
                        * comb(remaining[3], pv)
                        * comb(other, p_other)
                    )
                    all_valid += weight
                    favorable += weight * opening_success(
                        seen, (pm, pg, pv), cards, goal, deck_size, look_size,
                        allow_mail=allow_mail,
                    )

    denominator = exposed * comb(n, exposed) * comb(n - exposed, prize_size)
    assert Fraction(all_valid, denominator) == 1 - Fraction(
        comb(n - sum(cards[:3]), hand_size), comb(n, hand_size)
    )
    return favorable / all_valid


def exact(vip: int, disposable: int, goal: int, *,
          allow_mail: bool = True) -> Fraction:
    assert goal in (2, 3)
    return exact_counts(
        counts(vip, disposable), goal, hand_size=7,
        prize_size=6, look_size=4, allow_mail=allow_mail,
    )


def physical_toy_oracle(
    cards: tuple[int, ...], goal: int,
    *, hand_size: int = 3, prize_size: int = 2,
    look_size: int = 2,
) -> tuple[Fraction, int]:
    """Enumerate all labeled legal deals, paid Ball subsets, Mail inspections."""
    deck = tuple(category for category, k in enumerate(cards) for _ in range(k))
    all_ids = tuple(range(len(deck)))
    wins = Fraction(0)
    worlds = 0
    for hand in combinations(all_ids, hand_size):
        if not any(deck[i] in (0, 1, 2) for i in hand):
            continue
        others = tuple(i for i in all_ids if i not in hand)
        for prize in combinations(others, prize_size):
            pre_draw = tuple(i for i in others if i not in prize)
            for first_draw in pre_draw:
                remaining = [
                    i for i in pre_draw if i != first_draw
                ]
                visible = (*hand, first_draw)
                count = lambda category: sum(
                    deck[i] == category for i in visible
                )
                missing_mew = max(0, 1 - count(0))
                missing_genesect = max(0, goal - count(1))
                missing = missing_mew + missing_genesect
                targets_live = (
                    sum(deck[i] == 0 for i in remaining) >= missing_mew
                    and sum(deck[i] == 1 for i in remaining) >= missing_genesect
                )
                q, u, d = count(5), count(6), count(7)
                capacity = max(
                    (
                        q_uses + u_uses
                        for q_uses in range(q + 1)
                        for u_uses in range(u + 1)
                        if q_uses + 2 * u_uses <= d
                    ),
                    default=0,
                )
                used = min(capacity, missing)
                for target_category in (
                    [0] * missing_mew + [1] * missing_genesect
                )[:used]:
                    selected = next(
                        (i for i in remaining if deck[i] == target_category),
                        None,
                    )
                    if selected is not None:
                        remaining.remove(selected)

                @lru_cache(maxsize=None)
                def next_mail(
                    current: tuple[int, ...],
                    unused_mail: int,
                    available_vip: int,
                ) -> Fraction:
                    if unused_mail == 0:
                        return Fraction(
                            targets_live and missing - used <= 2 * available_vip
                        )
                    looks = tuple(
                        combinations(
                            current, min(look_size, len(current))
                        )
                    )
                    probability = Fraction(0)
                    for top in looks:
                        chosen = next(
                            (i for i in top if deck[i] == 3), None
                        )
                        after = (
                            current if chosen is None
                            else tuple(i for i in current if i != chosen)
                        )
                        probability += next_mail(
                            after,
                            unused_mail - 1,
                            available_vip + (chosen is not None),
                        )
                    return probability / len(looks)

                wins += next_mail(tuple(remaining), count(4), count(3))
                worlds += 1
    return wins / worlds, worlds


def self_test() -> None:
    # Four independent ten-card physical-card toy worlds; 10,500 legal deals.
    for toy in (
        (1, 2, 1, 1, 1, 1, 1, 1, 1),
        (1, 2, 1, 1, 1, 1, 1, 2, 0),
        (1, 2, 1, 2, 1, 1, 1, 1, 0),
    ):
        assert sum(toy) == 10
        for goal in (1, 2):
            grouped = exact_counts(
                toy, goal, hand_size=3, prize_size=2, look_size=2
            )
            physical, worlds = physical_toy_oracle(toy, goal)
            assert worlds == 10500
            assert grouped == physical, (toy, goal, grouped, physical)
            print(f"Physical toy oracle goal={goal}, 10500 deals: PASS")

    for goal in (2, 3):
        for vip in (3, 4):
            no_ball = exact(vip, 0, goal)
            assert no_ball == mail_exact(vip, goal)
            for d in (0, 6, 12, 24):
                integrated = exact(vip, d, goal)
                paid_only = paid_ball_exact(vip, d, goal)[
                    "vip_plus_paid_balls"
                ]
                assert integrated >= paid_only
                assert integrated >= no_ball
                assert exact(vip, d, goal, allow_mail=False) == paid_only
                print(
                    f"Mew + {goal} Genesect VIP={vip}, D={d}: "
                    f"joint={float(integrated):.9%}, "
                    f"paid-only={float(paid_only):.9%}"
                )


if __name__ == "__main__":
    self_test()
