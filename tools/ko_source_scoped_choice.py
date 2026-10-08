"""Compare player-optimal KO effect orders under independently selected rules sources.

A per-source chooser claim is evaluated independently. When sources disagree on
the chooser, results remain source-conditioned and expose a value interval.
Payoff functions and assumed opposing objectives come from the caller.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Callable, Iterable, Mapping

from ko_order_outcome_space import OrderOutcome
from ko_order_component_factorization import factorized_ko_order_outcomes
from ko_trigger_order_authority import OrderingContext
from source_order_chooser import (
    ConcreteChooserStatus,
    OrderingPlayers,
    assess_concrete_ordering_player,
)


@dataclass(frozen=True)
class SourceChoice:
    source_id: str
    authority_status: ConcreteChooserStatus
    chooser: str | None
    best_outcome: OrderOutcome | None
    optimal_outcomes: tuple[OrderOutcome, ...]
    viewpoint_payoff: float | None


@dataclass(frozen=True)
class SourceChoiceResult:
    choices: tuple[SourceChoice, ...]
    outcome_count: int
    # For a zero-sum two-player game under all included resolved sources.
    payoff_envelope: tuple[float, float] | None
    optimal_outcome_union: tuple[OrderOutcome, ...]

    @property
    def value_invariant(self) -> bool:
        """All resolved source policies agree on the optimal utility value."""
        return (
            self.payoff_envelope is not None
            and self.payoff_envelope[0] == self.payoff_envelope[1]
        )

    @property
    def instance_destination_invariant(self) -> bool:
        """All resolved source-optimal destination choices coincide physically."""
        return len(self.optimal_outcome_union) == 1


def choose_ko_outcome_by_source(
    programs: Mapping[str, Mapping[str, str]],
    *,
    context: OrderingContext,
    source_ids: Iterable[str],
    players: OrderingPlayers,
    viewpoint_player: str,
    opposing_player: str,
    payoff: Callable[[tuple[tuple[str, str], ...]], float],
    precedences: Iterable[tuple[str, str]] = (),
) -> SourceChoiceResult:
    """Evaluate each selected source without assigning source precedence.

    The first named player maximizes the caller's payoff, while the opposing
    player minimizes it. This assumes zero-sum preferences for these
    endpoints, with no probabilistic distribution over effect orders.

    If a source has no applicable authority claim or lacks required context,
    its entry remains unresolved. The interval summarizes only resolved
    sources; it is not a confidence interval or win-rate estimate.
    """
    if not viewpoint_player or not opposing_player or viewpoint_player == opposing_player:
        raise ValueError("provide two distinct non-empty players")

    sources = tuple(source_ids)
    if len(set(sources)) != len(sources):
        raise ValueError("source IDs must be unique")
    if not sources:
        raise ValueError("at least one rules source required")

    outcomes = factorized_ko_order_outcomes(programs, precedences=precedences)
    scored = tuple((outcome, float(payoff(outcome.destinations))) for outcome in outcomes)
    if any(not isfinite(value) for _outcome, value in scored):
        raise ValueError("payoff must be a finite number")

    choices: list[SourceChoice] = []
    utilities: list[float] = []
    for source_id in sources:
        assessment = assess_concrete_ordering_player(context, (source_id,), players)
        if assessment.status != ConcreteChooserStatus.RESOLVED:
            choices.append(
                SourceChoice(source_id, assessment.status, None, None, (), None)
            )
            continue

        chooser = assessment.chooser
        if chooser not in {viewpoint_player, opposing_player}:
            raise ValueError(
                f"source {source_id!r} chooses unknown player {chooser!r}"
            )
        score = (
            max(value for _outcome, value in scored)
            if chooser == viewpoint_player
            else min(value for _outcome, value in scored)
        )
        optimal_outcomes = tuple(sorted(
            (outcome for outcome, value in scored if value == score),
            key=lambda row: (row.witness_order, row.destinations),
        ))
        optimal = optimal_outcomes[0]
        choices.append(
            SourceChoice(
                source_id, ConcreteChooserStatus.RESOLVED,
                chooser, optimal, optimal_outcomes, score
            )
        )
        utilities.append(score)

    union = {
        outcome.destinations: outcome
        for choice in choices
        for outcome in choice.optimal_outcomes
    }
    return SourceChoiceResult(
        choices=tuple(choices),
        outcome_count=len(outcomes),
        payoff_envelope=(
            (min(utilities), max(utilities)) if utilities else None
        ),
        optimal_outcome_union=tuple(
            union[destinations] for destinations in sorted(union)
        ),
    )
