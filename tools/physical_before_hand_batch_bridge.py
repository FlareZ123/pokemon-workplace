"""Synchronize direct Prize-origin E-31 effects with batch observer beliefs."""

from __future__ import annotations

from collections.abc import Mapping

from before_hand_prize_executor import resolve_direct_before_hand_trigger
from before_hand_prize_profiles import BeforeHandPrizeProfile
from pending_prize_batch_belief import resolve_next_pending_batch_visibility
from physical_pending_prize_batch_bridge import (
    PhysicalPendingBatchBeliefs,
    _assert_pending_truth,
)
from prize_position_belief import PrizeGroup


def resolve_direct_before_hand_with_batch_beliefs(
    state: PhysicalPendingBatchBeliefs,
    profile: BeforeHandPrizeProfile,
    *,
    actor_id: str,
    group_by_card_class: Mapping[str, PrizeGroup],
    use_trigger: bool,
    during_own_turn: bool,
    bench_open: bool | None = None,
    board_object_id: str | None = None,
    attached_to: str | None = None,
    coin_heads: bool | None = None,
    pre_hand_destination: str = "hand",
):
    """Resolve direct E-31 effects and apply the actual destination's visibility.

    Cards played to the Bench or attached as Energy reveal their identities
    publicly. A declined trigger entering hand remains private to its owner.
    The underlying BeforeHandResolution is returned for additional Prize awards.
    """
    state.observers.belief_for(actor_id)
    if not state.pending.pending:
        raise ValueError("no pending Prize card")

    head_id = state.pending.pending[0].instance_id
    instance = state.pending.physical.ledger.instance(head_id)
    group = group_by_card_class.get(instance.card_class)
    effect = resolve_direct_before_hand_trigger(
        state.pending,
        profile,
        use_trigger=use_trigger,
        during_own_turn=during_own_turn,
        bench_open=bench_open,
        board_object_id=board_object_id,
        attached_to=attached_to,
        coin_heads=coin_heads,
        pre_hand_destination=pre_hand_destination,
    )
    zone = effect.after.physical.ledger.instance(head_id).zone
    observer_ids = tuple(name for name, _ in state.observers.beliefs)
    if zone in {"discard", "lost_zone", "in_play", "attached"}:
        visible = {observer_id: group for observer_id in observer_ids}
    elif zone == "hand":
        visible = {actor_id: group}
    else:
        raise ValueError(f"unsupported E-31 destination zone: {zone!r}")

    latent = resolve_next_pending_batch_visibility(
        state.observers, instance_id=head_id, visible_groups=visible,
    )
    result = PhysicalPendingBatchBeliefs(effect.after, latent)
    _assert_pending_truth(result, group_by_card_class)
    return result, effect
