"""Fail-closed full-text coverage audit for attack-applied hand restrictions.

A recognized restriction is only one component of an attack's consequences.
This module reuses the source-scoped restrictions and conservative attack
compilers; it does not certify whole-game attack execution.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from pathlib import Path
import re

from attack_text_coverage_inventory import build_coverage
from simple_attack_board_semantics import compile_legal_index
from source_scoped_restriction_activation import (
    RestrictionActivationProfile,
    build_restriction_activation_profiles,
)

_HAND = re.compile(r"\bfrom (?:their|his or her|your) hand\b", re.I)
_SENTENCES = re.compile(r"(?<=\.)\s+")

# Match complete known secondary sentences; new ones stay opaque.
_EXTRA = {
    "Flip a coin.": "coin_flip",
    "Choose Item cards or Supporter cards.": "player_choice",
    "(You can't use more than 1 GX attack in a game.)": "gx_budget",
    "Shuffle this Pokémon and all cards attached to it into your deck.": "self_shuffle",
    "Discard all Energy from this Pokémon.": "self_energy_discard",
    "Your opponent's Active Pokémon is now Confused.": "special_condition",
    "If your opponent has a Stadium in play, discard it.": "stadium_discard",
    "If 1 of your Pokémon used Cold Snap during your last turn, this attack can't be used.": "attack_history_gate",
    "You can use this attack only if you go second, and only on your first turn.": "first_turn_gate",
    "You can use this attack only if you go second, and only during your first turn.": "first_turn_gate",
    "If this Pokémon has at least 5 extra Darkness Energy attached to it (in addition to this attack's cost), your opponent's Active Pokémon is Knocked Out.": "conditional_knockout",
    "If this Pokémon has at least 1 extra Psychic Energy attached to it (in addition to this attack's cost), each player draws cards until they have 7 cards in their hand.": "conditional_draw",
}


@dataclass(frozen=True)
class AttackLockAudit:
    attack_id: str
    card_name: str
    attack_name: str
    profile: RestrictionActivationProfile
    other_handlers: tuple[str, ...]
    opaque_clauses: tuple[str, ...]

    @property
    def lock_only(self) -> bool:
        return not self.other_handlers and not self.opaque_clauses


def audit_text(text: str, profile: RestrictionActivationProfile):
    if profile.activation_family != "attack_applied":
        raise ValueError("requires attack-applied restriction profile")
    if text != profile.restriction.text:
        raise ValueError("attack body and restricted source text differ")
    other: list[str] = []
    opaque: list[str] = []
    locks = 0
    for sentence in _SENTENCES.split(text):
        if "can't" in sentence.lower() and _HAND.search(sentence):
            locks += 1
        elif sentence in _EXTRA:
            other.append(_EXTRA[sentence])
        else:
            opaque.append(sentence)
    if locks == 0:
        raise ValueError("no source hand restriction located")
    required = {
        "coin_heads": "coin_flip",
        "coin_branch": "coin_flip",
        "player_choice": "player_choice",
        "stadium_discard_if_you_do": "stadium_discard",
    }.get(profile.application_gate)
    if required and required not in other:
        raise ValueError(f"restriction gate missing its handler: {required}")
    return tuple(dict.fromkeys(other)), tuple(opaque)


def build_attack_lock_audit(resources_root: Path) -> tuple[AttackLockAudit, ...]:
    index = compile_legal_index(resources_root)
    audited = []
    for profile in build_restriction_activation_profiles(resources_root):
        if profile.activation_family != "attack_applied":
            continue
        source = profile.restriction
        candidates = [
            row for row in index[source.card_id]
            if source.source == f"attack:{row.attack_name}"
            and row.raw_text == source.text
        ]
        if len(candidates) != 1:
            raise ValueError(f"nonunique attack binding: {source.card_id}")
        row = candidates[0]
        if row.fixed_damage is None:
            raise ValueError(f"unknown printed damage: {row.attack_id}")
        other, opaque = audit_text(row.raw_text, profile)
        audited.append(AttackLockAudit(
            row.attack_id, row.card_name, row.attack_name, profile, other, opaque
        ))
    if len({row.attack_id for row in audited}) != len(audited):
        raise ValueError("duplicate attack binding")
    return tuple(sorted(audited, key=lambda a: a.attack_id))


def build_lock_aware_coverage(resources_root: Path) -> dict:
    """Overlay typed lock semantics without altering damage-only acceptance."""
    base = build_coverage(resources_root)
    audited = build_attack_lock_audit(resources_root)
    by_id = {entry.attack_id: entry for entry in audited}
    counts: Counter[str] = Counter()
    for row in base["rows"]:
        entry = by_id.get(row.attack_id)
        if entry is None:
            counts[row.kind] += 1
        elif row.kind != "uncompiled_effect_text":
            raise ValueError(f"unexpected base coverage: {row.attack_id}")
        else:
            counts[
                "source_scoped_lock_only" if entry.lock_only
                else "source_scoped_lock_with_other_handlers"
            ] += 1
    return {
        "total": base["total"],
        "base_uncompiled": base["counts"]["uncompiled_effect_text"],
        "remaining_uncompiled": counts["uncompiled_effect_text"],
        "counts": dict(sorted(counts.items())),
        "audited": audited,
        "handler_profiles": dict(sorted(Counter(
            entry.other_handlers for entry in audited
        ).items())),
        "opaque": tuple(
            (entry.attack_id, clause)
            for entry in audited for clause in entry.opaque_clauses
        ),
    }
