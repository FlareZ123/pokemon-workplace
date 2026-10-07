"""Audit player-choice effect-order clauses in the bundled v3.4 rulebook."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AuthorityEvidence:
    case: str
    chooser_role: str
    text: str


CLAUSES = (
    (
        "damaged_pokemon_triggers",
        "affected_pokemon_player",
        re.compile(
            r"If several 6\. Effects activating when a Pokémon is damaged are "
            r"activated at the same time, the player of the Pokémon taking the "
            r"damage gets to choose in which order to apply those effects\.",
            re.IGNORECASE,
        ),
    ),
    (
        "multi_pokemon_ko_triggers",
        "current_turn_player",
        re.compile(
            r"If several Pokémon get Knocked Out at the same time, activating "
            r"several effects in step 2 of the Knock Out resolution process, "
            r"the player whose turn is currently being played gets to decide "
            r"in which order to apply those effects\.",
            re.IGNORECASE,
        ),
    ),
    (
        "energy_attachment_triggers",
        "current_turn_player",
        re.compile(
            r"If there are several effects that would activate when an Energy "
            r"is attached, the player whose turn it is currently decides in "
            r"which order to apply those effects\.",
            re.IGNORECASE,
        ),
    ),
    (
        "pokemon_checkup_effects",
        "next_turn_player",
        re.compile(
            r"(?:"
            r"If there are several such effects to apply, the player whose turn "
            r"would be next can decide in which order to apply them"
            r"|"
            r"If there are several effects that would activate during Pokémon "
            r"Checkup, the player whose turn would be next can decide in which "
            r"order to apply them"
            r")",
            re.IGNORECASE,
        ),
    ),
    (
        "end_of_turn_effects",
        "current_turn_player",
        re.compile(
            r"If several such effects are active at the same time, the player "
            r"whose turn is ending decides in which order to apply those effects\.",
            re.IGNORECASE,
        ),
    ),
)


def normalize(text: str) -> str:
    return " ".join(text.split())


def audit_rulebook(path: Path) -> tuple[AuthorityEvidence, ...]:
    text = normalize(path.read_text(encoding="utf-8"))
    rows: list[AuthorityEvidence] = []
    for case, chooser_role, pattern in CLAUSES:
        matches = tuple(pattern.finditer(text))
        if not matches:
            raise AssertionError(f"missing rulebook authority clause: {case}")
        rows.extend(
            AuthorityEvidence(case, chooser_role, match.group(0))
            for match in matches
        )
    return tuple(rows)
