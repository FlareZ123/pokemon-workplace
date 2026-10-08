from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from tools.build_expanded_legality_baseline import classify_effective_legality, load_json

DivergenceAxis = Literal["material_transition", "target_domain"]


@dataclass(frozen=True)
class TrainerSemanticDivergence:
    name: str
    source_ids: tuple[str, ...]
    target_id: str
    axis: DivergenceAxis
    source_fragments: tuple[str, ...]
    target_fragments: tuple[str, ...]
    witness: str
    witness_card_id: str | None = None


CASES = (
    TrainerSemanticDivergence(
        name="Apricorn Maker",
        source_ids=("ecard3-121",),
        target_id="sm7-124",
        axis="target_domain",
        source_fragments=(
            "Search your deck for up to 2 Trainer cards with Ball in their names",
        ),
        target_fragments=(
            'Search your deck for up to 2 Item cards that have the word "Ball" in their name',
        ),
        witness=(
            "Ball Guy is a legal Expanded Supporter whose name contains the word Ball. "
            "The historical effect can search a Trainer card with Ball in its name, "
            "while the current effect is restricted to Item cards."
        ),
        witness_card_id="swsh45-57",
    ),
    TrainerSemanticDivergence(
        name="Friend Ball",
        source_ids=("ecard3-126",),
        target_id="sm7-131",
        axis="target_domain",
        source_fragments=(
            "Search your deck for a Baby Pokémon, Basic Pokémon, or Evolution card of the same type",
        ),
        target_fragments=(
            "Search your deck for a Pokémon with the same type as 1 of your opponent's Pokémon in play",
        ),
        witness=(
            "Restored Pokémon are neither Basic Pokémon nor Evolution cards under the official rules. "
            "With a Fighting Pokémon on the opponent's field, current Friend Ball can search an Expanded-legal "
            "Fighting Restored Archen, while the historical target classes cannot."
        ),
        witness_card_id="bw3-66",
    ),
    TrainerSemanticDivergence(
        name="Pokémon Fan Club",
        source_ids=("ecard2-130", "pop4-9"),
        target_id="sm5-133",
        axis="material_transition",
        source_fragments=("put them onto your",),
        target_fragments=("put them into your hand",),
        witness=(
            "With an open Bench and an eligible Basic Pokémon in the deck, "
            "the historical effect puts that Pokémon directly onto the Bench, "
            "while the current effect puts it into the hand."
        ),
    ),
    TrainerSemanticDivergence(
        name="Super Potion",
        source_ids=("base1-90", "base4-117"),
        target_id="xy1-128",
        axis="material_transition",
        source_fragments=("remove up to 4 damage counters",),
        target_fragments=("Heal 60 damage",),
        witness=(
            "Give the target Pokémon exactly 60 damage and at least one attached Energy. "
            "The historical effect can remove at most 4 damage counters (40 damage), "
            "while the current effect heals all 60 damage."
        ),
    ),
    TrainerSemanticDivergence(
        name="TV Reporter",
        source_ids=("ex15-82", "ex3-88", "pop2-11"),
        target_id="sm7-149",
        axis="material_transition",
        source_fragments=("Draw 3 cards. Then discard any 1 card from your hand.",),
        target_fragments=("If you have no cards in your deck, you can't play this card.",),
        witness=(
            "During a turn with an empty deck, one other card in hand, and an unused "
            "Supporter action, the current print is explicitly unplayable. Under the "
            "current partial-resolution rules the historical text can draw zero cards "
            "and still discard the other hand card, so it changes the game state."
        ),
    ),
)


def _rules_text(card: dict[str, object]) -> str:
    return "\n".join(str(rule) for rule in (card.get("rules") or ()))


def _load_cards(resources_root: Path) -> tuple[set[str], dict[str, dict[str, object]]]:
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
    return expanded_sets, cards_by_id


def _validate_witness_card(
    case: TrainerSemanticDivergence,
    cards_by_id: dict[str, dict[str, object]],
    expanded_sets: set[str],
) -> None:
    if case.witness_card_id is None:
        return

    witness = cards_by_id[case.witness_card_id]
    if witness.get("_set_id") not in expanded_sets:
        raise ValueError(f"Witness is outside Expanded set scope: {case.witness_card_id}")
    if classify_effective_legality(witness)[0] != "Legal":
        raise ValueError(f"Witness is not effectively legal: {case.witness_card_id}")

    if case.name == "Apricorn Maker":
        if witness.get("supertype") != "Trainer":
            raise ValueError("Apricorn Maker witness must be a Trainer")
        subtypes = set(witness.get("subtypes") or ())
        if "Supporter" not in subtypes or "Item" in subtypes:
            raise ValueError("Apricorn Maker witness must be a non-Item Supporter")
        if "Ball" not in str(witness.get("name") or ""):
            raise ValueError("Apricorn Maker witness name must contain Ball")
    elif case.name == "Friend Ball":
        subtypes = set(witness.get("subtypes") or ())
        if "Restored" not in subtypes:
            raise ValueError("Friend Ball witness must be a Restored Pokémon")
        if not (witness.get("types") or ()):
            raise ValueError("Friend Ball witness must have a Pokémon type")


def collect_proven_trainer_semantic_non_equivalent_ids(
    resources_root: Path,
) -> dict[str, str]:
    expanded_sets, cards_by_id = _load_cards(resources_root)

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

        _validate_witness_card(case, cards_by_id, expanded_sets)

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


def distinguishing_witnesses() -> dict[str, object]:
    # These compact state witnesses make the material differences executable
    # without pretending to be a full game simulator.
    super_potion = {
        "starting_damage": 60,
        "historical_remaining_damage": 20,
        "current_remaining_damage": 0,
    }
    tv_reporter = {
        "deck_cards": 0,
        "other_hand_cards": 1,
        "historical_changes_state": True,
        "current_playable": False,
    }
    fan_club = {
        "historical_destination": "bench",
        "current_destination": "hand",
    }
    apricorn_maker = {
        "witness_card": "Ball Guy",
        "witness_subtype": "Supporter",
        "historical_eligible": True,
        "current_eligible": False,
    }
    return {
        "Apricorn Maker": apricorn_maker,
        "Friend Ball": {
            "witness_card": "Archen",
            "witness_subtype": "Restored",
            "historical_eligible": False,
            "current_eligible": True,
        },
        "Pokémon Fan Club": fan_club,
        "Super Potion": super_potion,
        "TV Reporter": tv_reporter,
    }


def summarize_trainer_semantic_divergence(resources_root: Path) -> dict[str, object]:
    reasons = collect_proven_trainer_semantic_non_equivalent_ids(resources_root)
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
                "witness_card_id": case.witness_card_id,
            }
            for case in CASES
        ],
        "distinguishing_witnesses": distinguishing_witnesses(),
    }
