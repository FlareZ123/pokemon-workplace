"""Derive continuous source-scoped restrictions from canonical board state.

The source-scoped restriction layer models activation geometry, while the
Ability-lock causal layer owns effective suppression. This bridge combines the
two so callers do not supply stale ``ability_enabled`` or position booleans by
hand.
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Sequence

from ability_lock_causal_state import AbilityLockCausalState
from ability_lock_dependency_graph import (
    resolve_ability_lock_dependencies,
    targets_for_source,
)
from active_source_scoped_restrictions import (
    ContinuousRestrictionSource,
    active_restrictions_for_player,
)
from attack_restriction_turn_windows import AttackRestrictionWindow
from board_object_kernel import BoardPokemon, BoardState
from continuous_source_scoped_restrictions import ContinuousRestrictionContext
from source_scoped_action_restrictions import SourceScopedActionRestriction
from source_scoped_restriction_activation import RestrictionActivationProfile


def _validate_lock_state(
    lock_state: AbilityLockCausalState,
    player_board: BoardState,
    opponent_board: BoardState,
    *,
    stadium_name: str | None,
) -> tuple[frozenset[str], frozenset[str]]:
    resolution = lock_state.resolution
    if (
        not resolution.resolved
        or resolution.active_sources is None
        or resolution.player_suppressed_object_ids is None
        or resolution.opponent_suppressed_object_ids is None
    ):
        raise ValueError(
            "continuous restriction derivation requires a resolved Ability-lock state"
        )

    snapshot = resolve_ability_lock_dependencies(
        player_board,
        opponent_board,
        stadium_name=stadium_name,
    )
    if (
        snapshot.potential_sources != resolution.potential_sources
        or snapshot.suppression_edges != resolution.suppression_edges
    ):
        raise ValueError("Ability-lock state does not match the current board graph")

    if snapshot.resolved and snapshot != resolution:
        raise ValueError("Ability-lock state is stale for the current board")

    expected_player: set[str] = set()
    expected_opponent: set[str] = set()
    for source in resolution.active_sources:
        if source not in snapshot.potential_sources:
            raise ValueError("Ability-lock state contains an inactive source")
        player_ids, opponent_ids = targets_for_source(
            source,
            player_board,
            opponent_board,
            stadium_name=stadium_name,
        )
        expected_player.update(player_ids)
        expected_opponent.update(opponent_ids)

    if (
        frozenset(expected_player) != resolution.player_suppressed_object_ids
        or frozenset(expected_opponent) != resolution.opponent_suppressed_object_ids
    ):
        raise ValueError("Ability-lock suppression overlay is stale for the current board")

    return (
        resolution.player_suppressed_object_ids,
        resolution.opponent_suppressed_object_ids,
    )


def _continuous_profiles_by_card(
    profiles: Sequence[RestrictionActivationProfile],
) -> dict[str, tuple[RestrictionActivationProfile, ...]]:
    rows: dict[str, list[RestrictionActivationProfile]] = defaultdict(list)
    for profile in profiles:
        if profile.duration_family == "continuous":
            rows[profile.restriction.card_id].append(profile)
    return {card_id: tuple(card_profiles) for card_id, card_profiles in rows.items()}


def _context_for_source(
    pokemon: BoardPokemon,
    source_board: BoardState,
    other_board: BoardState,
    *,
    suppressed_object_ids: frozenset[str],
    stadium_name: str | None,
) -> ContinuousRestrictionContext:
    return ContinuousRestrictionContext(
        source_in_play=True,
        ability_enabled=(
            pokemon.abilities_enabled
            and pokemon.object_id not in suppressed_object_ids
        ),
        source_active=source_board.active_id == pokemon.object_id,
        tool_attached=pokemon.tool is not None,
        stadium_in_play=stadium_name is not None,
        player_pokemon_in_play=len(source_board.objects),
        opponent_pokemon_in_play=len(other_board.objects),
    )


def derive_continuous_restriction_sources(
    player_board: BoardState,
    opponent_board: BoardState,
    *,
    profiles: Sequence[RestrictionActivationProfile],
    lock_state: AbilityLockCausalState,
    stadium_name: str | None = None,
    player_id: str = "player",
    opponent_id: str = "opponent",
) -> tuple[ContinuousRestrictionSource, ...]:
    """Compile live continuous-restriction source contexts from two boards.

    ``lock_state`` remains the authority for causal Ability-suppression
    precedence. This function validates that the state still matches the supplied
    boards and Stadium before using its suppression overlay.
    """

    player_board.validate()
    opponent_board.validate()
    if not player_id or not opponent_id:
        raise ValueError("player identifiers must be non-empty")
    if player_id == opponent_id:
        raise ValueError("players must be distinct")

    player_suppressed, opponent_suppressed = _validate_lock_state(
        lock_state,
        player_board,
        opponent_board,
        stadium_name=stadium_name,
    )
    profiles_by_card = _continuous_profiles_by_card(profiles)

    sources: list[ContinuousRestrictionSource] = []
    for (
        board,
        other_board,
        source_player,
        other_player,
        suppressed,
    ) in (
        (
            player_board,
            opponent_board,
            player_id,
            opponent_id,
            player_suppressed,
        ),
        (
            opponent_board,
            player_board,
            opponent_id,
            player_id,
            opponent_suppressed,
        ),
    ):
        for pokemon in board.objects:
            if pokemon.print_id is None:
                continue
            context = _context_for_source(
                pokemon,
                board,
                other_board,
                suppressed_object_ids=suppressed,
                stadium_name=stadium_name,
            )
            for profile in profiles_by_card.get(pokemon.print_id, ()):
                sources.append(
                    ContinuousRestrictionSource(
                        profile=profile,
                        context=context,
                        source_player=source_player,
                        other_player=other_player,
                    )
                )

    return tuple(sources)


def active_restrictions_from_boards(
    player: str,
    player_board: BoardState,
    opponent_board: BoardState,
    *,
    profiles: Sequence[RestrictionActivationProfile],
    lock_state: AbilityLockCausalState,
    stadium_name: str | None = None,
    player_id: str = "player",
    opponent_id: str = "opponent",
    attack_windows: Sequence[AttackRestrictionWindow] = (),
) -> tuple[SourceScopedActionRestriction, ...]:
    """Return active restrictions after deriving continuous sources from boards."""

    if player not in {player_id, opponent_id}:
        raise ValueError("unknown player")
    continuous_sources = derive_continuous_restriction_sources(
        player_board,
        opponent_board,
        profiles=profiles,
        lock_state=lock_state,
        stadium_name=stadium_name,
        player_id=player_id,
        opponent_id=opponent_id,
    )
    return active_restrictions_for_player(
        player,
        continuous_sources=continuous_sources,
        attack_windows=attack_windows,
    )
