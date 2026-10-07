from __future__ import annotations

from collections import Counter
from datetime import date
from pathlib import Path
from typing import Any

from tools.build_expanded_legality_baseline import classify_effective_legality, load_json

HISTORICAL_REPRINT_SOURCE = "Official 2012 Modified-Legal Reprint List"
HISTORICAL_REPRINT_DATE = date(2012, 3, 13)

NO_REFERENCE_REPRINTS: dict[str, tuple[str, ...]] = {
    "Switch": (
        "base1-95", "base4-123", "ecard1-157", "ex1-92", "ex6-102",
        "ex11-102", "ex15-83", "dp1-119", "dp3-128", "dp7-93",
    ),
    "Energy Search": (
        "base3-59", "ecard1-153", "ex1-90", "ex10-94", "ex14-86",
        "dp1-117", "dp5-90",
    ),
    "Poké Ball": (
        "base2-64", "base4-121", "ex1-86", "ex6-95", "ex10-87",
        "ex14-82", "dp1-110", "dp5-85", "pl1-113",
    ),
    "Energy Switch": (
        "ecard2-120", "ex1-82", "ex6-90", "ex10-84", "ex16-75",
        "dp1-107", "dp7-84",
    ),
    "Super Scoop Up": (
        "neo1-98", "ecard1-151", "ex6-99", "ex11-100", "dp1-115", "dp5-87",
    ),
    "Full Heal": ("ecard1-154",),
    "Recycle": ("base3-61",),
    "Double Colorless Energy": ("base1-96",),
}

NO_REFERENCE_REPRINT_IDS = frozenset(
    card_id for ids in NO_REFERENCE_REPRINTS.values() for card_id in ids
)


def _parse_release_date(value: str) -> date:
    year, month, day = (int(part) for part in value.split("/"))
    return date(year, month, day)


def summarize_historical_reprint_evidence(resources_root: Path) -> dict[str, Any]:
    sets = load_json(resources_root / "sets" / "en.json")
    set_by_id = {row["id"]: row for row in sets}
    expanded_sets = frozenset(
        row["id"] for row in sets if (row.get("legalities") or {}).get("expanded") == "Legal"
    )

    cards_by_id: dict[str, dict[str, Any]] = {}
    for path in sorted((resources_root / "cards" / "en").glob("*.json")):
        for raw in load_json(path):
            card = dict(raw)
            card["_set_id"] = path.stem
            cards_by_id[card["id"]] = card

    missing = sorted(NO_REFERENCE_REPRINT_IDS - set(cards_by_id))
    if missing:
        raise ValueError(f"Historical reprint IDs missing from database: {missing}")

    identity_errors = []
    for expected_name, ids in NO_REFERENCE_REPRINTS.items():
        for card_id in ids:
            actual = cards_by_id[card_id].get("name")
            if actual != expected_name:
                identity_errors.append((card_id, expected_name, actual))
    if identity_errors:
        raise ValueError(f"Historical reprint identity mismatch: {identity_errors}")

    legal_by_name: dict[str, list[dict[str, Any]]] = {}
    for card in cards_by_id.values():
        if card["_set_id"] not in expanded_sets:
            continue
        if classify_effective_legality(card)[0] != "Legal":
            continue
        legal_by_name.setdefault(card["name"], []).append(card)

    bridges: dict[str, dict[str, Any]] = {}
    for name, ids in NO_REFERENCE_REPRINTS.items():
        targets = legal_by_name.get(name, [])
        if not targets:
            raise ValueError(f"No current legal Expanded counterpart for {name}")
        dated_targets = [
            card
            for card in targets
            if _parse_release_date(set_by_id[card["_set_id"]]["releaseDate"])
            <= HISTORICAL_REPRINT_DATE
        ]
        if not dated_targets:
            raise ValueError(f"No BW-onward counterpart for {name} released by bridge date")
        bridges[name] = {
            "historical_print_ids": list(ids),
            "bw_onward_targets_available_by_bridge_date": sorted(
                card["id"] for card in dated_targets
            ),
            "current_legal_target_ids": sorted(card["id"] for card in targets),
        }

    supertypes = Counter(cards_by_id[card_id]["supertype"] for card_id in NO_REFERENCE_REPRINT_IDS)
    return {
        "source": HISTORICAL_REPRINT_SOURCE,
        "source_date": HISTORICAL_REPRINT_DATE.isoformat(),
        "counts": {
            "historical_no_reference_prints": len(NO_REFERENCE_REPRINT_IDS),
            "names": len(NO_REFERENCE_REPRINTS),
            "trainer_prints": supertypes["Trainer"],
            "energy_prints": supertypes["Energy"],
        },
        "prints_by_name": {
            name: len(ids) for name, ids in sorted(NO_REFERENCE_REPRINTS.items())
        },
        "bridges": bridges,
    }
