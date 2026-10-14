"""Test Lost Block versus Billowing Smoke decisions with latent Prize identities."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

from identity_materialization import assert_conserved
from physical_pending_prize_batch_bridge import stage_physical_pending_batch
from pending_prize_override_observer_bridge import (
    resolve_pending_override_with_observers,
)
from prize_destination_overrides import PrizeDestinationOverride
from results.pending_prize_batch_correlation.reproduce import example


def close(a: float, b: float) -> None:
    assert abs(a - b) < 1e-12, (a, b)


def fails(expected: type[Exception], fn) -> None:
    try:
        fn()
    except expected:
        return
    raise AssertionError("expected a rejected illegal transition")


def main() -> None:
    physical, observers = example()
    groups = {name: name for name in ("A", "B", "X", "C")}
    staged = stage_physical_pending_batch(
        physical,
        observers,
        actor_id="actor",
        positions=(0, 1),
        group_by_card_class=groups,
    )
    lost = PrizeDestinationOverride("Lost Block", "lost_zone")
    smoke = PrizeDestinationOverride("Billowing Smoke", "discard")

    pending = resolve_pending_override_with_observers(
        staged, (lost, smoke),
        actor_id="actor", group_by_card_class=groups,
    )
    assert not pending.resolved
    assert pending.decision.requires_choice
    assert pending.after is None
    assert staged.pending.physical.ledger.instance("p0").zone == "prize_pending"

    # An ordinary hand-bound first Prize is hidden, but a public subsequent
    # override choice changes the opponent's posterior over the top card.
    private = resolve_pending_override_with_observers(
        staged, (), actor_id="actor", group_by_card_class=groups,
    )
    assert private.after is not None
    close(private.after.observers.belief_for("opponent").top_probability("A"), 0.5)
    public = resolve_pending_override_with_observers(
        private.after, (lost, smoke),
        actor_id="actor", group_by_card_class=groups,
        chosen_effect_id="Lost Block",
    )
    assert public.after is not None
    assert public.decision.destination_zone == "lost_zone"
    close(public.after.observers.belief_for("opponent").top_probability("A"), 1.0)
    assert public.after.pending.pending == ()
    assert public.after.pending.physical.ledger.instance("p0").zone == "hand"
    assert public.after.pending.physical.ledger.instance("p1").zone == "lost_zone"
    assert_conserved(physical.ledger, public.after.pending.physical.ledger)

    # The published Japanese ruling allows a different destination choice
    # for each exact Prize card in a two-Prize KO batch.
    first = resolve_pending_override_with_observers(
        staged, (lost, smoke),
        actor_id="actor", group_by_card_class=groups,
        chosen_effect_id="Billowing Smoke",
    )
    assert first.after is not None
    assert first.after.pending.physical.ledger.instance("p0").zone == "discard"
    second = resolve_pending_override_with_observers(
        first.after, (lost, smoke),
        actor_id="actor", group_by_card_class=groups,
        chosen_effect_id="Lost Block",
    )
    assert second.after is not None
    assert second.after.pending.physical.ledger.instance("p1").zone == "lost_zone"
    assert second.after.pending.pending == ()
    close(second.after.observers.belief_for("opponent").top_probability("A"), 1.0)
    assert_conserved(physical.ledger, second.after.pending.physical.ledger)

    reversed_first = resolve_pending_override_with_observers(
        staged, (lost, smoke),
        actor_id="actor", group_by_card_class=groups,
        chosen_effect_id="Lost Block",
    )
    assert reversed_first.after is not None
    reversed_second = resolve_pending_override_with_observers(
        reversed_first.after, (lost, smoke),
        actor_id="actor", group_by_card_class=groups,
        chosen_effect_id="Billowing Smoke",
    )
    assert reversed_second.after is not None
    assert reversed_second.after.pending.physical.ledger.instance("p0").zone == "lost_zone"
    assert reversed_second.after.pending.physical.ledger.instance("p1").zone == "discard"
    assert_conserved(physical.ledger, reversed_second.after.pending.physical.ledger)

    fails(ValueError, lambda: resolve_pending_override_with_observers(
        staged, (lost, smoke), actor_id="actor",
        group_by_card_class=groups, chosen_effect_id="Invalid",
    ))
    fails(ValueError, lambda: resolve_pending_override_with_observers(
        staged, (), actor_id="actor", group_by_card_class=groups,
        chosen_effect_id="Lost Block",
    ))
    fails(KeyError, lambda: resolve_pending_override_with_observers(
        staged, (), actor_id="unknown", group_by_card_class=groups,
    ))
    fails(ValueError, lambda: resolve_pending_override_with_observers(
        public.after, (), actor_id="actor", group_by_card_class=groups,
    ))

    print("Pending Prize replacement + observer correlation regressions passed")


if __name__ == "__main__":
    main()
