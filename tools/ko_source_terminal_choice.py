"""Exact source-conditioned KO decisions using convolved *terminal* state payoffs.

The chooser depends on the explicitly selected official source profile.
Optimization operates on conserved game states, avoiding combinatorial
duplication of routes among gameplay-equivalent card copies.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Callable, Iterable, Mapping

from ko_order_histogram_convolution import (
    ConvolvedKOState, KOConvolution, convolve_ko_terminal_states,
)
from ko_trigger_order_authority import OrderingContext
from simultaneous_knockout_conservation import PendingKnockOutBatch
from source_order_chooser import (
    ConcreteChooserStatus, OrderingPlayers, assess_concrete_ordering_player,
)
from stack_knockout_conservation import StackBoardMaterialState


@dataclass(frozen=True)
class SourceTerminalChoice:
    source_id: str
    authority_status: ConcreteChooserStatus
    chooser: str | None
    selected: ConvolvedKOState | None
    optimal: tuple[ConvolvedKOState, ...]
    payoff: float | None


@dataclass(frozen=True)
class SourceTerminalChoices:
    source_choices: tuple[SourceTerminalChoice, ...]
    convolution: KOConvolution
    payoff_envelope: tuple[float, float] | None

    @property
    def value_invariant(self) -> bool:
        return (
            self.payoff_envelope is not None
            and self.payoff_envelope[0] == self.payoff_envelope[1]
        )

    @property
    def terminal_state_invariant(self) -> bool:
        states = {
            item.state
            for choice in self.source_choices for item in choice.optimal
        }
        return len(states) == 1 and bool(states)


def choose_ko_terminal_by_source(
    pending: PendingKnockOutBatch,
    programs: Mapping[str, Mapping[str, str]],
    *,
    context: OrderingContext,
    source_ids: Iterable[str],
    players: OrderingPlayers,
    viewpoint_player: str,
    opposing_player: str,
    payoff: Callable[[StackBoardMaterialState], float],
    promote_id: str | None = None,
    precedences: Iterable[tuple[str, str]] = (),
) -> SourceTerminalChoices:
    """Resolve source-specific zero-sum choices over full conserved states.

    The viewpoint maximizes, and its opposing player minimizes. Source
    authority is not combined or silently reconciled. Order multiplicities
    represent exact labeled order counts, never player-choice probabilities.
    """
    if (
        not viewpoint_player
        or not opposing_player
        or viewpoint_player == opposing_player
    ):
        raise ValueError("two distinct nonempty player IDs required")
    sources = tuple(source_ids)
    if not sources or len(sources) != len(set(sources)):
        raise ValueError("unique nonempty rules-source list required")

    convolution = convolve_ko_terminal_states(
        pending, programs, promote_id=promote_id,
        precedences=precedences,
    )
    scored = tuple(
        (endpoint, float(payoff(endpoint.state)))
        for endpoint in convolution.outcomes
    )
    if any(not isfinite(value) for _state, value in scored):
        raise ValueError("nonfinite terminal-state payoff")

    choices: list[SourceTerminalChoice] = []
    accepted_values: list[float] = []
    for source_id in sources:
        assessment = assess_concrete_ordering_player(
            context, (source_id,), players,
        )
        if assessment.status != ConcreteChooserStatus.RESOLVED:
            choices.append(SourceTerminalChoice(
                source_id, assessment.status, None, None, (), None,
            ))
            continue

        chooser = assessment.chooser
        if chooser not in (viewpoint_player, opposing_player):
            raise ValueError(
                f"source {source_id!r} authorizes unrelated player {chooser!r}"
            )
        value = (
            max(score for _outcome, score in scored)
            if chooser == viewpoint_player
            else min(score for _outcome, score in scored)
        )
        optimal = tuple(
            row for row, score in scored if score == value
        )
        selected = min(
            optimal, key=lambda row: (row.witness_order, row.signature)
        )
        choices.append(SourceTerminalChoice(
            source_id, ConcreteChooserStatus.RESOLVED,
            chooser, selected, optimal, value,
        ))
        accepted_values.append(value)

    return SourceTerminalChoices(
        source_choices=tuple(choices),
        convolution=convolution,
        payoff_envelope=(
            (min(accepted_values), max(accepted_values))
            if accepted_values else None
        ),
    )
