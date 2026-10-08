"""Compile typed transition profiles for literal full-hand reset effects."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path

from catalog_full_hand_resets import ResetFamily, catalog_full_hand_resets


@dataclass(frozen=True)
class ResetTransitionProfile:
    name: str
    source_kind: str
    effect_name: str
    draw_count: int
    print_count: int
    hand_disposition: str
    source_gate: str
    requires_bench_slot: bool
    supporter_cost: bool
    once_per_game_resource: str
    first_turn_rule: str
    ends_turn: bool
    fresh_hand_actionable_same_turn: bool
    draw_position_source: str
    deck_position_sensitive: bool


def _load_card(resources_root: Path, print_id: str) -> dict:
    set_id = print_id.split("-", 1)[0]
    rows = json.loads(
        (resources_root / "cards" / "en" / f"{set_id}.json").read_text(
            encoding="utf-8"
        )
    )
    return next(card for card in rows if card["id"] == print_id)


def _effect_text(card: dict, family: ResetFamily) -> str:
    if family.source_kind == "trainer":
        candidates = card.get("rules") or []
    elif family.source_kind == "ability":
        candidates = [
            ability.get("text") or ""
            for ability in card.get("abilities") or []
            if (ability.get("name") or "") == family.effect_name
        ]
    else:
        candidates = [
            attack.get("text") or ""
            for attack in card.get("attacks") or []
            if (attack.get("name") or "") == family.effect_name
        ]

    matches = [
        text
        for text in candidates
        if "discard your hand and draw" in text.lower()
    ]
    if not matches:
        raise ValueError(f"no reset text found for {family.name}")
    return " ".join(matches[0].split())


def _source_gate(family: ResetFamily, text: str) -> tuple[str, bool]:
    if family.source_kind == "trainer":
        return "trainer_from_hand", False
    if family.source_kind == "attack":
        return "active_attack", False
    if "from your hand onto your Bench" in text:
        return "hand_to_bench", True
    return "in_play_ability", False


def _first_turn_rule(text: str) -> str:
    lowered = text.lower()
    if "once during your first turn" in lowered:
        return "first_turn_only"
    if "if you go first" in lowered and "first turn" in lowered:
        return "going_first_exception"
    return "none"


def _once_per_game_resource(text: str) -> str:
    if "VSTAR Power" in text:
        return "vstar_power"
    if "GX attack" in text:
        return "gx_attack"
    return "none"


def compile_reset_transition_profiles(
    resources_root: Path = Path("resources"),
) -> tuple[ResetTransitionProfile, ...]:
    profiles = []

    for family in catalog_full_hand_resets(resources_root):
        card = _load_card(resources_root, family.print_ids[0])
        text = _effect_text(card, family)
        source_gate, requires_bench_slot = _source_gate(family, text)
        draw_position_source = (
            "top_or_bottom_choice"
            if "bottom of your deck" in text.lower()
            else "top"
        )

        profiles.append(
            ResetTransitionProfile(
                name=family.name,
                source_kind=family.source_kind,
                effect_name=family.effect_name,
                draw_count=family.draw_count,
                print_count=len(family.print_ids),
                hand_disposition="discard_all",
                source_gate=source_gate,
                requires_bench_slot=requires_bench_slot,
                supporter_cost=family.supporter,
                once_per_game_resource=_once_per_game_resource(text),
                first_turn_rule=_first_turn_rule(text),
                ends_turn=family.ends_turn,
                fresh_hand_actionable_same_turn=not family.ends_turn,
                draw_position_source=draw_position_source,
                deck_position_sensitive=family.position_sensitive,
            )
        )

    return tuple(
        sorted(
            profiles,
            key=lambda row: (row.source_kind, row.name, row.effect_name),
        )
    )


def main() -> None:
    profiles = compile_reset_transition_profiles()
    print(
        json.dumps(
            {
                "profile_count": len(profiles),
                "profiles": [asdict(profile) for profile in profiles],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
