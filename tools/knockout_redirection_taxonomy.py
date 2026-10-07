"""Classify explicit Knock Out zone-redirection texts into routing signatures."""

from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

from physical_transition_text_catalog import build


SELF_TO_HAND = "pokemon_to_hand_attached_discard"
ALL_TO_LOST = "pokemon_and_attached_to_lost_zone"
POKEMON_TO_LOST = "pokemon_to_lost_zone_attached_discard"
ATTACHED_ENERGY_TO_HAND = "attached_energy_to_hand_default_discard"


def classify_redirection(text: str) -> str | None:
    lower = text.lower()

    if (
        "put it into your hand instead of the discard pile" in lower
        and "discard all" in lower
        and "attached" in lower
    ):
        return SELF_TO_HAND

    if (
        "put that pokémon and all cards attached to it in the lost zone"
        in lower
        and "instead of the discard pile" in lower
    ):
        return ALL_TO_LOST

    if (
        "put that pokémon in the lost zone instead of the discard pile"
        in lower
        and "discard all attached cards" in lower
    ):
        return POKEMON_TO_LOST

    if (
        "energy attached to that pokémon into your hand instead of the discard pile"
        in lower
    ):
        return ATTACHED_ENERGY_TO_HAND

    return None


def build_taxonomy(resources_root: Path) -> dict[str, Any]:
    catalog = build(resources_root)
    rows = [
        row
        for row in catalog["rows"]
        if "knock_out_zone_redirection" in row["categories"]
    ]

    classified = []
    unmatched = []
    for row in rows:
        signature = classify_redirection(row["text"])
        record = {
            "card_id": row["card_id"],
            "card_name": row["card_name"],
            "source_kind": row["source_kind"],
            "source_name": row["source_name"],
            "text": row["text"],
        }
        if signature is None:
            unmatched.append(record)
        else:
            classified.append({**record, "routing_signature": signature})

    counts = Counter(row["routing_signature"] for row in classified)
    cards_by_signature = {
        signature: sorted(
            {
                row["card_id"]
                for row in classified
                if row["routing_signature"] == signature
            }
        )
        for signature in sorted(counts)
    }

    return {
        "redirection_print_text_rows": len(rows),
        "redirection_cards": len({row["card_id"] for row in rows}),
        "routing_signature_counts": dict(sorted(counts.items())),
        "cards_by_signature": cards_by_signature,
        "unmatched": unmatched,
    }
