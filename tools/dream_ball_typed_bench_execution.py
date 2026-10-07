"""Execute Dream Ball's typed deck search directly into Bench topology.

Dream Ball is a Prize-origin E-31 Item. The existing before-hand executor keeps
the physical Dream Ball instance in a resolving_trainer zone while its search
body resolves. This module composes that state with the typed search allocator
and the promotion-pending board so the exact selected Pokemon copy moves from
an exchangeable deck count into one materialized in-play board object.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, replace

from before_hand_prize_executor import (
    BeforeHandItemResolutionState,
    begin_before_hand_item_play,
    finish_before_hand_item_play,
    resolve_before_hand_item_effect,
)
from before_hand_prize_profiles import BeforeHandPrizeProfile
from board_position_state import BoardPokemon, PokemonCard
from identity_materialization import (
    IdentityLedger,
    assert_conserved,
    materialize,
    put_in_play_instance,
)
from item_play_source_scope import ItemPlayRestriction
from pokemon_board_metadata import PokemonBoardMetadata
from prize_pending_take import PrizePendingTakeState
from promotion_pending_conservation import PromotionPendingState
from search_zone_transition import SearchZoneTarget, apply_typed_search_action
from top_prize_physical_bridge import TopPrizePhysicalState
from typed_search_target_allocator import (
    TargetGroup,
    TypedTargetAction,
    selector_from_label,
)


DREAM_BALL_CARD_CLASS = "swsh7-146"
_SELECTED_ZONE = "dream_ball_selected"


@dataclass(frozen=True)
class DreamBallBenchTarget:
    """One exact searchable Pokemon class plus board metadata."""

    search_target: SearchZoneTarget
    card_name: str
    retreat_cost: int
    evolves_from: str | None = None

    def __post_init__(self) -> None:
        if not self.card_name:
            raise ValueError("card_name must be non-empty")
        if self.retreat_cost < 0:
            raise ValueError("retreat_cost must be non-negative")


def dream_ball_target_from_metadata(
    metadata: PokemonBoardMetadata,
    *,
    copies: int,
) -> DreamBallBenchTarget:
    """Bind exact database metadata to one typed Dream Ball search target."""

    if copies < 0:
        raise ValueError("copies must be non-negative")
    return DreamBallBenchTarget(
        SearchZoneTarget(
            metadata.card_id,
            TargetGroup(
                metadata.name,
                copies,
                metadata.tags,
            ),
        ),
        metadata.name,
        metadata.retreat_cost,
        metadata.evolves_from,
    )


@dataclass(frozen=True)
class DreamBallBenchTransition:
    before_resolving: BeforeHandItemResolutionState
    after_resolving: BeforeHandItemResolutionState
    before_board: PromotionPendingState
    after_board: PromotionPendingState
    selected_card_class: str
    materialized_instance_id: str
    pokemon_id: str


@dataclass(frozen=True)
class DreamBallNoTargetTransaction:
    """One complete Dream Ball play whose typed deck search selects no Pokémon."""

    before_prizes: PrizePendingTakeState
    before_board: PromotionPendingState
    after_prizes: PrizePendingTakeState
    after_board: PromotionPendingState


@dataclass(frozen=True)
class DreamBallItemTransaction:
    """One complete Prize-origin Dream Ball play with synchronized board state."""

    before_prizes: PrizePendingTakeState
    before_board: PromotionPendingState
    after_prizes: PrizePendingTakeState
    after_board: PromotionPendingState
    bench_transition: DreamBallBenchTransition


def execute_dream_ball_bench_search(
    resolving: BeforeHandItemResolutionState,
    board: PromotionPendingState,
    *,
    targets: Sequence[DreamBallBenchTarget],
    search_action: TypedTargetAction,
    pokemon_id: str,
    instance_id: str,
) -> DreamBallBenchTransition:
    """Execute one exact Dream Ball Pokemon search into an open Bench slot."""

    if resolving.profile.card_id != DREAM_BALL_CARD_CLASS:
        raise ValueError("resolving Item is not Dream Ball")
    if not resolving.profile.searches_pokemon_to_bench:
        raise ValueError("Dream Ball profile lacks its Pokemon-to-Bench search")
    if resolving.physical.ledger != board.ledger:
        raise ValueError("Dream Ball and board states must share one physical ledger")
    if board.open_bench_slots <= 0:
        raise ValueError("Dream Ball requires an open Bench slot")
    if not pokemon_id or any(row.pokemon_id == pokemon_id for row in board.pokemon):
        raise ValueError("pokemon_id must be a new non-empty board object ID")
    if not instance_id:
        raise ValueError("instance_id must be non-empty")

    bound = tuple(targets)
    search_targets = tuple(row.search_target for row in bound)
    if len(search_action.target_cost) != len(bound):
        raise ValueError("target_cost length does not match Dream Ball targets")
    if sum(search_action.target_cost) != 1:
        raise ValueError("Dream Ball must select exactly one Pokemon target")

    selected_indices = tuple(
        index
        for index, cost in enumerate(search_action.target_cost)
        if cost
    )
    if len(selected_indices) != 1:
        raise ValueError("Dream Ball exact witness must identify one target class")
    selected_index = selected_indices[0]
    if search_action.target_cost[selected_index] != 1:
        raise ValueError("Dream Ball cannot select multiple copies of one target")

    pokemon_selector = selector_from_label("Pokemon")
    selected = bound[selected_index]
    if not pokemon_selector.matches(selected.search_target.group):
        raise ValueError("Dream Ball selected target is not a Pokemon")

    zone_transition = apply_typed_search_action(
        board.ledger.exchangeable,
        search_targets,
        search_action,
        source_zone="deck",
        destination_zone=_SELECTED_ZONE,
    )
    ledger = IdentityLedger(
        zone_transition.after,
        board.ledger.instances,
    )
    ledger = materialize(
        ledger,
        card_class=selected.search_target.card_class,
        card_name=selected.card_name,
        source_zone=_SELECTED_ZONE,
        instance_id=instance_id,
    )
    ledger = put_in_play_instance(
        ledger,
        instance_id,
        pokemon_id,
    )

    pokemon = BoardPokemon(
        pokemon_id,
        (
            PokemonCard(
                instance_id,
                selected.card_name,
                selected.evolves_from,
            ),
        ),
        retreat_cost=selected.retreat_cost,
        evolution_eligible=False,
    )
    after_board = replace(
        board,
        ledger=ledger,
        pokemon=board.pokemon + (pokemon,),
    )

    physical = TopPrizePhysicalState(
        ledger,
        resolving.physical.top_instance_id,
        resolving.physical.prize_instance_ids,
        resolving.physical.face_up,
    )
    after_resolving = BeforeHandItemResolutionState(
        physical,
        resolving.remaining_pending,
        resolving.item_instance_id,
        resolving.profile,
    )

    assert_conserved(resolving.physical.ledger, ledger)
    return DreamBallBenchTransition(
        before_resolving=resolving,
        after_resolving=after_resolving,
        before_board=board,
        after_board=after_board,
        selected_card_class=selected.search_target.card_class,
        materialized_instance_id=instance_id,
        pokemon_id=pokemon_id,
    )


def execute_dream_ball_item_transaction(
    prizes: PrizePendingTakeState,
    board: PromotionPendingState,
    *,
    profile: BeforeHandPrizeProfile,
    during_own_turn: bool,
    targets: Sequence[DreamBallBenchTarget],
    search_action: TypedTargetAction,
    pokemon_id: str,
    instance_id: str,
    active_item_restrictions: Sequence[ItemPlayRestriction] = (),
) -> DreamBallItemTransaction:
    """Execute Dream Ball from Prize pending through Item discard atomically."""

    if prizes.physical.ledger != board.ledger:
        raise ValueError("Prize and board states must share one physical ledger")

    resolving = begin_before_hand_item_play(
        prizes,
        profile,
        during_own_turn=during_own_turn,
        active_item_restrictions=active_item_restrictions,
    )
    resolving_board = board.with_ledger(resolving.physical.ledger)

    bench_transition = execute_dream_ball_bench_search(
        resolving,
        resolving_board,
        targets=targets,
        search_action=search_action,
        pokemon_id=pokemon_id,
        instance_id=instance_id,
    )
    effect = resolve_before_hand_item_effect(
        bench_transition.after_resolving,
        secondary_effect_resolved=True,
    )
    after_prizes = finish_before_hand_item_play(effect)
    after_board = bench_transition.after_board.with_ledger(
        after_prizes.physical.ledger
    )

    if after_prizes.physical.ledger != after_board.ledger:
        raise AssertionError("Dream Ball transaction ended with split physical ledgers")
    assert_conserved(prizes.physical.ledger, after_prizes.physical.ledger)

    return DreamBallItemTransaction(
        before_prizes=prizes,
        before_board=board,
        after_prizes=after_prizes,
        after_board=after_board,
        bench_transition=bench_transition,
    )


def execute_dream_ball_no_target_transaction(
    prizes: PrizePendingTakeState,
    board: PromotionPendingState,
    *,
    profile: BeforeHandPrizeProfile,
    during_own_turn: bool,
    active_item_restrictions: Sequence[ItemPlayRestriction] = (),
) -> DreamBallNoTargetTransaction:
    """Play Dream Ball and legally select no Pokémon from its typed deck search."""

    if profile.card_id != DREAM_BALL_CARD_CLASS:
        raise ValueError("profile is not Dream Ball")
    if prizes.physical.ledger != board.ledger:
        raise ValueError("Prize and board states must share one physical ledger")
    if board.open_bench_slots <= 0:
        raise ValueError("Dream Ball cannot be played with a full Bench")

    resolving = begin_before_hand_item_play(
        prizes,
        profile,
        during_own_turn=during_own_turn,
        active_item_restrictions=active_item_restrictions,
    )
    effect = resolve_before_hand_item_effect(
        resolving,
        secondary_effect_resolved=True,
    )
    after_prizes = finish_before_hand_item_play(effect)
    after_board = board.with_ledger(after_prizes.physical.ledger)

    if after_prizes.physical.ledger != after_board.ledger:
        raise AssertionError("Dream Ball no-target branch split physical ledgers")
    assert_conserved(prizes.physical.ledger, after_prizes.physical.ledger)

    return DreamBallNoTargetTransaction(
        before_prizes=prizes,
        before_board=board,
        after_prizes=after_prizes,
        after_board=after_board,
    )
