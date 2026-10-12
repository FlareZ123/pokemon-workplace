"""Single-turn, one-KO payoff of Boss's Orders vs Guzma forced own pivot.

Each own Pokemon has a bitmask identifying which of two opposing Pokemon it can
knock out with one attack (bit 0: initially Active, bit 1: initially Benched).
The opponent's Pokemon are worth 1..3 Prize cards. Neither damage without KO nor
future turns are valued. An optional single Switch Item may be sequenced before
or after a Supporter and is blocked by Item lock.
"""

from functools import lru_cache
from itertools import product


def best_prizes(
    own_masks: tuple[int, ...],
    opponent_prizes: tuple[int, int],
    supporter: str,
    switch_held: bool = False,
    items_allowed: bool = True,
) -> tuple[int, tuple[str, ...]]:
    """Return maximum immediate Prize payout and a legal sequence of actions.

    Own slot 0 is initially Active; others are Benched. Opposing 0 is Active,
    opposing 1 is Benched. Supporter is 'none', 'boss' or 'guzma'.
    """
    if supporter not in ("none", "boss", "guzma"):
        raise ValueError(supporter)
    if not 1 <= len(own_masks) <= 6:
        raise ValueError("own board must contain one to six Pokemon")
    if any(m not in range(4) for m in own_masks):
        raise ValueError("attack mask must be a two-bit integer")
    if any(p not in (1, 2, 3) for p in opponent_prizes):
        raise ValueError("opponent Prize values must be 1, 2 or 3")

    @lru_cache(maxsize=None)
    def explore(own_active: int, opponent_active: int,
                used_switch: bool, used_supporter: bool) -> tuple[int, tuple[str, ...]]:
        payout = (opponent_prizes[opponent_active]
                  if own_masks[own_active] & (1 << opponent_active) else 0)
        best = (payout, (f"attack own#{own_active} into opp#{opponent_active}",))

        if switch_held and items_allowed and not used_switch:
            for own_index in range(len(own_masks)):
                if own_index != own_active:
                    value, rest = explore(own_index, opponent_active, True, used_supporter)
                    candidate = value, (f"Switch own#{own_active}->own#{own_index}",) + rest
                    if candidate[0] > best[0]:
                        best = candidate

        if supporter != "none" and not used_supporter and opponent_active == 0:
            if supporter == "boss":
                new_own = (own_active,)
            else:
                # Guzma's own switch follows a successful opponent switch.
                # If the own Bench is empty, that second part cannot execute.
                new_own = tuple(i for i in range(len(own_masks)) if i != own_active)
                if not new_own:
                    new_own = (own_active,)
            for own_index in new_own:
                value, rest = explore(own_index, 1, used_switch, True)
                candidate = value, (f"{supporter} opp#1; own#{own_active}->own#{own_index}",) + rest
                if candidate[0] > best[0]:
                    best = candidate
        return best

    return explore(0, 0, False, False)


def census() -> dict:
    """Enumerate all abstract one-turn board states up to five own Bench slots."""
    counts = {}
    witnesses = {}
    switch_parity = 0
    for own_size in range(1, 7):
        for masks in product(range(4), repeat=own_size):
            for prizes in product((1, 2, 3), repeat=2):
                boss, _ = best_prizes(masks, prizes, "boss")
                guzma, _ = best_prizes(masks, prizes, "guzma")
                delta = guzma - boss
                key = (own_size, "guzma" if delta > 0 else "boss" if delta < 0 else "equal")
                counts[key] = counts.get(key, 0) + 1
                if delta:
                    witnesses.setdefault(key, (masks, prizes, boss, guzma))
                boss_with_switch, _ = best_prizes(masks, prizes, "boss", True, True)
                guzma_with_switch, _ = best_prizes(masks, prizes, "guzma", True, True)
                assert boss_with_switch == guzma_with_switch
                switch_parity += 1
    return {"counts": counts, "witnesses": witnesses, "switch_parity": switch_parity}
