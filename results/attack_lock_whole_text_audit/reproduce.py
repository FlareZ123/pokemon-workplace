"""Single-file regression for source-verified attack-lock whole-text coverage."""
from __future__ import annotations

from collections import Counter
from dataclasses import replace
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from attack_lock_whole_text_audit import (
    audit_text, build_attack_lock_audit, build_lock_aware_coverage,
)
from attack_text_coverage_inventory import materialize_damage_only_verified
from board_position_state import BoardPokemon, PokemonCard, make_state
from simple_attack_board_semantics import compile_legal_index

RESOURCES = ROOT / "resources"


def main() -> None:
    audited = build_attack_lock_audit(RESOURCES)
    print("Source-bound lock-attack printings:", len(audited))
    assert len(audited) == 77
    assert len({a.attack_id for a in audited}) == 77
    assert sum(a.lock_only for a in audited) == 53
    assert not any(a.opaque_clauses for a in audited)
    distinct_texts = len({a.profile.restriction.text for a in audited})
    assert distinct_texts == 33

    expected = {
        (): 53,
        ("stadium_discard",): 1,
        ("self_shuffle",): 1,
        ("conditional_knockout", "gx_budget"): 2,
        ("attack_history_gate",): 1,
        ("gx_budget",): 3,
        ("first_turn_gate",): 3,
        ("coin_flip",): 4,
        ("conditional_draw", "gx_budget"): 4,
        ("special_condition",): 1,
        ("player_choice",): 1,
        ("self_energy_discard",): 3,
    }
    actual = Counter(a.other_handlers for a in audited)
    assert actual == Counter(expected), actual
    print("Distinct texts:", distinct_texts)
    print("Source printings requiring other handlers:", 77 - 53)
    for handlers, count in sorted(actual.items()):
        print(f"  {count:2} : {', '.join(handlers) or 'no other handlers'}")

    by_card = {}
    for audit in audited:
        by_card.setdefault(audit.profile.restriction.card_id, []).append(audit)
    examples = {
        "me2pt5-16": (),
        "me1-31": ("stadium_discard",),
        "sm11-91": ("self_shuffle",),
        "sm11-125": ("conditional_knockout", "gx_budget"),
        "sm9-53": ("conditional_draw", "gx_budget"),
        "sm12-52": ("attack_history_gate",),
        "sm4-34": ("gx_budget",),
        "sm7-116": ("first_turn_gate",),
        "sm9-26": ("coin_flip",),
        "sv3pt5-49": ("special_condition",),
        "sv4-112": ("player_choice",),
        "sv7-51": ("self_energy_discard",),
        "swsh11-3": ("coin_flip",),
    }
    for card_id, expected_handlers in examples.items():
        matches = by_card[card_id]
        assert len(matches) == 1
        assert matches[0].other_handlers == expected_handlers
        print(card_id, matches[0].attack_name, expected_handlers)

    # New clause = opaque, not certified as a complete attack.
    sample = by_card["me2pt5-16"][0]
    changed = sample.profile.restriction.text + " Draw a card."
    revised = replace(sample.profile, restriction=replace(
        sample.profile.restriction, text=changed,
    ))
    other, opaque = audit_text(changed, revised)
    assert not other
    assert opaque == ("Draw a card.",)

    # Gate-specific source semantics cannot quietly lose their outcome.
    gate = by_card["sm9-26"][0]
    invalid_text = gate.profile.restriction.text.replace("Flip a coin. ", "")
    invalid = replace(gate.profile, restriction=replace(
        gate.profile.restriction, text=invalid_text,
    ))
    try:
        audit_text(invalid_text, invalid)
    except ValueError as exc:
        assert "gate missing" in str(exc)
    else:
        raise AssertionError("coin gate silently accepted without coin instruction")

    coverage = build_lock_aware_coverage(RESOURCES)
    assert coverage["total"] == 19992
    assert coverage["base_uncompiled"] == 8182
    assert coverage["remaining_uncompiled"] == 8105
    assert coverage["counts"]["source_scoped_lock_only"] == 53
    assert coverage["counts"]["source_scoped_lock_with_other_handlers"] == 24
    assert sum(coverage["counts"].values()) == 19992
    assert not coverage["opaque"]
    print("Opaque fixed/blank source texts:", 8182, "->", 8105)

    # The legacy damage-only entry point MUST still refuse recognized locks.
    index = compile_legal_index(RESOURCES)
    board = make_state((
        BoardPokemon("active", (PokemonCard("a", "A"),), retreat_cost=1),
        BoardPokemon("bench", (PokemonCard("b", "B"),), retreat_cost=1),
    ), active_id="active")
    for item in audited:
        source = next(
            r for r in index[item.profile.restriction.card_id]
            if r.attack_id == item.attack_id
        )
        try:
            materialize_damage_only_verified(source, board)
        except ValueError as exc:
            assert "additional semantic handlers" in str(exc)
        else:
            raise AssertionError(f"unsafe damage-only execution: {source.attack_id}")

    print("PASS: 77 source/print bindings, 33 full texts, 77 damage-only refusals")


if __name__ == "__main__":
    main()
