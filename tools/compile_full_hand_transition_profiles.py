"""Combine literal discard resets and return-to-deck redraws as typed transitions."""
from __future__ import annotations
from dataclasses import asdict, dataclass
import json
from pathlib import Path
import re

from catalog_full_hand_replacements import catalog_full_hand_replacements
from compile_reset_transition_profiles import compile_reset_transition_profiles

_DRAW_NUMBER = re.compile(r"\bdraws?\s+(\d+)\s+cards?\b", re.I)


@dataclass(frozen=True)
class FullHandTransitionProfile:
    name: str
    effect_name: str
    source_kind: str
    source_gate: str
    target_scope: str
    hand_destination: str
    draw_mode: str
    fixed_draw_count: int | None
    draw_position_source: str
    supporter_cost: bool
    once_per_game_resource: str
    first_turn_rule: str
    ends_turn: bool
    print_count: int
    source_text: str


def _source_gate(kind: str, text: str) -> str:
    lower = text.lower()
    if kind == "supporter": return "supporter_from_hand"
    if kind == "item": return "item_from_hand"
    if kind == "stadium": return "stadium_activated_in_play"
    if kind == "attack": return "active_attack"
    if "from your hand to evolve" in lower: return "hand_evolution_trigger"
    if "from your hand onto your bench" in lower: return "hand_to_bench"
    return "in_play_ability"


def _draw_shape(text: str) -> tuple[str, int | None]:
    lower = text.lower()
    figures = [int(x) for x in _DRAW_NUMBER.findall(text)]
    # Conservative: do not promote conditional/opponent-relative effects or
    # cards with multiple numeric draw instructions to a fixed draw edge.
    sensitive = ("if ", "flip a coin", "choose 1:", "equal to", "for each",
                 "until you have", "a card for each", "draw up to")
    if len(figures) == 1 and not any(s in lower for s in sensitive):
        return "fixed", figures[0]
    return "card_text_dependent", None


def compile_full_hand_transition_profiles(
    resources_root: Path = Path("resources"),
) -> tuple[FullHandTransitionProfile, ...]:
    profiles = []
    for row in compile_reset_transition_profiles(resources_root):
        kind = "supporter" if row.source_kind == "trainer" else row.source_kind
        assert row.hand_disposition == "discard_all"
        profiles.append(FullHandTransitionProfile(
            name=row.name, effect_name=row.effect_name, source_kind=kind,
            source_gate="supporter_from_hand" if kind == "supporter" else row.source_gate,
            target_scope="self", hand_destination="discard_all",
            draw_mode="fixed", fixed_draw_count=row.draw_count,
            draw_position_source=row.draw_position_source,
            supporter_cost=row.supporter_cost,
            once_per_game_resource=row.once_per_game_resource,
            first_turn_rule=row.first_turn_rule,
            ends_turn=row.ends_turn, print_count=row.print_count,
            source_text="catalog_full_hand_resets:literal_draw_count",
        ))
    for row in catalog_full_hand_replacements(resources_root):
        text = row.example_text
        mode, count = _draw_shape(text)
        kind = row.source_kind
        resource = (
            "gx_attack" if kind == "attack" and row.effect_name.endswith("-GX")
            else "vstar_power" if kind == "ability" and "VSTAR Power" in text
            else "none"
        )
        profiles.append(FullHandTransitionProfile(
            name=row.name, effect_name=row.effect_name, source_kind=kind,
            source_gate=_source_gate(kind, text), target_scope=row.target_scope,
            hand_destination=row.hand_destination,
            draw_mode=mode, fixed_draw_count=count,
            draw_position_source="top", supporter_cost=kind == "supporter",
            once_per_game_resource=resource,
            first_turn_rule="text_condition" if "first turn" in text.lower() else "none",
            ends_turn=row.ends_turn, print_count=len(row.print_ids), source_text=text,
        ))
    return tuple(sorted(profiles, key=lambda x: (x.hand_destination, x.name, x.effect_name, x.source_text)))


def main() -> None:
    profiles = compile_full_hand_transition_profiles()
    print(json.dumps({"profile_count": len(profiles),
        "print_count": sum(x.print_count for x in profiles),
        "profiles": [asdict(p) for p in profiles]}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
