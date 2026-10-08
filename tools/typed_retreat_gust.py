"""Typed opponent retreat-vs-Switch options in a bounded gust endgame.

Each Pokemon has Prize value, attack-hits-to-KO, effective Retreat Cost, and
a tuple of attached physical Energy cards measured in generic Energy units.
A normal retreat is allowed only when payable and not blocked. Selected
Energy cards are discarded. An Item Switch token instead preserves Energy
and ignores the target's normal retreat prohibition, subject to Item play.
"""
from dataclasses import dataclass, replace
from functools import lru_cache
from itertools import combinations


@dataclass(frozen=True, order=True)
class Target:
    prize: int
    hits: int
    retreat_cost: int = 0
    energy_cards: tuple[int, ...] = ()
    retreat_blocked: bool = False


@lru_cache(None)
def retreat_payment_remainders(
    energy_cards: tuple[int, ...], cost: int
) -> tuple[tuple[int, ...], ...]:
    """All inclusion-minimal physically payable card sets, expressed as remainders.

    A multi-unit Energy card must be discarded whole. A combination is minimal
    if removing any selected card would make its units insufficient to retreat.
    This retains different legal payment choices with different residual cards.
    """
    if cost == 0:
        return (energy_cards,)
    remainders = set()
    for length in range(1, len(energy_cards) + 1):
        for indexes in combinations(range(len(energy_cards)), length):
            total = sum(energy_cards[i] for i in indexes)
            if total >= cost and all(total - energy_cards[i] < cost for i in indexes):
                remainders.add(tuple(v for i, v in enumerate(energy_cards) if i not in indexes))
    return tuple(sorted(remainders))


@lru_cache(None)
def minimum_attacks(
    active: Target,
    bench: tuple[Target, ...],
    gusts: int,
    switch_items: int = 0,
    item_play_allowed: bool = True,
    prizes_needed: int = 6,
) -> int:
    actions = [(active, bench, gusts)]
    if gusts:
        for i, target in enumerate(bench):
            survivors = tuple(sorted((active,) + bench[:i] + bench[i + 1 :]))
            actions.append((target, survivors, gusts - 1))

    costs = []
    for target, others, remaining_gusts in actions:
        if target.hits > 1:
            wounded = replace(target, hits=target.hits - 1)
            replies = [
                minimum_attacks(
                    wounded, others, remaining_gusts,
                    switch_items, item_play_allowed, prizes_needed
                )
            ]
            for j, replacement in enumerate(others):
                rest = others[:j] + others[j + 1 :]
                if not wounded.retreat_blocked:
                    for energy_left in retreat_payment_remainders(
                        wounded.energy_cards, wounded.retreat_cost
                    ):
                        outgoing = replace(wounded, energy_cards=energy_left)
                        replies.append(
                            minimum_attacks(
                                replacement, tuple(sorted((outgoing,) + rest)),
                                remaining_gusts, switch_items,
                                item_play_allowed, prizes_needed
                            )
                        )
                if switch_items and item_play_allowed:
                    replies.append(
                        minimum_attacks(
                            replacement, tuple(sorted((wounded,) + rest)),
                            remaining_gusts, switch_items - 1,
                            item_play_allowed, prizes_needed
                        )
                    )
            costs.append(1 + max(replies))
        elif target.prize >= prizes_needed or not others:
            costs.append(1)
        else:
            costs.append(
                1 + max(
                    minimum_attacks(
                        promoted, others[:j] + others[j + 1 :],
                        remaining_gusts, switch_items,
                        item_play_allowed, prizes_needed - target.prize
                    )
                    for j, promoted in enumerate(others)
                )
            )
    return min(costs)
