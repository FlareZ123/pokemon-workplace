from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

# The bundled card database already marks many historical Expanded bans, but its
# legality metadata lags official 2025-2026 announcements for these prints.
# Sources are preserved in the generated result so this overlay can be audited.
OFFICIAL_BAN_OVERLAY = {
    "swsh2-22": {
        "name": "Flapple",
        "effective_date": "2025-10-10",
        "reason_key": "apple_drop",
        "source": "https://www.pokemon.com/uk/play-pokemon/about/mega-evolution/mega-evolution-banned-list-and-rule-changes-announcement",
    },
    "swsh45sv-SV013": {
        "name": "Flapple",
        "effective_date": "2025-10-10",
        "reason_key": "apple_drop",
        "source": "https://www.pokemon.com/uk/play-pokemon/about/mega-evolution/mega-evolution-banned-list-and-rule-changes-announcement",
    },
    "swsh10tg-TG02": {
        "name": "Flapple",
        "effective_date": "2025-10-10",
        "reason_key": "apple_drop",
        "source": "https://www.pokemon.com/uk/play-pokemon/about/mega-evolution/mega-evolution-banned-list-and-rule-changes-announcement",
    },
    "swshp-SWSH022": {
        "name": "Flapple",
        "effective_date": "2025-10-10",
        "reason_key": "apple_drop",
        "source": "https://www.pokemon.com/uk/play-pokemon/about/mega-evolution/mega-evolution-banned-list-and-rule-changes-announcement",
    },
    "swsh7-83": {
        "name": "Medicham V",
        "effective_date": "2026-04-10",
        "reason_key": "yoga_loop",
        "source": "https://www.pokemon.com/uk/play-pokemon/about/mega-evolution/mega-evolution-perfect-order-banned-list-and-rule-changes-announcement",
    },
    "swsh7-185": {
        "name": "Medicham V",
        "effective_date": "2026-04-10",
        "reason_key": "yoga_loop",
        "source": "https://www.pokemon.com/uk/play-pokemon/about/mega-evolution/mega-evolution-perfect-order-banned-list-and-rule-changes-announcement",
    },
    "swsh7-186": {
        "name": "Medicham V",
        "effective_date": "2026-04-10",
        "reason_key": "yoga_loop",
        "source": "https://www.pokemon.com/uk/play-pokemon/about/mega-evolution/mega-evolution-perfect-order-banned-list-and-rule-changes-announcement",
    },
}

TOURNAMENT_BAN_RULE_FRAGMENT = "cannot be used at official tournaments"

GAMEPLAY_KEYS = (
    "name",
    "supertype",
    "subtypes",
    "hp",
    "types",
    "evolvesFrom",
    "abilities",
    "attacks",
    "rules",
    "ancientTrait",
    "weaknesses",
    "resistances",
    "retreatCost",
    "convertedRetreatCost",
)


def gameplay_fingerprint(card: dict[str, Any]) -> str:
    payload = {key: card.get(key) for key in GAMEPLAY_KEYS if key in card}
    encoded = json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()[:16]


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def has_tournament_ban_rule(card: dict[str, Any]) -> bool:
    return any(
        TOURNAMENT_BAN_RULE_FRAGMENT in rule.lower()
        for rule in (card.get("rules") or [])
    )


def classify_effective_legality(card: dict[str, Any]) -> tuple[str, str]:
    card_id = card["id"]
    database_status = (card.get("legalities") or {}).get("expanded")
    if card_id in OFFICIAL_BAN_OVERLAY:
        return "Banned", "official_overlay"
    if database_status == "Banned":
        return "Banned", "database"
    if has_tournament_ban_rule(card):
        return "Banned", "card_text_tournament_ban"
    if database_status == "Legal":
        return "Legal", "database"
    return "Legal", "set_fallback"


def build(resources_root: Path) -> dict[str, Any]:
    sets = load_json(resources_root / "sets" / "en.json")
    set_by_id = {entry["id"]: entry for entry in sets}
    expanded_sets = {
        entry["id"]
        for entry in sets
        if (entry.get("legalities") or {}).get("expanded") == "Legal"
    }

    cards: list[dict[str, Any]] = []
    overlay_seen: set[str] = set()

    for path in sorted((resources_root / "cards" / "en").glob("*.json")):
        set_id = path.stem
        if set_id not in expanded_sets:
            continue
        set_meta = set_by_id[set_id]
        for raw in load_json(path):
            card_id = raw["id"]
            database_status = (raw.get("legalities") or {}).get("expanded")
            overlay = OFFICIAL_BAN_OVERLAY.get(card_id)
            if overlay is not None:
                overlay_seen.add(card_id)
                if raw.get("name") != overlay["name"]:
                    raise ValueError(f"Overlay name mismatch for {card_id}: {raw.get('name')!r}")

            effective_status, legality_source = classify_effective_legality(raw)

            cards.append(
                {
                    "id": card_id,
                    "name": raw.get("name"),
                    "set_id": set_id,
                    "set_name": set_meta.get("name"),
                    "series": set_meta.get("series"),
                    "release_date": set_meta.get("releaseDate"),
                    "supertype": raw.get("supertype"),
                    "database_status": database_status,
                    "unlimited_status": (raw.get("legalities") or {}).get("unlimited"),
                    "effective_status": effective_status,
                    "legality_source": legality_source,
                    "fingerprint": gameplay_fingerprint(raw),
                    "overlay": overlay,
                    "tournament_ban_rule": has_tournament_ban_rule(raw),
                }
            )

    missing_overlay = sorted(set(OFFICIAL_BAN_OVERLAY) - overlay_seen)
    if missing_overlay:
        raise ValueError(f"Overlay card IDs not found in database: {missing_overlay}")

    status_counts = Counter(card["effective_status"] for card in cards)
    source_counts = Counter(card["legality_source"] for card in cards)
    supertype_counts = Counter(card["supertype"] for card in cards if card["effective_status"] == "Legal")
    series_counts = Counter(card["series"] for card in cards if card["effective_status"] == "Legal")

    by_name: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for card in cards:
        by_name[card["name"]].append(card)

    mixed_legality_names = []
    for name, rows in sorted(by_name.items()):
        statuses = {row["effective_status"] for row in rows}
        if statuses == {"Legal", "Banned"}:
            mixed_legality_names.append(
                {
                    "name": name,
                    "banned_print_ids": [row["id"] for row in rows if row["effective_status"] == "Banned"],
                    "legal_print_ids": [row["id"] for row in rows if row["effective_status"] == "Legal"],
                    "distinct_gameplay_fingerprints": len({row["fingerprint"] for row in rows}),
                }
            )

    banned_rows = [card for card in cards if card["effective_status"] == "Banned"]
    banned_by_name: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for card in banned_rows:
        banned_by_name[card["name"]].append(card)

    database_mismatches = [
        {
            "id": card["id"],
            "name": card["name"],
            "database_status": card["database_status"],
            "effective_status": card["effective_status"],
            "effective_date": card["overlay"]["effective_date"],
            "source": card["overlay"]["source"],
        }
        for card in cards
        if card["legality_source"] == "official_overlay" and card["database_status"] != "Banned"
    ]

    card_text_tournament_bans = [
        {
            "id": card["id"],
            "name": card["name"],
            "set_id": card["set_id"],
            "database_status": card["database_status"],
            "unlimited_status": card["unlimited_status"],
        }
        for card in cards
        if card["legality_source"] == "card_text_tournament_ban"
    ]

    return {
        "scope": {
            "format": "paper Expanded",
            "policy": "Black & White Series onward, current Expanded bans, and explicit official-tournament exclusions",
            "expanded_set_count": len(expanded_sets),
            "earliest_expanded_set_release": min(set_by_id[sid]["releaseDate"] for sid in expanded_sets),
            "latest_expanded_set_release": max(set_by_id[sid]["releaseDate"] for sid in expanded_sets),
        },
        "counts": {
            "prints_total": len(cards),
            "prints_by_effective_status": dict(sorted(status_counts.items())),
            "legality_source": dict(sorted(source_counts.items())),
            "legal_unique_names": len({card["name"] for card in cards if card["effective_status"] == "Legal"}),
            "banned_unique_names": len(banned_by_name),
            "legal_distinct_gameplay_fingerprints": len({card["fingerprint"] for card in cards if card["effective_status"] == "Legal"}),
            "legal_prints_by_supertype": dict(sorted(supertype_counts.items())),
            "legal_prints_by_series": dict(sorted(series_counts.items())),
        },
        "database_mismatches": database_mismatches,
        "card_text_tournament_bans": card_text_tournament_bans,
        "mixed_legality_names": mixed_legality_names,
        "banned_cards": {
            name: [
                {
                    "id": row["id"],
                    "set_id": row["set_id"],
                    "set_name": row["set_name"],
                    "database_status": row["database_status"],
                    "legality_source": row["legality_source"],
                    "effective_date": row["overlay"]["effective_date"] if row["overlay"] else None,
                    "source": row["overlay"]["source"] if row["overlay"] else None,
                }
                for row in sorted(rows, key=lambda item: item["id"])
            ]
            for name, rows in sorted(banned_by_name.items())
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a reproducible paper Expanded legality baseline from the bundled card database.")
    parser.add_argument("--resources-root", type=Path, default=Path("resources"))
    parser.add_argument("--output", type=Path, default=Path("results/expanded_legality_baseline/summary.json"))
    args = parser.parse_args()

    result = build(args.resources_root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    lock_path = args.output.with_suffix(args.output.suffix + ".lock")
    with lock_path.open("a+b") as lock_file:
        if os.name == "nt":
            import msvcrt

            msvcrt.locking(lock_file.fileno(), msvcrt.LK_LOCK, 1)
        else:
            import fcntl

            fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)

        tmp_path: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w", encoding="utf-8", dir=args.output.parent, delete=False
            ) as tmp_file:
                tmp_file.write(payload)
                tmp_file.flush()
                os.fsync(tmp_file.fileno())
                tmp_path = Path(tmp_file.name)
            os.replace(tmp_path, args.output)
        finally:
            if tmp_path is not None and tmp_path.exists():
                tmp_path.unlink()

    print(json.dumps(result["counts"], indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
