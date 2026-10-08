"""Audit explicit optional boost branches of legal Expanded attack text.

This intentionally narrows the scan to a printed `N+` attack whose text begins
with a `You may ... If you do, this attack does N more damage` clause. It
preserves variable-per-card bonuses rather than treating them as flat boosts.
"""

from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
import re

from build_expanded_legality_baseline import classify_effective_legality


OPTIONAL = re.compile(
    r"^You may (?P<cost>.+?)\. If you do, this attack does "
    r"(?P<bonus>\d+) more damage(?P<suffix>.*)$",
    re.IGNORECASE,
)
PRINTED = re.compile(r"^(?P<base>\d+)\+$")


def classify_cost(cost: str) -> str:
    lowered = cost.casefold()
    if "stadium" in lowered:
        return "stadium_discard"
    if "face-down prize cards face up" in lowered:
        return "prize_reveal"
    if "top 3 cards of each player" in lowered:
        return "deck_top_discard"
    if "tool" in lowered:
        return "tool_discard"
    if "from your hand" in lowered:
        return "hand_discard"
    if "into your hand" in lowered or "return a" in lowered:
        return "attached_energy_return"
    if "energy" in lowered and "discard" in lowered:
        return "attached_energy_discard"
    raise ValueError(f"unreviewed optional boost cost: {cost}")


def optional_attack_profile(attack: dict) -> dict[str, object] | None:
    text = " ".join((attack.get("text") or "").split())
    match = OPTIONAL.fullmatch(text)
    printed = PRINTED.fullmatch(attack.get("damage") or "")
    if not match or not printed:
        return None

    cost = match.group("cost")
    suffix = match.group("suffix")
    variable_bonus = "for each" in suffix.casefold()
    return {
        "attack_name": attack["name"],
        "printed_damage": attack["damage"],
        "base_damage": int(printed.group("base")),
        "bonus_per_unit": int(match.group("bonus")),
        "variable_bonus": variable_bonus,
        "cost": cost,
        "cost_family": classify_cost(cost),
        "text": text,
    }


def build_catalog(resources: Path) -> dict[str, object]:
    sets = json.loads((resources / "sets" / "en.json").read_text(encoding="utf-8"))
    allowed_sets = {
        row["id"]
        for row in sets
        if (row.get("legalities") or {}).get("expanded") == "Legal"
    }
    rows: list[dict[str, object]] = []
    for path in sorted((resources / "cards" / "en").glob("*.json")):
        if path.stem not in allowed_sets:
            continue
        for card in json.loads(path.read_text(encoding="utf-8")):
            if classify_effective_legality(card)[0] != "Legal":
                continue
            for attack in card.get("attacks") or ():
                profile = optional_attack_profile(attack)
                if profile is not None:
                    rows.append({
                        "card_id": card["id"],
                        "card_name": card["name"],
                        **profile,
                    })

    distinct = {
        (row["card_name"], row["attack_name"], row["printed_damage"], row["text"])
        for row in rows
    }
    unique_names = {row["card_name"] for row in rows}
    return {
        "print_rows": len(rows),
        "unique_effect_signatures": len(distinct),
        "unique_card_names": len(unique_names),
        "variable_bonus_prints": sum(bool(r["variable_bonus"]) for r in rows),
        "variable_bonus_signatures": len({
            (r["card_name"], r["attack_name"], r["printed_damage"], r["text"])
            for r in rows if r["variable_bonus"]
        }),
        "by_cost_family": dict(sorted(
            Counter(str(row["cost_family"]) for row in rows).items()
        )),
        "rows": rows,
    }


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1] / "resources"
    catalog = build_catalog(root)
    print(json.dumps({k: v for k, v in catalog.items() if k != "rows"}, indent=2))
