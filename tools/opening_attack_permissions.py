"""Source-attested opening-turn attack permissions in paper Expanded.

An exception printed on one attack never unlocks a sibling attack.
"""

from __future__ import annotations

import json
import re
from collections import Counter
from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class OpeningKind(str, Enum):
    FIRST_PLAYER_EXCEPTION = "first_player_exception"
    SECOND_FIRST_ONLY = "second_first_only"
    SECOND_FIRST_BANNED = "second_first_banned"
    SECOND_FIRST_BONUS = "second_first_bonus"


@dataclass(frozen=True)
class OpeningAttack:
    print_id: str
    pokemon: str
    attack_name: str
    kind: OpeningKind
    text: str


def classify(text: str) -> OpeningKind | None:
    """Recognize all audited first-turn English attack wording families."""
    normalized = " ".join(text.split())
    if re.search(
        r"^If you go first, you can use this attack (?:on|during) your first turn\.",
        normalized,
    ):
        return OpeningKind.FIRST_PLAYER_EXCEPTION
    if re.search(
        r"^You can use this attack only if you go second, and only (?:on|during) your first turn\.",
        normalized,
    ):
        return OpeningKind.SECOND_FIRST_ONLY
    if re.search(
        r"^If you go second, you can't use this attack during your first turn\.",
        normalized,
    ):
        return OpeningKind.SECOND_FIRST_BANNED
    if re.search(r"If you go second.*first turn", normalized):
        return OpeningKind.SECOND_FIRST_BONUS
    if "first turn" in normalized.lower():
        raise ValueError(f"Unrecognized first-turn attack text: {normalized}")
    return None


def legal_opening_attack(
    kind: OpeningKind | None, *, went_first: bool, own_turn: int
) -> bool:
    """Whether a specific attack may be announced in the opening window."""
    if own_turn < 1:
        raise ValueError("own_turn must be positive")
    if kind is OpeningKind.SECOND_FIRST_ONLY:
        return not went_first and own_turn == 1
    if kind is OpeningKind.SECOND_FIRST_BANNED and not went_first and own_turn == 1:
        return False
    if kind is OpeningKind.FIRST_PLAYER_EXCEPTION and went_first and own_turn == 1:
        return True
    return not (went_first and own_turn == 1)


def scan_card_dir(root: Path) -> tuple[OpeningAttack, ...]:
    """Inventory database Expanded-Legal exact prints, not merged names."""
    entries: list[OpeningAttack] = []
    for path in sorted(root.glob("*.json")):
        for card in json.loads(path.read_text(encoding="utf-8")):
            if card.get("legalities", {}).get("expanded") != "Legal":
                continue
            for attack in card.get("attacks") or ():
                text = attack.get("text") or ""
                kind = classify(text)
                if kind is not None:
                    entries.append(
                        OpeningAttack(
                            print_id=card["id"],
                            pokemon=card["name"],
                            attack_name=attack["name"],
                            kind=kind,
                            text=text,
                        )
                    )
    return tuple(entries)


def counts(entries: tuple[OpeningAttack, ...]) -> dict[str, int]:
    return dict(sorted(Counter(row.kind.value for row in entries).items()))
