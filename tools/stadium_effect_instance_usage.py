"""Per-in-play-instance usage for voluntary Stadium effects.

Brooklet Hill's official ruling shows that after one copy's once-per-turn effect
is used and that Stadium leaves play, a newly played copy with the same name has
a fresh effect-use window. Stadium play quota and Stadium effect-use history are
therefore separate state.
"""

from __future__ import annotations

from dataclasses import dataclass, replace

from turn_action_budget import TurnAction, TurnActionBudget


@dataclass(frozen=True)
class StadiumCard:
    copy_id: str
    name: str

    def __post_init__(self) -> None:
        if not self.copy_id or not self.name:
            raise ValueError("Stadium card identity must be non-empty")


@dataclass(frozen=True)
class StadiumInPlay:
    card: StadiumCard
    instance_id: str

    def __post_init__(self) -> None:
        if not self.instance_id:
            raise ValueError("in-play Stadium instance_id must be non-empty")


@dataclass(frozen=True)
class StadiumEffectState:
    budget: TurnActionBudget
    hand: tuple[StadiumCard, ...] = ()
    discard: tuple[StadiumCard, ...] = ()
    in_play: StadiumInPlay | None = None
    used_effect_instances: frozenset[str] = frozenset()

    def __post_init__(self) -> None:
        cards = list(self.hand) + list(self.discard)
        if self.in_play is not None:
            cards.append(self.in_play.card)
        ids = [card.copy_id for card in cards]
        if len(ids) != len(set(ids)):
            raise ValueError("a physical Stadium copy cannot occupy two zones")


def can_use_current_stadium_effect(state: StadiumEffectState) -> bool:
    return (
        not state.budget.turn_ended
        and state.in_play is not None
        and state.in_play.instance_id not in state.used_effect_instances
    )


def use_current_stadium_effect(
    state: StadiumEffectState,
) -> StadiumEffectState | None:
    """Mark the current in-play Stadium instance's voluntary effect as used."""

    if not can_use_current_stadium_effect(state):
        return None
    assert state.in_play is not None
    return replace(
        state,
        used_effect_instances=(
            state.used_effect_instances | {state.in_play.instance_id}
        ),
    )


def discard_current_stadium(
    state: StadiumEffectState,
) -> StadiumEffectState | None:
    """Discard the current Stadium through an external effect such as an Item."""

    if state.in_play is None or state.budget.turn_ended:
        return None
    return replace(
        state,
        discard=state.discard + (state.in_play.card,),
        in_play=None,
    )


def play_stadium_from_hand(
    state: StadiumEffectState,
    copy_id: str,
    *,
    instance_id: str,
) -> StadiumEffectState | None:
    """Play a Stadium from hand, creating a caller-supplied in-play instance."""

    if not instance_id or not state.budget.can(TurnAction.STADIUM_PLAY):
        return None

    selected = None
    remaining = []
    for card in state.hand:
        if card.copy_id == copy_id and selected is None:
            selected = card
        else:
            remaining.append(card)
    if selected is None:
        return None
    if state.in_play is not None and state.in_play.card.name == selected.name:
        return None
    if instance_id in state.used_effect_instances:
        return None

    budget = state.budget.consume(TurnAction.STADIUM_PLAY)
    if budget is None:
        return None

    discard = state.discard
    if state.in_play is not None:
        discard = discard + (state.in_play.card,)

    return replace(
        state,
        budget=budget,
        hand=tuple(remaining),
        discard=discard,
        in_play=StadiumInPlay(selected, instance_id),
    )


def begin_stadium_turn(
    state: StadiumEffectState,
    *,
    action_budget: TurnActionBudget | None = None,
) -> StadiumEffectState:
    """Enter a new actor turn, preserving the current in-play Stadium.

    A voluntary Stadium effect reading 'once during each player's turn'
    refreshes on a true turn boundary, including an extra turn for the
    same actor. This helper is explicitly called by a turn scheduler;
    it must not be used to refresh usage during an ongoing turn.

    The caller may supply the next actor's canonical action budget.
    """

    next_budget = action_budget if action_budget is not None else state.budget.next_turn()
    if next_budget.turn_ended:
        raise ValueError("a new actor turn requires an open action budget")
    return replace(
        state,
        budget=next_budget,
        used_effect_instances=frozenset(),
    )
