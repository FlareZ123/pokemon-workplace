"""Adversarial gust endgame with bounded opponent switching after non-KO hits.

Each escape token licenses one voluntary opponent switch on their intervening
turn after an attack leaves their Active alive. The attacker still uses at most
one gust per attack turn. KO promotion is free and does not spend an escape.
No healing, new Pokemon, Energy payment, or defender damage output is modeled.
"""
from functools import lru_cache
from tools.durable_gust_minimax import Pokemon


@lru_cache(None)
def minimum_attacks(
    active: Pokemon,
    bench: tuple[Pokemon, ...],
    gusts: int,
    escapes: int,
    prizes_needed: int = 6,
) -> int:
    actions = [(active, bench, gusts)]
    if gusts:
        for i, target in enumerate(bench):
            actions.append(
                (target, tuple(sorted((active,) + bench[:i] + bench[i + 1 :])), gusts - 1)
            )

    costs = []
    for target, other, next_gusts in actions:
        reward, hits = target
        if hits > 1:
            wounded = (reward, hits - 1)
            # Before the attacker's next turn, defender can leave the
            # damaged target Active or pay one escape to switch it away.
            continuations = [
                minimum_attacks(wounded, other, next_gusts, escapes, prizes_needed)
            ]
            if escapes:
                continuations.extend(
                    minimum_attacks(
                        replacement,
                        tuple(sorted((wounded,) + other[:j] + other[j + 1 :])),
                        next_gusts,
                        escapes - 1,
                        prizes_needed,
                    )
                    for j, replacement in enumerate(other)
                )
            costs.append(1 + max(continuations))
        elif reward >= prizes_needed or not other:
            costs.append(1)
        else:
            costs.append(
                1 + max(
                    minimum_attacks(
                        replacement,
                        other[:j] + other[j + 1 :],
                        next_gusts,
                        escapes,
                        prizes_needed - reward,
                    )
                    for j, replacement in enumerate(other)
                )
            )
    return min(costs)
