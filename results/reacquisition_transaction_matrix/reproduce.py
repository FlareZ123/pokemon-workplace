"""Cross-validate the full reacquisition filler matrix with exact Trainer transactions."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from discard_cost_witness import (  # noqa: E402
    DiscardCandidate,
    DiscardSelection,
    enumerate_discard_selections,
)
from multicopy_zone_state import ZoneCountState  # noqa: E402
from search_zone_transition import SearchZoneTarget  # noqa: E402
from temporal_resource_ledger import (  # noqa: E402
    TemporalAction,
    minimum_initial_filler,
)
from trainer_search_profile_compiler import (  # noqa: E402
    compile_multi_output_trainer_profiles,
)
from trainer_search_transaction import (  # noqa: E402
    TrainerSearchExecutionState,
    execute_trainer_retrieval_transaction,
)
from typed_search_retrieval import (  # noqa: E402
    TypedRetrievalAction,
    enumerate_typed_retrieval_actions,
)
from typed_search_target_allocator import (  # noqa: E402
    ITEM,
    POKEMON_TOOL,
    SPECIAL_ENERGY,
    STADIUM,
    SUPPORTER,
    TargetGroup,
)


SECRET_BOX = "secret_box"
FILLER = "initial_filler"
TAG_CALL = "tag_call"
TM_EVOLUTION = "tm_evolution"
GUZMA_HALA = "guzma_hala"
ARTAZON = "artazon"
JET_ENERGY = "jet_energy"


def representative(profiles: tuple, name: str):
    matches = [profile for profile in profiles if profile.name == name]
    if not matches:
        raise AssertionError(f"{name} missing")
    return matches[0]


def action_for_cost(
    profile,
    targets: tuple[SearchZoneTarget, ...],
    target_cost: tuple[int, ...],
) -> TypedRetrievalAction:
    actions = enumerate_typed_retrieval_actions(
        profile.base_outputs + profile.conditional_outputs,
        tuple(target.group for target in targets),
    )
    matches = [action for action in actions if action.target_cost == target_cost]
    if len(matches) != 1:
        raise AssertionError(
            f"expected one retrieval for {target_cost}, found {len(matches)}"
        )
    return matches[0]


def selection_classes(
    candidates: tuple[DiscardCandidate, ...],
    selection: DiscardSelection,
) -> tuple[str, ...]:
    return tuple(
        candidate.card_class
        for candidate, amount in zip(candidates, selection.counts, strict=True)
        for _ in range(amount)
    )


def initial_state(fillers: int) -> TrainerSearchExecutionState:
    counts = {
        (SECRET_BOX, "hand"): 1,
        (TAG_CALL, "deck"): 1,
        (TM_EVOLUTION, "deck"): 2,
        (GUZMA_HALA, "deck"): 1,
        (ARTAZON, "deck"): 2,
        (JET_ENERGY, "deck"): 2,
    }
    if fillers:
        counts[(FILLER, "hand")] = fillers
    return TrainerSearchExecutionState(
        zones=ZoneCountState.from_mapping(counts)
    )


def execute_secret_box(
    state: TrainerSearchExecutionState,
    secret_box_profile,
    secret_targets: tuple[SearchZoneTarget, ...],
    secret_action: TypedRetrievalAction,
) -> TrainerSearchExecutionState | None:
    candidates = (DiscardCandidate(FILLER),)
    selections = enumerate_discard_selections(
        state.zones,
        candidates,
        3,
    )
    if not selections:
        return None
    if len(selections) != 1:
        raise AssertionError("filler-only Secret Box payment should be unique")

    transaction = execute_trainer_retrieval_transaction(
        state,
        profile=secret_box_profile,
        action_card_class=SECRET_BOX,
        targets=secret_targets,
        retrieval_action=secret_action,
        discard_candidates=candidates,
        discard_selection=selections[0],
    )
    return transaction.after


def exact_minimum_fillers(
    secret_box_profile,
    guzma_hala_profile,
    secret_targets: tuple[SearchZoneTarget, ...],
    secret_action: TypedRetrievalAction,
    gh_targets: tuple[SearchZoneTarget, ...],
    gh_action: TypedRetrievalAction,
    final_requirements: dict[str, int],
    *,
    max_fillers: int = 6,
) -> tuple[int, tuple[str, ...]]:
    candidates = (
        DiscardCandidate(FILLER),
        DiscardCandidate(TAG_CALL),
        DiscardCandidate(TM_EVOLUTION),
        DiscardCandidate(ARTAZON),
    )

    for fillers in range(max_fillers + 1):
        initial = initial_state(fillers)
        after_box = execute_secret_box(
            initial,
            secret_box_profile,
            secret_targets,
            secret_action,
        )
        if after_box is None:
            continue

        selections = enumerate_discard_selections(
            after_box.zones,
            candidates,
            2,
        )
        for selection in selections:
            transaction = execute_trainer_retrieval_transaction(
                after_box,
                profile=guzma_hala_profile,
                action_card_class=GUZMA_HALA,
                targets=gh_targets,
                retrieval_action=gh_action,
                discard_candidates=candidates,
                discard_selection=selection,
            )
            final = transaction.after
            if not all(
                final.zones.count(card_class, "hand") >= required
                for card_class, required in final_requirements.items()
            ):
                continue

            classes = {
                card_class
                for card_class, _zone, _count in initial.zones.counts
            } | {
                card_class
                for card_class, _zone, _count in final.zones.counts
            }
            for card_class in classes:
                assert (
                    initial.zones.total(card_class)
                    == final.zones.total(card_class)
                )
            assert final.budget.supporter_used
            return fillers, selection_classes(candidates, selection)

    raise AssertionError("no exact transaction witness within filler bound")


def ledger_minimum(
    second_generates: tuple[str, ...],
    requirements: dict[str, int],
) -> int:
    secret_box = TemporalAction(
        "Secret Box",
        consumes=("Secret Box",),
        discard_cost=3,
        generates=(
            "Guzma & Hala",
            "Tag Call",
            "Technical Machine: Evolution",
            "Artazon",
        ),
    )
    guzma_hala = TemporalAction(
        "Guzma & Hala",
        consumes=("Guzma & Hala",),
        discard_cost=2,
        generates=second_generates,
    )
    fillers, _witness = minimum_initial_filler(
        ("Secret Box",),
        (secret_box, guzma_hala),
        final_hand_requirements=requirements,
        max_fillers=6,
    )
    return fillers


def main() -> None:
    profiles = compile_multi_output_trainer_profiles(ROOT / "resources")
    secret_box = representative(profiles, "Secret Box")
    guzma_hala = representative(profiles, "Guzma & Hala")

    secret_targets = (
        SearchZoneTarget(
            TAG_CALL,
            TargetGroup("Tag Call", 1, frozenset({ITEM})),
        ),
        SearchZoneTarget(
            TM_EVOLUTION,
            TargetGroup("TM Evolution", 2, frozenset({POKEMON_TOOL})),
        ),
        SearchZoneTarget(
            GUZMA_HALA,
            TargetGroup("Guzma & Hala", 1, frozenset({SUPPORTER})),
        ),
        SearchZoneTarget(
            ARTAZON,
            TargetGroup("Artazon", 2, frozenset({STADIUM})),
        ),
    )
    secret_action = action_for_cost(
        secret_box,
        secret_targets,
        (1, 1, 1, 1),
    )

    gh_targets = (
        SearchZoneTarget(
            ARTAZON,
            TargetGroup("Remaining Artazon", 1, frozenset({STADIUM})),
        ),
        SearchZoneTarget(
            TM_EVOLUTION,
            TargetGroup("Remaining TM Evolution", 1, frozenset({POKEMON_TOOL})),
        ),
        SearchZoneTarget(
            JET_ENERGY,
            TargetGroup("Jet Energy", 2, frozenset({SPECIAL_ENERGY})),
        ),
    )
    gh_modes = {
        "no_reacquisition": {
            "target_cost": (0, 0, 1),
            "generated": ("Jet Energy",),
        },
        "tool_reacquisition": {
            "target_cost": (0, 1, 1),
            "generated": ("Technical Machine: Evolution", "Jet Energy"),
        },
        "stadium_reacquisition": {
            "target_cost": (1, 0, 1),
            "generated": ("Artazon", "Jet Energy"),
        },
        "tool_and_stadium_reacquisition": {
            "target_cost": (1, 1, 1),
            "generated": (
                "Technical Machine: Evolution",
                "Artazon",
                "Jet Energy",
            ),
        },
    }
    requirement_profiles = {
        "aichi_core": {
            "exact": {
                TM_EVOLUTION: 1,
                ARTAZON: 1,
                JET_ENERGY: 1,
            },
            "ledger": {
                "Technical Machine: Evolution": 1,
                "Artazon": 1,
                "Jet Energy": 1,
            },
        },
        "item_also_independent": {
            "exact": {
                TAG_CALL: 1,
                TM_EVOLUTION: 1,
                ARTAZON: 1,
                JET_ENERGY: 1,
            },
            "ledger": {
                "Tag Call": 1,
                "Technical Machine: Evolution": 1,
                "Artazon": 1,
                "Jet Energy": 1,
            },
        },
    }
    expected = {
        "aichi_core": {
            "no_reacquisition": 4,
            "tool_reacquisition": 3,
            "stadium_reacquisition": 3,
            "tool_and_stadium_reacquisition": 3,
        },
        "item_also_independent": {
            "no_reacquisition": 5,
            "tool_reacquisition": 4,
            "stadium_reacquisition": 4,
            "tool_and_stadium_reacquisition": 3,
        },
    }

    matrix = {}
    for profile_name, requirements in requirement_profiles.items():
        row = {}
        for mode_name, mode in gh_modes.items():
            gh_action = action_for_cost(
                guzma_hala,
                gh_targets,
                mode["target_cost"],
            )
            exact_fillers, exact_discards = exact_minimum_fillers(
                secret_box,
                guzma_hala,
                secret_targets,
                secret_action,
                gh_targets,
                gh_action,
                requirements["exact"],
            )
            abstract_fillers = ledger_minimum(
                mode["generated"],
                requirements["ledger"],
            )
            assert exact_fillers == abstract_fillers
            assert exact_fillers == expected[profile_name][mode_name]
            row[mode_name] = {
                "minimum_initial_fillers": exact_fillers,
                "guzma_hala_discard_witness": exact_discards,
            }
        matrix[profile_name] = row

    print(
        json.dumps(
            {
                "all_eight_cells_match_temporal_ledger": True,
                "exact_transaction_matrix": matrix,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
