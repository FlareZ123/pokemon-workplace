"""Physical Ultra Ball discard payment can create a live Teleport Room payload.

Bounded, named-card island: one Sky Field copy in hand, one Ultra Ball,
two junk cards, one Basic in hand, and one Basic searchable from deck.
The canonical Trainer transaction owns the exact two-card discard and search.
This bridge reconciles those zone moves with the physical Stadium/Bench kernel.
"""
from __future__ import annotations

from dataclasses import dataclass, replace

from bench_teleport_capacity_bridge import BenchPokemon, BenchTeleportState
from discard_cost_witness import DiscardCandidate, DiscardSelection
from multicopy_zone_state import ZoneCountState
from raichu_search_to_crobat_execution import ULTRA_BALL_PROFILE
from search_zone_transition import SearchZoneTarget
from stadium_entry_channels import StadiumCopy
from trainer_search_transaction import (
    TrainerSearchExecutionState,
    TrainerSearchTransaction,
    execute_trainer_search_transaction,
)
from typed_search_target_allocator import (
    BASIC_POKEMON,
    TargetGroup,
    enumerate_typed_target_profiles,
    make_demand,
)


CANDIDATES = (
    DiscardCandidate("sky_field"),
    DiscardCandidate("junk_a"),
    DiscardCandidate("junk_b"),
)


@dataclass(frozen=True)
class PayloadTransaction:
    trainer: TrainerSearchTransaction
    board_after_search: BenchTeleportState

    @property
    def sky_discarded(self) -> bool:
        before = self.trainer.before.zones.count("sky_field", "discard")
        after = self.trainer.after.zones.count("sky_field", "discard")
        return after == before + 1


def assert_stadium_projection(
    board: BenchTeleportState, zones: ZoneCountState
) -> None:
    """Check exact physical Stadium class counts across coupled kernels."""
    for name, card_class in (
        ("Sky Field", "sky_field"),
        ("Collapsed Stadium", "collapsed_stadium"),
    ):
        for physical_zone, counted_zone in (
            ("hand", "hand"),
            ("discard", "discard"),
            ("in_play", "stadium_in_play"),
        ):
            if physical_zone == "in_play":
                actual = int(
                    board.stadiums.in_play is not None
                    and board.stadiums.in_play.name == name
                )
            else:
                actual = sum(
                    card.name == name
                    for card in getattr(board.stadiums, physical_zone)
                )
            if zones.count(card_class, counted_zone) != actual:
                raise ValueError(
                    f"Stadium projection mismatch: {card_class}/{counted_zone}"
                )


def _sky_hand_card(board: BenchTeleportState) -> StadiumCopy:
    cards = tuple(card for card in board.stadiums.hand if card.name == "Sky Field")
    if len(cards) != 1:
        raise ValueError("witness requires exactly one physical Sky Field in hand")
    return cards[0]


def execute_ultra_ball_for_entrant(
    board: BenchTeleportState,
    execution: TrainerSearchExecutionState,
    *,
    discard_selection: DiscardSelection,
) -> PayloadTransaction:
    """Search one Basic while preserving Sky Field's physical discard identity."""
    assert_stadium_projection(board, execution.zones)
    if board.stadiums.budget != execution.budget:
        raise ValueError("board and Trainer budgets must match")
    sky_card = _sky_hand_card(board)
    if execution.zones.count("sky_field", "hand") != 1:
        raise ValueError("Trainer and physical Sky Field hand count disagree")
    if execution.zones.count("searched_basic", "deck") != 1:
        raise ValueError("witness requires exactly one searchable Basic")

    target = SearchZoneTarget(
        "searched_basic",
        TargetGroup("Searched Basic", 1, frozenset({BASIC_POKEMON})),
    )
    demand = make_demand("searched Basic target", "Pokémon")
    allocation = enumerate_typed_target_profiles(
        ULTRA_BALL_PROFILE.base_outputs,
        (target.group,),
        (demand,),
    )
    search_action = next(
        row for row in allocation.actions
        if row.output == (1,) and row.target_cost == (1,)
    )
    txn = execute_trainer_search_transaction(
        execution,
        profile=ULTRA_BALL_PROFILE,
        action_card_class="ultra_ball",
        demands=(demand,),
        targets=(target,),
        search_action=search_action,
        discard_candidates=CANDIDATES,
        discard_selection=discard_selection,
    )
    if txn.discard_cost != 2:
        raise AssertionError("Ultra Ball must discard exactly two other cards")
    sky_delta = (
        txn.after.zones.count("sky_field", "discard")
        - txn.before.zones.count("sky_field", "discard")
    )
    if sky_delta not in (0, 1):
        raise AssertionError("nonphysical Sky Field discard delta")

    stadiums = board.stadiums
    if sky_delta:
        stadiums = replace(
            stadiums,
            hand=tuple(card for card in stadiums.hand if card.copy_id != sky_card.copy_id),
            discard=stadiums.discard + (sky_card,),
        )
    searched = BenchPokemon("searched_basic")
    if searched.copy_id in {mon.copy_id for mon in (board.active,) + board.bench + board.hand_pokemon}:
        raise ValueError("searched Basic already materialized on board")
    after_board = replace(
        board,
        stadiums=replace(stadiums, budget=txn.after.budget),
        hand_pokemon=board.hand_pokemon + (searched,),
    )
    assert_stadium_projection(after_board, txn.after.zones)
    return PayloadTransaction(txn, after_board)


def mirror_teleport_to_trainer_zones(
    previous: BenchTeleportState,
    following: BenchTeleportState,
    zones: ZoneCountState,
) -> ZoneCountState:
    """Mirror one successful physical Teleport transition into counted zones."""
    assert_stadium_projection(previous, zones)
    source = previous.stadiums.in_play
    target = following.stadiums.in_play
    if source is None:
        raise ValueError("Teleport source Stadium missing")
    out = zones.move("collapsed_stadium", "stadium_in_play", "discard")
    if target is not None:
        if target.name != "Sky Field":
            raise ValueError("this witness only mirrors Sky Field placement")
        out = out.move("sky_field", "discard", "stadium_in_play")
    assert_stadium_projection(following, out)
    return out


def mirror_bench_entries(
    zones: ZoneCountState, *copy_ids: str
) -> ZoneCountState:
    out = zones
    for identifier in copy_ids:
        out = out.move(identifier, "hand", "bench")
    return out
