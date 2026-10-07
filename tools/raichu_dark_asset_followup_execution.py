"""Physical bounded follow-up witness for Harto Raichu.

This executes the dominant qualitative branch behind raichu_dark_asset_followup:
Quick Ball -> Crobat V -> Dark Asset draws Ultra Ball -> Ultra Ball -> Alolan
Raichu. It reuses the canonical Trainer transaction for both Items.
"""

from __future__ import annotations

from dataclasses import dataclass

from bench_state_kernel import BenchState
from discard_cost_witness import (
    DiscardCandidate,
    DiscardSelection,
    enumerate_discard_selections,
)
from raichu_search_to_crobat_execution import (
    ULTRA_BALL_PROFILE,
    SearchToCrobatExecution,
    execute_search_to_crobat,
)
from search_zone_transition import SearchZoneTarget
from trainer_search_transaction import (
    TrainerSearchExecutionState,
    TrainerSearchTransaction,
    execute_trainer_search_transaction,
)
from typed_search_target_allocator import (
    POKEMON,
    TargetGroup,
    enumerate_typed_target_profiles,
    make_demand,
)


@dataclass(frozen=True)
class QuickDarkAssetUltraExecution:
    first: SearchToCrobatExecution
    after_dark_asset_draw: TrainerSearchExecutionState
    second: TrainerSearchTransaction
    final: TrainerSearchExecutionState


def execute_quick_dark_asset_ultra_raichu(
    state: TrainerSearchExecutionState,
    bench: BenchState,
    *,
    quick_discard_candidates: tuple[DiscardCandidate, ...],
    quick_discard_selection: DiscardSelection | None = None,
    ultra_discard_candidates: tuple[DiscardCandidate, ...],
    ultra_discard_selection: DiscardSelection | None = None,
    crobat_card_class: str = "crobat_v",
    ultra_ball_card_class: str = "ultra_ball",
    target_card_class: str = "alolan_raichu",
) -> QuickDarkAssetUltraExecution:
    """Execute one exact Quick -> Crobat -> draw Ultra -> target witness."""

    first = execute_search_to_crobat(
        state,
        bench,
        action_card_class="quick_ball",
        crobat_card_class=crobat_card_class,
        discard_candidates=quick_discard_candidates,
        discard_selection=quick_discard_selection,
    )
    if not first.crobat_benched:
        raise ValueError("Crobat V could not enter the Bench")
    if first.dark_asset_draw_count < 1:
        raise ValueError("Dark Asset has no draw capacity")
    if first.zones_after_bench.count(ultra_ball_card_class, "deck") < 1:
        raise ValueError("the exact Dark Asset Ultra Ball witness is not in deck")

    after_draw_zones = first.zones_after_bench.move(
        ultra_ball_card_class,
        "deck",
        "hand",
    )
    after_draw = TrainerSearchExecutionState(
        zones=after_draw_zones,
        budget=first.transaction.after.budget,
        channels=first.transaction.after.channels,
    )

    if after_draw.zones.count(target_card_class, "deck") < 1:
        raise ValueError("Alolan Raichu target is not in deck")

    target = SearchZoneTarget(
        target_card_class,
        TargetGroup(
            "Alolan Raichu",
            after_draw.zones.count(target_card_class, "deck"),
            frozenset({POKEMON}),
        ),
    )
    demand = make_demand("Alolan Raichu", "Pokémon")
    allocation = enumerate_typed_target_profiles(
        ULTRA_BALL_PROFILE.base_outputs,
        (target.group,),
        (demand,),
    )
    action = next(
        candidate
        for candidate in allocation.actions
        if candidate.output == (1,) and candidate.target_cost == (1,)
    )

    selection = ultra_discard_selection
    if selection is None:
        selections = enumerate_discard_selections(
            after_draw.zones,
            ultra_discard_candidates,
            ULTRA_BALL_PROFILE.required_discard_other_cards,
        )
        if not selections:
            raise ValueError(
                "post-Dark-Asset Ultra Ball lacks two allowed discard cards"
            )
        selection = selections[0]

    second = execute_trainer_search_transaction(
        after_draw,
        profile=ULTRA_BALL_PROFILE,
        action_card_class=ultra_ball_card_class,
        demands=(demand,),
        targets=(target,),
        search_action=action,
        discard_candidates=ultra_discard_candidates,
        discard_selection=selection,
    )

    return QuickDarkAssetUltraExecution(
        first=first,
        after_dark_asset_draw=after_draw,
        second=second,
        final=second.after,
    )
