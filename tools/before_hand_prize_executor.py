"""Execute typed Prize-origin E-31 profiles against the pending queue."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from before_hand_prize_profiles import BeforeHandPrizeProfile
from identity_materialization import assert_conserved, move_instance
from item_play_source_scope import ItemPlayRestriction, restriction_blocks_source
from prize_pending_take import (
    PendingPrize,
    PrizePendingTakeState,
    resolve_next_pending_prize,
)
from top_prize_physical_bridge import TopPrizePhysicalState

RESOLVING_TRAINER_ZONE = "resolving_trainer"


@dataclass(frozen=True)
class BeforeHandResolution:
    before: PrizePendingTakeState
    after: PrizePendingTakeState
    profile: BeforeHandPrizeProfile
    used_trigger: bool
    additional_prize_awards: int


@dataclass(frozen=True)
class BeforeHandItemResolutionState:
    physical: TopPrizePhysicalState
    remaining_pending: tuple[PendingPrize, ...]
    item_instance_id: str
    profile: BeforeHandPrizeProfile

    def __post_init__(self) -> None:
        if self.profile.activation_family != "item_play":
            raise ValueError("resolving profile must be an Item-play family")
        item = self.physical.ledger.instance(self.item_instance_id)
        if item.zone != RESOLVING_TRAINER_ZONE:
            raise ValueError("resolving Item must occupy resolving_trainer")
        if any(
            row.instance_id == self.item_instance_id
            for row in self.remaining_pending
        ):
            raise ValueError("resolving Item cannot remain in pending queue")


@dataclass(frozen=True)
class BeforeHandItemResolution:
    resolving: BeforeHandItemResolutionState
    after: PrizePendingTakeState
    additional_prize_awards: int


def _pending_head(
    state: PrizePendingTakeState,
    profile: BeforeHandPrizeProfile,
) -> PendingPrize:
    if not state.pending:
        raise ValueError("no pending Prize card remains")
    head = state.pending[0]
    instance = state.physical.ledger.instance(head.instance_id)
    if instance.card_class != profile.card_id:
        raise ValueError(
            f"pending card class {instance.card_class!r} does not match "
            f"profile {profile.card_id!r}"
        )
    return head


def _validate_trigger_window(
    head: PendingPrize,
    profile: BeforeHandPrizeProfile,
    *,
    during_own_turn: bool,
) -> None:
    if not head.was_face_down:
        raise ValueError("Prize-origin before-hand trigger requires face-down take")
    if profile.during_own_turn_explicit and not during_own_turn:
        raise ValueError("card text requires the Prize to be taken during your turn")


def _extra_prize_awards(
    profile: BeforeHandPrizeProfile,
    *,
    coin_heads: bool | None,
) -> int:
    if profile.extra_prize_mode == "none":
        if coin_heads is not None:
            raise ValueError("coin result supplied for a non-coin profile")
        return 0
    if profile.extra_prize_mode == "guaranteed":
        if coin_heads is not None:
            raise ValueError("coin result supplied for a guaranteed profile")
        return 1
    if profile.extra_prize_mode == "coin_heads":
        if coin_heads is None:
            raise ValueError("coin result is required for this profile")
        return int(coin_heads)
    raise ValueError(
        f"unsupported extra Prize mode: {profile.extra_prize_mode!r}"
    )


def resolve_direct_before_hand_trigger(
    state: PrizePendingTakeState,
    profile: BeforeHandPrizeProfile,
    *,
    use_trigger: bool,
    during_own_turn: bool,
    bench_open: bool | None = None,
    board_object_id: str | None = None,
    attached_to: str | None = None,
    coin_heads: bool | None = None,
) -> BeforeHandResolution:
    """Resolve self-to-Bench or self-attach profiles, or decline to hand."""

    head = _pending_head(state, profile)

    if not use_trigger:
        if coin_heads is not None:
            raise ValueError("coin result supplied when trigger was declined")
        resolved = resolve_next_pending_prize(state)
        return BeforeHandResolution(
            state,
            resolved.after,
            profile,
            False,
            0,
        )

    _validate_trigger_window(
        head,
        profile,
        during_own_turn=during_own_turn,
    )

    if profile.activation_family == "self_to_bench":
        if profile.card_text_requires_open_bench and bench_open is not True:
            raise ValueError("card text requires an open Bench")
        if not board_object_id:
            raise ValueError("self-to-Bench trigger requires board_object_id")
        resolved = resolve_next_pending_prize(
            state,
            destination_zone="in_play",
            board_object_id=board_object_id,
        )
    elif profile.activation_family == "self_attach":
        if not attached_to:
            raise ValueError("self-attach trigger requires attached_to")
        resolved = resolve_next_pending_prize(
            state,
            destination_zone="attached",
            attached_to=attached_to,
        )
    else:
        raise ValueError(
            "direct resolver supports only self-to-Bench and self-attach profiles"
        )

    return BeforeHandResolution(
        state,
        resolved.after,
        profile,
        True,
        _extra_prize_awards(profile, coin_heads=coin_heads),
    )


def begin_before_hand_item_play(
    state: PrizePendingTakeState,
    profile: BeforeHandPrizeProfile,
    *,
    during_own_turn: bool,
    active_item_restrictions: Sequence[ItemPlayRestriction] = (),
) -> BeforeHandItemResolutionState:
    """Move a Prize-origin Item from pending into temporary resolution."""

    head = _pending_head(state, profile)
    if profile.activation_family != "item_play":
        raise ValueError("profile is not an Item-play family")

    _validate_trigger_window(
        head,
        profile,
        during_own_turn=during_own_turn,
    )

    if any(
        restriction_blocks_source(restriction, "prize_pending")
        for restriction in active_item_restrictions
    ):
        raise ValueError("Item play is blocked from the pending Prize source")

    ledger = move_instance(
        state.physical.ledger,
        head.instance_id,
        RESOLVING_TRAINER_ZONE,
    )
    assert_conserved(state.physical.ledger, ledger)

    physical = TopPrizePhysicalState(
        ledger,
        state.physical.top_instance_id,
        state.physical.prize_instance_ids,
        state.physical.face_up,
    )
    return BeforeHandItemResolutionState(
        physical,
        state.pending[1:],
        head.instance_id,
        profile,
    )


def finish_before_hand_item_play(
    state: BeforeHandItemResolutionState,
    *,
    secondary_effect_resolved: bool = False,
    coin_heads: bool | None = None,
) -> BeforeHandItemResolution:
    """Finish the Prize-origin Item, then restore the pending queue."""

    profile = state.profile
    if profile.searches_pokemon_to_bench and not secondary_effect_resolved:
        raise ValueError("Dream Ball search effect must be resolved first")
    if not profile.searches_pokemon_to_bench and secondary_effect_resolved:
        raise ValueError("unexpected secondary-effect completion marker")

    additional = _extra_prize_awards(profile, coin_heads=coin_heads)

    ledger = move_instance(
        state.physical.ledger,
        state.item_instance_id,
        "discard",
    )
    assert_conserved(state.physical.ledger, ledger)

    physical = TopPrizePhysicalState(
        ledger,
        state.physical.top_instance_id,
        state.physical.prize_instance_ids,
        state.physical.face_up,
    )
    after = PrizePendingTakeState(
        physical,
        state.remaining_pending,
    )
    return BeforeHandItemResolution(
        state,
        after,
        additional,
    )
