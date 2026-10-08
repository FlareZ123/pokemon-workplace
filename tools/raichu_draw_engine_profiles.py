"""Card-grounded draw-engine profiles for Harto Miki's Raichu list."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path

from build_expanded_legality_baseline import classify_effective_legality


@dataclass(frozen=True)
class DrawEngineProfile:
    print_id: str
    name: str
    ability_name: str
    trigger: str
    hand_effect: str
    first_turn_only: bool
    pokemon_v: bool
    forest_seal_host: bool


EXPECTED = {
    "swsh3-104": {
        "name": "Crobat V",
        "ability": "Dark Asset",
        "trigger_text": "When you play this Pokémon from your hand onto your Bench during your turn",
        "effect_text": "draw cards until you have 6 cards in your hand",
        "trigger": "hand_to_bench",
        "hand_effect": "draw_to_six",
        "first_turn_only": False,
        "pokemon_v": True,
    },
    "sm10-57": {
        "name": "Dedenne-GX",
        "ability": "Dedechange",
        "trigger_text": "When you play this Pokémon from your hand onto your Bench during your turn",
        "effect_text": "discard your hand and draw 6 cards",
        "trigger": "hand_to_bench",
        "hand_effect": "discard_hand_draw_six",
        "first_turn_only": False,
        "pokemon_v": False,
    },
    "sv2-169": {
        "name": "Squawkabilly ex",
        "ability": "Squawk and Seize",
        "trigger_text": "Once during your first turn",
        "effect_text": "discard your hand and draw 6 cards",
        "trigger": "announced_first_turn",
        "hand_effect": "discard_hand_draw_six",
        "first_turn_only": True,
        "pokemon_v": False,
    },
}


def _load_cards(resources_root: Path) -> dict[str, dict]:
    wanted = set(EXPECTED) | {"swsh12-156"}
    found: dict[str, dict] = {}
    for path in sorted((resources_root / "cards" / "en").glob("*.json")):
        rows = json.loads(path.read_text(encoding="utf-8"))
        for card in rows:
            if card.get("id") in wanted:
                found[card["id"]] = card
    missing = wanted - set(found)
    if missing:
        raise ValueError(f"missing expected cards: {sorted(missing)}")
    return found


def compile_raichu_draw_engine_profiles(
    resources_root: Path = Path("resources"),
) -> tuple[DrawEngineProfile, ...]:
    cards = _load_cards(resources_root)
    forest = cards["swsh12-156"]

    status, _ = classify_effective_legality(forest)
    if status != "Legal":
        raise ValueError("Forest Seal Stone must be legal in the research snapshot")
    forest_rules = " ".join(forest.get("rules") or [])
    if "The Pokémon V this card is attached to can use the VSTAR Power" not in forest_rules:
        raise ValueError("Forest Seal Stone Pokémon V host text changed")

    profiles: list[DrawEngineProfile] = []
    for print_id, expected in EXPECTED.items():
        card = cards[print_id]
        status, _ = classify_effective_legality(card)
        if status != "Legal":
            raise ValueError(f"{print_id} is not legal in the research snapshot")
        if card.get("name") != expected["name"]:
            raise ValueError(f"unexpected name for {print_id}")

        abilities = card.get("abilities") or []
        matching = [a for a in abilities if a.get("name") == expected["ability"]]
        if len(matching) != 1:
            raise ValueError(f"expected one {expected['ability']} on {print_id}")
        text = matching[0].get("text") or ""
        if expected["trigger_text"] not in text or expected["effect_text"] not in text:
            raise ValueError(f"unexpected ability text for {print_id}: {text!r}")

        subtypes = set(card.get("subtypes") or [])
        pokemon_v = "V" in subtypes
        if pokemon_v != expected["pokemon_v"]:
            raise ValueError(f"unexpected Pokémon V classification for {print_id}")

        profiles.append(
            DrawEngineProfile(
                print_id=print_id,
                name=expected["name"],
                ability_name=expected["ability"],
                trigger=expected["trigger"],
                hand_effect=expected["hand_effect"],
                first_turn_only=expected["first_turn_only"],
                pokemon_v=pokemon_v,
                forest_seal_host=pokemon_v,
            )
        )

    return tuple(profiles)


def post_quick_ball_hand_transition(
    profile: DrawEngineProfile,
    *,
    action_hand_size: int = 7,
    engine_source: str = "deck",
) -> dict[str, int | str]:
    """Return hand sizes for a Quick Ball -> engine sequence.

    The action snapshot has seven cards after setup plus one ordinary draw in
    the preceding Raichu models. Quick Ball leaves hand, then one payment card
    leaves hand. A searched engine enters hand; an already-held engine does not.
    """

    if action_hand_size < 2:
        raise ValueError("Quick Ball plus its payment require at least two cards")
    if engine_source not in {"deck", "hand", "in_play"}:
        raise ValueError("engine_source must be deck, hand, or in_play")

    after_payment = action_hand_size - 2
    after_search = after_payment + int(engine_source == "deck")

    if engine_source == "in_play":
        if profile.trigger == "hand_to_bench":
            return {
                "after_quick_ball_payment": after_payment,
                "before_ability": after_payment,
                "cards_drawn": 0,
                "cards_discarded_by_ability": 0,
                "final_hand_size": after_payment,
                "ability_status": "entry_trigger_unavailable",
            }
        before_ability = after_payment
    else:
        before_ability = after_search - 1

    if profile.hand_effect == "draw_to_six":
        cards_drawn = max(0, 6 - before_ability)
        discarded = 0
    elif profile.hand_effect == "discard_hand_draw_six":
        cards_drawn = 6
        discarded = before_ability
    else:
        raise ValueError("unsupported hand effect")

    return {
        "after_quick_ball_payment": after_payment,
        "before_ability": before_ability,
        "cards_drawn": cards_drawn,
        "cards_discarded_by_ability": discarded,
        "final_hand_size": 6,
        "ability_status": "available",
    }
