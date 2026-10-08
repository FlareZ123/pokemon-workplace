from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from tools.build_expanded_legality_baseline import classify_effective_legality, load_json
from tools.reprint_policy_evidence import HANDBOOK_SOURCE

ACE_SPEC_RULE = "You can't have more than 1 ACE SPEC card in your deck."


@dataclass(frozen=True)
class DeckRuleDivergence:
    name: str
    source_ids: tuple[str, ...]
    target_id: str
    missing_source_rule: str
    axis: str
    witness: str
    source: str


CASES = (
    DeckRuleDivergence(
        name="Computer Search",
        source_ids=("base1-71", "base4-101"),
        target_id="bw7-137",
        missing_source_rule=ACE_SPEC_RULE,
        axis="rule_category",
        witness=(
            "The current Expanded print is an ACE SPEC and explicitly limits the deck "
            "to one ACE SPEC card. The historical prints contain no ACE SPEC rule. "
            "A deck containing two Computer Search cards therefore distinguishes the "
            "construction semantics of the source and target prints."
        ),
        source=HANDBOOK_SOURCE,
    ),
)


def _load_cards(resources_root: Path) -> tuple[set[str], dict[str, dict]]:
    sets = load_json(resources_root / "sets" / "en.json")
    expanded_sets = {
        row["id"]
        for row in sets
        if (row.get("legalities") or {}).get("expanded") == "Legal"
    }
    cards_by_id: dict[str, dict] = {}
    for path in sorted((resources_root / "cards" / "en").glob("*.json")):
        for raw in load_json(path):
            card = dict(raw)
            card["_set_id"] = path.stem
            cards_by_id[card["id"]] = card
    return expanded_sets, cards_by_id


def collect_proven_deck_rule_non_equivalent_ids(
    resources_root: Path,
) -> dict[str, str]:
    expanded_sets, cards_by_id = _load_cards(resources_root)
    result: dict[str, str] = {}

    for case in CASES:
        target = cards_by_id[case.target_id]
        if target["name"] != case.name:
            raise ValueError(f"Target name mismatch for {case.target_id}")
        if target["_set_id"] not in expanded_sets:
            raise ValueError(f"Target is outside Expanded set scope: {case.target_id}")
        if classify_effective_legality(target)[0] != "Legal":
            raise ValueError(f"Target is not effectively legal: {case.target_id}")
        if case.missing_source_rule not in (target.get("rules") or ()):
            raise ValueError(f"Target deck rule missing for {case.target_id}")

        target_subtypes = set(target.get("subtypes") or ())
        if "ACE SPEC" not in target_subtypes:
            raise ValueError(f"Target lacks ACE SPEC subtype: {case.target_id}")

        for source_id in case.source_ids:
            source = cards_by_id[source_id]
            if source["name"] != case.name:
                raise ValueError(f"Source name mismatch for {source_id}")
            if source["_set_id"] in expanded_sets:
                raise ValueError(f"Source unexpectedly inside Expanded set scope: {source_id}")
            if case.missing_source_rule in (source.get("rules") or ()):
                raise ValueError(f"Source unexpectedly has target deck rule: {source_id}")
            if "ACE SPEC" in set(source.get("subtypes") or ()):
                raise ValueError(f"Source unexpectedly has ACE SPEC subtype: {source_id}")

            result[source_id] = (
                f"Same-name functional divergence ({case.axis}): {case.witness} "
                f"Current Standard/Expanded reprint policy requires all printed text "
                f"to be functionally identical. Source: {case.source}"
            )

    return dict(sorted(result.items()))


def summarize_deck_rule_divergence(resources_root: Path) -> dict[str, object]:
    reasons = collect_proven_deck_rule_non_equivalent_ids(resources_root)
    return {
        "counts": {
            "cases": len(CASES),
            "source_prints": len(reasons),
            "names": len(CASES),
        },
        "cases": [
            {
                "name": case.name,
                "source_ids": list(case.source_ids),
                "target_id": case.target_id,
                "axis": case.axis,
                "missing_source_rule": case.missing_source_rule,
                "witness": case.witness,
                "source": case.source,
            }
            for case in CASES
        ],
    }
