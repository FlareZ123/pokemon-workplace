"""Compile a conservative subset of Prize-zone card text into transition atoms."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import re
from typing import Iterable

OFFICIAL_BAN_OVERLAY = {
    "swsh2-22",
    "swsh45sv-SV013",
    "swsh10tg-TG02",
    "swshp-SWSH022",
    "swsh7-83",
    "swsh7-185",
    "swsh7-186",
}
TOURNAMENT_BAN_FRAGMENT = "cannot be used at official tournaments"


@dataclass(frozen=True)
class PrizeEffectRow:
    card_id: str
    card_name: str
    source: str
    text: str
    atoms: tuple[str, ...]


def _has(pattern: str, text: str) -> bool:
    return re.search(pattern, text, flags=re.IGNORECASE | re.DOTALL) is not None


def compile_prize_effect(text: str) -> tuple[str, ...]:
    """Return conservative transition atoms directly supported by wording."""

    atoms: set[str] = set()

    if _has(r"look at (?:1 of )?your face-down Prize cards?", text):
        atoms.add("inspect_own_prize")
    if _has(r"look at (?:1 of )?your opponent(?:'s)? face-down Prize cards?", text):
        atoms.add("inspect_opponent_prize")

    if _has(r"turn (?:1|all) of your face-down Prize cards? face up|turn all of your Prize cards face up", text):
        atoms.add("face_up_own_prize")
    if _has(r"turn (?:1|all) of your opponent(?:'s)? face-down Prize cards? face up", text):
        atoms.add("face_up_opponent_prize")

    if _has(r"Prize cards?.*put (?:1 of )?(?:them|it) into your hand|Prize cards? and put 1 of them into your hand", text):
        atoms.add("prize_to_hand")
    if _has(r"put up to \d+ Prize cards into your hand", text):
        atoms.add("prize_to_hand")
    if _has(r"put a card from your hand face down as a Prize card|put this .* in its place as a face-down Prize card|put this .* in its place|shuffle this .* into your remaining Prize cards", text):
        atoms.add("hand_to_prize")

    if _has(r"top (?:card|\\d+ cards?) of (?:your|their) deck.*Prize|cards from the top of (?:your|their) deck.*Prize|top of (?:your|their) deck.*Prize", text):
        atoms.add("deck_to_prize")
    if _has(r"Prize cards?.*shuffle them into .*deck|shuffle .*Prize cards into .*deck|Prize cards.*, shuffle them, and put them on the bottom of .*deck", text):
        atoms.add("prize_to_deck")

    if _has(r"discard pile to their Prize cards face down", text):
        atoms.add("discard_to_prize")
    if _has(r"discard 1 of your Prize cards", text):
        atoms.add("prize_to_discard")
    if _has(r"discard 1 of your Prize cards.*if it's an Energy card, attach it", text):
        atoms.add("prize_to_attached")

    if _has(r"switch .*face-down Prize cards? with the top card of .*deck|top card of .*deck.*switch .* with .*face-down Prize cards?", text):
        atoms.add("swap_prize_topdeck")
        atoms.add("deck_to_prize")
        atoms.add("prize_to_deck")

    if _has(r"opponent.*face-down Prize card.*opponent.*hand.*switch those cards", text):
        atoms.add("swap_prize_hand")
        atoms.add("prize_to_hand")
        atoms.add("hand_to_prize")

    if _has(r"shuffle .*Prize cards|Prize cards, shuffle", text):
        atoms.add("shuffle_prizes")

    if _has(r"take (?:a|\d+) Prize cards?", text):
        atoms.add("take_prize")
    if _has(r"take \d+ more Prize cards?|take 1 more Prize card", text):
        atoms.add("take_extra_prize")

    if _has(r"Prize cards they would take in the Lost Zone instead of into their hand", text):
        atoms.add("taken_prize_to_lost_zone")
    if _has(r"discards? any Prize cards they would take .* instead of putting those cards into their hand", text):
        atoms.add("taken_prize_to_discard")

    if _has(r"took (?:this card|this Pokémon) as a face-down Prize card.*before you put it into your hand", text):
        atoms.add("before_hand_prize_trigger")

    return tuple(sorted(atoms))


def _is_legal(card: dict) -> bool:
    if card["id"] in OFFICIAL_BAN_OVERLAY:
        return False
    if (card.get("legalities") or {}).get("expanded") == "Banned":
        return False
    return not any(
        TOURNAMENT_BAN_FRAGMENT in rule.lower()
        for rule in (card.get("rules") or [])
    )


def _effect_texts(card: dict) -> Iterable[tuple[str, str]]:
    for rule in card.get("rules") or []:
        yield "rule", rule
    for attack in card.get("attacks") or []:
        text = attack.get("text") or ""
        if text:
            yield f"attack:{attack.get('name', '')}", text
    for ability in card.get("abilities") or []:
        text = ability.get("text") or ""
        if text:
            yield f"ability:{ability.get('name', '')}", text


def build_catalog(resources_root: Path) -> tuple[PrizeEffectRow, ...]:
    sets = json.loads((resources_root / "sets" / "en.json").read_text(encoding="utf-8"))
    expanded_sets = {
        row["id"]
        for row in sets
        if (row.get("legalities") or {}).get("expanded") == "Legal"
    }

    rows: list[PrizeEffectRow] = []
    for path in sorted((resources_root / "cards" / "en").glob("*.json")):
        if path.stem not in expanded_sets:
            continue
        cards = json.loads(path.read_text(encoding="utf-8"))
        for card in cards:
            if not _is_legal(card):
                continue
            for source, text in _effect_texts(card):
                if "prize" not in text.lower():
                    continue
                atoms = compile_prize_effect(text)
                if atoms:
                    rows.append(
                        PrizeEffectRow(
                            card_id=card["id"],
                            card_name=card["name"],
                            source=source,
                            text=text,
                            atoms=atoms,
                        )
                    )

    return tuple(rows)


def rows_for_card(
    rows: Iterable[PrizeEffectRow],
    card_id: str,
) -> tuple[PrizeEffectRow, ...]:
    return tuple(row for row in rows if row.card_id == card_id)
