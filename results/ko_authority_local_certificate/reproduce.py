"""Check local source-aware KO certificates against old full enumeration."""

from math import factorial
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

from ko_authority_invariant_projection import (
    PhysicalCertainty, project_authority_neutral_ko,
)
from ko_authority_local_certificate import certify_authority_neutral_components
from ko_trigger_order_authority import (
    JAPAN_LOST_CITY_QA, LOST_CITY_LOST_OUT, TPCI_FEB_2026,
    OrderingContext, TimingWindow, TriggerKind,
)
from results.ko_authority_neutral_projection.reproduce import setup
from results.ko_exchangeable_factorization_stress.reproduce import (
    build_pending, competing_programs,
)
from source_order_chooser import (
    ConcreteChooserStatus, OrderingPlayers,
)


def main():
    context = OrderingContext(
        timing_window=TimingWindow.DURING_TURN,
        trigger_kind=TriggerKind.POKEMON_KNOCKED_OUT,
        interaction_id=LOST_CITY_LOST_OUT,
    )
    sources = (JAPAN_LOST_CITY_QA, TPCI_FEB_2026)
    players = OrderingPlayers(
        current_player="attacker",
        knocked_out_pokemon_owner="defender",
    )

    for n in range(5):
        initial, pending, programs = setup(n)
        fast = certify_authority_neutral_components(
            pending, programs, context=context,
            source_ids=sources, players=players, promote_id="b"
        )
        full = project_authority_neutral_ko(
            pending, programs, context=context,
            source_ids=sources, players=players, promote_id="b"
        )
        assert fast.authority == full.authority
        assert fast.authority.status == ConcreteChooserStatus.AUTHORITY_CONFLICT
        assert fast.physical.invariant == (
            full.certainty == PhysicalCertainty.INVARIANT
        )
        assert fast.physical.candidate_total_orders == full.candidate_total_orders
        if n == 0:
            assert fast.physical.terminal_state == full.terminal_state
            assert fast.physical.terminal_state is not None
            assert fast.physical.terminal_state.ledger.totals() == initial.totals()
        else:
            assert fast.physical.terminal_state is None
        assert fast.physical.local_route_outcomes_checked <= 2

    # For 20 synthetic effect instances, 10 independent binary conflicts
    # require 20 local outcome checks rather than enumerating 1024 global
    # routes. The source here is just a generic chosen timing policy, not a
    # card-text coexistence claim for these synthetic effect programs.
    _, large_pending = build_pending(10)
    generic_context = OrderingContext(
        timing_window=TimingWindow.DURING_TURN,
        trigger_kind=TriggerKind.POKEMON_KNOCKED_OUT,
    )
    large = certify_authority_neutral_components(
        large_pending, competing_programs(10),
        context=generic_context,
        source_ids=(TPCI_FEB_2026,),
        players=players,
        promote_id="b",
    )
    assert large.authority.status == ConcreteChooserStatus.RESOLVED
    assert large.authority.chooser == "attacker"
    assert not large.physical.invariant
    assert large.physical.component_count == 10
    assert large.physical.local_route_outcomes_checked == 20
    assert large.physical.candidate_total_orders == factorial(20)
    assert large.physical.terminal_state is None

    print(
        "Source-aware component-local KO certificate passed: official "
        "Lost City / Lost Out authority conflict with zero to four Water "
        "attachments; 20-effect synthetic branch sensitivity established "
        "from 20 local outcomes"
    )


if __name__ == "__main__":
    main()
