"""Minimal nested attack-copy resolution kernel for paper Expanded research.

The kernel separates the declared attack identity from copied attack bodies. It
is intentionally small and models only the state channels needed to test copy
semantics, edge-local restrictions, perspective, global GX use, and no-progress
recursion hazards.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Callable, Iterable

from energy_action_budget import (
    EnergyRouteProfile,
    EnergyRouteType,
    evaluate_energy_routes,
    unit,
)


@dataclass(frozen=True)
class PokemonRef:
    card_id: str
    name: str
    owner: str
    zone: str
    types: tuple[str, ...] = ()
    subtypes: tuple[str, ...] = ()
    attacks: tuple[str, ...] = ()
    has_rule_box: bool = False
    attached_energy_units: tuple[frozenset[str], ...] = ()
    previous_evolution_attacks: tuple[str, ...] = ()


@dataclass(frozen=True)
class CopySelector:
    source: str
    require_non_gx: bool = False
    required_type: str | None = None
    required_subtype: str | None = None
    require_no_rule_box: bool = False
    move_selected_source_to: str | None = None
    require_selected_energy: bool = False
    required_name_prefix: str | None = None
    chooser: str = "actor"
    optional_selection: bool = False
    precommit_source_to: str | None = None

    def __post_init__(self) -> None:
        if self.chooser not in {"actor", "opponent"}:
            raise ValueError("copy chooser must be 'actor' or 'opponent'")


@dataclass(frozen=True)
class TurnBoundaryEffect:
    take_another_turn: bool = False
    skip_pokemon_checkup: bool = False

    def __post_init__(self) -> None:
        if self.skip_pokemon_checkup and not self.take_another_turn:
            raise ValueError("checkup skip requires an extra-turn effect")


@dataclass(frozen=True)
class AttackDef:
    attack_id: str
    name: str
    is_gx: bool = False
    copy_selector: CopySelector | None = None
    effect_label: str | None = None
    pre_event: str | None = None
    post_event: str | None = None
    progress_delta: int = 0
    turn_boundary_effect: TurnBoundaryEffect | None = None
    energy_cost: tuple[str, ...] = ()


@dataclass(frozen=True)
class State:
    pokemon: tuple[PokemonRef, ...]
    gx_used_by: frozenset[str] = frozenset()
    last_declared_attack: tuple[tuple[str, str], ...] = ()
    progress: int = 0
    events: tuple[str, ...] = ()
    pending_turn_boundary: TurnBoundaryEffect | None = None

    def last_attack_for(self, player: str) -> str | None:
        return dict(self.last_declared_attack).get(player)

    def with_last_attack(self, player: str, attack_id: str) -> "State":
        values = dict(self.last_declared_attack)
        values[player] = attack_id
        return replace(self, last_declared_attack=tuple(sorted(values.items())))


@dataclass(frozen=True)
class TraceStep:
    depth: int
    declared_attack_id: str
    body_attack_id: str
    body_attack_name: str
    selected_attack_id: str | None
    progress: int
    selected_body_executed: bool | None = None
    body_execution_gate_passed: bool | None = None


@dataclass(frozen=True)
class Resolution:
    state: State
    declared_attack_id: str
    body_chain: tuple[str, ...]
    trace: tuple[TraceStep, ...]


class CopyResolutionError(RuntimeError):
    pass


class IllegalCopyTarget(CopyResolutionError):
    pass


class GXAlreadyUsed(CopyResolutionError):
    pass


class CopyCycleError(CopyResolutionError):
    pass


class ConflictingTurnBoundaryEffect(CopyResolutionError):
    pass


class AmbiguousCopySource(CopyResolutionError):
    pass


class MissingCopyChooser(CopyResolutionError):
    pass


ChoicePolicy = Callable[[AttackDef, tuple[str, ...], State], str | None]
SourceChoicePolicy = Callable[
    [AttackDef, str, tuple[str, ...], State],
    str,
]
CopiedBodyGatePolicy = Callable[[AttackDef, State], bool]


def opponent_of(player: str) -> str:
    if player == "P1":
        return "P2"
    if player == "P2":
        return "P1"
    raise ValueError(f"Unsupported player: {player}")


def _candidate_attacks(
    *,
    actor_player: str,
    actor_card_id: str,
    attack: AttackDef,
    attacks: dict[str, AttackDef],
    state: State,
    source_override: tuple[PokemonRef, ...] | None = None,
) -> tuple[tuple[str, ...], dict[str, tuple[str, ...]]]:
    selector = attack.copy_selector
    if selector is None:
        return (), {}

    candidates: list[str] = []
    sources: dict[str, list[str]] = {}
    if selector.source == "opponent_last_attack":
        attack_id = state.last_attack_for(opponent_of(actor_player))
        if attack_id is not None:
            candidates.append(attack_id)
    else:
        if source_override is not None:
            cards = list(source_override)
        elif selector.source == "self_previous_evolution":
            actor = next(
                (card for card in state.pokemon if card.card_id == actor_card_id),
                None,
            )
            cards = []
            if actor is not None:
                candidates.extend(actor.previous_evolution_attacks)
        elif selector.source == "own_discard":
            cards = [p for p in state.pokemon if p.owner == actor_player and p.zone == "discard"]
        elif selector.source == "own_bench":
            cards = [p for p in state.pokemon if p.owner == actor_player and p.zone == "bench"]
        elif selector.source == "own_deck_top":
            cards = [p for p in state.pokemon if p.owner == actor_player and p.zone == "deck_top"]
        elif selector.source == "opponent_active":
            opponent = opponent_of(actor_player)
            cards = [p for p in state.pokemon if p.owner == opponent and p.zone == "active"]
        elif selector.source == "opponent_in_play":
            opponent = opponent_of(actor_player)
            cards = [p for p in state.pokemon if p.owner == opponent and p.zone in {"active", "bench"}]
        elif selector.source == "opponent_revealed":
            opponent = opponent_of(actor_player)
            cards = [p for p in state.pokemon if p.owner == opponent and p.zone == "revealed"]
        elif selector.source == "opponent_hand":
            opponent = opponent_of(actor_player)
            cards = [p for p in state.pokemon if p.owner == opponent and p.zone == "hand"]
        else:
            raise ValueError(f"Unsupported copy source: {selector.source}")

        for card in cards:
            if selector.required_type is not None and selector.required_type not in card.types:
                continue
            if selector.required_subtype is not None and selector.required_subtype not in card.subtypes:
                continue
            if selector.require_no_rule_box and card.has_rule_box:
                continue
            if (
                selector.required_name_prefix is not None
                and not card.name.startswith(selector.required_name_prefix)
            ):
                continue
            for attack_id in card.attacks:
                candidate = attacks[attack_id]
                if selector.require_non_gx and candidate.is_gx:
                    continue
                candidates.append(attack_id)
                sources.setdefault(attack_id, []).append(card.card_id)

    if selector.source == "opponent_last_attack":
        filtered = []
        for attack_id in candidates:
            candidate = attacks[attack_id]
            if selector.require_non_gx and candidate.is_gx:
                continue
            filtered.append(attack_id)
        candidates = filtered

    return tuple(candidates), {
        attack_id: tuple(source_ids)
        for attack_id, source_ids in sources.items()
    }



def _selected_attack_energy_ready(
    *,
    actor_card_id: str,
    selected_attack: AttackDef,
    state: State,
) -> bool:
    if not selected_attack.energy_cost:
        return True

    actor = next(
        (card for card in state.pokemon if card.card_id == actor_card_id),
        None,
    )
    if actor is None or not actor.attached_energy_units:
        return False

    route = EnergyRouteType(
        "attached Energy on copying Pokémon",
        1,
        (
            EnergyRouteProfile(
                units=tuple(
                    unit(*sorted(types))
                    for types in actor.attached_energy_units
                ),
            ),
        ),
    )
    return evaluate_energy_routes(
        selected_attack.energy_cost,
        {},
        set(),
        (route,),
    ).exact_feasible

def resolve_attack(
    *,
    actor_player: str,
    actor_card_id: str,
    declared_attack_id: str,
    attacks: dict[str, AttackDef],
    state: State,
    choose: ChoicePolicy,
    choose_opponent: ChoicePolicy | None = None,
    choose_source: SourceChoicePolicy | None = None,
    copied_body_gate: CopiedBodyGatePolicy | None = None,
    max_depth: int = 32,
) -> Resolution:
    if declared_attack_id not in attacks:
        raise KeyError(declared_attack_id)

    trace: list[TraceStep] = []
    body_chain: list[str] = []
    gx_used_before_resolution = actor_player in state.gx_used_by
    seen: set[
        tuple[
            str,
            str,
            int,
            frozenset[str],
            TurnBoundaryEffect | None,
            tuple[tuple[str, str], ...],
        ]
    ] = set()

    def execute(body_attack_id: str, current: State, depth: int) -> State:
        if depth > max_depth:
            raise CopyCycleError(f"copy depth exceeded {max_depth}")

        body = attacks[body_attack_id]
        if (
            depth > 0
            and copied_body_gate is not None
            and not copied_body_gate(body, current)
        ):
            body_chain.append(body_attack_id)
            trace.append(
                TraceStep(
                    depth=depth,
                    declared_attack_id=declared_attack_id,
                    body_attack_id=body_attack_id,
                    body_attack_name=body.name,
                    selected_attack_id=None,
                    progress=current.progress,
                    selected_body_executed=False,
                    body_execution_gate_passed=False,
                )
            )
            return current

        cycle_key = (
            actor_card_id,
            body_attack_id,
            current.progress,
            current.gx_used_by,
            current.pending_turn_boundary,
            tuple(sorted((card.card_id, card.zone) for card in current.pokemon)),
        )
        if cycle_key in seen:
            raise CopyCycleError(
                f"no-progress copy cycle at {body_attack_id} with progress={current.progress}"
            )
        seen.add(cycle_key)

        if body.is_gx:
            if gx_used_before_resolution:
                raise GXAlreadyUsed(f"{actor_player} has already used a GX attack")
            current = replace(
                current,
                gx_used_by=current.gx_used_by | {actor_player},
            )

        if body.turn_boundary_effect is not None:
            if (
                current.pending_turn_boundary is not None
                and current.pending_turn_boundary != body.turn_boundary_effect
            ):
                raise ConflictingTurnBoundaryEffect(
                    "conflicting pending turn-boundary effects"
                )
            current = replace(
                current,
                pending_turn_boundary=body.turn_boundary_effect,
            )

        if body.progress_delta:
            current = replace(current, progress=current.progress + body.progress_delta)
        if body.pre_event is not None:
            current = replace(current, events=current.events + (body.pre_event,))

        body_chain.append(body_attack_id)

        selector = body.copy_selector
        source_override: tuple[PokemonRef, ...] | None = None
        if selector is not None and selector.precommit_source_to is not None:
            if selector.source != "own_deck_top":
                raise ValueError(
                    "precommit source movement is currently supported only for own_deck_top"
                )
            source_override = tuple(
                card
                for card in current.pokemon
                if card.owner == actor_player and card.zone == "deck_top"
            )
            if len(source_override) > 1:
                raise ValueError("modeled deck_top must identify at most one card")
            source_ids = {card.card_id for card in source_override}
            current = replace(
                current,
                pokemon=tuple(
                    replace(card, zone=selector.precommit_source_to)
                    if card.card_id in source_ids
                    else card
                    for card in current.pokemon
                ),
            )

        candidates, candidate_sources = _candidate_attacks(
            actor_player=actor_player,
            actor_card_id=actor_card_id,
            attack=body,
            attacks=attacks,
            state=current,
            source_override=source_override,
        )

        if body.copy_selector is None:
            if body.effect_label is not None:
                current = replace(current, events=current.events + (body.effect_label,))
            if body.post_event is not None:
                current = replace(current, events=current.events + (body.post_event,))
            trace.append(
                TraceStep(
                    depth=depth,
                    declared_attack_id=declared_attack_id,
                    body_attack_id=body_attack_id,
                    body_attack_name=body.name,
                    selected_attack_id=None,
                    progress=current.progress,
                    selected_body_executed=None,
                )
            )
            return current

        selector = body.copy_selector
        assert selector is not None

        if not candidates:
            trace.append(
                TraceStep(
                    depth=depth,
                    declared_attack_id=declared_attack_id,
                    body_attack_id=body_attack_id,
                    body_attack_name=body.name,
                    selected_attack_id=None,
                    progress=current.progress,
                    selected_body_executed=False,
                )
            )
            if body.post_event is not None:
                current = replace(
                    current,
                    events=current.events + (body.post_event,),
                )
            return current

        if selector.chooser == "actor":
            choose_attack = choose
        else:
            if choose_opponent is None:
                raise MissingCopyChooser(
                    f"{body_attack_id} requires an opponent choice policy"
                )
            choose_attack = choose_opponent

        selected = choose_attack(body, candidates, current)
        if selected is None:
            if not selector.optional_selection:
                raise IllegalCopyTarget(
                    f"{body_attack_id} requires a selected attack"
                )
            trace.append(
                TraceStep(
                    depth=depth,
                    declared_attack_id=declared_attack_id,
                    body_attack_id=body_attack_id,
                    body_attack_name=body.name,
                    selected_attack_id=None,
                    progress=current.progress,
                    selected_body_executed=False,
                )
            )
            if body.post_event is not None:
                current = replace(
                    current,
                    events=current.events + (body.post_event,),
                )
            return current
        if selected not in candidates:
            raise IllegalCopyTarget(
                f"choice {selected!r} is not legal for {body_attack_id}; candidates={candidates!r}"
            )

        if (
            selector is not None
            and selector.require_selected_energy
            and not _selected_attack_energy_ready(
                actor_card_id=actor_card_id,
                selected_attack=attacks[selected],
                state=current,
            )
        ):
            trace.append(
                TraceStep(
                    depth=depth,
                    declared_attack_id=declared_attack_id,
                    body_attack_id=body_attack_id,
                    body_attack_name=body.name,
                    selected_attack_id=selected,
                    progress=current.progress,
                    selected_body_executed=False,
                )
            )
            if body.post_event is not None:
                current = replace(
                    current,
                    events=current.events + (body.post_event,),
                )
            return current

        if selector is not None and selector.move_selected_source_to is not None:
            source_ids = candidate_sources.get(selected, ())
            if not source_ids:
                raise IllegalCopyTarget(
                    f"copy source for {selected!r} cannot be materialized"
                )
            if len(source_ids) == 1:
                selected_source = source_ids[0]
            else:
                if choose_source is None:
                    raise AmbiguousCopySource(
                        f"multiple physical sources supply {selected!r}: {source_ids!r}"
                    )
                selected_source = choose_source(
                    body,
                    selected,
                    source_ids,
                    current,
                )
                if selected_source not in source_ids:
                    raise IllegalCopyTarget(
                        f"source choice {selected_source!r} is not legal; sources={source_ids!r}"
                    )
            current = replace(
                current,
                pokemon=tuple(
                    replace(card, zone=selector.move_selected_source_to)
                    if card.card_id == selected_source
                    else card
                    for card in current.pokemon
                ),
            )

        trace.append(
            TraceStep(
                depth=depth,
                declared_attack_id=declared_attack_id,
                body_attack_id=body_attack_id,
                body_attack_name=body.name,
                selected_attack_id=selected,
                progress=current.progress,
                selected_body_executed=True,
            )
        )
        current = execute(selected, current, depth + 1)
        if body.post_event is not None:
            current = replace(current, events=current.events + (body.post_event,))
        return current

    next_state = execute(declared_attack_id, state, 0)
    next_state = next_state.with_last_attack(actor_player, declared_attack_id)
    return Resolution(
        state=next_state,
        declared_attack_id=declared_attack_id,
        body_chain=tuple(body_chain),
        trace=tuple(trace),
    )


def choose_exact(sequence: Iterable[str | None]) -> ChoicePolicy:
    remaining = iter(sequence)

    def choose(_attack: AttackDef, candidates: tuple[str, ...], _state: State) -> str:
        selected = next(remaining)
        if selected is not None and selected not in candidates:
            raise IllegalCopyTarget(f"expected {selected!r}; candidates={candidates!r}")
        return selected

    return choose


def choose_source_exact(sequence: Iterable[str]) -> SourceChoicePolicy:
    remaining = iter(sequence)

    def choose_source(
        _attack: AttackDef,
        _selected_attack_id: str,
        source_ids: tuple[str, ...],
        _state: State,
    ) -> str:
        selected_source = next(remaining)
        if selected_source not in source_ids:
            raise IllegalCopyTarget(
                f"expected source {selected_source!r}; sources={source_ids!r}"
            )
        return selected_source

    return choose_source
