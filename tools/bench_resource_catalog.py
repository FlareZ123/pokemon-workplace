from __future__ import annotations

import argparse
import json
import os
import re
import tempfile
from pathlib import Path
from typing import Any, Iterable

from build_expanded_legality_baseline import OFFICIAL_BAN_OVERLAY

BENCH_ENTRY_RE = re.compile(r"when you play this pok[eé]mon from your hand onto your bench", re.IGNORECASE)
RESOURCE_ACCESS_RE = re.compile(
    r"search your deck|draw cards|draw \d|put (?:a|\d|up to \d) .* from your discard pile into your hand|"
    r"put a supporter card from your discard pile into your hand|put \d .* into your hand",
    re.IGNORECASE,
)

CLEANUP_PATTERNS = [
    re.compile(r"put 1 of your pok[eé]mon.*into your hand", re.IGNORECASE),
    re.compile(r"put 1 of your pok[eé]mon in play into your hand", re.IGNORECASE),
    re.compile(r"put 1 pok[eé]mon into your hand", re.IGNORECASE),
    re.compile(r"return 1 of your pok[eé]mon.*to your hand", re.IGNORECASE),
    re.compile(r"shuffle 1 of your pok[eé]mon.*into your deck", re.IGNORECASE),
    re.compile(r"discard up to 2 of your benched pok[eé]mon", re.IGNORECASE),
    re.compile(r"discard 1 of your benched pok[eé]mon v", re.IGNORECASE),
]


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def iter_legal_cards(resources_root: Path) -> Iterable[dict[str, Any]]:
    sets = load_json(resources_root / "sets" / "en.json")
    expanded_sets = {
        entry["id"] for entry in sets if (entry.get("legalities") or {}).get("expanded") == "Legal"
    }
    for path in sorted((resources_root / "cards" / "en").glob("*.json")):
        if path.stem not in expanded_sets:
            continue
        for card in load_json(path):
            status = (card.get("legalities") or {}).get("expanded")
            if card["id"] in OFFICIAL_BAN_OVERLAY or status == "Banned":
                continue
            yield card


def normalize_space(text: str) -> str:
    return " ".join(text.split())


def effect_fragments(card: dict[str, Any]) -> list[str]:
    parts = list(card.get("rules") or [])
    parts.extend(ability.get("text", "") for ability in card.get("abilities") or [])
    parts.extend(attack.get("text", "") for attack in card.get("attacks") or [])
    return [normalize_space(part) for part in parts]


def capacity_effect(card: dict[str, Any]) -> dict[str, Any] | None:
    text = ""
    for fragment in effect_fragments(card):
        lower_fragment = fragment.lower()
        if (
            "can have up to 8 pokémon on" in lower_fragment
            or "can have 8 pokémon on" in lower_fragment
            or "can't have more than 4 benched pokémon" in lower_fragment
            or "can't have more than 3 benched pokémon" in lower_fragment
        ):
            text = fragment
            break
    if not text:
        return None
    lower = text.lower()
    if "can have up to 8 pokémon on" in lower or "can have 8 pokémon on" in lower:
        cap = 8
        effect_type = "extension"
    elif "can't have more than 4 benched pokémon" in lower:
        cap = 4
        effect_type = "restriction"
    elif "can't have more than 3 benched pokémon" in lower:
        cap = 3
        effect_type = "restriction"
    else:
        return None

    if "this ↓ player" in lower:
        target = "chosen_side"
    elif "each player" in lower:
        target = "both"
    elif "your opponent" in lower:
        target = "opponent"
    else:
        target = "self"

    return {
        "id": card["id"],
        "name": card["name"],
        "supertype": card.get("supertype"),
        "subtypes": card.get("subtypes") or [],
        "effect_type": effect_type,
        "cap": cap,
        "target": target,
        "text": text,
    }


def bench_entry_rows(card: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    prize_rule = any("takes 2 Prize cards" in rule for rule in card.get("rules") or [])
    for ability in card.get("abilities") or []:
        text = normalize_space(ability.get("text", ""))
        if not BENCH_ENTRY_RE.search(text):
            continue
        rows.append(
            {
                "id": card["id"],
                "name": card["name"],
                "ability": ability.get("name"),
                "text": text,
                "two_prize_rule": prize_rule,
                "resource_access": bool(RESOURCE_ACCESS_RE.search(text)),
            }
        )
    return rows


def cleanup_row(card: dict[str, Any]) -> dict[str, Any] | None:
    if card.get("supertype") != "Trainer":
        return None
    text = ""
    for fragment in card.get("rules") or []:
        normalized = normalize_space(fragment)
        if any(pattern.search(normalized) for pattern in CLEANUP_PATTERNS):
            text = normalized
            break
    if not text:
        return None
    return {
        "id": card["id"],
        "name": card["name"],
        "subtypes": card.get("subtypes") or [],
        "text": text,
    }


def dedupe(rows: list[dict[str, Any]], keys: tuple[str, ...]) -> list[dict[str, Any]]:
    grouped: dict[tuple[Any, ...], dict[str, Any]] = {}
    print_ids: dict[tuple[Any, ...], list[str]] = {}
    for row in rows:
        key = tuple(row[k] for k in keys)
        grouped.setdefault(key, {k: row[k] for k in row if k != "id"})
        print_ids.setdefault(key, []).append(row["id"])
    result = []
    for key in sorted(grouped, key=lambda item: tuple(str(x) for x in item)):
        entry = dict(grouped[key])
        entry["print_ids"] = sorted(print_ids[key])
        result.append(entry)
    return result


def build(resources_root: Path) -> dict[str, Any]:
    capacity_prints = []
    entry_prints = []
    cleanup_prints = []
    for card in iter_legal_cards(resources_root):
        effect = capacity_effect(card)
        if effect is not None:
            capacity_prints.append(effect)
        entry_prints.extend(bench_entry_rows(card))
        cleanup = cleanup_row(card)
        if cleanup is not None:
            cleanup_prints.append(cleanup)

    capacity_variants = dedupe(
        capacity_prints, ("name", "effect_type", "cap", "target", "text")
    )
    entry_variants = dedupe(
        entry_prints, ("name", "ability", "text", "two_prize_rule", "resource_access")
    )
    cleanup_variants = dedupe(cleanup_prints, ("name", "text"))

    resource_access = [row for row in entry_variants if row["resource_access"]]
    two_prize_resource_access = [row for row in resource_access if row["two_prize_rule"]]

    return {
        "scope": "paper Expanded, Black & White onward, using the repository legality overlay",
        "counts": {
            "capacity_effect_prints": len(capacity_prints),
            "capacity_effect_text_variants": len(capacity_variants),
            "bench_entry_trigger_prints": len(entry_prints),
            "bench_entry_trigger_text_variants": len(entry_variants),
            "bench_entry_resource_access_text_variants": len(resource_access),
            "bench_entry_two_prize_resource_access_text_variants": len(two_prize_resource_access),
            "cleanup_trainer_prints": len(cleanup_prints),
            "cleanup_trainer_text_variants": len(cleanup_variants),
        },
        "capacity_effects": capacity_variants,
        "bench_entry_resource_access": resource_access,
        "cleanup_trainers": cleanup_variants,
    }


def atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lock_path = path.with_suffix(path.suffix + ".lock")
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
                mode="w", encoding="utf-8", dir=path.parent, delete=False
            ) as tmp_file:
                json.dump(payload, tmp_file, indent=2, ensure_ascii=False)
                tmp_file.write("\n")
                tmp_file.flush()
                os.fsync(tmp_file.fileno())
                tmp_path = Path(tmp_file.name)
            os.replace(tmp_path, path)
        finally:
            if tmp_path is not None and tmp_path.exists():
                tmp_path.unlink()


def main() -> None:
    parser = argparse.ArgumentParser(description="Catalog Expanded Bench-capacity, Bench-entry, and cleanup resources.")
    parser.add_argument("--resources-root", type=Path, default=Path("resources"))
    parser.add_argument(
        "--output", type=Path, default=Path("results/bench_capacity_geometry/catalog.json")
    )
    args = parser.parse_args()
    result = build(args.resources_root)
    atomic_write_json(args.output, result)
    print(json.dumps(result["counts"], indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
