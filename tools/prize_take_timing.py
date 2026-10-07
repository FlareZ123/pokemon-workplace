"""Before-hand Prize timing built on conserved Prize-taking belief updates."""

from __future__ import annotations

from dataclasses import dataclass, replace

from board_position_state import (
    BoardPokemon,
    BoardState,
    PokemonCard,
    validate_state,
)
from identity_materialization import (
    IdentityLedger,
    assert_conserved,
    dematerialize,
    materialize,
    move_instance,
    put_in_play_instance,
    validate_board_position_stack_bindings,
)
from prize_belief_kernel import PrizeBelief
from prize_take_conservation import (
    observation_probability,
    take_observed_random_prize,
)

PRIZE = "prize"
PENDING = "prize_pending"
HAND = "hand"


@dataclass(frozen=True)
class PrizeTruthBeliefState:
    ledger: IdentityLedger
    belief: PrizeBelief
    group_by_card_class: tuple[tuple[str, str | None], ...]

    def __post_init__(self) -> None:
        keys = [card_class for card_class, _group in self.group_by_card_class]
        if len(keys) != len(set(keys)):
            raise ValueError("card-class belief-group mappings must be unique")
        if self.group_by_card_class != tuple(
            sorted(self.group_by_card_class, key=lambda row: row[0])
        ):
            raise ValueError("card-class belief-group mappings must be sorted")
        mapping = dict(self.group_by_card_class)
        if any(
            group is not None and group not in self.belief.groups
            for group in mapping.values()
        ):
            raise ValueError("mapped groups must occur in the Prize belief")

        prize_rows: list[str] = []
        for card_class, zone, count in self.ledger.exchangeable.counts:
            if zone == PRIZE:
                prize_rows.extend([card_class] * count)
        for row in self.ledger.instances:
            if row.zone == PRIZE:
                prize_rows.append(row.card_class)

        if len(prize_rows) != self.belief.prize_count:
            raise ValueError(
                "physical Prize count must match belief.prize_count"
            )

        actual = [0] * len(self.belief.groups)
        for card_class in prize_rows:
            if card_class not in mapping:
                raise ValueError(
                    f"missing Prize-belief group mapping for {card_class!r}"
                )
            group = mapping[card_class]
            if group is not None:
                actual[self.belief.groups.index(group)] += 1
        actual_state = tuple(actual)
        if not any(
            belief_state == actual_state and mass > 0.0
            for belief_state, mass in self.belief.masses
        ):
            raise ValueError(
                "physical Prize composition has zero probability under the belief"
            )


@dataclass(frozen=True)
class PrizeTakeEvent:
    instance_id: str
    card_class: str
    card_name: str
    observed_group: str | None
    observation_probability: float


@dataclass(frozen=True)
class PrizeTakeStart:
    state: PrizeTruthBeliefState
    event: PrizeTakeEvent


@dataclass(frozen=True)
class PrizeTimingBoardState:
    prize_state: PrizeTruthBeliefState
    board: BoardState

    def __post_init__(self) -> None:
        validate_state(self.board)
        validate_board_position_stack_bindings(
            self.prize_state.ledger,
            self.board,
        )


def begin_face_down_prize_take(
    state: PrizeTruthBeliefState,
    *,
    card_class: str,
    card_name: str,
    observed_group: str | None,
    instance_id: str,
) -> PrizeTakeStart:
    """Remove/reveal one face-down Prize and keep its exact copy pending."""

    mapping = dict(state.group_by_card_class)
    if card_class not in mapping:
        raise ValueError("selected Prize class has no belief-group mapping")
    if mapping[card_class] != observed_group:
        raise ValueError(
            "observed group does not match the selected physical card class"
        )

    probability = observation_probability(state.belief, observed_group)
    if probability <= 0.0:
        raise ValueError("observation has zero probability under this belief")
    remaining_belief = take_observed_random_prize(
        state.belief,
        observed_group,
    )

    ledger = materialize(
        state.ledger,
        card_class=card_class,
        card_name=card_name,
        source_zone=PRIZE,
        instance_id=instance_id,
    )
    ledger = move_instance(ledger, instance_id, PENDING)
    next_state = PrizeTruthBeliefState(
        ledger,
        remaining_belief,
        state.group_by_card_class,
    )
    assert_conserved(state.ledger, next_state.ledger)
    return PrizeTakeStart(
        next_state,
        PrizeTakeEvent(
            instance_id=instance_id,
            card_class=card_class,
            card_name=card_name,
            observed_group=observed_group,
            observation_probability=probability,
        ),
    )


def complete_prize_take_to_hand(
    state: PrizeTruthBeliefState,
    instance_id: str,
) -> PrizeTruthBeliefState:
    """Finish an unresolved taken Prize through the ordinary hand destination."""

    current = state.ledger.instance(instance_id)
    if current.zone != PENDING:
        raise ValueError("Prize instance is not in the before-hand pending zone")
    ledger = move_instance(state.ledger, instance_id, HAND)
    ledger = dematerialize(ledger, instance_id)
    next_state = PrizeTruthBeliefState(
        ledger,
        state.belief,
        state.group_by_card_class,
    )
    assert_conserved(state.ledger, next_state.ledger)
    return next_state


def complete_prize_take_to_bench(
    state: PrizeTimingBoardState,
    *,
    instance_id: str,
    pokemon_id: str,
    retreat_cost: int,
) -> PrizeTimingBoardState | None:
    """Put a pending taken Basic Pokemon onto the Bench.

    Card-specific eligibility, such as a Lucky Bonus-style Ability, is an
    upstream semantic decision. This function enforces only physical identity
    and Bench-capacity mechanics.
    """

    current = state.prize_state.ledger.instance(instance_id)
    if current.zone != PENDING:
        return None
    board = state.board
    if len(board.bench_ids) >= board.bench_capacity:
        return None
    if any(pokemon.pokemon_id == pokemon_id for pokemon in board.pokemon):
        return None
    if retreat_cost < 0:
        raise ValueError("retreat_cost must be non-negative")

    ledger = put_in_play_instance(
        state.prize_state.ledger,
        instance_id,
        pokemon_id,
    )
    pokemon = BoardPokemon(
        pokemon_id,
        (PokemonCard(instance_id, current.card_name),),
        retreat_cost=retreat_cost,
    )
    next_board = replace(
        board,
        pokemon=board.pokemon + (pokemon,),
    )
    validate_state(next_board)

    next_prize_state = PrizeTruthBeliefState(
        ledger,
        state.prize_state.belief,
        state.prize_state.group_by_card_class,
    )
    assert_conserved(state.prize_state.ledger, next_prize_state.ledger)
    next_state = PrizeTimingBoardState(next_prize_state, next_board)
    return next_state
