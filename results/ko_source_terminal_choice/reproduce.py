"""Validate source choices on conserved states against physical-route oracle."""

from math import factorial
from pathlib import Path
from random import Random
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

from ko_source_scoped_choice import choose_ko_outcome_by_source
from ko_source_terminal_choice import choose_ko_terminal_by_source
from ko_trigger_order_authority import (
    ADVANCED_RULEBOOK_3_4,
    JAPAN_LOST_OUT_AEGISLASH_QA, LOST_OUT_AEGISLASH, TPCI_FEB_2026,
    OrderingContext, TimingWindow, TriggerKind,
)
from knockout_redirection_routes import destinations_for_redirection
from knockout_redirection_taxonomy import ALL_TO_LOST, SELF_TO_HAND
from knockout_zone_routing import discard_pending_with_zone_routes
from results.knockout_redirection_routes.reproduce import build_pending
from results.ko_exchangeable_factorization_stress.reproduce import (
    build_pending as large_pending, competing_programs,
)
from source_order_chooser import (
    ConcreteChooserStatus, OrderingPlayers,
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
    players = OrderingPlayers(
        current_player="attacker", knocked_out_pokemon_owner="defender"
    )
    sources = (JAPAN_LOST_OUT_AEGISLASH_QA, TPCI_FEB_2026)

    def stack_in_hand(state):
        return sum(
            state.ledger.exchangeable.count(name, "hand")
            for name in ("aegislash", "doublade", "honedge")
        )

    known = choose_ko_outcome_by_source(
        programs, context=context, source_ids=sources, players=players,
        viewpoint_player="defender", opposing_player="attacker",
        payoff=lambda routes: sum(
            zone == "hand"
            for instance, zone in routes
            if instance in {"aegislash-a", "doublade-a", "honedge-a"}
        ),
    )
    new = choose_ko_terminal_by_source(
        pending, programs, context=context, source_ids=sources,
        players=players, viewpoint_player="defender",
        opposing_player="attacker", payoff=stack_in_hand, promote_id="b"
    )
    assert new.payoff_envelope == known.payoff_envelope == (0, 3)
    assert not new.value_invariant
    assert not new.terminal_state_invariant
    assert [row.chooser for row in new.source_choices] == [
        "defender", "attacker"
    ]
    for old_row, new_row in zip(known.choices, new.source_choices):
        assert old_row.viewpoint_payoff == new_row.payoff
        assert old_row.authority_status == new_row.authority_status
        assert new_row.selected is not None
        assert old_row.best_outcome is not None
        state = discard_pending_with_zone_routes(
            pending, promote_id="b",
            destinations=dict(old_row.best_outcome.destinations),
        )
        assert state == new_row.selected.state
        assert new_row.selected.state.ledger.totals() == initial.totals()

    # Equal utility intentionally leaves every terminal state possible.
    tied = choose_ko_terminal_by_source(
        pending, programs, context=context, source_ids=sources,
        players=players, viewpoint_player="defender",
        opposing_player="attacker", payoff=lambda state: 0,
        promote_id="b",
    )
    assert tied.payoff_envelope == (0, 0)
    assert tied.value_invariant
    assert not tied.terminal_state_invariant
    assert all(len(row.optimal) == 2 for row in tied.source_choices)

    unknown = choose_ko_terminal_by_source(
        pending, programs, context=context,
        source_ids=(ADVANCED_RULEBOOK_3_4,), players=players,
        viewpoint_player="defender", opposing_player="attacker",
        payoff=stack_in_hand, promote_id="b",
    )
    assert unknown.payoff_envelope is None
    assert unknown.source_choices[0].authority_status == ConcreteChooserStatus.NO_AUTHORITY_CLAIMS

    generic_context = OrderingContext(
        timing_window=TimingWindow.DURING_TURN,
        trigger_kind=TriggerKind.POKEMON_KNOCKED_OUT,
    )
    small_players = players
    rng = Random(260810)
    ids = tuple(
        c.card_id
        for p in pending.state.board.pokemon
        if p.pokemon_id == "a"
        for c in p.stack + p.attachments
    )
    random_cases = 0
    for n in range(1, 7):
        for _ in range(20):
            effects = {
                f"e{i}": {
                    instance: rng.choice(("hand", "discard", "lost_zone"))
                    for instance in ids if rng.random() < 0.5
                }
                for i in range(n)
            }
            old = choose_ko_outcome_by_source(
                effects, context=generic_context,
                source_ids=(TPCI_FEB_2026,), players=small_players,
                viewpoint_player="defender", opposing_player="attacker",
                payoff=lambda destinations: sum(
                    instance.startswith("water-") and zone == "hand"
                    for instance, zone in destinations
                ),
            )
            new = choose_ko_terminal_by_source(
                pending, effects, context=generic_context,
                source_ids=(TPCI_FEB_2026,), players=small_players,
                viewpoint_player="defender", opposing_player="attacker",
                payoff=lambda state: state.ledger.exchangeable.count(
                    "basic-water", "hand"
                ),
                promote_id="b",
            )
            assert old.payoff_envelope == new.payoff_envelope
            old_states = {
                discard_pending_with_zone_routes(
                    pending, promote_id="b",
                    destinations=dict(outcome.destinations),
                )
                for outcome in old.choices[0].optimal_outcomes
            }
            new_states = {
                row.state for row in new.source_choices[0].optimal
            }
            assert old_states == new_states
            random_cases += 1
    assert random_cases == 120

    # 40 independent Water pairs create 2^40 physical routes but just 41
    # strategically distinguishable counts for this complete-state payoff.
    n = 40
    large_initial, pending_big = large_pending(n)
    effects = competing_programs(n)
    sources = (TPCI_FEB_2026,)
    for current, selected_count in (
        ("defender", 40), ("attacker", 0)
    ):
        result = choose_ko_terminal_by_source(
            pending_big, effects, context=generic_context,
            source_ids=sources,
            players=OrderingPlayers(current_player=current),
            viewpoint_player="defender", opposing_player="attacker",
            payoff=lambda state: state.ledger.exchangeable.count(
                "basic-water", "hand"
            ),
            promote_id="b",
        )
        assert result.convolution.component_count == n
        assert result.convolution.local_route_outcomes_checked == 2 * n
        assert result.convolution.full_disposals == n + 1
        assert result.convolution.candidate_total_orders == factorial(2 * n)
        choice = result.source_choices[0]
        assert choice.chooser == current
        assert choice.payoff == selected_count
        assert choice.selected is not None
        assert choice.selected.state.ledger.totals() == large_initial.totals()
        assert choice.selected.state.ledger.exchangeable.count(
            "basic-water", "hand"
        ) == selected_count
        assert len(choice.optimal) == 1

    print(
        "Source-conditioned terminal KO choices passed: 120 randomized "
        "checks against physical-instance source solver; 80-effect "
        "synthetic game chooses 0 or 40 Water cards from 41 conserved states"
    )


if __name__ == "__main__":
    main()
