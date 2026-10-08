"""Minimax attack counts for a bounded six-Prize gust endgame.

The opponent adversarially chooses every replacement Active after a Knock Out.
Each remaining opposing Pokemon is a one-attack KO worth 1, 2, or 3 Prizes.
A gust consumes one finite Supporter-like token on the current attack turn.
The attacker wins by taking the required Prizes OR removing all opposing Pokemon.
Neither player benches new Pokemon; no damage persists across attacks.
"""
from functools import lru_cache
from itertools import combinations_with_replacement
from typing import Iterator


@lru_cache(maxsize=None)
def minimum_attacks(
    active: int, bench: tuple[int, ...], gusts: int, prizes_needed: int = 6
) -> int:
    """Attacks needed against worst-case opponent promotions, optimal gust timing."""
    if prizes_needed <= 0:
        return 0
    if not bench:
        return 1  # Knock out the final opposing Pokemon to win.

    actions = [(active, bench, gusts)]
    if gusts:
        for i, prize in enumerate(bench):
            # Gust swaps the chosen Benched Pokemon with the current Active.
            survivors = tuple(sorted((active,) + bench[:i] + bench[i + 1 :]))
            actions.append((prize, survivors, gusts - 1))

    action_costs = []
    for prize, survivors, remaining_gusts in actions:
        if prize >= prizes_needed or not survivors:
            action_costs.append(1)
            continue
        worst_promotion = max(
            minimum_attacks(
                promoted,
                survivors[:i] + survivors[i + 1 :],
                remaining_gusts,
                prizes_needed - prize,
            )
            for i, promoted in enumerate(survivors)
        )
        action_costs.append(1 + worst_promotion)
    return min(action_costs)


def must_gust_now(
    active: int, bench: tuple[int, ...], gusts: int, prizes_needed: int = 6
) -> int:
    """Attacks if a gust is required on turn one; future decisions are optimal."""
    if not gusts or not bench:
        return minimum_attacks(active, bench, gusts, prizes_needed)

    costs = []
    for i, prize in enumerate(bench):
        survivors = tuple(sorted((active,) + bench[:i] + bench[i + 1 :]))
        if prize >= prizes_needed:
            costs.append(1)
            continue
        costs.append(
            1
            + max(
                minimum_attacks(
                    promoted,
                    survivors[:j] + survivors[j + 1 :],
                    gusts - 1,
                    prizes_needed - prize,
                )
                for j, promoted in enumerate(survivors)
            )
        )
    return min(costs)


def enumerate_boards() -> Iterator[tuple[int, tuple[int, ...], tuple[int, ...]]]:
    """All prize-multiset / Active-value classes with 2..6 Pokemon and >=6 Prizes."""
    for count in range(2, 7):
        for values in combinations_with_replacement((1, 2, 3), count):
            if sum(values) < 6:
                continue
            for active in sorted(set(values)):
                bench = list(values)
                bench.remove(active)
                yield active, tuple(bench), values
