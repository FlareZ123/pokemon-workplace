"""Catalog effectively legal Expanded Abilities with immediate Knock Out triggers."""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

from build_expanded_legality_baseline import classify_effective_legality


TRIGGER_PATTERNS = (
    ("self", re.compile(
        r"(?:when|if) this pokémon(?: [^,.]{0,100})? is knocked out\\b",
        re.IGNORECASE,
    )),
    ("allied", re.compile(
        r"(?:when|if) (?:1 of )?your (?!opponent)[^,.]{0,120}"
        r"pokémon is knocked out\\b",
        re.IGNORECASE,
    )),
    ("opponent", re.compile(
        r"(?:when|if) your opponent(?:'s|’s) [^,.]{0,120}"
        r"pokémon is knocked out\\b",
        re.IGNORECASE,
    )),
    ("attached", re.compile(
        r"when the pokémon this card is attached to is knocked out\\b",
        re.IGNORECASE,
    )),
)

EXCLUDED_CONTEXTS = (
    "even if",
    "would be knocked out",
    "during your opponent's last turn",
)


def normalize(text: str) -> str:
    return " ".join(text.split()).replace("Knocket Out", "Knocked Out")


def trigger_scopes(text: str) -> tuple[str, ...]:
    value = normalize(text)
    lower = value.lower()
    if any(fragment in lower for fragment in EXCLUDED_CONTEXTS):
        return ()
    return tuple(
        name
        for name, pattern in TRIGGER_PATTERNS
        if pattern.search(value)
    )


def effect_families(text: str) -> tuple[str, ...]:
    lower = normalize(text).lower()
    families: list[str] = []

    if "attacking pokémon is knocked out" in lower:
        families.append("attacker_knockout")
    if "damage counter" in lower and ("put " in lower or "place " in lower):
        families.append("damage_counters")
    if (
        "can't take any prize" in lower
        or "takes 1 fewer prize" in lower
        or "take 1 more prize" in lower
    ):
        families.append("prize_modifier")
    if (
        "lost zone instead of the discard pile" in lower
        or "put it into your hand instead of the discard pile" in lower
        or "shuffle this pokémon and all cards attached to it into your deck" in lower
    ):
        families.append("pokemon_zone_redirect")
    if "energy" in lower and (
        "move " in lower
        or "put all basic water energy" in lower
    ):
        families.append("energy_relocation")
    if "search your deck" in lower:
        families.append("deck_search")
    if "discard" in lower and "opponent's hand" in lower:
        families.append("hand_disruption")
    if "discard the top" in lower and "opponent's deck" in lower:
        families.append("deck_mill")
    if "discard an energy from your opponent's active pokémon" in lower:
        families.append("energy_disruption")
    if re.search(
        r"attacking pokémon is now (?:confused|poisoned|burned|asleep)",
        lower,
    ):
        families.append("special_condition")
    if (
        "choose which of your opponent's benched pokémon becomes their new "
        "active pokémon" in lower
    ):
        families.append("promotion_control")

    return tuple(families)


def build(resources_root: Path) -> dict:
    sets = json.loads(
        (resources_root / "sets" / "en.json").read_text(encoding="utf-8")
    )
    expanded_set_ids = {
        row["id"]
        for row in sets
        if (row.get("legalities") or {}).get("expanded") == "Legal"
    }

    rows: list[dict] = []
    for path in sorted((resources_root / "cards" / "en").glob("*.json")):
        if path.stem not in expanded_set_ids:
            continue
        for card in json.loads(path.read_text(encoding="utf-8")):
            if classify_effective_legality(card)[0] != "Legal":
                continue
            for ability in card.get("abilities") or []:
                text = normalize(ability.get("text") or "")
                scopes = trigger_scopes(text)
                if not scopes:
                    continue
                rows.append(
                    {
                        "card_id": card["id"],
                        "card_name": card["name"],
                        "ability_name": ability["name"],
                        "trigger_scopes": list(scopes),
                        "effect_families": list(effect_families(text)),
                        "text": text,
                    }
                )

    signatures = {
        (
            row["ability_name"],
            row["text"],
            tuple(row["trigger_scopes"]),
        )
        for row in rows
    }
    scope_print_counts = Counter(
        scope for row in rows for scope in row["trigger_scopes"]
    )
    family_print_counts = Counter(
        family for row in rows for family in row["effect_families"]
    )
    scope_signature_counts = Counter(
        scope
        for _name, _text, scopes in signatures
        for scope in scopes
    )
    family_signature_counts = Counter(
        family
        for _name, text, _scopes in signatures
        for family in effect_families(text)
    )

    return {
        "summary": {
            "matched_prints": len(rows),
            "matched_names": len({row["card_name"] for row in rows}),
            "distinct_ability_signatures": len(signatures),
            "prints_by_trigger_scope": dict(sorted(scope_print_counts.items())),
            "signatures_by_trigger_scope": dict(
                sorted(scope_signature_counts.items())
            ),
            "prints_by_effect_family": dict(sorted(family_print_counts.items())),
            "signatures_by_effect_family": dict(
                sorted(family_signature_counts.items())
            ),
            "unclassified_effect_prints": sum(
                not row["effect_families"] for row in rows
            ),
        },
        "rows": rows,
    }


def main() -> None:
    import sys

    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("resources")
    print(json.dumps(build(root), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
