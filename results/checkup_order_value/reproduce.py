"""Reproduce noncommutative Pokémon Checkup ordering value."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from checkup_order_value import (  # noqa: E402
    CounterEffect,
    CounterEffectKind,
    schedule_outcomes,
)
from effect_order_authority import (  # noqa: E402
    OrderAuthorityCase,
    OrderAuthorityContext,
    ordering_player,
)
from special_condition_state import enumerate_checkup_schedules  # noqa: E402


def load_card(path: str, card_id: str) -> dict[str, object]:
    cards = json.loads((ROOT / path).read_text(encoding="utf-8"))
    return next(card for card in cards if card["id"] == card_id)


def ability_text(card: dict[str, object], ability_name: str) -> str:
    abilities = card.get("abilities", [])
    assert isinstance(abilities, list)
    return next(
        ability["text"]
        for ability in abilities
        if ability.get("name") == ability_name
    )


def main() -> None:
    garganacl = load_card("resources/cards/en/sv2.json", "sv2-123")
    froslass = load_card("resources/cards/en/svp.json", "svp-117")
    assert garganacl["name"] == "Garganacl"
    assert froslass["name"] == "Froslass"
    assert ability_text(garganacl, "Blessed Salt") == (
        "During Pokémon Checkup, heal 20 damage from each of your Pokémon."
    )
    assert ability_text(froslass, "Freezing Shroud") == (
        "During Pokémon Checkup, put 1 damage counter on each Pokémon that has "
        "an Ability (both yours and your opponent's), except any Froslass."
    )

    effects = {
        "Blessed Salt": CounterEffect(
            "Blessed Salt", CounterEffectKind.HEAL, 2
        ),
        "Freezing Shroud": CounterEffect(
            "Freezing Shroud", CounterEffectKind.PUT, 1
        ),
    }
    schedules = enumerate_checkup_schedules(tuple(effects))
    outcomes = schedule_outcomes(
        schedules,
        initial_damage_counters=0,
        condition_block_damage_counters=1,
        effects=effects,
    )

    by_total: dict[int, list[tuple[str, ...]]] = {}
    for schedule, total in outcomes:
        by_total.setdefault(total, []).append(schedule)
    assert set(by_total) == {0, 1, 2}
    assert {total: len(rows) for total, rows in by_total.items()} == {
        0: 2,
        1: 2,
        2: 2,
    }

    chooser = ordering_player(
        OrderAuthorityCase.POKEMON_CHECKUP_EFFECTS,
        OrderAuthorityContext(
            current_turn_player="A",
            next_turn_player="B",
        ),
    )
    assert chooser == "B"

    reverse_chooser = ordering_player(
        OrderAuthorityCase.POKEMON_CHECKUP_EFFECTS,
        OrderAuthorityContext(
            current_turn_player="B",
            next_turn_player="A",
        ),
    )
    assert reverse_chooser == "A"

    print("chooser when A's turn just ended:", chooser)
    print("reachable final damage counters:", sorted(by_total))
    for total in sorted(by_total):
        print(total, "counters:")
        for schedule in by_total[total]:
            print("  ", " -> ".join(schedule))
    print("chooser when B's turn just ended:", reverse_chooser)
    print("checkup order-value regression passed")


if __name__ == "__main__":
    main()
