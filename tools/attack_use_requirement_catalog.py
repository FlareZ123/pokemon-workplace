"""Catalog explicit attack-use requirements in paper Expanded."""

from __future__ import annotations

from collections import Counter
import re
from pathlib import Path
from typing import Any

from simple_attack_board_semantics import legal_cards


USE_ONLY_RE = re.compile(
    r"^You can use this attack only if (?P<condition>.+?)\. ",
    re.IGNORECASE,
)


def dependency_family(condition: str) -> str:
    lowered = condition.casefold()
    if "go second" in lowered and "first turn" in lowered:
        return "turn_order_first_turn"
    if "during your last turn" in lowered:
        return "attack_history"
    if "exactly 1 prize card remaining" in lowered:
        return "opponent_prizes_exact_1"
    if "exactly 2 prize cards remaining" in lowered:
        return "opponent_prizes_exact_2"
    if "at least 3 more prize cards remaining than your opponent" in lowered:
        return "relative_prize_gap_at_least_3"
    if "more prize cards remaining than your opponent" in lowered:
        return "relative_prize_advantage"
    if "total of both players' remaining prize cards is 6 or less" in lowered:
        return "total_remaining_prizes_at_most_6"
    if "10 or more cards in the lost zone" in lowered:
        return "lost_zone_count_at_least_10"
    if "this pokémon has any damage counters on it" in lowered:
        return "self_has_damage"
    if "opponent's active pokémon is affected by a special condition" in lowered:
        return "opponent_active_special_condition"
    if "no supporter cards in your discard pile" in lowered:
        return "discard_lacks_supporter"
    if "grass, water, and lightning pokémon on your bench" in lowered:
        return "bench_types_grass_water_lightning"
    return "unclassified"


def build(resources_root: Path) -> dict[str, Any]:
    signatures: dict[tuple[str, str], dict[str, Any]] = {}
    print_rows = 0

    for card in legal_cards(resources_root):
        for attack in card.get("attacks") or ():
            text = attack.get("text") or ""
            match = USE_ONLY_RE.match(text)
            if match is None:
                continue
            print_rows += 1
            key = (attack.get("name") or "", text)
            row = signatures.setdefault(
                key,
                {
                    "attack_name": attack.get("name") or "",
                    "attack_text": text,
                    "condition_text": match.group("condition"),
                    "dependency_family": dependency_family(match.group("condition")),
                    "card_names": set(),
                    "print_ids": [],
                },
            )
            row["card_names"].add(card.get("name") or "")
            row["print_ids"].append(card["id"])

    output_rows = []
    for row in signatures.values():
        output_rows.append(
            {
                **row,
                "card_names": sorted(row["card_names"]),
                "print_ids": sorted(row["print_ids"]),
            }
        )
    output_rows.sort(
        key=lambda row: (
            row["dependency_family"],
            row["attack_name"],
            row["attack_text"],
        )
    )

    counts = Counter(row["dependency_family"] for row in output_rows)
    return {
        "scope": {
            "format": "paper Expanded, Black & White onward",
            "print_rows": print_rows,
            "signatures": len(output_rows),
            "card_names": len(
                {
                    card_name
                    for row in output_rows
                    for card_name in row["card_names"]
                }
            ),
        },
        "dependency_family_counts": dict(sorted(counts.items())),
        "signatures": output_rows,
    }
