"""Canonical removed-card zone histogram for an already-prepared KO batch.

For one fixed pending batch and fixed survivor promotion, these signatures
distinguish exactly the terminal exchangeable-count states reachable through
destination-only, first-assignment KO routing. The signature never replaces
full physical-state validation for untrusted rules inputs.
"""

from __future__ import annotations

from collections import Counter
from typing import Mapping

from simultaneous_knockout_conservation import PendingKnockOutBatch

DISCARD = "discard"
BOARD_BOUND_ZONES = frozenset({"in_play", "attached"})


def terminal_zone_signature(
    pending: PendingKnockOutBatch,
    *,
    destinations: Mapping[str, str],
) -> tuple[tuple[str, str, int], ...]:
    """Count removed cards by (gameplay card-class, resolved destination).

    Only cards in the specified pending KO batch can be assigned destinations.
    Unassigned removed cards go to discard. Every removed card is materialized
    in the source ledger, and card-class equivalence follows that ledger's
    already-chosen semantic resolution.
    """
    board = pending.state.board
    assert board is not None
    if any(not zone or zone in BOARD_BOUND_ZONES for zone in destinations.values()):
        raise ValueError("invalid KO destination zone")

    removed_ids = tuple(
        instance_id
        for pokemon in board.pokemon
        if pokemon.pokemon_id in pending.knocked_out_ids
        for instance_id in (
            *(card.card_id for card in pokemon.stack),
            *(card.card_id for card in pokemon.attachments),
        )
    )
    if not set(destinations) <= set(removed_ids):
        raise ValueError("KO routes must refer only to removed physical instances")
    counts = Counter(
        (
            pending.state.ledger.instance(instance_id).card_class,
            destinations.get(instance_id, DISCARD),
        )
        for instance_id in removed_ids
    )
    return tuple(sorted((card_class, zone, count) for (card_class, zone), count in counts.items()))
