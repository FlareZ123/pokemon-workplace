"""Can a held Float Stone rescue Guzma versus Vileplume and Jamming Tower?

A fixed board-state turn kernel. Tool play and Tool effect permission are
independent of Item play permission, as in current Pokemon Tool rules.
"""
from functools import lru_cache

from tools.shadow_rider_guzma_damage import RETREAT_COST, max_geist_damage


@lru_cache(maxsize=None)
def max_prizes(energy: tuple[int, ...], *, tool_in_hand: bool,
               item_allowed: bool, tool_play_allowed: bool = True,
               tool_effective: bool = True, preattached: int = -1,
               source: str = 'guzma', switch_held: bool = False,
               target_hp: int = 210) -> tuple[int, tuple[str, ...]]:
    """Return highest immediate Prize payout under all legal action orders."""
    assert len(energy) == 6 and all(0 <= count <= 11 for count in energy)
    assert source in ('guzma', 'boss')
    assert -1 <= preattached < 6

    @lru_cache(maxsize=None)
    def solve(e: tuple[int, ...], active: int, gusted: bool, retreated: bool,
              supporter_used: bool, switch_used: bool, stone_owner: int,
              stone_held: bool):
        can_attack = active < 3 and e[active] >= 3
        knockout = gusted and can_attack and max_geist_damage(e) >= target_hp
        best = (2 if knockout else 0, ('Max Geist' if can_attack else 'no KO',))

        if stone_held and tool_play_allowed and stone_owner == -1:
            for target in range(6):
                reward, trace = solve(e, active, gusted, retreated, supporter_used,
                                      switch_used, target, False)
                if reward > best[0]:
                    best = (reward, (f'attach Float Stone to own{target}',) + trace)

        if not retreated:
            cost = 0 if tool_effective and stone_owner == active else RETREAT_COST[active]
            if e[active] >= cost:
                remaining = list(e)
                remaining[active] -= cost
                for target in range(6):
                    if target != active:
                        reward, trace = solve(tuple(remaining), target, gusted, True,
                                              supporter_used, switch_used,
                                              stone_owner, stone_held)
                        if reward > best[0]:
                            best = (reward, (f'retreat own{active}->own{target}, pay{cost}',) + trace)

        if switch_held and item_allowed and not switch_used:
            for target in range(6):
                if target != active:
                    reward, trace = solve(e, target, gusted, retreated,
                                          supporter_used, True, stone_owner, stone_held)
                    if reward > best[0]:
                        best = (reward, (f'Switch own{active}->own{target}',) + trace)

        if not supporter_used:
            targets = (active,) if source == 'boss' else tuple(i for i in range(6) if i != active)
            for target in targets:
                reward, trace = solve(e, target, True, retreated, True,
                                      switch_used, stone_owner, stone_held)
                if reward > best[0]:
                    best = (reward, (f'{source} opp bench, own{active}->own{target}',) + trace)
        return best

    return solve(energy, 0, False, False, False, False, preattached, tool_in_hand)
