"""Source-grounded Shadow Rider Max Geist vs forced Guzma pivot, one turn.

Only Psychic Basics are attached; no new hand Energy or Ability attachment is
available. Model targeted gust to a healthy 210-HP opposing Shadow Rider V.
"""
from functools import lru_cache

# Champion's six in-play Pokemon: active VMAX; two Benched VMAX;
# Tapu Lele-GX, Lillie's Clefairy ex, and Mimikyu (all currently unready).
RETREAT_COST = (2, 2, 2, 1, 1, 1)


def max_geist_damage(psychic_energy: tuple[int, ...]) -> int:
    return 10 + 30 * sum(psychic_energy)


@lru_cache(maxsize=None)
def max_prizes(energy: tuple[int, ...], supporter: str, *, target_hp: int = 210,
               float_stone_on: int = -1, switch_held: bool = False,
               items_allowed: bool = True) -> tuple[int, tuple[str, ...]]:
    """Exact best immediate Prize payoff on fixed mirror geometry."""
    assert len(energy) == 6 and all(0 <= e <= 11 for e in energy)
    assert supporter in ('boss', 'guzma')
    assert -1 <= float_stone_on < 6

    @lru_cache(maxsize=None)
    def solve(energy: tuple[int, ...], own_active: int, opp_gusted: bool,
              retreated: bool, supported: bool, item_used: bool):
        attack_ready = own_active in (0, 1, 2) and energy[own_active] >= 3
        knockout = opp_gusted and attack_ready and max_geist_damage(energy) >= target_hp
        ans = (2 if knockout else 0, ('Max Geist' if attack_ready else 'no eligible KO',))
        if not retreated:
            cost = 0 if float_stone_on == own_active else RETREAT_COST[own_active]
            if energy[own_active] >= cost:
                after = list(energy)
                after[own_active] -= cost
                for replacement in range(6):
                    if replacement != own_active:
                        value, line = solve(tuple(after), replacement, opp_gusted,
                                            True, supported, item_used)
                        if value > ans[0]:
                            ans = (value,(f'retreat own{own_active}->own{replacement}, pay{cost}',)+line)
        if switch_held and items_allowed and not item_used:
            for replacement in range(6):
                if replacement != own_active:
                    value, line = solve(energy, replacement, opp_gusted,
                                        retreated, supported, True)
                    if value > ans[0]:
                        ans = (value,(f'Switch own{own_active}->own{replacement}',)+line)
        if not supported:
            targets = (own_active,) if supporter == 'boss' else tuple(i for i in range(6) if i != own_active)
            for new_active in targets:
                value,line = solve(energy,new_active,True,retreated,True,item_used)
                if value > ans[0]:
                    ans = (value,(f'{supporter} gust, own{own_active}->own{new_active}',)+line)
        return ans

    return solve(energy, 0, False, False, False, False)
