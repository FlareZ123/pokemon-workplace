from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from tools.build_expanded_legality_baseline import classify_effective_legality, load_json

DivergenceAxis = Literal[
    "material_transition",
    "target_domain",
    "event_semantics",
]


@dataclass(frozen=True)
class NameReuseDivergence:
    name: str
    source_ids: tuple[str, ...]
    target_id: str
    axis: DivergenceAxis
    source_fragments: tuple[str, ...]
    target_fragments: tuple[str, ...]
    witness: str


CASES = (
    NameReuseDivergence(
        name="Master Ball",
        source_ids=("ecard1-143", "ex8-88", "ex11-99", "ex16-78", "gym2-116"),
        target_id="bw10-94",
        axis="material_transition",
        source_fragments=("7 cards",),
        target_fragments=("Search your deck for a Pokémon", "ACE SPEC"),
        witness=(
            "Put the only desired Pokémon below the top seven cards. "
            "The historical effect cannot take it while the current effect can."
        ),
    ),
    NameReuseDivergence(
        name="Pokémon Breeder",
        source_ids=("base1-76", "base4-105", "base6-102"),
        target_id="sm35-63",
        axis="event_semantics",
        source_fragments=("Stage 2 Evolution card",),
        target_fragments=("Draw 2 cards", "heal 20 damage"),
        witness=(
            "A matching Basic plus Stage 2 in hand gives the historical card an evolution transition. "
            "The current Supporter performs draw and healing instead."
        ),
    ),
    NameReuseDivergence(
        name="Pokémon Center",
        source_ids=("base1-85", "base4-114", "basep-40"),
        target_id="bw4-90",
        axis="target_domain",
        source_fragments=("all of your own Pokémon", "discard all Energy"),
        target_fragments=("Benched Pokémon", "heal 20 damage"),
        witness=(
            "With only the Active Pokémon damaged, the historical effect can heal it. "
            "The current Stadium effect targets a Benched Pokémon."
        ),
    ),
    NameReuseDivergence(
        name="Max Revive",
        source_ids=("gym2-117",),
        target_id="g1-65",
        axis="material_transition",
        source_fragments=("Discard 2 Energy cards", "onto your Bench"),
        target_fragments=("on top of your deck",),
        witness=(
            "With an open Bench, a Basic Pokémon in the discard pile, and two Energy in hand, "
            "the historical effect puts the Pokémon into play while the current effect puts a Pokémon on the deck."
        ),
    ),
    NameReuseDivergence(
        name="Revive",
        source_ids=("base1-89",),
        target_id="bw1-102",
        axis="material_transition",
        source_fragments=("damage counters", "half its HP"),
        target_fragments=("Basic Pokémon from your discard pile onto your Bench",),
        witness=(
            "Reviving the same Basic produces a damaged Pokémon under the historical effect "
            "and an undamaged Pokémon under the current effect."
        ),
    ),
    NameReuseDivergence(
        name="Devolution Spray",
        source_ids=("base1-72",),
        target_id="bw6-113",
        axis="material_transition",
        source_fragments=("Discard all Evolution cards",),
        target_fragments=("put the highest stage Evolution card on it into your hand",),
        witness=(
            "Devolving a two-card evolution stack sends the removed card to different zones."
        ),
    ),
    NameReuseDivergence(
        name="Power Plant",
        source_ids=("ecard2-139",),
        target_id="sm10-183",
        axis="event_semantics",
        source_fragments=("discard a basic Energy card", "discard pile"),
        target_fragments=("Pokémon-GX and Pokémon-EX", "have no Abilities"),
        witness=(
            "A state with a usable Pokémon-GX Ability and no relevant Energy exchange is changed "
            "by the current Stadium and not by the historical Stadium."
        ),
    ),
    NameReuseDivergence(
        name="Magnetic Storm",
        source_ids=("ex5-91",),
        target_id="xy2-91",
        axis="target_domain",
        source_fragments=("Psychic Pokémon and Fighting Pokémon", "not affected by Resistance"),
        target_fragments=("Each Pokémon in play has no Resistance",),
        witness=(
            "A non-Psychic, non-Fighting attacker facing Resistance is affected by the current Stadium "
            "while the historical effect does not remove that Resistance interaction."
        ),
    ),
)


def _rules_text(card: dict[str, object]) -> str:
    return "\n".join(str(rule) for rule in (card.get("rules") or ()))


def collect_proven_name_reuse_non_equivalent_ids(
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

        target_text = _rules_text(target)
        for fragment in case.target_fragments:
            if fragment not in target_text:
                raise ValueError(
                    f"Target witness fragment missing for {case.target_id}: {fragment!r}"
                )

        for source_id in case.source_ids:
            source = cards_by_id[source_id]
            if source.get("name") != case.name:
                raise ValueError(f"Source name mismatch for {source_id}")
            if source.get("_set_id") in expanded_sets:
                raise ValueError(f"Source unexpectedly inside Expanded set scope: {source_id}")
            source_text = _rules_text(source)
            for fragment in case.source_fragments:
                if fragment not in source_text:
                    raise ValueError(
                        f"Source witness fragment missing for {source_id}: {fragment!r}"
                    )
            result[source_id] = (
                f"Same-name functional divergence ({case.axis}): {case.witness}"
            )

    return dict(sorted(result.items()))


def summarize_name_reuse_divergence(resources_root: Path) -> dict[str, object]:
    reasons = collect_proven_name_reuse_non_equivalent_ids(resources_root)
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
                "witness": case.witness,
            }
            for case in CASES
        ],
    }
