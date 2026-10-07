from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from tools.build_expanded_legality_baseline import classify_effective_legality, load_json


@dataclass(frozen=True)
class OptionalityDivergence:
    name: str
    source_ids: tuple[str, ...]
    target_id: str
    source_fragment: str
    target_fragment: str
    witness: str


CASES = (
    OptionalityDivergence(
        name="PokéNav",
        source_ids=("ex1-88", "ex9-81", "ex14-83"),
        target_id="sm7-140",
        source_fragment="choose a Basic Pokémon, Evolution card, or Energy card",
        target_fragment="You may reveal a Pokémon or Energy card",
        witness=(
            "Place at least one eligible card in the top three. "
            "Current PokéNav can decline to take it; the historical wording requires a choice."
        ),
    ),
    OptionalityDivergence(
        name="Pokégear 3.0",
        source_ids=("hgss1-96",),
        target_id="swsh1-174",
        source_fragment="Choose a Supporter card you find there",
        target_fragment="You may reveal a Supporter card you find there",
        witness=(
            "Place a Supporter in the top seven. "
            "Current Pokégear 3.0 can decline to take it and shuffle the inspected cards back; "
            "the historical wording requires a choice."
        ),
    ),
    OptionalityDivergence(
        name="Dusk Ball",
        source_ids=("dp2-110", "dp5-80"),
        target_id="sv8-175",
        source_fragment="Choose 1 Pokémon you find there",
        target_fragment="You may reveal a Pokémon you find there",
        witness=(
            "Place a Pokémon among the bottom seven. "
            "Current Dusk Ball can decline to take it; the historical wording requires a choice."
        ),
    ),
)


def _rules_text(card: dict[str, object]) -> str:
    return "\n".join(str(rule) for rule in (card.get("rules") or ()))


def collect_proven_optionality_non_equivalent_ids(
    resources_root: Path,
) -> dict[str, str]:
    sets = load_json(resources_root / "sets" / "en.json")
    expanded_sets = {
        row["id"]
        for row in sets
        if (row.get("legalities") or {}).get("expanded") == "Legal"
    }

    cards_by_id: dict[str, dict[str, object]] = {}
    for path in sorted((resources_root / "cards" / "en").glob("*.json")):
        for raw in load_json(path):
            card = dict(raw)
            card["_set_id"] = path.stem
            cards_by_id[card["id"]] = card

    result: dict[str, str] = {}
    for case in CASES:
        target = cards_by_id[case.target_id]
        if target.get("name") != case.name:
            raise ValueError(f"Target name mismatch for {case.target_id}")
        if target.get("_set_id") not in expanded_sets:
            raise ValueError(f"Target is outside Expanded set scope: {case.target_id}")
        if classify_effective_legality(target)[0] != "Legal":
            raise ValueError(f"Target is not effectively legal: {case.target_id}")
        if case.target_fragment not in _rules_text(target):
            raise ValueError(f"Current optionality fragment missing for {case.target_id}")

        for source_id in case.source_ids:
            source = cards_by_id[source_id]
            if source.get("name") != case.name:
                raise ValueError(f"Source name mismatch for {source_id}")
            if source.get("_set_id") in expanded_sets:
                raise ValueError(f"Source unexpectedly inside Expanded set scope: {source_id}")
            if case.source_fragment not in _rules_text(source):
                raise ValueError(f"Historical choose fragment missing for {source_id}")
            result[source_id] = (
                "Same-name functional divergence (material_transition/optionality): "
                + case.witness
            )

    return dict(sorted(result.items()))


def summarize_optionality_divergence(resources_root: Path) -> dict[str, object]:
    reasons = collect_proven_optionality_non_equivalent_ids(resources_root)
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
                "witness": case.witness,
            }
            for case in CASES
        ],
    }
