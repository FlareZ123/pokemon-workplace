from __future__ import annotations

import argparse
import json
import os
import re
import tempfile
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable

from build_expanded_legality_baseline import OFFICIAL_BAN_OVERLAY


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def normalize(text: str) -> str:
    return " ".join(text.split())


def iter_legal_cards(resources_root: Path) -> Iterable[dict[str, Any]]:
    sets = load_json(resources_root / "sets" / "en.json")
    expanded_sets = {
        row["id"] for row in sets if (row.get("legalities") or {}).get("expanded") == "Legal"
    }
    for path in sorted((resources_root / "cards" / "en").glob("*.json")):
        if path.stem not in expanded_sets:
            continue
        for card in load_json(path):
            status = (card.get("legalities") or {}).get("expanded")
            if card["id"] in OFFICIAL_BAN_OVERLAY or status == "Banned":
                continue
            yield card


def is_explicit_stadium_removal(text: str) -> bool:
    lower = normalize(text).lower()
    if "stadium" not in lower:
        return False
    if "stadium cards in your discard pile" in lower or "stadium card from your discard pile" in lower:
        return False
    if "discard a stadium card from your hand" in lower or "discard any stadium cards from your hand" in lower:
        return False
    generic_replacement = (
        "discard it if another stadium comes into play",
        "discard this card if another stadium card comes into play",
        "discard this card if another stadium comes into play",
    )
    if any(phrase in lower for phrase in generic_replacement) and lower.count("discard") == 1:
        return False

    patterns = (
        r"discard (?:a|any|that|the) stadium(?: card)?(?: in play)?",
        r"discard your opponent[’']s stadium(?: card)?",
        r"stadium.*(?:put|place) (?:it|that card) in the lost zone",
        r"choose .*stadium.*(?:put|place) (?:it|that card) in the lost zone",
        r"choose .*stadium.*discard",
        r"(?:stadium(?: card)? (?:is|in)|has a stadium).*discard it",
    )
    return any(re.search(pattern, lower) for pattern in patterns)


def action_class(card: dict[str, Any], source_kind: str) -> str:
    if source_kind == "ability":
        return "Ability"
    if source_kind == "attack":
        return "Attack"
    for subtype in card.get("subtypes") or []:
        if subtype in {"Item", "Supporter"}:
            return subtype
    return "Trainer"


def card_effects(card: dict[str, Any]) -> Iterable[tuple[str, str | None, str]]:
    for rule in card.get("rules") or []:
        yield "rule", None, normalize(rule)
    for ability in card.get("abilities") or []:
        yield "ability", ability.get("name"), normalize(ability.get("text", ""))
    for attack in card.get("attacks") or []:
        yield "attack", attack.get("name"), normalize(attack.get("text", ""))


def build(resources_root: Path) -> dict[str, Any]:
    print_rows = []
    for card in iter_legal_cards(resources_root):
        if "Stadium" in (card.get("subtypes") or []):
            continue
        for source_kind, effect_name, text in card_effects(card):
            if not is_explicit_stadium_removal(text):
                continue
            cls = action_class(card, source_kind)
            print_rows.append(
                {
                    "id": card["id"],
                    "name": card["name"],
                    "action_class": cls,
                    "effect_name": effect_name,
                    "text": text,
                    "requires_bench_entry": bool(
                        cls == "Ability"
                        and re.search(
                            r"play this pok[eé]mon from your hand onto your bench",
                            text,
                            re.IGNORECASE,
                        )
                    ),
                    "ends_turn": cls == "Attack",
                    "consumes_supporter_window": cls == "Supporter",
                    "requires_item_permission": cls == "Item",
                }
            )

    grouped: dict[tuple[Any, ...], list[str]] = defaultdict(list)
    representatives: dict[tuple[Any, ...], dict[str, Any]] = {}
    keys = (
        "name",
        "action_class",
        "effect_name",
        "text",
        "requires_bench_entry",
        "ends_turn",
        "consumes_supporter_window",
        "requires_item_permission",
    )
    for row in print_rows:
        key = tuple(row[k] for k in keys)
        grouped[key].append(row["id"])
        representatives.setdefault(key, {k: row[k] for k in keys})

    variants = []
    for key in sorted(grouped, key=lambda value: tuple(str(x) for x in value)):
        entry = dict(representatives[key])
        entry["print_ids"] = sorted(grouped[key])
        variants.append(entry)

    names_by_class: dict[str, set[str]] = defaultdict(set)
    for row in variants:
        names_by_class[row["action_class"]].add(row["name"])

    return {
        "scope": "legal paper Expanded prints with explicit non-Stadium-card Stadium-removal effects",
        "counts": {
            "effect_prints": len(print_rows),
            "effect_text_variants": len(variants),
            "unique_names": len({row["name"] for row in variants}),
            "unique_names_by_action_class": {
                key: len(value) for key, value in sorted(names_by_class.items())
            },
            "bench_entry_ability_names": len(
                {row["name"] for row in variants if row["requires_bench_entry"]}
            ),
        },
        "names_by_action_class": {
            key: sorted(value) for key, value in sorted(names_by_class.items())
        },
        "variants": variants,
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
    parser = argparse.ArgumentParser(description="Catalog explicit legal Expanded Stadium-removal effects.")
    parser.add_argument("--resources-root", type=Path, default=Path("resources"))
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results/stadium_removal_channels/catalog.json"),
    )
    args = parser.parse_args()
    result = build(args.resources_root)
    atomic_write_json(args.output, result)
    print(json.dumps(result["counts"], indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
