"""Live opposing Active-only versus Stadium Ability lock during Guzma pivot.

A source-faithful bounded attacking turn: Latias ex grants no Retreat Cost to
our Basics if its Ability is live. Active Galarian Weezing disables it only
until the Weezing is gusted out; Path to the Peak continues to suppress it.
"""
from functools import lru_cache

from tools.shadow_rider_guzma_damage import RETREAT_COST, max_geist_damage


@lru_cache(maxsize=None)
def max_two_prize_gust(energy: tuple[int, ...], *, latias_on_bench: bool,
                       source: str = 'guzma', lock: str = 'none',
                       target_hp: int = 210) -> tuple[int, tuple[str, ...]]:
    """Best immediate two-Prize KO under a dynamic Ability-lock state."""
    assert len(energy)==6 and all(0 <= amount <= 11 for amount in energy)
    assert source in ('guzma','boss')
    assert lock in ('none','active_weezing','path_to_peak')

    @lru_cache(maxsize=None)
    def solve(e, active, gusted, retreated, supported):
        attack_ready=active in (0,1,2) and e[active]>=3
        knockout=gusted and attack_ready and max_geist_damage(e)>=target_hp
        best=(2 if knockout else 0,('Max Geist into gusted 2Prize target' if knockout else 'no target KO',))
        if not retreated:
            # Gust removes Neutralizing Gas by moving its source off Active.
            latias_works=latias_on_bench and (lock=='none' or (lock=='active_weezing' and gusted))
            cost=0 if latias_works and active in (3,4,5) else RETREAT_COST[active]
            if e[active]>=cost:
                after=list(e)
                after[active]-=cost
                for other in range(6):
                    if other!=active:
                        reward,trace=solve(tuple(after),other,gusted,True,supported)
                        if reward>best[0]:
                            best=(reward,(f'retreat own{active}->own{other}, pay{cost}',)+trace)
        if not supported:
            own_options=(active,) if source=='boss' else tuple(i for i in range(6) if i!=active)
            for other in own_options:
                reward,trace=solve(e,other,True,retreated,True)
                if reward>best[0]:
                    best=(reward,(f'{source} gust opponent; own{active}->own{other}',)+trace)
        return best

    return solve(energy,0,False,False,False)
