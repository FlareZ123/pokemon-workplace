"""Combinatorial upper bounds for direct Pokemon zone-exit target geometry."""

from __future__ import annotations

from math import comb


def target_set_upper_bound(
    geometry: str,
    *,
    own_board_count: int,
    own_bench_count: int,
    opponent_board_count: int,
    opponent_bench_count: int,
) -> int | None:
    """Return the coarse number of target sets before card-specific filters."""

    counts = (
        own_board_count,
        own_bench_count,
        opponent_board_count,
        opponent_bench_count,
    )
    if any(count < 0 for count in counts):
        raise ValueError("board counts must be non-negative")
    if own_bench_count > own_board_count:
        raise ValueError("own Bench cannot exceed own board count")
    if opponent_bench_count > opponent_board_count:
        raise ValueError("opponent Bench cannot exceed opponent board count")

    if geometry == "self":
        return int(own_board_count > 0)
    if geometry == "own_one":
        return own_board_count
    if geometry == "own_bench_one":
        return own_bench_count
    if geometry == "opponent_active":
        return int(opponent_board_count > 0)
    if geometry == "opponent_bench_one":
        return opponent_bench_count
    if geometry == "opponent_one":
        return opponent_board_count
    if geometry == "own_any_number":
        return 2 ** own_board_count
    if geometry == "opponent_bench_one_and_self":
        return (
            opponent_bench_count
            if own_board_count > 0
            else 0
        )
    if geometry == "opponent_bench_all":
        return 1
    if geometry == "opponent_bench_all_except_selected_three":
        selected_survivors = min(3, opponent_bench_count)
        return comb(opponent_bench_count, selected_survivors)
    if geometry == "both_active":
        return int(
            own_board_count > 0
            and opponent_board_count > 0
        )
    if geometry == "unqualified_one_to_your_hand":
        return None

    raise ValueError(f"unknown target geometry: {geometry}")


def any_number_own_board_continuations(
    bench_count: int,
) -> int:
    """Count target-selection plus later-promotion continuations.

    One Active and bench_count Benched Pokemon are initially in play. Any subset
    may leave. If the Active leaves while survivors remain, each surviving Bench
    Pokemon is a distinct replacement-Active continuation. Removing the entire
    board is one terminal continuation.
    """

    if bench_count < 0:
        raise ValueError("bench_count must be non-negative")

    active_kept = 2 ** bench_count
    active_removed_with_survivors = (
        0
        if bench_count == 0
        else bench_count * 2 ** (bench_count - 1)
    )
    terminal_all_removed = 1
    return (
        active_kept
        + active_removed_with_survivors
        + terminal_all_removed
    )


def ordered_promotion_continuations(
    first_player_candidates: int,
    second_player_candidates: int,
) -> int:
    """Count ordered visible promotion pairs when both players must replace."""

    if first_player_candidates < 0 or second_player_candidates < 0:
        raise ValueError("promotion candidate counts must be non-negative")
    return first_player_candidates * second_player_candidates
