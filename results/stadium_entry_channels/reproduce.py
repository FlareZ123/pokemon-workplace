"""Reproduce the Stadium play-versus-placement distinction."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from build_expanded_legality_baseline import classify_effective_legality
from stadium_entry_channels import (
    StadiumCopy,
    StadiumEntryState,
    play_stadium_from_hand,
    teleport_room_options,
    use_teleport_room,
)
from turn_action_budget import TurnAction, TurnActionBudget


def normalize(text: str) -> str:
    return " ".join(text.split())


def iter_expanded_cards() -> list[dict]:
    sets = json.loads(
        (ROOT / "resources" / "sets" / "en.json").read_text(encoding="utf-8")
    )
    expanded_sets = {
        row["id"]
        for row in sets
        if (row.get("legalities") or {}).get("expanded") == "Legal"
    }

    cards = []
    for path in sorted((ROOT / "resources" / "cards" / "en").glob("*.json")):
        if path.stem not in expanded_sets:
            continue
        for card in json.loads(path.read_text(encoding="utf-8")):
            status, _ = classify_effective_legality(card)
            if status == "Legal":
                cards.append(card)
    return cards


def direct_stadium_placement_effects() -> list[tuple[str, str, str, str]]:
    pattern = re.compile(
        r"put (?:a|1|the|any)?\s*Stadium card\b.*?\binto play",
        re.IGNORECASE,
    )
    rows = []
    for card in iter_expanded_cards():
        for ability in card.get("abilities") or []:
            text = normalize(ability.get("text", ""))
            if pattern.search(text):
                rows.append((card["id"], card["name"], ability["name"], text))
        for attack in card.get("attacks") or []:
            text = normalize(attack.get("text", ""))
            if pattern.search(text):
                rows.append((card["id"], card["name"], attack["name"], text))
        for rule in card.get("rules") or []:
            text = normalize(rule)
            if pattern.search(text):
                rows.append((card["id"], card["name"], "rule", text))
    return rows


def main() -> None:
    manual = normalize(
        (ROOT / "resources" / "manual" / "EN_advanced_manual-2025-transcription-structured.md")
        .read_text(encoding="utf-8")
    )
    assert "Stadiums can be put into play and stay there" in manual
    assert "Players may only play one Stadium during their turn." in manual
    assert "Once a Stadium has been played from the hand, it stays in play." in manual
    assert (
        "Attacks, Abilities or Trainers can be used even if part of their instructions "
        "cannot be applied."
    ) in manual
    assert (
        "if you did the first part of the effect, you must then also do the second part"
        in manual
    )

    xy3 = json.loads(
        (ROOT / "resources" / "cards" / "en" / "xy3.json").read_text(
            encoding="utf-8"
        )
    )
    gothitelle = next(card for card in xy3 if card["id"] == "xy3-41")
    status, _ = classify_effective_legality(gothitelle)
    assert status == "Legal"
    teleport = next(
        ability
        for ability in gothitelle["abilities"]
        if ability["name"] == "Teleport Room"
    )
    assert normalize(teleport["text"]) == (
        "Once during your turn (before your attack), you may discard any Stadium "
        "card in play. If you do, put a Stadium card with a different name from "
        "your discard pile into play."
    )

    direct = direct_stadium_placement_effects()
    assert direct == [
        (
            "xy3-41",
            "Gothitelle",
            "Teleport Room",
            normalize(teleport["text"]),
        )
    ]

    alpha = StadiumCopy("alpha-1", "Alpha Stadium")
    beta = StadiumCopy("beta-1", "Beta Stadium")
    gamma = StadiumCopy("gamma-1", "Gamma Stadium")

    base = StadiumEntryState(
        budget=TurnActionBudget(),
        hand=(gamma,),
        discard=(beta,),
        in_play=alpha,
        teleport_room_sources=frozenset({"goth-1", "goth-2"}),
    )

    # Effect placement first: A -> B without spending Stadium play, then B -> C
    # by the ordinary play-from-hand action.
    after_teleport = use_teleport_room(base, "goth-1", "beta-1")
    assert after_teleport is not None
    assert after_teleport.in_play == beta
    assert after_teleport.budget.stadium_plays_used == 0
    assert after_teleport.budget.can(TurnAction.STADIUM_PLAY)

    after_play = play_stadium_from_hand(after_teleport, "gamma-1")
    assert after_play is not None
    assert after_play.in_play == gamma
    assert after_play.budget.stadium_plays_used == 1
    assert not after_play.budget.can(TurnAction.STADIUM_PLAY)

    # The channels also compose in the opposite order.
    play_first = play_stadium_from_hand(base, "gamma-1")
    assert play_first is not None
    assert play_first.budget.stadium_plays_used == 1
    teleport_second = use_teleport_room(play_first, "goth-1", "beta-1")
    assert teleport_second is not None
    assert teleport_second.in_play == beta
    assert teleport_second.budget.stadium_plays_used == 1

    # Two physical Gothitelle can each use their own once-per-turn Ability.
    cycle_one = use_teleport_room(base, "goth-1", "beta-1")
    assert cycle_one is not None
    cycle_two = use_teleport_room(cycle_one, "goth-2", "alpha-1")
    assert cycle_two is not None
    assert cycle_two.in_play == alpha
    assert cycle_two.budget.stadium_plays_used == 0
    cycle_then_play = play_stadium_from_hand(cycle_two, "gamma-1")
    assert cycle_then_play is not None
    assert cycle_then_play.in_play == gamma
    assert cycle_then_play.budget.stadium_plays_used == 1

    # Reusing the same physical Ability source is illegal.
    assert use_teleport_room(cycle_one, "goth-1", "alpha-1") is None

    # If a legal replacement exists, the second half is mandatory.
    assert use_teleport_room(base, "goth-1", None) is None
    options = teleport_room_options(base, "goth-1")
    assert len(options) == 1
    assert options[0].in_play == beta

    # If no differently named replacement exists, partial resolution still
    # discards the current Stadium and leaves the Stadium zone empty.
    removal_only = StadiumEntryState(
        budget=TurnActionBudget(),
        in_play=alpha,
        teleport_room_sources=frozenset({"goth-1"}),
    )
    removed = use_teleport_room(removal_only, "goth-1", None)
    assert removed is not None
    assert removed.in_play is None
    assert removed.discard == (alpha,)
    assert removed.budget.stadium_plays_used == 0

    # Teleport Room cannot start from an empty Stadium zone.
    empty = StadiumEntryState(
        budget=TurnActionBudget(),
        discard=(beta,),
        teleport_room_sources=frozenset({"goth-1"}),
    )
    assert use_teleport_room(empty, "goth-1", "beta-1") is None

    # The usual same-name Stadium play restriction remains separate.
    same_name_copy = StadiumCopy("alpha-2", "Alpha Stadium")
    same_name = StadiumEntryState(
        budget=TurnActionBudget(),
        hand=(same_name_copy,),
        in_play=alpha,
    )
    assert play_stadium_from_hand(same_name, "alpha-2") is None

    # Once the turn is over, neither the ordinary play nor this before-attack
    # Ability channel remains available.
    ended_budget = TurnActionBudget().consume(TurnAction.ATTACK)
    assert ended_budget is not None
    ended = StadiumEntryState(
        budget=ended_budget,
        hand=(gamma,),
        discard=(beta,),
        in_play=alpha,
        teleport_room_sources=frozenset({"goth-1"}),
    )
    assert play_stadium_from_hand(ended, "gamma-1") is None
    assert use_teleport_room(ended, "goth-1", "beta-1") is None

    print("stadium_entry_channels regression: PASS")
    print("direct legal Expanded Stadium-placement effects:", len(direct))


if __name__ == "__main__":
    main()
