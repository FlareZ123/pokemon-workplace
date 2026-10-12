from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from tools.build_expanded_legality_baseline import load_json
from tools.verified_card_metadata import (
    AUDITED_CARD_METADATA_IDS,
    normalize_verified_card_metadata,
)


def build_metadata_patch_manifest(resources_root: Path) -> dict[str, Any]:
    """Compile changed fields for all 72 audited physical source prints."""
    patches: dict[str, dict[str, Any]] = {}
    by_set: dict[str, set[str]] = {}
    for card_id in AUDITED_CARD_METADATA_IDS:
        set_id = card_id.split("-", 1)[0]
        by_set.setdefault(set_id, set()).add(card_id)

    for set_id in sorted(by_set):
        source = load_json(resources_root / "cards" / "en" / f"{set_id}.json")
        for card in source:
            card_id = card["id"]
            if card_id not in by_set[set_id]:
                continue
            corrected = normalize_verified_card_metadata(card)
            changes = {
                field: {"before": card.get(field), "after": corrected.get(field)}
                for field in ("subtypes", "rules")
                if card.get(field) != corrected.get(field)
            }
            if not changes:
                raise ValueError(f"Audited print has no remaining source-data defect: {card_id}")
            patches[card_id] = changes

    if set(patches) != AUDITED_CARD_METADATA_IDS:
        raise ValueError(
            "Audited print IDs missing from archive: "
            + repr(sorted(AUDITED_CARD_METADATA_IDS - set(patches)))
        )
    return {
        "schema_version": 1,
        "source": "resources/cards/en, audited exact-print corrections",
        "patches": dict(sorted(patches.items())),
    }


def manifest_json(resources_root: Path) -> str:
    return json.dumps(
        build_metadata_patch_manifest(resources_root),
        ensure_ascii=False,
        indent=2,
    ) + "\n"
