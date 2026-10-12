"""Reproduce self/team typed Energy no-cost abilities and context overrides."""
from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from board_object_kernel import EnergyAttachment, make_board, make_pokemon
from energy_board_conservation import EnergyBoardState
from multicopy_zone_state import ZoneCountState
from retreat_action_enumerator import enumerate_board_derived_retreat_actions
from retreat_cost_semantics import effective_retreat_cost
from retreat_dynamic_energy_units import RetreatEnergyProviderContext
from retreat_energy_transaction import RetreatEnergyTransactionState
from retreat_environment_modifiers import derive_environment_retreat_modifiers
from retreat_typed_energy_no_cost import (
    SOURCES, derive_typed_energy_no_retreat_cost,
    provides_required_energy_type,
)
from turn_action_budget import TurnActionBudget
from unified_state_kernel import make_state


SYMBOLS = frozenset("GRWLPFDMY")


def actor_for(source, *, matched=True, enabled=True):
    symbol = source.energy_type if matched else "C"
    energy = EnergyAttachment("energy", "Basic typed Energy", (symbol,))
    holder = make_pokemon(
        "holder", source.card_name, print_id=source.print_id,
        energy=(energy,), abilities_enabled=enabled,
    )
    if source.scope == "self":
        return make_board(holder)
    active = make_pokemon("active", "Any friendly Pokémon", energy=(energy,))
    source_pokemon = make_pokemon(
        "source", source.card_name, print_id=source.print_id,
        abilities_enabled=enabled,
    )
    return make_board(active, (source_pokemon,))


def source_regressions() -> None:
    for source in SOURCES:
        yes = actor_for(source)
        no = actor_for(source, matched=False)
        disabled = actor_for(source, enabled=False)

        assert len(derive_typed_energy_no_retreat_cost(yes)) == 1, source
        assert derive_typed_energy_no_retreat_cost(no) == (), source
        assert derive_typed_energy_no_retreat_cost(disabled) == (), source

        modifiers = derive_environment_retreat_modifiers(
            yes, make_board(make_pokemon("other", "Other")),
            stadium_print_id="swsh2-160",
        )
        assert effective_retreat_cost(2, modifiers) == 0, source

    # A friendly *Bench* aura cannot help a source on the opposing Bench.
    active = make_pokemon(
        "a", "Any Active",
        energy=(EnergyAttachment("d", "Basic Darkness Energy", ("D",)),),
    )
    enemy = make_board(
        make_pokemon("e", "Other"),
        (make_pokemon("darkrai", "Darkrai-EX", print_id="bw5-63"),),
    )
    assert derive_typed_energy_no_retreat_cost(make_board(active)) == ()
    assert not any(m.no_retreat_cost for m in derive_environment_retreat_modifiers(
        make_board(active), enemy,
    ))


def printed_special_energy_context() -> None:
    active = make_pokemon("active", "Basic", tags=("Basic",))
    stage1 = make_pokemon("active", "Stage 1", tags=("Stage1",))

    def tested(card, symbol, holder=active, context=None):
        return provides_required_energy_type(
            card, holder, symbol, context=context,
        )

    rainbow = EnergyAttachment("e", "Rainbow Energy", ("C",), "sm1-137")
    assert all(tested(rainbow, symbol) for symbol in SYMBOLS)
    assert not tested(
        EnergyAttachment("e", "Rainbow Energy", ("C",), "unverified"),
        "P",
    )

    prism = EnergyAttachment("e", "Prism Energy", ("C",), "bw4-93")
    assert tested(prism, "D") and not tested(prism, "D", holder=stage1)

    unit = EnergyAttachment(
        "e", "Unit Energy LightningPsychicMetal", ("C",), "sm5-138",
    )
    assert tested(unit, "P") and tested(unit, "L")
    assert not tested(unit, "W")

    all_types = EnergyAttachment(
        "e", "Aurora Energy", ("C",), "swsh1-186",
    )
    assert tested(all_types, "F")

    dragon = make_pokemon("active", "Dragon", tags=("Dragon",))
    double_dragon = EnergyAttachment(
        "e", "Double Dragon Energy", ("C", "C"), "xy6-97",
    )
    assert tested(double_dragon, "W", holder=dragon)
    assert not tested(double_dragon, "W", holder=stage1)

    reversal = EnergyAttachment(
        "e", "Reversal Energy", ("C", "C", "C"), "sv2-192",
    )
    behind = RetreatEnergyProviderContext(own_prizes_remaining=6,
                                          opponent_prizes_remaining=5)
    tied = RetreatEnergyProviderContext(own_prizes_remaining=5,
                                        opponent_prizes_remaining=5)
    assert tested(reversal, "D", holder=stage1, context=behind)
    assert not tested(reversal, "D", holder=stage1, context=tied)
    assert not tested(reversal, "D", holder=active, context=behind)

    counter = EnergyAttachment(
        "e", "Counter Energy", ("C", "C"), "sm4-100",
    )
    assert tested(counter, "D", holder=stage1, context=behind)
    assert not tested(counter, "D", holder=stage1, context=tied)
    assert not tested(counter, "D", holder=make_pokemon(
        "gx", "GX", tags=("Pokemon-GX",),
    ), context=behind)

    luminous = EnergyAttachment(
        "e", "Luminous Energy", ("C",), "sv2-191",
    )
    sole_holder = make_pokemon(
        "solo", "Solo", energy=(luminous,),
    )
    another_holder = make_pokemon(
        "multi", "Multi", energy=(
            luminous,
            EnergyAttachment("other", "Horror Psychic Energy", ("P",)),
        ),
    )
    basic_partner = make_pokemon("basic-partner", "Basic plus Luminous", energy=(
        luminous, EnergyAttachment("other-basic", "Basic Water Energy", ("W",)),
    ))
    assert tested(luminous, "P", holder=basic_partner)
    assert tested(luminous, "P", holder=sole_holder)
    assert not tested(luminous, "P", holder=another_holder)


def physical_aura_and_prize_context() -> None:
    def scenario(*, active_energy, active_tags=("Stage1",), behind=False,
                 aura_enabled=True):
        active = make_pokemon(
            "active", "Active Holder", tags=active_tags,
            energy=(active_energy,),
        )
        darkrai = make_pokemon(
            "darkrai", "Darkrai-EX", print_id="bw5-63",
            abilities_enabled=aura_enabled,
        )
        own = make_board(active, (
            make_pokemon("pivot", "Pivot"), darkrai,
        ))
        state = RetreatEnergyTransactionState(
            unified=make_state({}, turn_budget=TurnActionBudget()),
            energy=EnergyBoardState(
                zones=ZoneCountState.from_mapping({
                    ("attached_energy", "attached"): 1,
                }),
                board=own,
                instance_classes=((active_energy.instance_id, "attached_energy"),),
            ),
        )
        opponent = make_board(make_pokemon("opponent", "Opponent"))
        context = RetreatEnergyProviderContext(
            own_prizes_remaining=6 if behind else 5,
            opponent_prizes_remaining=5,
        )
        return enumerate_board_derived_retreat_actions(
            state, opponent, base_retreat_cost=2,
            provider_context=context,
            stadium_print_id="swsh2-160",
        )

    energy = EnergyAttachment(
        "rev", "Reversal Energy", ("C",), "sv2-192",
    )
    behind = scenario(active_energy=energy, behind=True)
    tied = scenario(active_energy=energy, behind=False)
    suppressed = scenario(active_energy=energy, behind=True,
                          aura_enabled=False)

    assert behind.preflight is not None
    assert tied.preflight is not None
    assert suppressed.preflight is not None
    assert behind.preflight.effective_retreat_cost == 0
    assert tied.preflight.effective_retreat_cost == 4
    assert suppressed.preflight.effective_retreat_cost == 4
    assert {
        (action.bench_object_id, action.discard_energy_ids)
        for action in behind.actions
    } == {("darkrai", ()), ("pivot", ())}
    assert tied.actions == ()
    assert suppressed.actions == ()
    assert behind.preflight.normalization.state.energy.board.get(
        "active"
    ).energy[0].units == ("C", "C", "C")


def main() -> None:
    source_regressions()
    printed_special_energy_context()
    physical_aura_and_prize_context()
    print("Typed Energy self/team Retreat source and physical continuity: PASS")
    print({"typed_source_prints": 27, "behind_prize_reversal_units": 3,
           "free_retreat_when_behind": True})


if __name__ == "__main__":
    main()
