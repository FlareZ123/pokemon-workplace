"""Exact KO endpoint counts via convolution of independent local zone histograms.

Unlike instance-route Cartesian expansion, this dynamic program groups
exchangeable terminal states after *each* independent conflict component.
Every returned state is verified by one full conserved physical disposal.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from math import factorial
from typing import Iterable, Mapping

from ko_order_component_factorization import (
    effect_dependency_components, lexicographic_interleaving,
)
from ko_order_outcome_space import ko_order_outcomes
from ko_order_zone_signature import terminal_zone_signature
from knockout_redirection_ordering import resolve_ordered_programs, resolved_route_map
from knockout_zone_routing import discard_pending_with_zone_routes
from simultaneous_knockout_conservation import PendingKnockOutBatch
from stack_knockout_conservation import StackBoardMaterialState

Signature = tuple[tuple[str, str, int], ...]


@dataclass(frozen=True)
class ConvolvedKOState:
    signature: Signature
    order_count: int
    witness_order: tuple[str, ...]
    state: StackBoardMaterialState


@dataclass(frozen=True)
class KOConvolution:
    outcomes: tuple[ConvolvedKOState, ...]
    component_count: int
    local_route_outcomes_checked: int
    full_disposals: int
    candidate_total_orders: int


def _signature(counts: Counter[tuple[str, str]]) -> Signature:
    return tuple(sorted(
        (card_class, zone, amount)
        for (card_class, zone), amount in counts.items()
        if amount
    ))


def _add(left: Signature, right: Signature) -> Signature:
    counts: Counter[tuple[str, str]] = Counter()
    for card_class, zone, amount in left + right:
        counts[(card_class, zone)] += amount
    return _signature(counts)


def convolve_ko_terminal_states(
    pending: PendingKnockOutBatch,
    programs: Mapping[str, Mapping[str, str]],
    *,
    promote_id: str | None = None,
    precedences: Iterable[tuple[str, str]] = (),
) -> KOConvolution:
    """Produce exact full terminal states without global instance-route expansion.

    Applicable only to a fixed pending KO batch, fixed promotion and static
    first-explicit-assignment destination programs. All precedence constraints
    and real effect eligibility must be established by the caller.
    """
    precedence = tuple(precedences)
    components = effect_dependency_components(
        programs, precedences=precedence,
    )
    group_of = {
        effect: i
        for i, component in enumerate(components)
        for effect in component
    }

    representative_routes: dict[str, str] = {}
    writers: dict[str, set[int]] = defaultdict(set)
    for effect, assignments in programs.items():
        for instance, zone in assignments.items():
            representative_routes.setdefault(instance, zone)
            writers[instance].add(group_of[effect])
    # Physical input validation is performed before any shortcut can apply.
    terminal_zone_signature(pending, destinations=representative_routes)

    board = pending.state.board
    assert board is not None
    removed = tuple(
        card.card_id
        for pokemon in board.pokemon
        if pokemon.pokemon_id in pending.knocked_out_ids
        for card in pokemon.stack + pokemon.attachments
    )
    base = Counter(
        (
            pending.state.ledger.instance(instance).card_class,
            representative_routes[instance]
            if len(writers[instance]) > 1 else "discard",
        )
        for instance in removed
        if len(writers[instance]) != 1
    )

    states: dict[Signature, tuple[int, tuple[str, ...]]] = {
        _signature(base): (1, ())
    }
    checked = 0
    for i, component in enumerate(components):
        local = ko_order_outcomes(
            {effect: programs[effect] for effect in component},
            precedences=tuple(
                (a, b) for a, b in precedence
                if group_of[a] == i
            ),
        )
        checked += len(local)
        exclusive = {
            instance for instance, groups in writers.items()
            if groups == {i}
        }
        local_groups: dict[Signature, tuple[int, tuple[str, ...]]] = {}
        for outcome in local:
            counts = Counter(
                (pending.state.ledger.instance(instance).card_class, zone)
                for instance, zone in outcome.destinations
                if instance in exclusive
            )
            key = _signature(counts)
            previous = local_groups.get(key)
            if previous is None:
                local_groups[key] = (outcome.order_count, outcome.witness_order)
            else:
                local_groups[key] = (
                    previous[0] + outcome.order_count,
                    min(previous[1], outcome.witness_order),
                )

        updated: dict[Signature, tuple[int, tuple[str, ...]]] = {}
        for prior_signature, (prior_count, prior_witness) in states.items():
            for current_signature, (count, witness) in local_groups.items():
                key = _add(prior_signature, current_signature)
                merged = lexicographic_interleaving(
                    (prior_witness, witness)
                )
                previous = updated.get(key)
                if previous is None:
                    updated[key] = (prior_count * count, merged)
                else:
                    updated[key] = (
                        previous[0] + prior_count * count,
                        min(previous[1], merged),
                    )
        states = updated

    interleavings = factorial(len(programs))
    for component in components:
        interleavings //= factorial(len(component))

    outcomes = []
    for signature, (partial_count, witness) in sorted(states.items()):
        resolved = resolve_ordered_programs(programs, witness)
        assert resolved is not None
        destinations = resolved_route_map(resolved)
        if terminal_zone_signature(
            pending, destinations=destinations
        ) != signature:
            raise AssertionError("local histogram composition lost a destination")
        state = discard_pending_with_zone_routes(
            pending, promote_id=promote_id, destinations=destinations
        )
        if state is None:
            raise ValueError("KO route or promotion cannot be executed")
        outcomes.append(ConvolvedKOState(
            signature=signature,
            order_count=partial_count * interleavings,
            witness_order=witness,
            state=state,
        ))

    return KOConvolution(
        outcomes=tuple(outcomes),
        component_count=len(components),
        local_route_outcomes_checked=checked,
        full_disposals=len(outcomes),
        candidate_total_orders=sum(row.order_count for row in outcomes),
    )
