"""Exact joint Prize-supply distribution with at most one Gladion + Item bridge.

The rescued Pokémon enters hand after Gladion. A separate Pokémon
Communication can put it into the deck, enabling Grand Tree's search.
Without that hand-to-deck step, rescuing a Prize is not sufficient for
the Grand Tree deck-search target requirement.
"""

from __future__ import annotations

from fractions import Fraction
from math import comb

from gothitelle_bootstrap_prize_availability import EvolutionSupply


def distribution_with_one_bridge(
    supply: EvolutionSupply, *,
    available: bool = True,
) -> dict[int, Fraction]:
    """Maximum complete chain count given one functional Prize-to-deck rescue.

    Assumptions: accessible Gladion and Pokémon Communication, ordinary
    Supporter and Item play permitted, no better recovery options, selected
    Prize known to Gladion, and both rescued Pokémon and the other needed
    Pokémon are directly searchable from deck after the Item resolves.
    """
    if not available:
        return supply.outcome_distribution()
    other = supply.unseen - supply.stage1 - supply.stage2
    denom = comb(supply.unseen, supply.prizes)
    result: dict[int, Fraction] = {}
    for p1 in range(supply.stage1 + 1):
        for p2 in range(supply.stage2 + 1):
            filler = supply.prizes - p1 - p2
            if not 0 <= filler <= other:
                continue
            weight = Fraction(
                comb(supply.stage1, p1)
                * comb(supply.stage2, p2)
                * comb(other, filler),
                denom,
            )
            stage1_left = supply.stage1 - p1
            stage2_left = supply.stage2 - p2
            reachable = [min(supply.action_cap, stage1_left, stage2_left)]
            if p1:
                reachable.append(min(supply.action_cap, stage1_left + 1, stage2_left))
            if p2:
                reachable.append(min(supply.action_cap, stage1_left, stage2_left + 1))
            count = max(reachable)
            result[count] = result.get(count, Fraction()) + weight
    assert sum(result.values(), Fraction()) == 1
    return dict(sorted(result.items()))


def full_supply_probability_with_one_bridge(supply: EvolutionSupply) -> Fraction:
    """When both stage categories have exactly action_cap copies.

    With a single rescue, reaching every desired chain means that at most
    one of the six Prize cards is from the union of required Pokémon.
    """
    if supply.stage1 != supply.action_cap or supply.stage2 != supply.action_cap:
        raise ValueError("Full-supply closed form requires equal target/card counts")
    rest = supply.unseen - supply.stage1 - supply.stage2
    n = supply.prizes
    denom = comb(supply.unseen, n)
    ways_zero = comb(rest, n) if n <= rest else 0
    ways_one = (
        (supply.stage1 + supply.stage2) * comb(rest, n - 1)
        if n >= 1 and n - 1 <= rest
        else 0
    )
    return Fraction(ways_zero + ways_one, denom)
