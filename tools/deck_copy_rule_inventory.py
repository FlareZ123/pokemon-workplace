from __future__ import annotations

from collections import Counter
from pathlib import Path

from tools.build_expanded_legality_baseline import load_json
from tools.deck_validator import (
    ACE_SPEC_RULE, POKEMON_STAR_RULE, RADIANT_RULE, PRISM_RULE_FRAGMENT,
    UNLIMITED_SELF_RULE, UNOWN_FAMILY_RULE, _card_record,
    _recognized_copy_constraint,
)

def _looks_like_copy_rule(rule: str) -> bool:
    lower = rule.lower()
    return (
        "in your deck" in lower
        and (
            "have more than" in lower
            or "as many of this card" in lower
            or "have up to 4 basic pokémon cards" in lower
        )
    )


def inventory_copy_rules(resources_root: Path) -> dict[str, object]:
    counts: Counter[str] = Counter()
    flagged: list[dict[str, str]] = []
    unexplained: list[dict[str, str]] = []
    for path in sorted((resources_root / "cards" / "en").glob("*.json")):
        for raw in load_json(path):
            record = _card_record(raw)
            for rule in record.rules:
                if not _looks_like_copy_rule(rule):
                    continue
                if ACE_SPEC_RULE in rule:
                    kind = "ace_spec"
                elif RADIANT_RULE in rule:
                    kind = "radiant"
                elif POKEMON_STAR_RULE in rule:
                    kind = "pokemon_star"
                elif PRISM_RULE_FRAGMENT in rule:
                    kind = "prism_star"
                elif UNLIMITED_SELF_RULE in rule:
                    kind = "unlimited_exact_print"
                elif UNOWN_FAMILY_RULE in rule:
                    kind = "unown_family"
                elif _recognized_copy_constraint(record, rule):
                    kind = "self_named_singleton"
                else:
                    kind = "unrecognized"
                    unexplained.append({"id": record.card_id, "name": record.name, "rule": rule})
                counts[kind] += 1
                flagged.append({"id": record.card_id, "name": record.name, "kind": kind})

    return {
        "total_rule_prints": len(flagged),
        "classes": dict(sorted(counts.items())),
        "unrecognized": unexplained,
        "rule_prints": flagged,
    }
