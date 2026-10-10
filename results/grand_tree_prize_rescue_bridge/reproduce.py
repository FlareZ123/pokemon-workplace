"""Test Prize -> hand -> deck -> Grand Tree with exact physical card IDs."""

from __future__ import annotations

import itertools
import json
import sys
from collections import Counter
from fractions import Fraction
from math import comb
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
for directory in (ROOT, ROOT / "tools"):
    if str(directory) not in sys.path:
        sys.path.insert(0, str(directory))

from gothitelle_bootstrap_prize_availability import EvolutionSupply
from grand_tree_prize_rescue_distribution import (
    distribution_with_one_bridge,
    full_supply_probability_with_one_bridge,
)
from gladion_communication_material_bridge import rescue_to_deck
from tools.board_position_state import BoardPokemon, PokemonCard, make_state
from tools.effect_evolution_source_gate import SourceActionContext
from tools.effect_evolution_timing import build_profiles
from tools.grand_tree_chain_execution import execute_grand_tree_chain
from tools.identity_materialization import (
    CardInstance, IdentityLedger, assert_conserved, move_instance,
    validate_board_position_stack_bindings,
)
from tools.multicopy_zone_state import ZoneCountState
from tools.stadium_effect_instance_usage import (
    StadiumCard, StadiumEffectState, StadiumInPlay,
)
from tools.top_prize_physical_bridge import TopPrizePhysicalState
from tools.turn_attack_window import fresh_turn
from turn_action_budget import TurnActionBudget


def check_card_rules() -> None:
    samples = (
        ("sm4", "sm4-95", "Gladion", "Supporter"),
        ("sm9", "sm9-152", "Pokémon Communication", "Item"),
        ("sv7", "sv7-136", "Grand Tree", "Stadium"),
        ("xy3", "xy3-39", "Gothita", "Basic"),
        ("xy3", "xy3-40", "Gothorita", "Stage 1"),
        ("xy3", "xy3-41", "Gothitelle", "Stage 2"),
    )
    for set_id, card_id, name, subtype in samples:
        cards = json.loads((ROOT / "resources" / "cards" / "en" / (set_id + ".json")).read_text())
        found = next(card for card in cards if card["id"] == card_id)
        assert found["name"] == name
        assert subtype in found["subtypes"]
        assert found["legalities"]["expanded"] == "Legal"
    manual = (ROOT / "resources" / "manual" /
              "EN_advanced_manual-2025-transcription-structured.md").read_text()
    assert "You may also decide to not pick any cards at all" in manual
    assert "search for any card(s) you want without any limitations on the" in manual


def physical_example() -> None:
    ids = [
        CardInstance("basic", "Gothita", "Gothita", "in_play",
                     board_object_id="target"),
        CardInstance("stage1", "Gothorita", "Gothorita", "prize"),
        CardInstance("stage2", "Gothitelle", "Gothitelle", "deck"),
        CardInstance("gladion", "Gladion", "Gladion", "hand"),
        CardInstance("communication", "Pokémon Communication",
                     "Pokémon Communication", "hand"),
        CardInstance("top", "Filler", "Other", "deck_top"),
    ]
    ids += [
        CardInstance("prize" + str(i), "Filler", "Other", "prize")
        for i in range(1, 6)
    ]
    ledger = IdentityLedger(ZoneCountState.from_mapping({}),
                            tuple(sorted(ids, key=lambda x: x.instance_id)))
    state = TopPrizePhysicalState(
        ledger, "top",
        ("stage1",) + tuple("prize" + str(i) for i in range(1, 6)),
        (False,) * 6,
    )
    assert ledger.instance("stage1").zone == "prize"

    # Gladion rescues into hand but that alone does NOT make the card
    # Grand Tree searchable.
    from gladion_physical_prize_transition import resolve_gladion_physical
    raw = resolve_gladion_physical(
        state, gladion_instance_id="gladion", selected_position=0
    )
    assert len(raw) == 720
    assert all(
        outcome.physical_after.ledger.instance("stage1").zone == "hand"
        for outcome in raw
    )
    assert all(
        outcome.physical_after.ledger.instance("gladion").zone == "prize"
        for outcome in raw
    )
    outcomes = rescue_to_deck(
        state, gladion_id="gladion", communication_id="communication",
        position=0, pokemon_classes=frozenset({"Gothorita", "Gothitelle"}),
    )
    assert len(outcomes) == len(raw)
    assert abs(sum(x.probability for x in outcomes) - 1.0) < 1e-12
    assert {x.returned_id for x in outcomes} == {"stage1"}
    assert all(x.ledger.instance("stage1").zone == "deck" for x in outcomes)
    assert all(x.ledger.instance("stage2").zone == "deck" for x in outcomes)
    assert all(x.ledger.instance("communication").zone == "discard" for x in outcomes)
    assert all(x.ledger.instance("gladion").zone == "prize" for x in outcomes)
    assert all(x.ledger.instance("top").zone == "deck" for x in outcomes)
    assert all(set(x.prizes) == {"gladion", *("prize" + str(i) for i in range(1, 6))}
               for x in outcomes)
    assert all(x.ledger.totals() == ledger.totals() for x in outcomes)

    target = BoardPokemon(
        "target", (PokemonCard("basic", "Gothita"),),
        retreat_cost=1, evolution_eligible=True,
    )
    board = make_state((target,), active_id="target", evolution_allowed=True)
    profile = next(x for x in build_profiles(ROOT / "resources") if x.card_id == "sv7-136")
    budget = TurnActionBudget(supporter_used=True)
    stadium = StadiumEffectState(
        budget=budget,
        in_play=StadiumInPlay(
            StadiumCard("tree-copy", "Grand Tree"), "tree-use"
        ),
    )
    context = SourceActionContext(
        is_players_first_turn=False, went_first=False,
        window=fresh_turn(action_budget=budget), stadium_state=stadium,
    )
    result = execute_grand_tree_chain(
        profile, context, board, "target",
        PokemonCard("stage1", "Gothorita", "Gothita"),
        stage1_retreat_cost=1,
        stage2=PokemonCard("stage2", "Gothitelle", "Gothorita"),
        stage2_retreat_cost=2,
    )
    assert result is not None
    assert result.stadium_state is not None
    assert result.stadium_state.used_effect_instances == {"tree-use"}

    physical = outcomes[0].ledger
    physical = move_instance(
        physical, "stage1", "in_play", board_object_id="target"
    )
    physical = move_instance(
        physical, "stage2", "in_play", board_object_id="target"
    )
    validate_board_position_stack_bindings(physical, result.board)
    assert_conserved(ledger, physical)
    assert [c.name for c in result.board.get("target").stack] == [
        "Gothita", "Gothorita", "Gothitelle"
    ]


def brute(supply: EvolutionSupply) -> dict[int, Fraction]:
    categories = (
        ("stage1",) * supply.stage1
        + ("stage2",) * supply.stage2
        + ("other",) * (supply.unseen - supply.stage1 - supply.stage2)
    )
    hist: Counter[int] = Counter()
    for taken in itertools.combinations(range(supply.unseen), supply.prizes):
        p1 = sum(categories[i] == "stage1" for i in taken)
        p2 = sum(categories[i] == "stage2" for i in taken)
        k = min(supply.action_cap, supply.stage1-p1, supply.stage2-p2)
        if p1:
            k = max(k, min(supply.action_cap, supply.stage1-p1+1, supply.stage2-p2))
        if p2:
            k = max(k, min(supply.action_cap, supply.stage1-p1, supply.stage2-p2+1))
        hist[k] += 1
    denominator = comb(supply.unseen, supply.prizes)
    return dict(sorted((k, Fraction(count, denominator)) for k, count in hist.items()))


def test_distribution() -> None:
    cases = 0
    for N in range(4, 10):
        for a in range(4):
            for b in range(4):
                if a+b>N:
                    continue
                for p in range(min(N,4)+1):
                    for cap in range(4):
                        supply = EvolutionSupply(N,p,a,b,cap)
                        assert distribution_with_one_bridge(supply) == brute(supply)
                        cases += 1
    assert cases > 1000
    supply = EvolutionSupply(50,6,3,3,3)
    original = supply.outcome_distribution()
    repaired = distribution_with_one_bridge(supply)
    full = full_supply_probability_with_one_bridge(supply)
    assert repaired[3] == full
    assert repaired[3] > original[3]
    assert repaired[3] - original[3] > Fraction(2,5)
    assert sum(repaired.values(), Fraction()) == 1
    print("small exhaustive cases", cases)
    print("before:", {k:round(float(v),9) for k,v in original.items()})
    print("after:", {k:round(float(v),9) for k,v in repaired.items()})
    print("P full improved", float(repaired[3] - original[3]))


if __name__ == "__main__":
    check_card_rules()
    physical_example()
    test_distribution()
    print("grand_tree_prize_rescue_bridge: PASS")
