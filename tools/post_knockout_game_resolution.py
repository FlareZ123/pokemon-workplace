"""Post-Knock-Out Prize and game-resolution mechanics.

The Advanced Player's Rulebook resolves Knock Outs before replacement Active
choices: triggered effects, disposal, Prize taking, then promotion when needed.
This module models the terminal check that follows the disposal/Prize boundary.
It deliberately keeps physical Prize-card identity outside this layer; callers
supply Prize-card awards while hidden-zone models own which physical cards move.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable, Mapping

from knockout_phase_resolution import TwoPlayerKnockOutPhase


class Outcome(str, Enum):
    CONTINUE = "continue"
    WIN = "win"
    LOSS = "loss"
    TIE = "tie"


@dataclass(frozen=True)
class PostKnockOutPlayerState:
    player_id: str
    prizes_before: int
    prize_award: int
    prizes_taken: int
    prizes_remaining: int
    surviving_pokemon: int

    def __post_init__(self) -> None:
        if not self.player_id:
            raise ValueError("player_id must be non-empty")
        if self.prizes_before < 0:
            raise ValueError("prizes_before must be non-negative")
        if self.prize_award < 0:
            raise ValueError("prize_award must be non-negative")
        if self.prizes_taken < 0:
            raise ValueError("prizes_taken must be non-negative")
        if self.prizes_remaining < 0:
            raise ValueError("prizes_remaining must be non-negative")
        if self.surviving_pokemon < 0:
            raise ValueError("surviving_pokemon must be non-negative")
        if self.prizes_taken != min(self.prize_award, self.prizes_before):
            raise ValueError("prizes_taken must equal the available awarded Prizes")
        if self.prizes_remaining != self.prizes_before - self.prizes_taken:
            raise ValueError("prizes_remaining is inconsistent with Prize taking")


@dataclass(frozen=True)
class Resolution:
    outcomes: tuple[tuple[str, Outcome], ...]
    loss_condition_counts: tuple[tuple[str, int], ...]

    def outcome(self, player_id: str) -> Outcome:
        return dict(self.outcomes)[player_id]

    def loss_count(self, player_id: str) -> int:
        return dict(self.loss_condition_counts)[player_id]

    @property
    def terminal(self) -> bool:
        return any(outcome != Outcome.CONTINUE for _, outcome in self.outcomes)


@dataclass(frozen=True)
class PostKnockOutResolution:
    players: tuple[PostKnockOutPlayerState, PostKnockOutPlayerState]
    resolution: Resolution

    def player(self, player_id: str) -> PostKnockOutPlayerState:
        for row in self.players:
            if row.player_id == player_id:
                return row
        raise KeyError(player_id)


def _validate_two_players(player_ids: Iterable[str]) -> tuple[str, str]:
    ids = tuple(player_ids)
    if len(ids) != 2 or len(set(ids)) != 2 or any(not player_id for player_id in ids):
        raise ValueError("exactly two distinct non-empty player IDs are required")
    return ids[0], ids[1]


def resolve_prize_and_board_loss_conditions(
    *,
    player_ids: tuple[str, str],
    prizes_remaining: Mapping[str, int],
    pokemon_in_play: Mapping[str, int],
) -> Resolution:
    """Resolve Prize/no-Pokemon loss conditions using the rulebook table.

    For a player P, the two conditions that make P lose are:
    - the opponent has taken all Prize cards;
    - P has no Pokemon in play.

    The rulebook's simultaneous-loss table is equivalent to comparing how many
    of those loss conditions each player fulfills. Equal positive counts tie;
    otherwise the player with more fulfilled loss conditions loses.
    """

    first, second = _validate_two_players(player_ids)
    ids = (first, second)
    if set(prizes_remaining) != set(ids):
        raise ValueError("prizes_remaining must contain exactly both players")
    if set(pokemon_in_play) != set(ids):
        raise ValueError("pokemon_in_play must contain exactly both players")
    if any(prizes_remaining[player_id] < 0 for player_id in ids):
        raise ValueError("Prize counts must be non-negative")
    if any(pokemon_in_play[player_id] < 0 for player_id in ids):
        raise ValueError("Pokemon counts must be non-negative")

    opponent = {first: second, second: first}
    loss_counts = {
        player_id: (
            int(prizes_remaining[opponent[player_id]] == 0)
            + int(pokemon_in_play[player_id] == 0)
        )
        for player_id in ids
    }

    first_losses = loss_counts[first]
    second_losses = loss_counts[second]
    if first_losses == second_losses == 0:
        outcomes = {first: Outcome.CONTINUE, second: Outcome.CONTINUE}
    elif first_losses == second_losses:
        outcomes = {first: Outcome.TIE, second: Outcome.TIE}
    elif first_losses > second_losses:
        outcomes = {first: Outcome.LOSS, second: Outcome.WIN}
    else:
        outcomes = {first: Outcome.WIN, second: Outcome.LOSS}

    return Resolution(
        outcomes=tuple((player_id, outcomes[player_id]) for player_id in ids),
        loss_condition_counts=tuple(
            (player_id, loss_counts[player_id]) for player_id in ids
        ),
    )


def resolve_post_knockout(
    phase: TwoPlayerKnockOutPhase,
    *,
    prizes_remaining_before: Mapping[str, int],
    prize_awards: Mapping[str, int],
) -> PostKnockOutResolution:
    """Apply KO Prize awards and resolve terminal Prize/board conditions.

    Survivor counts are computed from the complete Knock Out set before any
    replacement Active choice. Awarded Prize cards are capped at the number
    actually remaining. This lets a single KO that awards multiple Prizes take
    the final available Prize without making Prize counts negative.
    """

    ids = tuple(side.player_id for side in phase.sides)
    first, second = _validate_two_players(ids)
    ids = (first, second)
    if set(prizes_remaining_before) != set(ids):
        raise ValueError("prizes_remaining_before must contain exactly both players")
    if set(prize_awards) != set(ids):
        raise ValueError("prize_awards must contain exactly both players")

    rows: list[PostKnockOutPlayerState] = []
    for side in phase.sides:
        player_id = side.player_id
        before = prizes_remaining_before[player_id]
        award = prize_awards[player_id]
        if before < 0 or award < 0:
            raise ValueError("Prize counts and awards must be non-negative")

        board = side.pending.state.board
        assert board is not None
        knocked_out = set(side.pending.knocked_out_ids)
        survivors = sum(
            pokemon.pokemon_id not in knocked_out
            for pokemon in board.pokemon
        )
        taken = min(before, award)
        rows.append(
            PostKnockOutPlayerState(
                player_id=player_id,
                prizes_before=before,
                prize_award=award,
                prizes_taken=taken,
                prizes_remaining=before - taken,
                surviving_pokemon=survivors,
            )
        )

    by_player = {row.player_id: row for row in rows}
    resolution = resolve_prize_and_board_loss_conditions(
        player_ids=ids,
        prizes_remaining={
            player_id: by_player[player_id].prizes_remaining
            for player_id in ids
        },
        pokemon_in_play={
            player_id: by_player[player_id].surviving_pokemon
            for player_id in ids
        },
    )
    return PostKnockOutResolution(tuple(rows), resolution)


def resolve_start_of_turn_deck_out(
    *,
    player_ids: tuple[str, str],
    current_turn_player: str,
    current_turn_player_could_draw: bool,
) -> Resolution:
    """Resolve the beginning-of-turn empty-deck loss condition.

    A deck-out loss is checked for the player beginning that turn. Other
    terminal conditions should already have been resolved when they arose.
    """

    first, second = _validate_two_players(player_ids)
    if current_turn_player not in {first, second}:
        raise ValueError("current_turn_player must be one of the players")
    if current_turn_player_could_draw:
        outcomes = {first: Outcome.CONTINUE, second: Outcome.CONTINUE}
        losses = {first: 0, second: 0}
    else:
        other = second if current_turn_player == first else first
        outcomes = {
            current_turn_player: Outcome.LOSS,
            other: Outcome.WIN,
        }
        losses = {current_turn_player: 1, other: 0}
    ids = (first, second)
    return Resolution(
        outcomes=tuple((player_id, outcomes[player_id]) for player_id in ids),
        loss_condition_counts=tuple((player_id, losses[player_id]) for player_id in ids),
    )


def resolve_tiebreaker_progress(
    *,
    player_ids: tuple[str, str],
    prizes_remaining: Mapping[str, int],
) -> Resolution:
    """In a tiebreaker, the first player with fewer remaining Prizes wins."""

    first, second = _validate_two_players(player_ids)
    if set(prizes_remaining) != {first, second}:
        raise ValueError("prizes_remaining must contain exactly both players")
    if any(prizes_remaining[player_id] < 0 for player_id in (first, second)):
        raise ValueError("Prize counts must be non-negative")

    first_prizes = prizes_remaining[first]
    second_prizes = prizes_remaining[second]
    if first_prizes == second_prizes:
        outcomes = {first: Outcome.CONTINUE, second: Outcome.CONTINUE}
    elif first_prizes < second_prizes:
        outcomes = {first: Outcome.WIN, second: Outcome.LOSS}
    else:
        outcomes = {first: Outcome.LOSS, second: Outcome.WIN}
    return Resolution(
        outcomes=((first, outcomes[first]), (second, outcomes[second])),
        loss_condition_counts=((first, 0), (second, 0)),
    )
