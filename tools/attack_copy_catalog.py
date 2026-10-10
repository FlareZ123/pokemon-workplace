from __future__ import annotations

import argparse
import json
import os
import tempfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from build_expanded_legality_baseline import OFFICIAL_BAN_OVERLAY, classify_effective_legality


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def classify_source(text: str) -> str:
    t = text.lower()
    if "dragon pokémon in your discard pile" in t:
        return "own_discard_dragon"
    if "benched fusion strike pokémon" in t:
        return "own_bench_fusion_strike"
    if "benched n's pokémon" in t:
        return "own_bench_named_n"
    if "your benched pokémon's attacks" in t:
        return "own_bench_any"
    if "previous evolutions" in t:
        return "self_previous_evolution"
    if "top card of your deck" in t and "pokémon" in t:
        return "own_deck_top_card"
    if "top 10 cards of your opponent's deck" in t:
        return "opponent_deck_top10"
    if "opponent reveals their hand" in t:
        return "opponent_hand"
    if "during their last turn" in t or "during his or her last turn" in t:
        return "opponent_last_attack"
    if "active tera pokémon" in t:
        return "opponent_active_tera"
    if "active pokémon's non-gx attacks" in t:
        return "opponent_active_non_gx"
    if "defending pokémon's attacks" in t or "active pokémon's attacks" in t:
        return "opponent_active_any"
    if "opponent's pokémon in play" in t:
        return "opponent_in_play"
    if "opponent chooses an attack from 1 of their pokémon in play" in t:
        return "opponent_chooses_in_play"
    if "opponent's pokémon's attacks" in t:
        return "opponent_any_pokemon"
    return "other"


def has_direct_non_gx_filter(text: str) -> bool:
    return "non-gx" in text.lower() or "isn't a gx attack" in text.lower()


def is_optional(text: str) -> bool:
    return "you may" in text.lower()


def structural_same_attack_reentry(card: dict[str, Any], source_class: str) -> bool:
    name = card.get("name") or ""
    subtypes = set(card.get("subtypes") or [])
    types = set(card.get("types") or [])

    if source_class in {
        "opponent_active_any",
        "opponent_any_pokemon",
        "opponent_in_play",
        "opponent_chooses_in_play",
        "opponent_last_attack",
        "opponent_active_non_gx",
    }:
        return True
    if source_class == "own_bench_any":
        return True
    if source_class == "own_bench_fusion_strike":
        return "Fusion Strike" in subtypes
    if source_class == "own_bench_named_n":
        return name.startswith("N's ")
    if source_class == "own_discard_dragon":
        return "Dragon" in types
    if source_class == "opponent_hand":
        return True
    if source_class == "opponent_deck_top10":
        return True
    return False


def effective_legal(card: dict[str, Any]) -> bool:
    return classify_effective_legality(card)[0] == "Legal"


def build(resources_root: Path) -> dict[str, Any]:
    sets = load_json(resources_root / "sets" / "en.json")
    expanded_sets = {
        entry["id"]
        for entry in sets
        if (entry.get("legalities") or {}).get("expanded") == "Legal"
    }

    legal_cards: list[dict[str, Any]] = []
    by_id: dict[str, dict[str, Any]] = {}
    for path in sorted((resources_root / "cards" / "en").glob("*.json")):
        if path.stem not in expanded_sets:
            continue
        for card in load_json(path):
            if not effective_legal(card):
                continue
            legal_cards.append(card)
            by_id[card["id"]] = card

    print_rows: list[dict[str, Any]] = []
    for card in legal_cards:
        for attack in card.get("attacks") or []:
            text = attack.get("text") or ""
            if "as this attack" not in text.lower():
                continue
            source_class = classify_source(text)
            print_rows.append(
                {
                    "card_id": card["id"],
                    "card_name": card.get("name"),
                    "types": card.get("types") or [],
                    "subtypes": card.get("subtypes") or [],
                    "attack_name": attack.get("name"),
                    "attack_cost": attack.get("cost") or [],
                    "text": text,
                    "source_class": source_class,
                    "direct_non_gx_filter": has_direct_non_gx_filter(text),
                    "optional_selection": is_optional(text),
                    "structural_same_attack_reentry": structural_same_attack_reentry(card, source_class),
                }
            )

    signatures: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in print_rows:
        signatures[(row["attack_name"], row["text"])].append(row)

    signature_rows: list[dict[str, Any]] = []
    for (attack_name, text), rows in sorted(signatures.items()):
        source_classes = sorted({row["source_class"] for row in rows})
        signature_rows.append(
            {
                "attack_name": attack_name,
                "text": text,
                "card_names": sorted({row["card_name"] for row in rows}),
                "print_ids": sorted(row["card_id"] for row in rows),
                "source_classes": source_classes,
                "direct_non_gx_filter": any(row["direct_non_gx_filter"] for row in rows),
                "optional_selection": any(row["optional_selection"] for row in rows),
                "structural_same_attack_reentry": any(row["structural_same_attack_reentry"] for row in rows),
            }
        )

    source_counts = Counter(source for row in signature_rows for source in row["source_classes"])

    mimikyu = by_id["smp-SM99"]
    regidrago = by_id["swsh12-136"]
    dialga = by_id["sm5-100"]
    copycat = next(a for a in mimikyu["attacks"] if a["name"] == "Copycat")
    apex = next(a for a in regidrago["attacks"] if a["name"] == "Apex Dragon")
    timeless = next(a for a in dialga["attacks"] if a["name"] == "Timeless-GX")

    chain = {
        "outer": {
            "card_id": mimikyu["id"],
            "card_name": mimikyu["name"],
            "attack_name": copycat["name"],
            "text": copycat["text"],
        },
        "middle": {
            "card_id": regidrago["id"],
            "card_name": regidrago["name"],
            "attack_name": apex["name"],
            "text": apex["text"],
        },
        "endpoint": {
            "card_id": dialga["id"],
            "card_name": dialga["name"],
            "attack_name": timeless["name"],
            "text": timeless["text"],
        },
        "text_filter_checks": {
            "middle_attack_is_non_gx": not apex["name"].endswith("-GX"),
            "endpoint_card_is_dragon": "Dragon" in (dialga.get("types") or []),
            "middle_has_no_direct_non_gx_filter": not has_direct_non_gx_filter(apex["text"]),
        },
    }
    chain["text_filter_checks"]["all_pass"] = all(chain["text_filter_checks"].values())

    return {
        "scope": {
            "format": "paper Expanded",
            "expanded_set_count": len(expanded_sets),
            "legal_prints_scanned": len(legal_cards),
            "copy_detection": "attack text contains the phrase 'as this attack'",
        },
        "counts": {
            "copy_attack_prints": len(print_rows),
            "unique_copy_attack_signatures": len(signature_rows),
            "unique_card_names": len({row["card_name"] for row in print_rows}),
            "source_classes": dict(sorted(source_counts.items())),
            "signatures_with_direct_non_gx_filter": sum(row["direct_non_gx_filter"] for row in signature_rows),
            "signatures_with_structural_same_attack_reentry": sum(
                row["structural_same_attack_reentry"] for row in signature_rows
            ),
        },
        "signatures": signature_rows,
        "notable_chain": chain,
        "interpretation_notes": [
            "structural_same_attack_reentry is a static hazard flag, not a claim that a practical game state forces an infinite loop.",
            "source restrictions apply to the immediate selection edge encoded by that attack text; nested copied attacks must be resolved under their own text and current game state.",
            "energy-cost behavior is not inferred by this catalog; the rulebook and individual copy attack text must be consulted.",
        ],
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
                mode="w", encoding="utf-8", dir=path.parent, delete=False
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
    parser = argparse.ArgumentParser(description="Catalog Expanded attacks that execute another attack as this attack.")
    parser.add_argument("--resources-root", type=Path, default=Path("resources"))
    parser.add_argument("--output", type=Path, default=Path("results/attack_copy_semantics/catalog.json"))
    args = parser.parse_args()
    result = build(args.resources_root)
    atomic_write_json(args.output, result)
    print(json.dumps(result["counts"], indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
