"""Reproduce the CL Aichi Shadow Rider -> Regidrago counter-ALS result."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from attack_copy_kernel import (  # noqa: E402
    AttackDef,
    CopySelector,
    PokemonRef,
    State,
    TurnBoundaryEffect,
    choose_exact,
    resolve_attack,
)
from build_expanded_legality_baseline import classify_effective_legality  # noqa: E402
from shadow_rider_regidrago_counter_als import (  # noqa: E402
    PayloadZone,
    RoutingResources,
    copycat_required_energy_units,
    find_payload_route,
    mimikyu_energy_readiness,
    prize_collision_probability,
    supporter_line_feasible,
)


def card(set_id: str, card_id: str) -> dict:
    rows = json.loads(
        (ROOT / "resources" / "cards" / "en" / f"{set_id}.json").read_text(
            encoding="utf-8"
        )
    )
    return next(row for row in rows if row["id"] == card_id)


def legal(card_row: dict) -> None:
    assert classify_effective_legality(card_row)[0] == "Legal"


def attack(card_row: dict, name: str) -> dict:
    return next(row for row in card_row["attacks"] if row["name"] == name)


def main() -> None:
    mimikyu = card("sm2", "sm2-58")
    dialga = card("sm5", "sm5-100")
    regidrago = card("swsh12", "swsh12-136")
    shadow_rider = card("swsh6", "swsh6-75")
    treasure = card("sm6", "sm6-113")
    fog = card("swsh6", "swsh6-140")
    compressor = card("xy4", "xy4-92")
    heavy = card("swsh10", "swsh10-146")
    stretcher = card("sv6pt5", "sv6pt5-61")
    valley = card("xy4", "xy4-93")
    tulip = card("sv4", "sv4-181")
    guzma = card("sm3", "sm3-115")

    for row in (
        mimikyu,
        dialga,
        regidrago,
        shadow_rider,
        treasure,
        fog,
        compressor,
        heavy,
        stretcher,
        valley,
        tulip,
        guzma,
    ):
        legal(row)

    copycat = attack(mimikyu, "Copycat")
    apex = attack(regidrago, "Apex Dragon")
    timeless = attack(dialga, "Timeless-GX")
    assert mimikyu["types"] == ["Psychic"]
    assert mimikyu["subtypes"] == ["Basic"]
    assert copycat["cost"] == ["Psychic", "Colorless"]
    assert "isn't a GX attack" in copycat["text"]
    assert regidrago["types"] == ["Dragon"]
    assert "Dragon Pokémon in your discard pile" in apex["text"]
    assert dialga["types"] == ["Dragon"]
    assert "Take another turn after this one." in timeless["text"]
    assert "Skip the between-turns step." in timeless["text"]
    assert shadow_rider["abilities"][0]["name"] == "Underworld Door"
    assert "Benched Psychic Pokémon" in shadow_rider["abilities"][0]["text"]
    assert "cost Colorless less" in valley["rules"][0]

    routes = {
        (m.value, d.value): find_payload_route(m, d)
        for m in PayloadZone
        for d in PayloadZone
    }
    reachable = {
        key: route
        for key, route in routes.items()
        if route is not None
    }
    unreachable = {
        key
        for key, route in routes.items()
        if route is None
    }
    assert len(reachable) == 15
    assert unreachable == {("prize", "prize")}

    coupled = find_payload_route(
        PayloadZone.DECK,
        PayloadZone.HAND,
        RoutingResources(
            mysterious_treasure=1,
            fog_crystal=0,
            quick_ball=0,
            battle_compressor=0,
            hisuian_heavy_ball=0,
            night_stretcher=0,
            tulip=0,
            disposable_hand_cards=0,
        ),
    )
    assert coupled is not None
    assert coupled.actions == (
        "Mysterious Treasure: discard Dialga-GX, search Mimikyu",
    )

    compressor_stretcher = find_payload_route(
        PayloadZone.DECK,
        PayloadZone.DECK,
        RoutingResources(
            mysterious_treasure=0,
            fog_crystal=0,
            quick_ball=0,
            battle_compressor=1,
            hisuian_heavy_ball=0,
            night_stretcher=1,
            tulip=0,
            disposable_hand_cards=0,
        ),
    )
    assert compressor_stretcher is not None
    assert compressor_stretcher.actions == (
        "Battle Compressor: discard Mimikyu and Dialga-GX",
        "Night Stretcher: recover Mimikyu",
    )

    dialga_prized = find_payload_route(
        PayloadZone.DECK,
        PayloadZone.PRIZE,
        RoutingResources(
            mysterious_treasure=1,
            fog_crystal=0,
            quick_ball=0,
            battle_compressor=0,
            hisuian_heavy_ball=1,
            night_stretcher=0,
            tulip=0,
            disposable_hand_cards=0,
        ),
    )
    assert dialga_prized is not None
    assert len(dialga_prized.actions) == 2

    mimikyu_prized = find_payload_route(
        PayloadZone.PRIZE,
        PayloadZone.DECK,
        RoutingResources(
            mysterious_treasure=0,
            fog_crystal=0,
            quick_ball=0,
            battle_compressor=1,
            hisuian_heavy_ball=1,
            night_stretcher=0,
            tulip=0,
            disposable_hand_cards=0,
        ),
    )
    assert mimikyu_prized is not None
    assert len(mimikyu_prized.actions) == 2
    assert routes[("prize", "prize")] is None

    prizes = prize_collision_probability()
    assert abs(
        prizes.neither_prized - 0.8084745762711865
    ) < 1e-15
    assert abs(
        prizes.exactly_one_prized - 0.18305084745762712
    ) < 1e-15
    assert abs(
        prizes.both_prized - 0.00847457627118644
    ) < 1e-15

    item_locked = RoutingResources(item_play=False)
    assert (
        find_payload_route(
            PayloadZone.DECK,
            PayloadZone.DISCARD,
            item_locked,
        )
        is None
    )
    tulip_only = RoutingResources(
        mysterious_treasure=0,
        fog_crystal=0,
        quick_ball=0,
        battle_compressor=0,
        hisuian_heavy_ball=0,
        night_stretcher=0,
        tulip=1,
        item_play=False,
        disposable_hand_cards=0,
    )
    assert (
        find_payload_route(
            PayloadZone.DISCARD,
            PayloadZone.DISCARD,
            tulip_only,
        )
        is not None
    )

    assert copycat_required_energy_units(
        dimension_valley_live=False
    ) == 2
    assert copycat_required_energy_units(
        dimension_valley_live=True
    ) == 1
    assert mimikyu_energy_readiness(
        dimension_valley_live=True,
        psychic_energy_in_hand=1,
        underworld_door_uses=0,
        manual_attachment_available=True,
    ).ready
    assert mimikyu_energy_readiness(
        dimension_valley_live=False,
        psychic_energy_in_hand=2,
        underworld_door_uses=1,
        manual_attachment_available=True,
    ).ready
    assert not mimikyu_energy_readiness(
        dimension_valley_live=False,
        psychic_energy_in_hand=2,
        underworld_door_uses=0,
        manual_attachment_available=True,
    ).ready

    assert not supporter_line_feasible(
        recover_mimikyu_with_tulip=True,
        promote_mimikyu_with_guzma=True,
    )
    assert supporter_line_feasible(
        recover_mimikyu_with_tulip=False,
        promote_mimikyu_with_guzma=True,
    )

    attacks = {
        "copycat": AttackDef(
            "copycat",
            "Copycat",
            copy_selector=CopySelector(
                source="opponent_last_attack",
                require_non_gx=True,
            ),
            energy_cost=("Psychic", "Colorless"),
        ),
        "apex": AttackDef(
            "apex",
            "Apex Dragon",
            copy_selector=CopySelector(
                source="own_discard",
                required_type="Dragon",
            ),
        ),
        "timeless": AttackDef(
            "timeless",
            "Timeless-GX",
            is_gx=True,
            turn_boundary_effect=TurnBoundaryEffect(
                take_another_turn=True,
                skip_pokemon_checkup=True,
            ),
        ),
    }
    copy_state = State(
        pokemon=(
            PokemonRef(
                card_id="mimikyu",
                name="Mimikyu",
                owner="P1",
                zone="active",
                types=("Psychic",),
                attacks=("copycat",),
            ),
            PokemonRef(
                card_id="dialga",
                name="Dialga-GX",
                owner="P1",
                zone="discard",
                types=("Dragon",),
                attacks=("timeless",),
            ),
            PokemonRef(
                card_id="regidrago",
                name="Regidrago VSTAR",
                owner="P2",
                zone="active",
                types=("Dragon",),
                attacks=("apex",),
            ),
        ),
        last_declared_attack=(("P2", "apex"),),
    )
    resolution = resolve_attack(
        actor_player="P1",
        actor_card_id="mimikyu",
        declared_attack_id="copycat",
        attacks=attacks,
        state=copy_state,
        choose=choose_exact(("apex", "timeless")),
    )
    assert resolution.body_chain == (
        "copycat",
        "apex",
        "timeless",
    )
    assert "P1" in resolution.state.gx_used_by
    assert resolution.state.pending_turn_boundary == TurnBoundaryEffect(
        take_another_turn=True,
        skip_pokemon_checkup=True,
    )
    assert resolution.state.last_attack_for("P1") == "copycat"

    shortest = {
        f"{m}->{d}": (
            None if route is None else len(route.actions)
        )
        for (m, d), route in routes.items()
    }
    print(
        json.dumps(
            {
                "payload_zone_pairs_reachable": len(reachable),
                "payload_zone_pairs_total": len(routes),
                "unreachable_pairs": sorted(
                    [list(pair) for pair in unreachable]
                ),
                "both_prized_probability": prizes.both_prized,
                "exactly_one_prized_probability": (
                    prizes.exactly_one_prized
                ),
                "copycat_energy_without_valley": (
                    copycat_required_energy_units(
                        dimension_valley_live=False
                    )
                ),
                "copycat_energy_with_valley": (
                    copycat_required_energy_units(
                        dimension_valley_live=True
                    )
                ),
                "copy_chain": list(resolution.body_chain),
                "shortest_payload_actions": shortest,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
