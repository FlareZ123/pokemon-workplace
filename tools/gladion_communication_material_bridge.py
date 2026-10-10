"""Prize rescue through a physical Pokemon Communication hand-to-deck move."""

from __future__ import annotations

from dataclasses import dataclass
from gladion_physical_prize_transition import resolve_gladion_physical
from identity_materialization import IdentityLedger, assert_conserved, move_instance
from top_prize_physical_bridge import TopPrizePhysicalState


@dataclass(frozen=True)
class PhysicalBridgeOutcome:
    ledger: IdentityLedger
    prizes: tuple[str, ...]
    returned_id: str
    probability: float


def rescue_to_deck(
    state: TopPrizePhysicalState,
    *,
    gladion_id: str,
    communication_id: str,
    position: int,
    pokemon_classes: frozenset[str],
) -> tuple[PhysicalBridgeOutcome, ...]:
    """Enumerate Gladion's Prize permutations and deposit its target in deck.

    Rulebook type-restricted search permits choosing zero Pokemon afterward.
    Deck order is no longer represented after the required Item shuffle.
    """
    item = state.ledger.instance(communication_id)
    if item.zone != "hand" or item.card_name != "Pokémon Communication":
        raise ValueError("Pokemon Communication in hand is required")
    selected = state.prize_instance_ids[position]
    if state.ledger.instance(selected).card_class not in pokemon_classes:
        raise ValueError("Target must be a Pokemon")
    out = []
    for event in resolve_gladion_physical(
        state, gladion_instance_id=gladion_id, selected_position=position
    ):
        ledger = event.physical_after.ledger
        ledger = move_instance(ledger, selected, "deck")
        ledger = move_instance(ledger, communication_id, "discard")
        ledger = move_instance(ledger, state.top_instance_id, "deck")
        assert_conserved(state.ledger, ledger)
        out.append(PhysicalBridgeOutcome(
            ledger, event.physical_after.prize_instance_ids,
            selected, event.probability
        ))
    return tuple(out)
