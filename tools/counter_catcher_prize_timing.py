"""Conditional Counter Catcher gust versus unconditional Boss in a six-Prize race.

Counter Catcher is an Item whose gust is playable only while the acting player
has MORE Prize cards remaining than the opponent. Taking a KO changes the
acting player's remaining Prize count before the next opportunity to play it.
The opposing Prize count is held fixed as an explicit conditional scenario.
"""
from functools import lru_cache
from tools.gust_prize_minimax import enumerate_boards, minimum_attacks


@lru_cache(None)
def counter_catcher_attacks(
    active: int,
    bench: tuple[int, ...],
    catchers: int,
    prizes_needed: int,
    opponent_prizes_remaining: int,
) -> int:
    """Minimax attack count, with prize-threshold-gated targeted Item gusts."""
    if prizes_needed <= 0:
        return 0
    if not bench:
        return 1

    actions = [(active, bench, catchers)]
    if catchers and prizes_needed > opponent_prizes_remaining:
        for i, prize in enumerate(bench):
            survivors = tuple(sorted((active,) + bench[:i] + bench[i + 1 :]))
            actions.append((prize, survivors, catchers - 1))

    scores = []
    for reward, survivors, remaining_catchers in actions:
        if reward >= prizes_needed or not survivors:
            scores.append(1)
        else:
            scores.append(
                1 + max(
                    counter_catcher_attacks(
                        promoted, survivors[:i] + survivors[i + 1 :],
                        remaining_catchers, prizes_needed - reward,
                        opponent_prizes_remaining
                    )
                    for i, promoted in enumerate(survivors)
                )
            )
    return min(scores)


def census():
    """Comparisons against two unconditional Boss gusts for opp Prizes 1..5."""
    rows = []
    for opponent_prizes in range(1, 6):
        for active, bench, values in enumerate_boards():
            boss = minimum_attacks(active, bench, 2, 6)
            one = counter_catcher_attacks(active, bench, 1, 6, opponent_prizes)
            two = counter_catcher_attacks(active, bench, 2, 6, opponent_prizes)
            rows.append((opponent_prizes, active, bench, boss, one, two))
    return tuple(rows)
