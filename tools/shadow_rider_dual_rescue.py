"""Conditional Shadow Rider dual escape channels: Latias and Float Stone.

A persistent Garbotoxin Ability lock suppresses Skyliner if opponent's
Garbodor has ANY Tool attached. Jamming Tower blanks Tool effects but does
not detach the Tool, so it does not satisfy the condition for disabling
Garbotoxin. Stadiums Path to the Peak/Jamming Tower are mutually exclusive.
"""
from functools import lru_cache

from tools.shadow_rider_guzma_damage import RETREAT_COST, max_geist_damage


@lru_cache(maxsize=None)
def max_two_prize_ko(energy: tuple[int, ...], *, latias_present: bool,
                     garbotoxin_active: bool, stadium: str,
                     float_held: bool = False, float_owner: int = -1,
                     tool_play_allowed: bool = True,
                     target_hp: int = 210) -> tuple[int, tuple[str, ...]]:
    """Maximize KO on opposing Benched 210HP 2-Prize target with held Guzma."""
    assert stadium in ('none','path_to_peak','jamming_tower')
    assert len(energy)==6 and all(0 <= e <= 11 for e in energy)
    assert -1 <= float_owner < 6
    assert not (float_held and float_owner >= 0)

    @lru_cache(maxsize=None)
    def explore(e, active, gusted, retreated, supported, held, tool_owner):
        attackable=active<3 and e[active]>=3
        ko=gusted and attackable and max_geist_damage(e)>=target_hp
        best=(2 if ko else 0,('Max Geist 2Prize KO' if ko else 'no 2Prize KO',))

        if held and tool_play_allowed and tool_owner == -1:
            for i in range(6):
                score, path=explore(e, active, gusted, retreated, supported, False, i)
                if score>best[0]:best=(score,(f'attach Float Stone own{i}',)+path)

        if not retreated:
            skyliner = latias_present and not garbotoxin_active and stadium!='path_to_peak'
            stone = tool_owner==active and stadium!='jamming_tower'
            cost = 0 if stone or (skyliner and active>=3) else (
                2 if latias_present and active==5 else RETREAT_COST[active])
            if e[active]>=cost:
                update=list(e)
                update[active]-=cost
                for i in range(6):
                    if i!=active:
                        score,path=explore(tuple(update),i,gusted,True,supported,held,tool_owner)
                        if score>best[0]:best=(score,(f'retreat own{active}->own{i} pay{cost}',)+path)

        if not supported:
            for i in range(6):
                if i!=active:
                    score,path=explore(e,i,True,retreated,True,held,tool_owner)
                    if score>best[0]:best=(score,(f'Guzma opponent Bench, own{active}->own{i}',)+path)
        return best

    return explore(energy,0,False,False,False,float_held,float_owner)
