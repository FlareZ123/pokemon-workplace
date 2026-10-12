"""Joint early Mew V + Genesect V board and Mew VMAX-in-hand access.

Exact Prize-conditioned first-eight-card source planner. Reserves a payable
Ultra Ball for Mew VMAX when none is naturally held, then uses remaining
physically paid Quick/Ultra searches for missing Basics, then sequential
held Trainers' Mail -> VIP Pass top-four inspections. No other draws,
Supporters, evolution on turn one, locks, or match-win claims.
"""

from __future__ import annotations

from fractions import Fraction
from functools import lru_cache
from itertools import combinations
from math import comb

from results.mew_genesect_vip_opening.paid_ball_frontier import paid_capacity
from results.mew_genesect_vip_opening.trainers_mail_vip_bridge import (
    mail_hit_distribution,
)
from results.mew_genesect_vip_opening.vip_slot_cut_frontier import VARIANTS


def counts(vip: int, mail: int, quick: int, ultra: int,
           safe: int) -> tuple[int, ...]:
    """Mew, Gene, other Basic, VMAX, VIP, Mail, Quick, Ultra, D, other."""
    head = (4, 4, 3, 3, vip, mail, quick, ultra, safe)
    tail = 60 - sum(head)
    assert tail >= 0
    return (*head, tail)


def vectors(amount: int, capacities: tuple[int, ...]):
    if not capacities:
        if amount == 0:
            yield ()
        return
    for n in range(min(amount, capacities[0]) + 1):
        for rest in vectors(amount - n, capacities[1:]):
            yield (n, *rest)


def material_success(
    seen: tuple[int, ...],
    prized: tuple[int, int, int, int],
    cards: tuple[int, ...],
    genesect_goal: int,
    deck_size: int,
    look_size: int,
) -> Fraction:
    mew, gene, _, vmax, vip, mails, quick, ultra, safe, _ = seen
    pm, pg, pe, pv = prized
    need_mew = max(0, 1 - mew)
    need_gene = max(0, genesect_goal - gene)
    if (
        cards[0] - mew - pm < need_mew
        or cards[1] - gene - pg < need_gene
    ):
        return Fraction(0)

    # Mew VMAX is Stage 1 and cannot be obtained with Quick Ball or VIP.
    # A missing VMAX needs one genuine physical Ultra plus two approved
    # hand-discard cards and at least one unprized VMAX still in deck.
    fetch_stage = int(vmax == 0)
    if fetch_stage and (
        cards[3] - vmax - pe < 1 or ultra < 1 or safe < 2
    ):
        return Fraction(0)
    remaining_ultra = ultra - fetch_stage
    remaining_safe = safe - 2 * fetch_stage
    basics_missing = need_mew + need_gene
    balls_for_basics = min(
        basics_missing, paid_capacity(
            quick, remaining_ultra, remaining_safe
        ),
    )
    missing_after_balls = basics_missing - balls_for_basics
    if missing_after_balls <= 2 * vip:
        return Fraction(1)
    possible_new_vip = mail_hit_distribution(
        deck_size - fetch_stage - balls_for_basics,
        cards[4] - vip - pv,
        mails,
        look_size,
    )
    return sum(
        (
            probability
            for fetched_vip, probability in enumerate(possible_new_vip)
            if missing_after_balls <= 2 * (vip + fetched_vip)
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
) -> Fraction:
    total = sum(cards)
    exposed = hand_size + 1
    deck_size = total - exposed - prize_size
    numerator = Fraction(0)
    denominator = 0
    for seen in vectors(exposed, cards):
        basic_count = seen[0] + seen[1] + seen[2]
        if basic_count == 0:
            continue
        weight_visible = exposed if basic_count >= 2 else hand_size
        for count, held in zip(cards, seen):
            weight_visible *= comb(count, held)
        remaining = tuple(n - k for n, k in zip(cards, seen))
        other = (
            total - exposed - remaining[0] - remaining[1]
            - remaining[3] - remaining[4]
        )
        for pm in range(min(remaining[0], prize_size) + 1):
            for pg in range(min(remaining[1], prize_size - pm) + 1):
                for pe in range(min(remaining[3], prize_size - pm - pg) + 1):
                    for pv in range(
                        min(remaining[4], prize_size - pm - pg - pe) + 1
                    ):
                        p_other = prize_size - pm - pg - pe - pv
                        if p_other > other:
                            continue
                        weight = (
                            weight_visible
                            * comb(remaining[0], pm)
                            * comb(remaining[1], pg)
                            * comb(remaining[3], pe)
                            * comb(remaining[4], pv)
                            * comb(other, p_other)
                        )
                        denominator += weight
                        numerator += weight * material_success(
                            seen, (pm, pg, pe, pv), cards, goal,
                            deck_size, look_size,
                        )
    valid_initial = 1 - Fraction(
        comb(total - sum(cards[:3]), hand_size),
        comb(total, hand_size),
    )
    all_physical = (
        exposed * comb(total, exposed)
        * comb(total - exposed, prize_size)
    )
    assert Fraction(denominator, all_physical) == valid_initial
    return numerator / denominator


def joint_access(row: tuple, goal: int = 2, safe: int = 6) -> Fraction:
    _, add_vip, _, mail, quick, ultra = row
    return exact_counts(
        counts(3 + add_vip, mail, quick, ultra, safe),
        goal, hand_size=7, prize_size=6, look_size=4,
    )


def physical_oracle(
    cards: tuple[int, ...],
    goal: int,
    *,
    hand_size: int = 3,
    prize_size: int = 2,
    look_size: int = 2,
) -> tuple[Fraction, int]:
    """Fully independent labeled cards and random physical Mail inspections."""
    deck = tuple(i for i, n in enumerate(cards) for _ in range(n))
    ids = tuple(range(len(deck)))
    successes = Fraction(0)
    worlds = 0
    for opening in combinations(ids, hand_size):
        if not any(deck[i] in (0, 1, 2) for i in opening):
            continue
        rest = tuple(i for i in ids if i not in opening)
        for prizes in combinations(rest, prize_size):
            drawable = tuple(i for i in rest if i not in prizes)
            for first_draw in drawable:
                visible = (*opening, first_draw)
                live = [i for i in drawable if i != first_draw]
                count = lambda category: sum(
                    deck[i] == category for i in visible
                )
                need_mew = max(0, 1 - count(0))
                need_gene = max(0, goal - count(1))
                stage_needed = int(count(3) == 0)
                legal = (
                    sum(deck[i] == 0 for i in live) >= need_mew
                    and sum(deck[i] == 1 for i in live) >= need_gene
                )
                if stage_needed:
                    stage_card = next(
                        (i for i in live if deck[i] == 3), None
                    )
                    legal = (
                        legal and stage_card is not None
                        and count(7) >= 1 and count(8) >= 2
                    )
                    if legal:
                        live.remove(stage_card)
                worlds += 1
                if not legal:
                    continue

                q = count(6)
                u = count(7) - stage_needed
                d = count(8) - 2 * stage_needed
                # Independent physical payment-choice enumeration.
                cap = max(
                    (
                        q_use + u_use
                        for q_use in range(q + 1)
                        for u_use in range(u + 1)
                        if q_use + 2 * u_use <= d
                    ),
                    default=0,
                )
                balls = min(need_mew + need_gene, cap)
                for category in (
                    [0] * need_mew + [1] * need_gene
                )[:balls]:
                    chosen = next(
                        (i for i in live if deck[i] == category), None
                    )
                    assert chosen is not None
                    live.remove(chosen)
                missing_basics = need_mew + need_gene - balls

                @lru_cache(maxsize=None)
                def resolve_mail(
                    remaining: tuple[int, ...],
                    unused_mails: int,
                    held_vip: int,
                ) -> Fraction:
                    if unused_mails == 0:
                        return Fraction(
                            missing_basics <= 2 * held_vip
                        )
                    visible_top = tuple(
                        combinations(
                            remaining, min(look_size, len(remaining))
                        )
                    )
                    favorable = Fraction(0)
                    for top in visible_top:
                        chosen = next(
                            (i for i in top if deck[i] == 4), None
                        )
                        after = (
                            remaining if chosen is None
                            else tuple(i for i in remaining if i != chosen)
                        )
                        favorable += resolve_mail(
                            after,
                            unused_mails - 1,
                            held_vip + (chosen is not None),
                        )
                    return favorable / len(visible_top)

                successes += resolve_mail(
                    tuple(live), count(5), count(4)
                )
    return successes / worlds, worlds


def self_test() -> None:
    for small in (
        (1, 2, 1, 1, 1, 1, 1, 1, 2, 1),
        (1, 2, 1, 1, 1, 1, 1, 0, 2, 2),
        (1, 2, 1, 1, 1, 0, 1, 1, 2, 2),
    ):
        assert sum(small) == 12
        for goal in (1, 2):
            theory = exact_counts(
                small, goal, hand_size=3,
                prize_size=2, look_size=2,
            )
            oracle, count = physical_oracle(small, goal)
            assert count == 41328 and theory == oracle
            print(f"Stage/Basic toy {small} goal={goal}: 41328 worlds PASS")
    values = {row[0]: joint_access(row) for row in VARIANTS}
    assert values["4-VIP / minus Red"] == values["4-VIP / minus Karen"]
    assert values["4-VIP / minus Quick"] > values["4-VIP / minus Ultra"]
    for name, value in values.items():
        print(f"Mew V + two Genesect V + Mew VMAX, D=6, {name}: "
              f"{float(value):.9%}")


if __name__ == "__main__":
    self_test()
