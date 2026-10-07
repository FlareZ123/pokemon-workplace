"""Catalog interactions between Prize visibility and face-down-Prize effects."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from prize_information_actions import (
    _action_class,
    _effect_rows,
    _load_legal_cards,
    _normalize,
    build_catalog,
)


def own_face_down_prize_effects(resources_root: Path) -> list[dict[str, Any]]:
    """Return deduplicated legal effects that explicitly target own face-down Prizes."""
    variants: dict[tuple[str, str, str, str], dict[str, Any]] = {}

    for card in _load_legal_cards(resources_root):
        for source, effect_name, raw_text in _effect_rows(card):
            text = _normalize(raw_text)
            if "your face-down Prize cards" not in text:
                continue

            action_class = _action_class(card, source)
            key = (action_class, card["name"], effect_name, text)
            row = variants.setdefault(
                key,
                {
                    "action_class": action_class,
                    "card_name": card["name"],
                    "effect_name": effect_name,
                    "text": text,
                    "print_ids": [],
                },
            )
            row["print_ids"].append(card["id"])

    return sorted(
        variants.values(),
        key=lambda row: (
            row["action_class"],
            row["card_name"],
            row["effect_name"],
            row["text"],
        ),
    )


def direct_exact_prize_publicity(resources_root: Path) -> dict[str, list[dict[str, Any]]]:
    """Split direct exact-Prize inspection effects into public and private modes.

    "Public" here means the text turns all Prize cards face up, making their
    identities visible on the board. "Private" means the player looks at the
    face-down Prize cards without globally turning the set face up.
    """
    catalog = build_catalog(resources_root)
    direct = [
        row
        for row in catalog["exact_variants"]
        if row["mechanism"] == "exact_prize_inspection"
    ]

    public: list[dict[str, Any]] = []
    private: list[dict[str, Any]] = []

    for row in direct:
        if "face up" in row["text"].lower():
            public.append(row)
        else:
            private.append(row)

    return {
        "public": public,
        "private": private,
    }
