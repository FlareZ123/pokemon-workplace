"""Catalog effects that permit multiple attacks in one Expanded turn."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from build_expanded_legality_baseline import classify_effective_legality


MULTI_ATTACK_PHRASES = (
    "may attack twice a turn",
    "may attack twice each turn",
    "may use an attack it has twice",
)


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def effect_rows(card: dict[str, Any]) -> list[tuple[str, str, str]]:
    rows: list[tuple[str, str, str]] = []
    trait = card.get("ancientTrait")
    if trait:
        rows.append(("ancient_trait", trait.get("name") or "", trait.get("text") or ""))
    for ability in card.get("abilities") or []:
        rows.append(("ability", ability.get("name") or "", ability.get("text") or ""))
    for attack in card.get("attacks") or []:
        rows.append(("attack", attack.get("name") or "", attack.get("text") or ""))
    for index, rule in enumerate(card.get("rules") or []):
        rows.append(("rule", f"rule_{index}", rule))
    return rows


def build(resources_root: Path) -> dict[str, Any]:
    sets = load_json(resources_root / "sets" / "en.json")
    expanded_sets = {
        row["id"]
        for row in sets
        if (row.get("legalities") or {}).get("expanded") == "Legal"
    }

    instances: list[dict[str, Any]] = []
    for path in sorted((resources_root / "cards" / "en").glob("*.json")):
        if path.stem not in expanded_sets:
            continue
        for card in load_json(path):
            status, _ = classify_effective_legality(card)
            if status != "Legal":
                continue
            for source_kind, effect_name, text in effect_rows(card):
                lowered = text.lower()
                if not any(phrase in lowered for phrase in MULTI_ATTACK_PHRASES):
                    continue
                instances.append(
                    {
                        "print_id": card["id"],
                        "card_name": card["name"],
                        "source_kind": source_kind,
                        "effect_name": effect_name,
                        "text": text,
                        "ability_suppression_sensitive": source_kind == "ability",
                        "requires_festival_grounds": "festival grounds is in play" in lowered,
                    }
                )

    grouped: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in instances:
        grouped[(row["source_kind"], row["effect_name"], row["text"])].append(row)

    signatures = []
    for (source_kind, effect_name, text), rows in sorted(grouped.items()):
        signatures.append(
            {
                "source_kind": source_kind,
                "effect_name": effect_name,
                "text": text,
                "print_ids": sorted(row["print_id"] for row in rows),
                "card_names": sorted({row["card_name"] for row in rows}),
                "ability_suppression_sensitive": source_kind == "ability",
                "requires_festival_grounds": any(
                    row["requires_festival_grounds"] for row in rows
                ),
            }
        )

    source_counts = Counter(row["source_kind"] for row in instances)
    return {
        "scope": "paper Expanded, Black & White onward, bundled English snapshot",
        "counts": {
            "print_effect_instances": len(instances),
            "distinct_signatures": len(signatures),
            "distinct_card_names": len({row["card_name"] for row in instances}),
            "source_kinds": dict(sorted(source_counts.items())),
            "festival_condition_instances": sum(
                row["requires_festival_grounds"] for row in instances
            ),
        },
        "instances": sorted(instances, key=lambda row: row["print_id"]),
        "signatures": signatures,
    }


def atomic_write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(value, indent=2, ensure_ascii=False) + "\n"
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
                mode="w",
                encoding="utf-8",
                dir=path.parent,
                delete=False,
            ) as tmp_file:
                tmp_file.write(payload)
                tmp_file.flush()
                os.fsync(tmp_file.fileno())
                tmp_path = Path(tmp_file.name)
            os.replace(tmp_path, path)
        finally:
            if tmp_path is not None and tmp_path.exists():
                tmp_path.unlink()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Catalog legal Expanded effects that permit multiple attacks."
    )
    parser.add_argument("--resources-root", type=Path, default=Path("resources"))
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results/multi_attack_permission_catalog/catalog.json"),
    )
    args = parser.parse_args()
    result = build(args.resources_root)
    atomic_write_json(args.output, result)
    print(json.dumps(result["counts"], indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
