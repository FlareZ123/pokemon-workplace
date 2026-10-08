"""Independent physical-state checks for KO source-choice invariance certificates."""

from pathlib import Path
from random import Random
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

from ko_choice_invariance import assess_ko_choice_invariance
from ko_order_terminal_projection import project_terminal_outcomes
from ko_source_scoped_choice import choose_ko_outcome_by_source
from ko_trigger_order_authority import (
    ADVANCED_RULEBOOK_3_4,
    JAPAN_LOST_OUT_AEGISLASH_QA,
    LOST_OUT_AEGISLASH,
    TPCI_FEB_2026,
    OrderingContext, TimingWindow, TriggerKind
)
from knockout_redirection_routes import destinations_for_redirection
from knockout_redirection_taxonomy import ALL_TO_LOST, SELF_TO_HAND
from results.knockout_redirection_routes.reproduce import build_pending
from source_order_chooser import OrderingPlayers


def score_stack_hand(destinations):
    return sum(
        instance_id in {"honedge-a", "doublade-a", "aegislash-a"}
        and zone == "hand"
        for instance_id, zone in destinations
    )


def main():
    initial, pending = build_pending()
    returned = destinations_for_redirection(
        pending, pokemon_id="a", routing_signature=SELF_TO_HAND
    )
    lost = destinations_for_redirection(
        pending, pokemon_id="a", routing_signature=ALL_TO_LOST
    )
    assert returned is not None and lost is not None
    source_programs = {"durable-blade": returned, "lost-out": lost}
    context = OrderingContext(
        timing_window=TimingWindow.DURING_TURN,
        trigger_kind=TriggerKind.POKEMON_KNOCKED_OUT,
        interaction_id=LOST_OUT_AEGISLASH,
    )
    source_ids = (JAPAN_LOST_OUT_AEGISLASH_QA, TPCI_FEB_2026)
    players = OrderingPlayers(
        current_player="attacker", knocked_out_pokemon_owner="defender"
    )

    def choose(programs, *, profile_sources=source_ids, value=score_stack_hand,
               event_context=context, actor_roles=players):
        return choose_ko_outcome_by_source(
            programs, context=event_context, source_ids=profile_sources,
            players=actor_roles, viewpoint_player="defender",
            opposing_player="attacker", payoff=value,
        )

    disputed = assess_ko_choice_invariance(
        pending, choose(source_programs)
    )
    assert disputed.unresolved_source_ids == ()
    assert disputed.utility_value_invariant is False
    assert disputed.physical_instance_route_invariant is False
    assert disputed.conserved_terminal_state_invariant is False
    assert len(disputed.terminal_signatures) == 2

    tied = assess_ko_choice_invariance(
        pending, choose(source_programs, value=lambda destinations: 0)
    )
    assert tied.utility_value_invariant is True
    assert tied.physical_instance_route_invariant is False
    assert tied.conserved_terminal_state_invariant is False

    aligned = assess_ko_choice_invariance(
        pending, choose(
            source_programs,
            actor_roles=OrderingPlayers(
                current_player="defender",
                knocked_out_pokemon_owner="defender",
            ),
        ),
    )
    assert aligned.utility_value_invariant is True
    assert aligned.physical_instance_route_invariant is True
    assert aligned.conserved_terminal_state_invariant is True

    # Instance-route disagreement survives utility ties but disappears after
    # dematerializing equivalent Basic Water Energy copies.
    water_programs = {
        "first": {"water-1": "hand", "water-2": "discard"},
        "second": {"water-1": "discard", "water-2": "hand"},
    }
    generic = OrderingContext(
        timing_window=TimingWindow.DURING_TURN,
        trigger_kind=TriggerKind.POKEMON_KNOCKED_OUT,
        interaction_id="synthetic_water_routing",
    )
    water_choices = choose(
        water_programs, profile_sources=(TPCI_FEB_2026,),
        value=lambda destinations: 0, event_context=generic,
    )
    water_cert = assess_ko_choice_invariance(pending, water_choices)
    assert water_cert.unresolved_source_ids == ()
    assert water_cert.utility_value_invariant is True
    assert water_cert.physical_instance_route_invariant is False
    assert water_cert.conserved_terminal_state_invariant is True
    assert len(water_cert.terminal_signatures) == 1
    full = project_terminal_outcomes(pending, water_programs, promote_id="b")
    assert len(full) == 1 and full[0].state.ledger.totals() == initial.totals()

    # A source with no applicable authority claim cannot certify a decision.
    none = assess_ko_choice_invariance(
        pending, choose(
            source_programs, profile_sources=(ADVANCED_RULEBOOK_3_4,)
        ),
    )
    assert none.unresolved_source_ids == (ADVANCED_RULEBOOK_3_4,)
    assert none.utility_value_invariant is None
    assert none.physical_instance_route_invariant is None
    assert none.conserved_terminal_state_invariant is None

    # Regression over random precompiled destination programs. Give the
    # sole TPCi chooser utility 0 everywhere so every endpoint remains
    # optimal; prove the cheap histogram equivalence against actual physical
    # terminal-state grouping.
    board = pending.state.board
    assert board is not None
    knocked_out = next(row for row in board.pokemon if row.pokemon_id == "a")
    ids = tuple(
        [card.card_id for card in knocked_out.stack]
        + [card.card_id for card in knocked_out.attachments]
    )
    rng = Random(208601)
    for n in range(1, 6):
        for _ in range(22):
            programs = {
                f"effect-{i}": {
                    instance: rng.choice(("hand", "discard", "lost_zone"))
                    for instance in ids
                    if rng.random() < 0.57
                }
                for i in range(n)
            }
            choice = choose(
                programs, profile_sources=(TPCI_FEB_2026,),
                value=lambda destinations: 0, event_context=generic,
            )
            report = assess_ko_choice_invariance(pending, choice)
            full = project_terminal_outcomes(
                pending, programs, promote_id="b"
            )
            assert report.utility_value_invariant is True
            assert report.conserved_terminal_state_invariant == (len(full) == 1)
            assert len(report.terminal_signatures) == len(full)
    print(
        "KO choice invariance passed: authority-conditioned Aegislash, "
        "exchangeable two-Water collapse, 110 randomized full-kernel cases"
    )


if __name__ == "__main__":
    main()
