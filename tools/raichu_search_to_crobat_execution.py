"""Physical search-to-Crobat execution bridge for the Harto Raichu models.

This module reuses the canonical Trainer search transaction and typed Bench
kernel. Quick Ball and Ultra Ball profiles are deliberately narrow, audited
against the bundled Sword & Shield card records, and exist only to bridge the
deck-specific probability model into conserved physical state.
"""

from __future__ import annotations

from dataclasses import dataclass

from bench_state_kernel import BenchState, add_support
from discard_cost_witness import (
    DiscardCandidate,
    DiscardSelection,
    enumerate_discard_selections,
)
from multicopy_zone_state import ZoneCountState
from search_zone_transition import SearchZoneTarget
from trainer_search_profile_compiler import (
    CompiledTrainerSearchProfile,
    SearchOutput,
)
from trainer_search_transaction import (
    TrainerSearchExecutionState,
    TrainerSearchTransaction,
    execute_trainer_search_transaction,
)
from typed_search_target_allocator import (
    BASIC_POKEMON,
    POKEMON,
    TargetGroup,
    enumerate_typed_target_profiles,
    make_demand,
)


QUICK_BALL_PROFILE = CompiledTrainerSearchProfile(
    card_id="swsh1-179",
    name="Quick Ball",
    action_class="Item",
    base_outputs=(SearchOutput("Basic Pokémon", 1),),
    required_discard_other_cards=1,
)

ULTRA_BALL_PROFILE = CompiledTrainerSearchProfile(
    card_id="swsh9-150",
    name="Ultra Ball",
    action_class="Item",
    base_outputs=(SearchOutput("Pokémon", 1),),
    required_discard_other_cards=2,
)


@dataclass(frozen=True)
class SearchToCrobatExecution:
    transaction: TrainerSearchTransaction
    bench_before: BenchState
    bench_after: BenchState | None
    zones_after_bench: ZoneCountState
    hand_size_after_search: int
    hand_size_after_bench: int
    dark_asset_draw_count: int

    @property
    def crobat_benched(self) -> bool:
        return self.bench_after is not None


def _hand_size(zones: ZoneCountState) -> int:
    return sum(
        count
        for _card_class, zone, count in zones.counts
        if zone == "hand"
    )


def _profile_and_demand(
    action_card_class: str,
) -> tuple[CompiledTrainerSearchProfile, str]:
    if action_card_class == "quick_ball":
        return QUICK_BALL_PROFILE, "Basic Pokémon"
    if action_card_class == "ultra_ball":
        return ULTRA_BALL_PROFILE, "Pokémon"
    raise ValueError("action_card_class must be 'quick_ball' or 'ultra_ball'")


def execute_search_to_crobat(
    state: TrainerSearchExecutionState,
    bench: BenchState,
    *,
    action_card_class: str,
    crobat_card_class: str = "crobat_v",
    discard_candidates: tuple[DiscardCandidate, ...],
    discard_selection: DiscardSelection | None = None,
) -> SearchToCrobatExecution:
    """Execute Quick Ball/Ultra Ball -> Crobat V -> Bench -> Dark Asset width.

    Dark Asset itself is not resolved here. Its draw count is derived from the
    physical post-Bench hand size and capped only at zero from the hand side.
    A later draw transition should additionally cap by the remaining deck size.
    """

    profile, demand_label = _profile_and_demand(action_card_class)
    cost = profile.required_discard_other_cards

    if state.zones.count(crobat_card_class, "deck") < 1:
        raise ValueError("Crobat V target is not in deck")

    target = SearchZoneTarget(
        crobat_card_class,
        TargetGroup(
            "Crobat V",
            state.zones.count(crobat_card_class, "deck"),
            frozenset({BASIC_POKEMON}),
        ),
    )
    demand = make_demand("Crobat V target", demand_label)
    allocation = enumerate_typed_target_profiles(
        profile.base_outputs,
        (target.group,),
        (demand,),
    )
    action = next(
        candidate
        for candidate in allocation.actions
        if candidate.output == (1,) and candidate.target_cost == (1,)
    )

    selection = discard_selection
    if selection is None:
        selections = enumerate_discard_selections(
            state.zones,
            discard_candidates,
            cost,
        )
        if not selections:
            raise ValueError("search cost is not payable by supplied candidates")
        selection = selections[0]

    transaction = execute_trainer_search_transaction(
        state,
        profile=profile,
        action_card_class=action_card_class,
        demands=(demand,),
        targets=(target,),
        search_action=action,
        discard_candidates=discard_candidates,
        discard_selection=selection,
    )

    after_search = transaction.after.zones
    hand_size_after_search = _hand_size(after_search)

    next_bench = add_support(
        bench,
        name="Crobat V",
        retention_value=0.0,
        trigger_name="Dark Asset",
        entry_mode="hand",
    )
    if next_bench is None:
        return SearchToCrobatExecution(
            transaction=transaction,
            bench_before=bench,
            bench_after=None,
            zones_after_bench=after_search,
            hand_size_after_search=hand_size_after_search,
            hand_size_after_bench=hand_size_after_search,
            dark_asset_draw_count=0,
        )

    after_bench = after_search.move(
        crobat_card_class,
        "hand",
        "bench",
    )
    hand_size_after_bench = _hand_size(after_bench)
    dark_asset_draw_count = max(0, 6 - hand_size_after_bench)

    return SearchToCrobatExecution(
        transaction=transaction,
        bench_before=bench,
        bench_after=next_bench,
        zones_after_bench=after_bench,
        hand_size_after_search=hand_size_after_search,
        hand_size_after_bench=hand_size_after_bench,
        dark_asset_draw_count=dark_asset_draw_count,
    )
