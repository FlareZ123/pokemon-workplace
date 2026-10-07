"""Timed access to Harto Raichu's backup Gladion after a K0 discard.

The intended conditioning is:
- the visible Gladion was already discarded before deck inspection;
- Quick Ball successfully found Crobat V, so Crobat is known to have been in deck;
- the search reveals that Alolan Raichu is Prized.

After fixing those two identities, 50 unresolved cards remain: five occupy the
remaining Prize slots and 45 occupy the post-search deck. The backup Gladion is
one singleton among those 50 unresolved positions.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BackupGladionTimingResult:
    unresolved_cards: int
    remaining_prize_slots: int
    post_search_deck_size: int
    random_exposures: int
    backup_in_deck_probability: float
    timed_access_probability: float
    topology_minus_timed_access: float


def backup_gladion_timing(
    *,
    unresolved_cards: int = 50,
    remaining_prize_slots: int = 5,
    post_search_deck_size: int = 45,
    random_exposures: int = 1,
) -> BackupGladionTimingResult:
    """Return exact singleton backup access under the stated conditioning.

    Random exposures are distinct draws without replacement from the post-search
    deck. An already-executable deterministic search connector reaches the full
    backup-in-deck topology ceiling.
    """

    if unresolved_cards <= 0:
        raise ValueError("unresolved_cards must be positive")
    if remaining_prize_slots < 0:
        raise ValueError("remaining_prize_slots must be non-negative")
    if post_search_deck_size < 0:
        raise ValueError("post_search_deck_size must be non-negative")
    if remaining_prize_slots + post_search_deck_size != unresolved_cards:
        raise ValueError(
            "remaining Prize slots plus post-search deck must equal unresolved cards"
        )
    if not 0 <= random_exposures <= post_search_deck_size:
        raise ValueError("random_exposures must fit in the post-search deck")

    backup_in_deck = post_search_deck_size / unresolved_cards
    timed_access = random_exposures / unresolved_cards

    return BackupGladionTimingResult(
        unresolved_cards=unresolved_cards,
        remaining_prize_slots=remaining_prize_slots,
        post_search_deck_size=post_search_deck_size,
        random_exposures=random_exposures,
        backup_in_deck_probability=backup_in_deck,
        timed_access_probability=timed_access,
        topology_minus_timed_access=backup_in_deck - timed_access,
    )
