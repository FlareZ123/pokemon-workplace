"""Validate source-conditioned KO order optimization against authorized execution."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

from ko_redirection_authorized_order import (
    AuthorizedOrderStatus,
    authorize_and_resolve_order,
)
from ko_source_scoped_choice import choose_ko_outcome_by_source
from ko_trigger_order_authority import (
    ADVANCED_RULEBOOK_3_4,
    JAPAN_LOST_CITY_QA,
    JAPAN_LOST_OUT_AEGISLASH_QA,
    LOST_OUT_AEGISLASH,
    TPCI_FEB_2026,
    OrderingContext,
    TimingWindow,
    TriggerKind,
)
from knockout_redirection_ordering import resolved_route_map
from knockout_redirection_routes import destinations_for_redirection
from knockout_redirection_taxonomy import ALL_TO_LOST, SELF_TO_HAND
from knockout_zone_routing import discard_pending_with_zone_routes
from results.knockout_redirection_routes.reproduce import build_pending
from source_order_chooser import ConcreteChooserStatus, OrderingPlayers


STACK = frozenset(("honedge-a", "doublade-a", "aegislash-a"))


def retained_stack_payoff(routes):
    return sum(
        1 for instance_id, zone in routes
        if instance_id in STACK and zone == "hand"
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
    programs = {"durable-blade": returned, "lost-out": lost}
    context = OrderingContext(
        timing_window=TimingWindow.DURING_TURN,
        trigger_kind=TriggerKind.POKEMON_KNOCKED_OUT,
        interaction_id=LOST_OUT_AEGISLASH,
    )
    sources = (JAPAN_LOST_OUT_AEGISLASH_QA, TPCI_FEB_2026)
    players = OrderingPlayers(
        current_player="attacker", knocked_out_pokemon_owner="defender"
    )

    result = choose_ko_outcome_by_source(
        programs, context=context, source_ids=sources, players=players,
        viewpoint_player="defender", opposing_player="attacker",
        payoff=retained_stack_payoff,
    )
    assert result.outcome_count == 2
    assert result.payoff_envelope == (0.0, 3.0)
    by_source = {choice.source_id: choice for choice in result.choices}
    japan, tpci = by_source[sources[0]], by_source[sources[1]]
    assert japan.authority_status == tpci.authority_status == ConcreteChooserStatus.RESOLVED
    assert japan.chooser == "defender"
    assert japan.viewpoint_payoff == 3.0
    assert japan.best_outcome is not None
    assert japan.best_outcome.witness_order == ("durable-blade", "lost-out")
    assert tpci.chooser == "attacker"
    assert tpci.viewpoint_payoff == 0.0
    assert tpci.best_outcome is not None
    assert tpci.best_outcome.witness_order == ("lost-out", "durable-blade")

    # Each source-conditioned optimum is separately admissible under its own
    # sourced authority and conserves all physical cards through disposal.
    for row in (japan, tpci):
        assert row.best_outcome is not None
        assert row.chooser is not None
        checked = authorize_and_resolve_order(
            programs, row.best_outcome.witness_order,
            context=context, source_ids=(row.source_id,),
            players=players, submitted_by=row.chooser,
        )
        assert checked.status == AuthorizedOrderStatus.RESOLVED
        assert checked.resolutions is not None
        state = discard_pending_with_zone_routes(
            pending, promote_id="b",
            destinations=resolved_route_map(checked.resolutions),
        )
        assert state is not None
        assert state.ledger.totals() == initial.totals()
        assert state.ledger.exchangeable.count(
            "aegislash",
            "hand" if row == japan else "lost_zone"
        ) == 1

    # When the current player is also the owner, both source profiles assign
    # the same actor and the value envelope collapses.
    aligned = choose_ko_outcome_by_source(
        programs, context=context, source_ids=sources,
        players=OrderingPlayers(
            current_player="defender", knocked_out_pokemon_owner="defender"
        ),
        viewpoint_player="defender", opposing_player="attacker",
        payoff=retained_stack_payoff,
    )
    assert aligned.payoff_envelope == (3.0, 3.0)
    assert all(row.chooser == "defender" for row in aligned.choices)

    # A different caller utility reverses who prefers which KO endpoint.
    reversed_preferences = choose_ko_outcome_by_source(
        programs, context=context, source_ids=sources, players=players,
        viewpoint_player="defender", opposing_player="attacker",
        payoff=lambda destinations: -retained_stack_payoff(destinations),
    )
    assert reversed_preferences.payoff_envelope == (-3.0, 0.0)
    assert reversed_preferences.choices[0].viewpoint_payoff == 0.0
    assert reversed_preferences.choices[1].viewpoint_payoff == -3.0

    # With externally mandatory Lost Out-first ordering, chooser identity
    # no longer changes the physical endpoint.
    constrained = choose_ko_outcome_by_source(
        programs, context=context, source_ids=sources, players=players,
        viewpoint_player="defender", opposing_player="attacker",
        payoff=retained_stack_payoff,
        precedences=(("lost-out", "durable-blade"),),
    )
    assert constrained.outcome_count == 1
    assert constrained.payoff_envelope == (0.0, 0.0)

    # Ties preserve every optimal endpoint. A single representative chosen
    # lexicographically is insufficient to describe the physical outcome
    # uncertainty, even when the utility value is invariant across sources.
    tied = choose_ko_outcome_by_source(
        programs, context=context, source_ids=sources, players=players,
        viewpoint_player="defender", opposing_player="attacker",
        payoff=lambda destinations: 0,
    )
    assert tied.value_invariant
    assert tied.payoff_envelope == (0.0, 0.0)
    assert not tied.instance_destination_invariant
    assert len(tied.optimal_outcome_union) == 2
    assert all(len(choice.optimal_outcomes) == 2 for choice in tied.choices)
    assert not result.value_invariant
    assert aligned.value_invariant
    assert aligned.instance_destination_invariant
    assert constrained.value_invariant
    assert constrained.instance_destination_invariant

    # Missing or inapplicable source-specific claims remain unresolved.
    mixed = choose_ko_outcome_by_source(
        programs, context=context,
        source_ids=(ADVANCED_RULEBOOK_3_4, JAPAN_LOST_CITY_QA, TPCI_FEB_2026),
        players=players, viewpoint_player="defender",
        opposing_player="attacker", payoff=retained_stack_payoff,
    )
    assert [r.authority_status for r in mixed.choices] == [
        ConcreteChooserStatus.NO_AUTHORITY_CLAIMS,
        ConcreteChooserStatus.NO_AUTHORITY_CLAIMS,
        ConcreteChooserStatus.RESOLVED,
    ]
    assert mixed.payoff_envelope == (0.0, 0.0)

    missing = choose_ko_outcome_by_source(
        programs, context=context,
        source_ids=(JAPAN_LOST_OUT_AEGISLASH_QA,),
        players=OrderingPlayers(current_player="attacker"),
        viewpoint_player="defender", opposing_player="attacker",
        payoff=retained_stack_payoff,
    )
    assert missing.payoff_envelope is None
    assert missing.choices[0].authority_status == ConcreteChooserStatus.MISSING_PLAYER_CONTEXT

    for bad in (
        lambda: choose_ko_outcome_by_source(
            programs, context=context, source_ids=sources, players=players,
            viewpoint_player="defender", opposing_player="attacker",
            payoff=lambda outcome: float("nan"),
        ),
        lambda: choose_ko_outcome_by_source(
            programs, context=context, source_ids=(sources[0], sources[0]),
            players=players, viewpoint_player="defender", opposing_player="attacker",
            payoff=retained_stack_payoff,
        ),
    ):
        try:
            bad()
        except ValueError:
            pass
        else:
            raise AssertionError("invalid choice input accepted")

    print(
        "Source-scoped adversarial KO choice passed: Japanese Aegislash owner "
        "vs TPCi attacking-current-player yield [0,3] retained-stack utility "
        "envelope under the stated zero-sum assumption"
    )


if __name__ == "__main__":
    main()
