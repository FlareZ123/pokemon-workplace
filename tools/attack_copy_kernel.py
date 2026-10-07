"""Minimal nested attack-copy resolution kernel for paper Expanded research.

The kernel separates the declared attack identity from copied attack bodies. It
is intentionally small and models only the state channels needed to test copy
semantics, edge-local restrictions, perspective, global GX use, and no-progress
recursion hazards.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Callable, Iterable


@dataclass(frozen=True)
class PokemonRef:
    card_id: str
    name: str
    owner: str
    zone: str
    types: tuple[str, ...] = ()
    subtypes: tuple[str, ...] = ()
    attacks: tuple[str, ...] = ()


@dataclass(frozen=True)
class CopySelector:
    source: str
    require_non_gx: bool = False
    required_type: str | None = None
    required_subtype: str | None = None


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


@dataclass(frozen=True)
class State:
    pokemon: tuple[PokemonRef, ...]
    gx_used_by: frozenset[str] = frozenset()
    last_declared_attack: tuple[tuple[str, str], ...] = ()
    progress: int = 0
    events: tuple[str, ...] = ()

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


ChoicePolicy = Callable[[AttackDef, tuple[str, ...], State], str]


def opponent_of(player: str) -> str:
    if player == "P1":
        return "P2"
    if player == "P2":
        return "P1"
    raise ValueError(f"Unsupported player: {player}")


def _candidate_attacks(
    *,
    actor_player: str,
    attack: AttackDef,
    attacks: dict[str, AttackDef],
    state: State,
) -> tuple[str, ...]:
    selector = attack.copy_selector
    if selector is None:
        return ()

    candidates: list[str] = []
    if selector.source == "opponent_last_attack":
        attack_id = state.last_attack_for(opponent_of(actor_player))
        if attack_id is not None:
            candidates.append(attack_id)
    else:
        if selector.source == "own_discard":
            cards = [p for p in state.pokemon if p.owner == actor_player and p.zone == "discard"]
        elif selector.source == "own_bench":
            cards = [p for p in state.pokemon if p.owner == actor_player and p.zone == "bench"]
        elif selector.source == "opponent_active":
            opponent = opponent_of(actor_player)
            cards = [p for p in state.pokemon if p.owner == opponent and p.zone == "active"]
        elif selector.source == "opponent_in_play":
            opponent = opponent_of(actor_player)
            cards = [p for p in state.pokemon if p.owner == opponent and p.zone in {"active", "bench"}]
        elif selector.source == "opponent_revealed":
            opponent = opponent_of(actor_player)
            cards = [p for p in state.pokemon if p.owner == opponent and p.zone == "revealed"]
        else:
            raise ValueError(f"Unsupported copy source: {selector.source}")

        for card in cards:
            if selector.required_type is not None and selector.required_type not in card.types:
                continue
            if selector.required_subtype is not None and selector.required_subtype not in card.subtypes:
                continue
            candidates.extend(card.attacks)

    filtered = []
    for attack_id in candidates:
        candidate = attacks[attack_id]
        if selector.require_non_gx and candidate.is_gx:
            continue
        filtered.append(attack_id)
    return tuple(filtered)


def resolve_attack(
    *,
    actor_player: str,
    actor_card_id: str,
    declared_attack_id: str,
    attacks: dict[str, AttackDef],
    state: State,
    choose: ChoicePolicy,
    max_depth: int = 32,
) -> Resolution:
    if declared_attack_id not in attacks:
        raise KeyError(declared_attack_id)

    trace: list[TraceStep] = []
    body_chain: list[str] = []
    seen: set[tuple[str, str, int, frozenset[str]]] = set()

    def execute(body_attack_id: str, current: State, depth: int) -> State:
        if depth > max_depth:
            raise CopyCycleError(f"copy depth exceeded {max_depth}")

        body = attacks[body_attack_id]
        cycle_key = (actor_card_id, body_attack_id, current.progress, current.gx_used_by)
        if cycle_key in seen:
            raise CopyCycleError(
                f"no-progress copy cycle at {body_attack_id} with progress={current.progress}"
            )
        seen.add(cycle_key)

        if body.is_gx:
            if actor_player in current.gx_used_by:
                raise GXAlreadyUsed(f"{actor_player} has already used a GX attack")
            current = replace(current, gx_used_by=current.gx_used_by | {actor_player})

        if body.progress_delta:
            current = replace(current, progress=current.progress + body.progress_delta)
        if body.pre_event is not None:
            current = replace(current, events=current.events + (body.pre_event,))

        body_chain.append(body_attack_id)
        candidates = _candidate_attacks(
            actor_player=actor_player,
            attack=body,
            attacks=attacks,
            state=current,
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
                )
            )
            return current

        if not candidates:
            raise IllegalCopyTarget(f"no legal copy targets for {body_attack_id}")

        selected = choose(body, candidates, current)
        if selected not in candidates:
            raise IllegalCopyTarget(
                f"choice {selected!r} is not legal for {body_attack_id}; candidates={candidates!r}"
            )

        trace.append(
            TraceStep(
                depth=depth,
                declared_attack_id=declared_attack_id,
                body_attack_id=body_attack_id,
                body_attack_name=body.name,
                selected_attack_id=selected,
                progress=current.progress,
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


def choose_exact(sequence: Iterable[str]) -> ChoicePolicy:
    remaining = iter(sequence)

    def choose(_attack: AttackDef, candidates: tuple[str, ...], _state: State) -> str:
        selected = next(remaining)
        if selected not in candidates:
            raise IllegalCopyTarget(f"expected {selected!r}; candidates={candidates!r}")
        return selected

    return choose
