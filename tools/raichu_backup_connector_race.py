"""Exact one-draw connector race for Harto Raichu's backup Gladion.

Conditioning:
- visible Gladion has already been discarded for Quick Ball;
- Quick Ball found Crobat V and shuffled the remaining deck;
- the search established that Alolan Raichu is Prized;
- backup Gladion, Computer Search, and Forest Seal Stone are all still unresolved
  rather than already exposed in the current hand.

The 50 unresolved positions are five remaining Prize slots and 45 post-search
deck positions. Dark Asset exposes exactly the first deck position.

A drawn Computer Search or Forest Seal Stone can convert into the backup Gladion
only if the connector's external execution gate is live and the backup itself is
in one of the other deck positions.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BackupConnectorRaceResult:
    unresolved_cards: int
    remaining_prize_slots: int
    post_search_deck_size: int
    direct_backup_draw: float
    computer_search_rescue: float
    forest_seal_rescue: float
    union_access: float
    backup_in_deck_ceiling: float
    topology_minus_union: float


def backup_connector_race(
    *,
    unresolved_cards: int = 50,
    remaining_prize_slots: int = 5,
    post_search_deck_size: int = 45,
    computer_gate_live: bool = True,
    forest_seal_gate_live: bool = True,
) -> BackupConnectorRaceResult:
    """Return exact access through one Dark Asset exposure plus two connectors."""

    if unresolved_cards < 3:
        raise ValueError("at least three unresolved cards are required")
    if remaining_prize_slots < 0 or post_search_deck_size <= 0:
        raise ValueError("Prize slots must be non-negative and deck must be non-empty")
    if remaining_prize_slots + post_search_deck_size != unresolved_cards:
        raise ValueError(
            "remaining Prize slots plus post-search deck must equal unresolved cards"
        )

    direct = 1.0 / unresolved_cards
    connector = (
        1.0
        / unresolved_cards
        * (post_search_deck_size - 1)
        / (unresolved_cards - 1)
    )
    computer = connector if computer_gate_live else 0.0
    forest = connector if forest_seal_gate_live else 0.0
    union = direct + computer + forest
    ceiling = post_search_deck_size / unresolved_cards

    return BackupConnectorRaceResult(
        unresolved_cards=unresolved_cards,
        remaining_prize_slots=remaining_prize_slots,
        post_search_deck_size=post_search_deck_size,
        direct_backup_draw=direct,
        computer_search_rescue=computer,
        forest_seal_rescue=forest,
        union_access=union,
        backup_in_deck_ceiling=ceiling,
        topology_minus_union=ceiling - union,
    )
