"""Enumerate post-damage Energy backlash ordering without losing card identities.

The Pokémon that took attack damage chooses the order of its concurrent
step-6 damage reactions. Selection of a specific Energy and target Bench
remains a caller-supplied policy.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import permutations
from typing import Callable

from physical_copy_damage_reaction_bridge import PhysicalCopyReactionResult
from physical_energy_backlash_reactions import (
    EnergyReactionOutcome,
    PrintedEnergyReaction,
    apply_physical_energy_backlash,
)


EnergyChoicePolicy = Callable[
    [PhysicalCopyReactionResult, PrintedEnergyReaction],
    tuple[str | None, str | None],
]


@dataclass(frozen=True)
class EnergyReactionOrderResult:
    ordered_reactions: tuple[PrintedEnergyReaction, ...]
    step_outcomes: tuple[EnergyReactionOutcome, ...]
    final: PhysicalCopyReactionResult


def enumerate_energy_reaction_orders(
    initial: PhysicalCopyReactionResult,
    reactions: tuple[PrintedEnergyReaction, ...],
    *,
    choose: EnergyChoicePolicy,
) -> tuple[EnergyReactionOrderResult, ...]:
    """Apply each ordering as an immutable resource transition.

    The sequence engine enumerates trigger order; the caller supplies the
    card selection and receiving Bench per source. The input reactions
    must already have passed source and event eligibility validation.
    """

    results = []
    for ordered in permutations(reactions):
        state = initial
        steps = []
        for reaction in ordered:
            energy_instance_id, destination_pokemon_id = choose(state, reaction)
            state, outcome = apply_physical_energy_backlash(
                state,
                reaction,
                energy_instance_id=energy_instance_id,
                destination_pokemon_id=destination_pokemon_id,
            )
            steps.append(outcome)
        results.append(EnergyReactionOrderResult(ordered, tuple(steps), state))
    return tuple(results)
