"""Same-turn Boss/Guzma payoff with physical own Retreat Energy payment.

A bounded decision-tree extension of guzma_forced_pivot, reusing the shared
inclusion-minimal retreat-payment enumerator. All Energy is Colorless-compatible.
"""
from dataclasses import dataclass, replace
from functools import lru_cache

from tools.typed_retreat_gust import retreat_payment_remainders


@dataclass(frozen=True)
class Attacker:
    ko_mask: int
    attack_cost: int
    retreat_cost: int
    energy_cards: tuple[int, ...]
    retreat_blocked: bool = False


@lru_cache(maxsize=None)
def best_prizes(
    attackers: tuple[Attacker, ...],
    opponent_prizes: tuple[int, int],
    supporter: str,
    switch_held: bool = False,
    items_allowed: bool = True,
) -> tuple[int, tuple[str, ...]]:
    """Maximum same-turn Prize payout, plus a trace of a feasible line."""
    if supporter not in ("boss", "guzma"):
        raise ValueError(supporter)
    if not 1 <= len(attackers) <= 6:
        raise ValueError("one to six own Pokemon are required")
    if any(p.ko_mask not in range(4) or p.attack_cost < 0 or
           p.retreat_cost < 0 or any(e not in (1, 2) for e in p.energy_cards)
           for p in attackers):
        raise ValueError("invalid attacker configuration")

    @lru_cache(maxsize=None)
    def run(board: tuple[Attacker, ...], own_active: int, opp_active: int,
            retreated: bool, supporter_played: bool, switch_played: bool):
        p = board[own_active]
        prizes = (opponent_prizes[opp_active] if
                  p.ko_mask & (1 << opp_active) and
                  sum(p.energy_cards) >= p.attack_cost else 0)
        answer = (prizes, (f"attack own#{own_active} into opp#{opp_active}",))

        if not retreated and not p.retreat_blocked:
            for remaining_energy in retreat_payment_remainders(p.energy_cards, p.retreat_cost):
                new_board = board[:own_active] + (replace(p, energy_cards=remaining_energy),) + board[own_active+1:]
                for new_active in range(len(board)):
                    if new_active == own_active:
                        continue
                    prize, trace = run(new_board, new_active, opp_active,
                                       True, supporter_played, switch_played)
                    if prize > answer[0]:
                        answer = (prize, (f"retreat own#{own_active}->own#{new_active}",) + trace)

        if switch_held and items_allowed and not switch_played:
            for new_active in range(len(board)):
                if new_active == own_active:
                    continue
                prize, trace = run(board, new_active, opp_active,
                                   retreated, supporter_played, True)
                if prize > answer[0]:
                    answer = (prize, (f"Switch own#{own_active}->own#{new_active}",) + trace)

        if not supporter_played and opp_active == 0:
            if supporter == "boss":
                targets = (own_active,)
            else:
                targets = tuple(i for i in range(len(board)) if i != own_active) or (own_active,)
            for new_active in targets:
                prize, trace = run(board, new_active, 1,
                                   retreated, True, switch_played)
                if prize > answer[0]:
                    answer = (prize, (f"{supporter} opp#1; own#{own_active}->own#{new_active}",) + trace)
        return answer

    return run(attackers, 0, 0, False, False, False)
