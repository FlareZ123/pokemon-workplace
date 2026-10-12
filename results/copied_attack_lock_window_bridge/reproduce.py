"""Single runnable test: a copied attack body creates the correct hand lock."""
from __future__ import annotations

from dataclasses import replace
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from attack_copy_kernel import (
    AttackDef, CopySelector, PokemonRef, State, choose_exact, resolve_attack,
)
from attack_lock_whole_text_audit import build_attack_lock_audit
from attack_restriction_turn_windows import (
    begin_turn, end_turn, restriction_affects_player,
)
from copied_attack_lock_window_bridge import create_copied_attack_lock_window
from simple_attack_board_semantics import compile_legal_index
from source_scoped_action_restrictions import (
    CardActionAttempt, restriction_blocks_attempt,
)
from turn_sequence_kernel import TurnSequenceState, advance_turn, close_turn_with_attack


def copy_source(audit, index, *, fail_gate: bool = False):
    row = next(
        row for row in index[audit.profile.restriction.card_id]
        if row.attack_id == audit.attack_id
    )
    leaf = row.to_leaf_attack_def()
    outer = AttackDef(
        "persian:haughty-order", "Haughty Order",
        copy_selector=CopySelector("opponent_revealed"),
        pre_event="reveal_top_10", post_event="shuffle_revealed",
    )
    resolution = resolve_attack(
        actor_player="P1", actor_card_id="p1-persian",
        declared_attack_id=outer.attack_id,
        attacks={outer.attack_id: outer, leaf.attack_id: leaf},
        state=State(pokemon=(PokemonRef(
            "revealed-source", row.card_name, "P2", "revealed",
            attacks=(leaf.attack_id,),
        ),)),
        choose=choose_exact((leaf.attack_id,)),
        copied_body_gate=(lambda _body, _state: False) if fail_gate else None,
    )
    return resolution


def get_audit(audits, card_id):
    matches = [
        a for a in audits if a.profile.restriction.card_id == card_id
    ]
    assert len(matches) == 1, (card_id, len(matches))
    return matches[0]


def must_reject(action, label):
    try:
        action()
    except ValueError as exc:
        print("REJECT", label, str(exc))
    else:
        raise AssertionError(f"accepted invalid copied lock: {label}")


def main():
    audited = build_attack_lock_audit(ROOT / "resources")
    index = compile_legal_index(ROOT / "resources")
    eligible = [
        a for a in audited
        if not a.opaque_clauses
        and set(a.other_handlers) <= {"coin_flip", "player_choice"}
    ]
    assert len(eligible) == 58
    print("Fully gate-supported copied lock printings:", len(eligible))

    budew = get_audit(audited, "me2pt5-16")
    budew_copy = copy_source(budew, index)
    applied = create_copied_attack_lock_window(
        budew_copy, budew, source_player="P1", other_player="P2",
    )
    assert applied.body_event == f"body:{budew.attack_id}"
    assert applied.window is not None
    assert not restriction_affects_player(applied.window, "P2")
    assert restriction_blocks_attempt(
        applied.restriction, CardActionAttempt("item", "hand")
    )
    assert not restriction_blocks_attempt(
        applied.restriction, CardActionAttempt("item", "prize_pending")
    )
    assert not restriction_blocks_attempt(
        applied.restriction, CardActionAttempt("supporter", "hand")
    )
    opponent = begin_turn(applied.window, "P2")
    assert restriction_affects_player(opponent, "P2")
    finished = end_turn(opponent, "P2")
    assert not restriction_affects_player(finished, "P2")
    print("COPY Budew: Item lock persists only through opponent next turn")

    psyduck = get_audit(audited, "sm9-26")
    copy = copy_source(psyduck, index)
    tails = create_copied_attack_lock_window(
        copy, psyduck, source_player="P1", other_player="P2",
        coin_heads=False,
    )
    assert tails.restriction is None and tails.window is None
    heads = create_copied_attack_lock_window(
        copy, psyduck, source_player="P1", other_player="P2",
        coin_heads=True,
    )
    assert heads.window is not None
    assert restriction_blocks_attempt(
        heads.restriction, CardActionAttempt("supporter", "hand")
    )
    must_reject(
        lambda: create_copied_attack_lock_window(
            copy, psyduck, source_player="P1", other_player="P2",
        ), "missing coin",
    )
    print("COPY Psyduck: coin result determines whether lock exists")

    crobat = get_audit(audited, "sv4-112")
    copy = copy_source(crobat, index)
    selected = create_copied_attack_lock_window(
        copy, crobat, source_player="P1", other_player="P2",
        selected_dimensions=frozenset({"item"}),
    )
    assert restriction_blocks_attempt(
        selected.restriction, CardActionAttempt("item", "hand")
    )
    assert not restriction_blocks_attempt(
        selected.restriction, CardActionAttempt("supporter", "hand")
    )
    must_reject(
        lambda: create_copied_attack_lock_window(
            copy, crobat, source_player="P1", other_player="P2",
            selected_dimensions=frozenset({"item", "supporter"}),
        ), "invalid simultaneous Item/Supporter branch",
    )
    print("COPY Crobat: Item or Supporter choice remains exclusive")

    vileplume = get_audit(audited, "swsh11-3")
    copy = copy_source(vileplume, index)
    heads = create_copied_attack_lock_window(
        copy, vileplume, source_player="P1", other_player="P2",
        coin_heads=True,
    )
    tails = create_copied_attack_lock_window(
        copy, vileplume, source_player="P1", other_player="P2",
        coin_heads=False,
    )
    assert restriction_blocks_attempt(
        heads.restriction, CardActionAttempt("supporter", "hand")
    )
    assert not restriction_blocks_attempt(
        heads.restriction, CardActionAttempt("item", "hand")
    )
    assert restriction_blocks_attempt(
        tails.restriction, CardActionAttempt("item", "hand")
    )
    assert not restriction_blocks_attempt(
        tails.restriction, CardActionAttempt("supporter", "hand")
    )
    print("COPY Vileplume: heads/tails select distinct lock dimensions")

    vanilla = get_audit(audited, "xy8-45")
    copy = copy_source(vanilla, index)
    applied = create_copied_attack_lock_window(
        copy, vanilla, source_player="P1", other_player="P2",
    )
    assert restriction_affects_player(applied.window, "P1")
    assert restriction_affects_player(applied.window, "P2")
    p2_turn = begin_turn(applied.window, "P2")
    p2_turn = end_turn(p2_turn, "P2")
    assert restriction_affects_player(p2_turn, "P2")
    p1_turn = begin_turn(p2_turn, "P1")
    p1_turn = end_turn(p1_turn, "P1")
    assert not restriction_affects_player(p1_turn, "P2")

    # An extra attacker turn must not prematurely trigger opponent-next-turn locks.
    extra_start = TurnSequenceState(current_player="P1", other_player="P2")
    extra_closed = close_turn_with_attack(extra_start, take_another_turn=True)
    assert extra_closed is not None
    extra_turn = advance_turn(extra_closed)
    assert extra_turn is not None and extra_turn.same_player_continues
    waiting = begin_turn(create_copied_attack_lock_window(
        budew_copy, budew, source_player="P1", other_player="P2",
    ).window, "P1")
    assert not restriction_affects_player(waiting, "P2")
    print("COPY Vanilluxe: long window; extra turn preserves pending short window")

    for card_id in ("sm11-91", "sm11-125", "sm9-53", "sv7-51", "sv3pt5-49", "me1-31"):
        compound = get_audit(audited, card_id)
        must_reject(
            lambda compound=compound: create_copied_attack_lock_window(
                budew_copy, compound, source_player="P1", other_player="P2",
            ), f"unexecuted secondary effects: {card_id}",
        )

    must_reject(
        lambda: create_copied_attack_lock_window(
            copy_source(budew, index, fail_gate=True), budew,
            source_player="P1", other_player="P2",
        ), "copied body skipped",
    )
    must_reject(
        lambda: create_copied_attack_lock_window(
            budew_copy, replace(budew, opaque_clauses=("Draw a card.",)),
            source_player="P1", other_player="P2",
        ), "opaque effect remains",
    )
    print("PASS: copied lock provenance, outcomes, lifetimes and fail-closed effects")


if __name__ == "__main__":
    main()
