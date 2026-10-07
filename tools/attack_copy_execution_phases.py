from __future__ import annotations

import argparse
import json
import os
import re
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any

OFFICIAL_BAN_OVERLAY = {
    "swsh2-22",
    "swsh45sv-SV013",
    "swsh10tg-TG02",
    "swshp-SWSH022",
    "swsh7-83",
    "swsh7-185",
    "swsh7-186",
}

COPY_PHRASE_RE = re.compile(r"\bas this attack\b", re.IGNORECASE)


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def legal_cards(resources_root: Path) -> list[dict[str, Any]]:
    sets = load_json(resources_root / "sets" / "en.json")
    expanded_sets = {
        entry["id"]
        for entry in sets
        if (entry.get("legalities") or {}).get("expanded") == "Legal"
    }
    cards: list[dict[str, Any]] = []
    for path in sorted((resources_root / "cards" / "en").glob("*.json")):
        if path.stem not in expanded_sets:
            continue
        for card in load_json(path):
            if card["id"] in OFFICIAL_BAN_OVERLAY:
                continue
            if (card.get("legalities") or {}).get("expanded") == "Banned":
                continue
            cards.append(card)
    return cards


def normalized_trailing_text(text: str) -> str:
    match = COPY_PHRASE_RE.search(text)
    if match is None:
        return ""
    return text[match.end():].lstrip(" .").strip()


def trailing_semantics(text: str) -> str:
    trailing = normalized_trailing_text(text)
    lowered = trailing.lower()
    if not trailing:
        return "none"
    if "necessary energy" in lowered and "attack does nothing" in lowered:
        return "selected_attack_energy_gate"
    if "can't use more than 1 gx attack" in lowered:
        return "gx_usage_rule"
    if "shuffle the revealed cards" in lowered:
        return "post_copy_cleanup"
    if "have rule boxes" in lowered:
        return "explanatory_reminder"
    return "unclassified"


def selected_attack_energy_gate_position(text: str) -> str | None:
    lowered = text.lower()
    if "necessary energy" not in lowered:
        return None
    match = COPY_PHRASE_RE.search(text)
    if match is None:
        return None
    energy_index = lowered.index("necessary energy")
    return "before_copy_clause" if energy_index < match.start() else "after_copy_clause"


def source_lifetime_pattern(text: str) -> str | None:
    lowered = text.lower()
    if (
        "opponent reveals their hand" in lowered
        and "discard a pokémon you find there" in lowered
        and "use one of that pokémon's non-gx attacks as this attack" in lowered
    ):
        return "selected_source_discarded_from_opponent_hand_before_body"
    if (
        "discard the top card of your deck" in lowered
        and "choose 1 of its attacks and use it as this attack" in lowered
    ):
        return "top_card_discarded_before_eligibility_and_body"
    return None


def build(resources_root: Path) -> dict[str, Any]:
    cards = legal_cards(resources_root)
    signatures: dict[tuple[str, str], dict[str, Any]] = {}
    print_rows = 0
    for card in cards:
        for attack in card.get("attacks") or []:
            text = attack.get("text") or ""
            if COPY_PHRASE_RE.search(text) is None:
                continue
            print_rows += 1
            key = (attack.get("name") or "", text)
            row = signatures.setdefault(
                key,
                {
                    "attack_name": attack.get("name") or "",
                    "attack_text": text,
                    "card_names": set(),
                    "print_ids": [],
                },
            )
            row["card_names"].add(card.get("name") or "")
            row["print_ids"].append(card["id"])

    output_rows = []
    for row in signatures.values():
        text = row["attack_text"]
        output_rows.append(
            {
                "attack_name": row["attack_name"],
                "attack_text": text,
                "card_names": sorted(row["card_names"]),
                "print_ids": sorted(row["print_ids"]),
                "trailing_text": normalized_trailing_text(text),
                "trailing_semantics": trailing_semantics(text),
                "selected_attack_energy_gate_position": selected_attack_energy_gate_position(text),
                "source_lifetime_pattern": source_lifetime_pattern(text),
            }
        )
    output_rows.sort(key=lambda row: (row["attack_name"], row["attack_text"]))

    trailing_counts = Counter(row["trailing_semantics"] for row in output_rows)
    energy_rows = [row for row in output_rows if row["selected_attack_energy_gate_position"]]
    lifetime_rows = [row for row in output_rows if row["source_lifetime_pattern"]]

    return {
        "scope": {
            "format": "paper Expanded, Black & White onward",
            "effectively_legal_cards_scanned": len(cards),
            "copy_attack_print_rows": print_rows,
            "copy_attack_signatures": len(output_rows),
        },
        "trailing_semantics_counts": dict(sorted(trailing_counts.items())),
        "energy_gate_rows": energy_rows,
        "source_lifetime_rows": lifetime_rows,
        "signatures": output_rows,
        "interpretation": [
            "Clause position is not a safe execution-order proxy for copy attacks.",
            "Copy Anything places its selected-attack Energy gate after the copy phrase, while Imittack places an Energy gate before it; both gates must be resolved before copied effects can matter.",
            "Hypnotic Reign and Seek Inspiration move the selected source card out of its lookup zone before the selected attack body executes, so a resolver should snapshot the chosen attack rather than require the source to remain queryable.",
            "Haughty Order has a true post-copy continuation: its revealed-card cleanup resumes after the selected attack body resolves.",
            "Trickster-GX carries an outer GX-use rule after the copy phrase; it is not ordinary post-copy cleanup.",
        ],
    }


def atomic_write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(value, indent=2, ensure_ascii=False) + "\n"
    lock_path = path.with_suffix(path.suffix + ".lock")
    with lock_path.open("a+b") as lock_file:
        if os.name == "nt":
            import msvcrt

            if lock_file.tell() == 0:
                lock_file.write(b"0")
                lock_file.flush()
                lock_file.seek(0)
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
    parser = argparse.ArgumentParser(
        description="Classify execution phases around Expanded attack-copy text."
    )
    parser.add_argument("--resources-root", type=Path, default=Path("resources"))
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results/attack_copy_execution_phases/catalog.json"),
    )
    args = parser.parse_args()
    result = build(args.resources_root)
    atomic_write_json(args.output, result)
    print(
        json.dumps(
            {
                "scope": result["scope"],
                "trailing_semantics_counts": result["trailing_semantics_counts"],
                "energy_gate_attacks": [
                    row["attack_name"] for row in result["energy_gate_rows"]
                ],
                "source_lifetime_attacks": [
                    row["attack_name"] for row in result["source_lifetime_rows"]
                ],
            },
            indent=2,
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
