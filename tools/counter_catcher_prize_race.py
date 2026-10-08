"""Counter Catcher versus Boss under an exogenous opponent Prize-clock scenario.

An attacker with 1..6 remaining Prize cards KOs exactly one defending Pokemon
per attack turn. Defender chooses its replacement Active after every KO.
Before the attacker's next turn, the defender takes exactly opponent_pace
Prize cards through a separately assumed opponent attack (0/1/2 per turn).
If this empties the opponent's Prizes before the attacker wins, attacker loses.

Counter Catcher can gust only when attacker Prizes > defender Prizes at the
current attack-turn start. Boss is unconditional. The model deliberately
avoids simulating whether the defender can make those KOs; this is a
conditional, deterministic Prize-clock sensitivity analysis.
"""
from functools import lru_cache

IMPOSSIBLE = 1000


@lru_cache(None)
def attacks_to_win(
    active: int,
    bench: tuple[int, ...],
    gusts: int,
    our_prizes: int,
    opponent_prizes: int,
    opponent_pace: int,
    source: str = "counter_catcher",
) -> int:
    if source not in ("counter_catcher", "boss"):
        raise ValueError("source must be counter_catcher or boss")
    if not (0 <= opponent_pace <= 2):
        raise ValueError("Opponent pace must be 0, 1, or 2 Prizes per turn")
    if our_prizes <= 0:
        return 0
    if opponent_prizes <= 0:
        return IMPOSSIBLE
    if not bench:
        return 1

    choices = [(active, bench, gusts)]
    if gusts and (source == "boss" or our_prizes > opponent_prizes):
        for i, reward in enumerate(bench):
            survivors = tuple(sorted((active,) + bench[:i] + bench[i + 1:]))
            choices.append((reward, survivors, gusts - 1))

    scores = []
    for reward, survivors, remaining_gusts in choices:
        if reward >= our_prizes or not survivors:
            scores.append(1)
            continue

        next_opp_prizes = opponent_prizes - opponent_pace
        if next_opp_prizes <= 0:
            scores.append(IMPOSSIBLE)
            continue

        worst_next = max(
            attacks_to_win(
                promoted,
                survivors[:i] + survivors[i + 1:],
                remaining_gusts,
                our_prizes - reward,
                next_opp_prizes,
                opponent_pace,
                source,
            )
            for i, promoted in enumerate(survivors)
        )
        scores.append(IMPOSSIBLE if worst_next >= IMPOSSIBLE else 1 + worst_next)
    return min(scores)
