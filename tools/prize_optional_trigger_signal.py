"""Policy-conditioned information from optional, public Prize-origin E-31 decisions."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from math import isclose

from before_hand_prize_executor import (
    BeforeHandResolution,
    resolve_direct_before_hand_trigger,
)
from before_hand_prize_profiles import BeforeHandPrizeProfile
from identity_materialization import assert_conserved
from observer_top_prize_beliefs import ObserverTopPrizeBeliefs
from pending_prize_identity_belief import (
    ObserverPendingPrizeBeliefs,
    PendingPrizeJointBelief,
    resolve_single_pending_visibility,
)
from prize_pending_take import PrizePendingTakeState
from prize_position_belief import PrizeGroup
from top_prize_physical_bridge import actual_joint_groups, belief_truth_probability


@dataclass(frozen=True)
class OptionalPrizeTriggerResolution:
    physical: BeforeHandResolution
    beliefs_after: ObserverTopPrizeBeliefs


def condition_on_pending_trigger_decision(
    state: ObserverPendingPrizeBeliefs,
    *,
    actor_id: str,
    actor_observed_group: PrizeGroup,
    observed_use: bool,
    use_probability_by_group: Mapping[PrizeGroup, float],
) -> ObserverPendingPrizeBeliefs:
    """Condition joint pending/top/remaining-Prize worlds on an optional action.

    A successful use reveals the physical card group. Declining reveals only
    the action. The policy is an exogenous hypothesis about player behavior.
    """

    actor = state.belief_for(actor_id)
    actor_support = {
        group
        for (_top, _prizes, group), probability in actor.masses
        if probability > 0.0
    }
    if actor_observed_group not in actor_support:
        raise ValueError("actor-observed pending group has zero belief support")

    supported = {
        group
        for _observer, belief in state.beliefs
        for (_top, _prizes, group), probability in belief.masses
        if probability > 0.0
    }
    if not supported <= set(use_probability_by_group):
        raise ValueError("policy must cover every supported pending group")
    if any(
        not 0.0 <= probability <= 1.0
        for probability in use_probability_by_group.values()
    ):
        raise ValueError("trigger-use probabilities must lie in [0, 1]")

    next_beliefs = []
    for observer_id, belief in state.beliefs:
        weighted = []
        evidence = 0.0
        for hidden_state, prior in belief.masses:
            pending_group = hidden_state[2]
            if observer_id == actor_id and pending_group != actor_observed_group:
                continue
            if observed_use and pending_group != actor_observed_group:
                continue  # An activated Prize card becomes public.
            probability_of_use = use_probability_by_group[pending_group]
            likelihood = (
                probability_of_use if observed_use else 1.0 - probability_of_use
            )
            weight = prior * likelihood
            if weight > 0.0:
                weighted.append((hidden_state, weight))
                evidence += weight

        if isclose(evidence, 0.0, abs_tol=1e-15, rel_tol=0.0):
            raise ValueError("observed trigger decision has zero policy likelihood")
        next_beliefs.append((
            observer_id,
            PendingPrizeJointBelief(
                belief.groups,
                belief.face_up,
                tuple(
                    (hidden, weight / evidence)
                    for hidden, weight in weighted
                ),
            ),
        ))

    return ObserverPendingPrizeBeliefs(tuple(next_beliefs))


def resolve_direct_optional_prize_trigger_with_observers(
    state: PrizePendingTakeState,
    beliefs: ObserverPendingPrizeBeliefs,
    profile: BeforeHandPrizeProfile,
    *,
    actor_id: str,
    group_by_card_class: Mapping[str, PrizeGroup],
    observed_use: bool,
    use_probability_by_group: Mapping[PrizeGroup, float],
    during_own_turn: bool,
    bench_open: bool | None = None,
    board_object_id: str | None = None,
    attached_to: str | None = None,
    coin_heads: bool | None = None,
) -> OptionalPrizeTriggerResolution:
    """Resolve one pending direct trigger while preserving latent correlations.

    Supports direct self-to-Bench/self-attach triggers. Nested extra-Prize
    settlement and Item plays must be handled by their separate executors.
    """

    if len(state.pending) != 1 or not state.pending[0].was_face_down:
        raise ValueError("requires exactly one originally face-down pending Prize")
    if profile.activation_family not in {"self_to_bench", "self_attach"}:
        raise ValueError("only direct Prize-trigger families are supported")

    actual_id = state.pending[0].instance_id
    actual_group = group_by_card_class.get(
        state.physical.ledger.instance(actual_id).card_class,
    )
    conditioned = condition_on_pending_trigger_decision(
        beliefs,
        actor_id=actor_id,
        actor_observed_group=actual_group,
        observed_use=observed_use,
        use_probability_by_group=use_probability_by_group,
    )
    physical = resolve_direct_before_hand_trigger(
        state,
        profile,
        use_trigger=observed_use,
        during_own_turn=during_own_turn,
        bench_open=bench_open,
        board_object_id=board_object_id,
        attached_to=attached_to,
        coin_heads=coin_heads,
    )
    assert_conserved(state.physical.ledger, physical.after.physical.ledger)

    visible_groups = (
        {
            observer_id: actual_group
            for observer_id, _belief in conditioned.beliefs
        }
        if observed_use
        else {actor_id: actual_group}
    )
    after_beliefs = resolve_single_pending_visibility(
        conditioned,
        visible_groups=visible_groups,
    )
    top_group, prizes = actual_joint_groups(
        physical.after.physical,
        group_by_card_class,
    )
    for observer_id, belief in after_beliefs.beliefs:
        if belief_truth_probability(
            belief,
            top_group=top_group,
            prize_groups=prizes,
        ) <= 0.0:
            raise AssertionError(
                f"observer {observer_id!r} excludes exact physical truth"
            )

    return OptionalPrizeTriggerResolution(physical, after_beliefs)
