"""SFT: canonical Teleport Room x Bench capacity composition, with detailed checks."""
from __future__ import annotations

import json
import math
import sys
from dataclasses import replace
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from bench_teleport_capacity_bridge import (
    BenchPokemon,
    bench_capacity,
    bench_from_hand,
    play_stadium,
    sample_state,
    teleport_room,
)
from stadium_entry_channels import StadiumCopy
from turn_action_budget import TurnAction, TurnActionBudget


def check_card_text() -> None:
    cards = {}
    for set_name in ("xy3", "xy6", "swsh9", "sv7", "sm2"):
        rows = json.loads(
            (ROOT / "resources" / "cards" / "en" / f"{set_name}.json")
            .read_text(encoding="utf-8")
        )
        cards.update({card["id"]: card for card in rows})
    goth = cards["xy3-41"]
    effect = goth["abilities"][0]["text"]
    assert goth["abilities"][0]["name"] == "Teleport Room"
    assert "discard any Stadium card in play" in effect
    assert "different name from your discard pile into play" in effect
    assert "8 Pokémon" in " ".join(cards["xy6-89"]["rules"])
    assert "more than 4 Benched" in " ".join(cards["swsh9-137"]["rules"])
    assert "Tera Pokémon in play" in " ".join(cards["sv7-131"]["rules"])
    roadblock = next(
        ability for ability in cards["sm2-66"]["abilities"]
        if ability["name"] == "Roadblock"
    )
    assert "more than 4 Benched" in roadblock["text"]
    assert "use the smaller number" in roadblock["text"]
    print("PASS: card text matches all five grounded effects")


def main() -> None:
    check_card_text()
    first = BenchPokemon("regular-1")
    second = BenchPokemon("regular-2")
    tera = BenchPokemon("tera-1", tera=True)
    sky = StadiumCopy("sky-1", "Sky Field")
    area = StadiumCopy("area-1", "Area Zero Underdepths")
    another_collapsed = StadiumCopy("collapsed-2", "Collapsed Stadium")
    ordinary_stadium = StadiumCopy("ordinary-stadium-1", "Ordinary Stadium")

    # A pre-established Active Gothitelle can discard Collapsed Stadium from
    # four-of-four occupancy, even with no eligible replacement in discard.
    base = sample_state(
        hand_pokemon=(first, second), stadium_plays_used=1,
    )
    assert bench_capacity(base) == 4
    assert bench_from_hand(base, first.copy_id) is None
    removed = teleport_room(base, "goth-1")
    assert len(removed) == 1
    cleared = removed[0]
    assert cleared.stadiums.in_play is None
    assert bench_capacity(cleared) == 5
    assert cleared.stadiums.budget.stadium_plays_used == 1
    assert cleared.stadiums.teleport_room_used == frozenset({"goth-1"})
    one_entered = bench_from_hand(cleared, first.copy_id)
    assert one_entered is not None
    assert len(one_entered.bench) == 5
    assert bench_from_hand(one_entered, second.copy_id) is None
    assert teleport_room(cleared, "goth-1") == ()
    print("PASS: no-replacement removal grants exactly one slot after Stadium quota spent")

    # Same-name copies are ineligible for Teleport Room's second half.
    same = sample_state(discarded_stadiums=(another_collapsed,))
    same_out = teleport_room(same, "goth-1")
    assert len(same_out) == 1
    assert same_out[0].stadiums.in_play is None
    assert len(same_out[0].stadiums.discard) == 2
    print("PASS: a discarded Collapsed copy is not a different-name replacement")

    # From the same full board, an in-discard Sky Field is immediately live.
    sky_base = sample_state(
        discarded_stadiums=(sky,),
        hand_pokemon=(first, second),
        stadium_plays_used=1,
    )
    sky_out = teleport_room(sky_base, "goth-1")
    assert len(sky_out) == 1
    sky_state = sky_out[0]
    assert sky_state.stadiums.in_play == sky
    assert bench_capacity(sky_state) == 8
    after_first = bench_from_hand(sky_state, first.copy_id)
    assert after_first is not None
    after_second = bench_from_hand(after_first, second.copy_id)
    assert after_second is not None and len(after_second.bench) == 6
    assert after_second.stadiums.budget.stadium_plays_used == 1
    print("PASS: Teleport to Sky Field admits two entrants despite used Stadium quota")

    # Area Zero reopens only one ordinary slot before a Tera arrives.
    area_base = sample_state(
        discarded_stadiums=(area,),
        hand_pokemon=(first, tera),
    )
    area_out = teleport_room(area_base, "goth-1")
    assert len(area_out) == 1
    area_state = area_out[0]
    assert bench_capacity(area_state) == 5
    t_first = bench_from_hand(area_state, tera.copy_id)
    assert t_first is not None and bench_capacity(t_first) == 8
    assert bench_from_hand(t_first, first.copy_id) is not None
    ordinary_first = bench_from_hand(area_state, first.copy_id)
    assert ordinary_first is not None
    assert bench_capacity(ordinary_first) == 5
    assert bench_from_hand(ordinary_first, tera.copy_id) is None
    print("PASS: discard-to-Area Zero preserves the Tera-first ordering constraint")

    # If multiple different-name Stadiums are in discard, choosing a
    # replacement is mandatory. Both branches remain available.
    mixed = sample_state(discarded_stadiums=(sky, ordinary_stadium))
    mixed_out = teleport_room(mixed, "goth-1")
    assert {s.stadiums.in_play for s in mixed_out} == {sky, ordinary_stadium}
    assert {bench_capacity(s) for s in mixed_out} == {5, 8}
    print("PASS: mandatory replacement branches are enumerated, no fake empty option")

    # Direct Stadium play and Teleport Room are independent channels.
    hand_sky = sample_state(
        hand_stadiums=(sky,), hand_pokemon=(first, second),
    )
    via_ability = teleport_room(hand_sky, "goth-1")[0]
    via_play = play_stadium(via_ability, sky.copy_id)
    assert len(via_play) == 1
    assert via_play[0].stadiums.budget.stadium_plays_used == 1
    assert bench_capacity(via_play[0]) == 8
    print("PASS: Teleport then ordinary Sky Field play uses only one Stadium play")

    # The same physical Bench occupants must obey a later contraction.
    retract_base = sample_state(
        discarded_stadiums=(sky,),
        hand_stadiums=(another_collapsed,),
        hand_pokemon=(first, second),
    )
    expanded = teleport_room(retract_base, "goth-1")[0]
    with_first = bench_from_hand(expanded, first.copy_id)
    assert with_first is not None
    with_second = bench_from_hand(with_first, second.copy_id)
    assert with_second is not None and len(with_second.bench) == 6
    contracted = play_stadium(with_second, another_collapsed.copy_id)
    assert len(contracted) == math.comb(6, 4)
    assert all(len(s.bench) == 4 and bench_capacity(s) == 4 for s in contracted)
    assert all(len(s.stadiums.teleport_room_sources) == 1 for s in contracted)
    print("PASS: Stadium contraction enumerates all 15 own-Bench discard choices")

    # A simultaneous opponent Roadblock cap remains binding even when
    # Teleport successfully places an eight-slot Sky Field.
    roadblock_state = sample_state(
        discarded_stadiums=(sky,),
        hand_pokemon=(first,),
        opponent_roadblock_live=True,
    )
    roadblock_after = teleport_room(roadblock_state, "goth-1")
    assert len(roadblock_after) == 1
    assert roadblock_after[0].stadiums.in_play == sky
    assert bench_capacity(roadblock_after[0]) == 4
    assert bench_from_hand(roadblock_after[0], first.copy_id) is None
    roadblock_removed = replace(roadblock_after[0], opponent_roadblock_live=False)
    assert bench_capacity(roadblock_removed) == 8
    assert bench_from_hand(roadblock_removed, first.copy_id) is not None
    assert bench_capacity(teleport_room(
        sample_state(opponent_roadblock_live=True), "goth-1"
    )[0]) == 4
    print("PASS: Roadblock overrides Sky Field and removal-only restoration")

    # A Benched Gothitelle is itself a contractible physical occupant.
    source_benched_base = sample_state(
        discarded_stadiums=(sky,),
        hand_stadiums=(another_collapsed,),
        hand_pokemon=(first, second),
    )
    goth_in_bench = replace(
        source_benched_base,
        active=BenchPokemon("attacker-1"),
        bench=(source_benched_base.active,) + source_benched_base.bench[:3],
    )
    after_sky = teleport_room(goth_in_bench, "goth-1")[0]
    with_one = bench_from_hand(after_sky, first.copy_id)
    assert with_one is not None
    with_two = bench_from_hand(with_one, second.copy_id)
    assert with_two is not None
    shortened = play_stadium(with_two, another_collapsed.copy_id)
    assert len(shortened) == 15
    kept = [row for row in shortened if "goth-1" in row.stadiums.teleport_room_sources]
    lost = [row for row in shortened if not row.stadiums.teleport_room_sources]
    assert len(kept) == 10 and len(lost) == 5
    assert all(row.stadiums.teleport_room_used == frozenset() for row in lost)
    print("PASS: physical contraction preserves source in 10 choices, loses it in 5")

    # An Ability lock or ended turn removes the Ability channel.
    locked = sample_state(ability_locked=True)
    assert teleport_room(locked, "goth-1") == ()
    ended_budget = TurnActionBudget().consume(TurnAction.ATTACK)
    assert ended_budget is not None
    ended = replace(base, stadiums=replace(base.stadiums, budget=ended_budget))
    assert teleport_room(ended, "goth-1") == ()
    assert teleport_room(base, "not-a-source") == ()
    print("PASS: source, lock and before-attack timing gates are enforced")
    print("bench_teleport_capacity_bridge regression: PASS")


if __name__ == "__main__":
    main()
