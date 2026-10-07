"""Physical Gladion resolution on an ordered Prize topology.

The transition composes with TopPrizePhysicalState. One selected face-down Prize
instance moves to hand, the played Gladion instance moves from hand into Prize,
and every remaining Prize instance is shuffled into a uniformly random physical
position. The deck top is unchanged and all remaining Prize cards become face down.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import permutations
from math import factorial

from identity_materialization import assert_conserved, move_instance
from top_prize_physical_bridge import TopPrizePhysicalState


@dataclass(frozen=True)
class GladionPhysicalOutcome:
    """One exact post-shuffle physical world and its probability."""

    selected_prize_instance_id: str
    probability: float
    physical_before: TopPrizePhysicalState
    physical_after: TopPrizePhysicalState


def resolve_gladion_physical(
    state: TopPrizePhysicalState,
    *,
    gladion_instance_id: str,
    selected_position: int,
) -> tuple[GladionPhysicalOutcome, ...]:
    """Enumerate exact uniformly random post-shuffle Prize topologies.

    The caller chooses one face-down Prize position after the acting player has
    inspected their face-down Prize cards. This kernel resolves only material
    movement and the mandatory shuffle, leaving observer knowledge and selection
    policy to a separate belief layer.
    """

    if not 0 <= selected_position < len(state.prize_instance_ids):
        raise IndexError("Prize position out of range")
    if state.face_up[selected_position]:
        raise ValueError("Gladion must select a face-down Prize card")

    gladion = state.ledger.instance(gladion_instance_id)
    if gladion.zone != "hand":
        raise ValueError("Gladion must be played from hand")
    if gladion_instance_id in state.prize_instance_ids:
        raise ValueError("played Gladion cannot already occupy a Prize slot")

    selected = state.prize_instance_ids[selected_position]

    ledger = move_instance(state.ledger, selected, "hand")
    ledger = move_instance(ledger, gladion_instance_id, "prize")
    assert_conserved(state.ledger, ledger)

    remaining = list(state.prize_instance_ids)
    remaining[selected_position] = gladion_instance_id
    prize_count = len(remaining)
    probability = 1.0 / factorial(prize_count)

    outcomes = tuple(
        GladionPhysicalOutcome(
            selected_prize_instance_id=selected,
            probability=probability,
            physical_before=state,
            physical_after=TopPrizePhysicalState(
                ledger,
                state.top_instance_id,
                ordering,
                (False,) * prize_count,
            ),
        )
        for ordering in permutations(remaining)
    )

    if abs(sum(outcome.probability for outcome in outcomes) - 1.0) > 1e-12:
        raise AssertionError("Gladion shuffle probability mass does not sum to one")
    return outcomes
