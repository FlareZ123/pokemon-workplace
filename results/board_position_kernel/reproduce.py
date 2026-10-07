from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from board_position_kernel import begin_next_turn, normal_evolve, normal_retreat, switch_active
from board_position_state import Attachment, AttachmentKind, BoardPokemon, PokemonCard, make_state
from lock_state_kernel import PokemonState


def basic(name: str, index: int) -> BoardPokemon:
    return BoardPokemon(f"p{index}", (PokemonCard(f"card-{index}", name),), 0)


def main() -> None:
    tool = Attachment("tool", "Air Balloon", AttachmentKind.TOOL)
    e1 = Attachment("e1", "Grass A", AttachmentKind.ENERGY, 1)
    e2 = Attachment("e2", "Grass B", AttachmentKind.ENERGY, 1)
    bench = tuple(basic(f"Bench {i}", i) for i in range(1, 6))

    locked_active = BoardPokemon(
        "active", (PokemonCard("bulba-a", "Bulbasaur"),), 2, damage_counters=3,
        attachments=(e1, e2, tool),
        combat=PokemonState(tool_attached=True, temporary_attack_lock=True, temporary_retreat_lock=True),
        special_conditions=frozenset({"Paralyzed"}),
    )
    locked = make_state((locked_active, *bench), active_id="active")
    assert normal_retreat(locked, "p1", discard_energy_ids=("e1", "e2")) is None
    switched = switch_active(locked, "p1")
    assert switched is not None and not switched.state.retreat_used
    moved = switched.state.get("active")
    assert len(switched.state.bench_ids) == 5 and moved.damage_counters == 3
    assert {a.card_id for a in moved.attachments} == {"e1", "e2", "tool"}
    assert moved.combat.tool_attached and not moved.combat.temporary_attack_lock
    assert not moved.combat.temporary_retreat_lock and not moved.special_conditions

    active = BoardPokemon(
        "active", (PokemonCard("bulba-b", "Bulbasaur"),), 2, damage_counters=3,
        attachments=(e1, e2, tool), combat=PokemonState(tool_attached=True, temporary_attack_lock=True),
        special_conditions=frozenset({"Poisoned"}),
    )
    state = make_state((active, *bench), active_id="active")
    retreated = normal_retreat(state, "p1", discard_energy_ids=("e1", "e2"))
    assert retreated is not None and retreated.state.retreat_used
    moved = retreated.state.get("active")
    assert retreated.discarded_card_ids == ("e1", "e2")
    assert moved.damage_counters == 3 and [a.card_id for a in moved.attachments] == ["tool"]
    assert moved.combat.tool_attached and not moved.special_conditions
    assert normal_retreat(retreated.state, "p2") is None
    assert switch_active(retreated.state, "p2") is not None

    dce = Attachment("dce", "Double Colorless Energy", AttachmentKind.ENERGY, 2)
    extra = Attachment("extra", "Basic Lightning Energy", AttachmentKind.ENERGY, 1)
    multi = make_state((
        BoardPokemon("multi", (PokemonCard("m", "Test Basic"),), 2, attachments=(dce, extra)),
        basic("Pivot", 20),
    ), active_id="multi")
    assert normal_retreat(multi, "p20", discard_energy_ids=("dce",)) is not None
    assert normal_retreat(multi, "p20", discard_energy_ids=("dce", "extra")) is not None

    evo_tool = Attachment("evo-tool", "Air Balloon", AttachmentKind.TOOL)
    evo_energy = Attachment("evo-energy", "Grass", AttachmentKind.ENERGY, 1)
    bulba = BoardPokemon(
        "evo", (PokemonCard("me1-1-copy", "Bulbasaur"),), 2, damage_counters=4,
        attachments=(evo_energy, evo_tool),
        combat=PokemonState(tool_attached=True, temporary_attack_lock=True, temporary_retreat_lock=True),
        special_conditions=frozenset({"Poisoned"}),
    )
    evo = make_state((bulba, basic("Pivot", 30)), active_id="evo")
    ivysaur = PokemonCard("me1-2-copy", "Ivysaur", "Bulbasaur")
    venusaur = PokemonCard("me1-3-copy", "Mega Venusaur ex", "Ivysaur")
    first = normal_evolve(evo, "evo", ivysaur, new_retreat_cost=3)
    assert first is not None
    p = first.state.get("evo")
    assert [c.name for c in p.stack] == ["Bulbasaur", "Ivysaur"] and p.damage_counters == 4
    assert p.combat.tool_attached and not p.combat.temporary_attack_lock and not p.special_conditions
    assert normal_evolve(first.state, "evo", venusaur, new_retreat_cost=4) is None
    second = normal_evolve(begin_next_turn(first.state), "evo", venusaur, new_retreat_cost=4)
    assert second is not None and second.state.get("evo").name == "Mega Venusaur ex"
    first_turn = make_state((bulba, basic("Pivot", 31)), active_id="evo", evolution_allowed=False)
    assert normal_evolve(first_turn, "evo", ivysaur, new_retreat_cost=3) is None

    print(json.dumps({
        "full_bench_switch_under_retreat_lock": True,
        "switch_consumes_retreat_action": False,
        "full_bench_normal_retreat": True,
        "dce_alone_pays_two_retreat_units": True,
        "dce_plus_lightning_can_pay_two_retreat_units": True,
        "same_turn_double_evolution_allowed": False,
        "next_turn_stage_two_name": second.state.get("evo").name,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
