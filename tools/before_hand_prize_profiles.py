"""Typed profiles for legal Prize-origin E-31 before-hand effects."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import re
from typing import Iterable

from build_expanded_legality_baseline import classify_effective_legality

PRIZE_TRIGGER_RE = re.compile(
    r"took (?:this card|this Pokémon|it) as a face-down Prize card.*"
    r"before you put it into your hand",
    flags=re.IGNORECASE | re.DOTALL,
)


@dataclass(frozen=True)
class BeforeHandPrizeProfile:
    card_id: str
    card_name: str
    source: str
    activation_family: str
    self_destination: str
    during_own_turn_explicit: bool
    card_text_requires_open_bench: bool
    extra_prize_mode: str
    searches_pokemon_to_bench: bool


def _effect_rows(card: dict) -> Iterable[tuple[str, str]]:
    for index, rule in enumerate(card.get("rules") or []):
        yield f"rule:{index}", rule
    for ability in card.get("abilities") or []:
        text = ability.get("text") or ""
        if text:
            yield f"ability:{ability.get('name', '')}", text
    for attack in card.get("attacks") or []:
        text = attack.get("text") or ""
        if text:
            yield f"attack:{attack.get('name', '')}", text


def compile_before_hand_prize_profile(
    card: dict,
) -> BeforeHandPrizeProfile | None:
    """Compile one card when its Prize-origin E-31 wording is recognized."""

    trigger_rows = [
        (source, text)
        for source, text in _effect_rows(card)
        if PRIZE_TRIGGER_RE.search(text)
    ]
    if not trigger_rows:
        return None
    if len(trigger_rows) != 1:
        raise ValueError(
            f"expected one Prize-origin before-hand trigger on {card['id']}"
        )

    source, trigger_text = trigger_rows[0]
    supertype = card.get("supertype")
    subtypes = set(card.get("subtypes") or [])

    if (
        supertype == "Pokémon"
        and "may put it onto your Bench" in trigger_text
    ):
        activation_family = "self_to_bench"
        self_destination = "in_play"
    elif (
        supertype == "Energy"
        and "may attach this card to 1 of your Pokémon" in trigger_text
    ):
        activation_family = "self_attach"
        self_destination = "attached"
    elif (
        supertype == "Trainer"
        and "Item" in subtypes
        and "You can play this card only if" in trigger_text
    ):
        activation_family = "item_play"
        self_destination = "discard_after_use"
    else:
        raise ValueError(
            f"unrecognized Prize-origin before-hand family: {card['id']}"
        )

    full_text = "\n".join(text for _source, text in _effect_rows(card))
    full_text_lower = full_text.lower()
    if "flip a coin. if heads, take 1 more prize card." in full_text_lower:
        extra_prize_mode = "coin_heads"
    elif "take 1 more prize card" in full_text_lower:
        extra_prize_mode = "guaranteed"
    else:
        extra_prize_mode = "none"

    return BeforeHandPrizeProfile(
        card_id=card["id"],
        card_name=card["name"],
        source=source,
        activation_family=activation_family,
        self_destination=self_destination,
        during_own_turn_explicit="during your turn" in trigger_text,
        card_text_requires_open_bench="Bench isn't full" in trigger_text,
        extra_prize_mode=extra_prize_mode,
        searches_pokemon_to_bench=(
            "Search your deck for a Pokémon and put it onto your Bench."
            in full_text
        ),
    )


def build_before_hand_prize_profiles(
    resources_root: Path,
) -> tuple[BeforeHandPrizeProfile, ...]:
    """Compile every effectively legal profile in Expanded-marked sets."""

    sets = json.loads(
        (resources_root / "sets" / "en.json").read_text(encoding="utf-8")
    )
    expanded_sets = {
        row["id"]
        for row in sets
        if (row.get("legalities") or {}).get("expanded") == "Legal"
    }

    profiles = []
    for path in sorted((resources_root / "cards" / "en").glob("*.json")):
        if path.stem not in expanded_sets:
            continue

        cards = json.loads(path.read_text(encoding="utf-8"))
        for card in cards:
            status, _source = classify_effective_legality(card)
            if status != "Legal":
                continue
            profile = compile_before_hand_prize_profile(card)
            if profile is not None:
                profiles.append(profile)

    return tuple(sorted(profiles, key=lambda row: row.card_id))
