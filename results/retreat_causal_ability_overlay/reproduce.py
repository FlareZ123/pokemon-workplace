"""Causal Ability suppression changes Retreat legality and payment cost."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from ability_lock_causal_state import initialize_snapshot_lock_state
from board_derived_retreat import attempt_board_derived_retreat
from board_object_kernel import EnergyAttachment, ToolAttachment, make_board, make_pokemon
from energy_board_conservation import EnergyBoardState
from multicopy_zone_state import ZoneCountState
from retreat_energy_transaction import RetreatEnergyTransactionState
from turn_action_budget import TurnActionBudget
from unified_state_kernel import make_state


def actor(active, *bench):
    cards = [energy for pokemon in (active, *bench) for energy in pokemon.energy]
    classes = tuple(sorted(
        (card.instance_id, "class-" + card.instance_id)
        for card in cards
    ))
    return RetreatEnergyTransactionState(
        unified=make_state({}, turn_budget=TurnActionBudget()),
        energy=EnergyBoardState(
            zones=ZoneCountState.from_mapping({
                (card_class, "attached"): 1
                for _, card_class in classes
            }),
            board=make_board(active, bench),
            instance_classes=classes,
        ),
    )


def attempt(ours, opponent, *, base=2, selected=(), lock=None):
    return attempt_board_derived_retreat(
        ours, "pivot",
        base_retreat_cost=base,
        discard_energy_ids=selected,
        opponent_board=opponent,
        ability_lock_state=lock,
    )


def main() -> None:
    pivot = make_pokemon("pivot", "Pivot")
    float_stone = ToolAttachment("float", "Float Stone", print_id="xy8-137")
    active = make_pokemon(
        "active", "Our Active", tags=("Stage1",), tool=float_stone,
    )
    snorlax = make_pokemon(
        "snorlax", "Snorlax", print_id="pgo-55", tags=("Basic",),
    )
    opponent = make_board(snorlax)

    # An unsuppressed Snorlax forbids normal Retreat despite Float Stone.
    alone = actor(active, pivot)
    raw = attempt(alone, opponent)
    assert raw.effective_retreat_cost == 0
    assert raw.retreat_denial_source_ids == ("snorlax",)
    assert raw.transaction is None

    # Our Benched Alolan Muk suppresses the opponent's Basic Snorlax,
    # removing the Retreat prohibition. The source itself remains in play.
    muk = make_pokemon(
        "muk", "Alolan Muk", print_id="sm1-58", tags=("Stage1",),
    )
    with_muk = actor(active, pivot, muk)
    causal = initialize_snapshot_lock_state(with_muk.energy.board, opponent)
    assert causal.resolved
    assert causal.resolution.opponent_suppressed_object_ids is not None
    assert "snorlax" in causal.resolution.opponent_suppressed_object_ids
    unlocked = attempt(with_muk, opponent, lock=causal)
    assert unlocked.suppressed_opponent_ability_ids == ("snorlax",)
    assert unlocked.retreat_denial_source_ids == ()
    assert unlocked.transaction is not None and unlocked.transaction.committed

    # When Muk leaves the Bench, the source returns without changing cost.
    restored = initialize_snapshot_lock_state(alone.energy.board, opponent)
    reblocked = attempt(alone, opponent, lock=restored)
    assert reblocked.retreat_denial_source_ids == ("snorlax",)
    assert reblocked.transaction is None

    # Garbotoxin can suppress an opposing Cradily whose Special Condition
    # prohibition otherwise prevents Float Stone's zero-cost Retreat.
    poisoned_active = make_pokemon(
        "active", "Our Active", tags=("Stage1",),
        special_conditions=("Poisoned",), tool=float_stone,
    )
    garbodor = make_pokemon(
        "garb", "Garbodor", print_id="xy9-57", tags=("Stage1",),
        tool=ToolAttachment("garbtool", "Float Stone"),
    )
    our_garb = actor(poisoned_active, pivot, garbodor)
    cradily = make_board(make_pokemon(
        "cradily", "Cradily", print_id="sm12-11", tags=("Stage2",),
    ))
    assert attempt(our_garb, cradily).retreat_denial_source_ids == ("cradily",)
    garb_lock = initialize_snapshot_lock_state(our_garb.energy.board, cradily)
    assert garb_lock.resolved
    cleared = attempt(our_garb, cradily, lock=garb_lock)
    assert cleared.retreat_denial_source_ids == ()
    assert cleared.transaction is not None and cleared.transaction.committed

    # Opposing Neutralizing Gas suppresses a friendly Benched Sneasler,
    # restoring a two-unit payment requirement from a free Retreat.
    dce = EnergyAttachment(
        "dce", "Double Colorless Energy", ("C", "C"), print_id="base1-96",
    )
    funded = make_pokemon(
        "active", "Our Active", tags=("Stage1",), energy=(dce,),
    )
    sneasler = make_pokemon(
        "sneasler", "Hisuian Sneasler", print_id="swsh10-93",
        tags=("Stage1",),
    )
    our_sneasler = actor(funded, pivot, sneasler)
    weezing = make_board(make_pokemon(
        "weezing", "Galarian Weezing", print_id="swsh2-113",
        tags=("Stage1", "Darkness"),
    ))
    baseline = attempt(our_sneasler, weezing, base=2)
    assert baseline.effective_retreat_cost == 0
    assert baseline.transaction is not None and baseline.transaction.committed
    gas = initialize_snapshot_lock_state(our_sneasler.energy.board, weezing)
    assert gas.resolved
    gas_cost = attempt(
        our_sneasler, weezing, base=2, selected=("dce",), lock=gas,
    )
    assert gas_cost.suppressed_own_ability_ids == ("sneasler",)
    assert gas_cost.effective_retreat_cost == 2
    assert gas_cost.transaction is not None and gas_cost.transaction.committed
    assert gas_cost.transaction.state.energy.zones.count(
        "class-dce", "discard"
    ) == 1

    # Reciprocal Active Wobbuffet and Weezing Ability locks have a cycle.
    # A snapshot without causal precedence cannot authorize the Retreat.
    wob = make_pokemon(
        "active", "Wobbuffet", print_id="xy4-36",
        tags=("Basic", "Psychic"), tool=float_stone,
    )
    w_state = actor(wob, pivot)
    cycle = initialize_snapshot_lock_state(w_state.energy.board, weezing)
    assert not cycle.resolved
    pending = attempt(w_state, weezing, lock=cycle)
    assert pending.unresolved_ability_lock
    assert pending.transaction is None
    assert pending.effective_retreat_cost == 0

    print("Retreat causal Ability overlay: PASS")
    print("source suppression unlocks; suppressing support raises payment cost")
    print("unresolved reciprocal source cycle blocks commit")


if __name__ == "__main__":
    main()
