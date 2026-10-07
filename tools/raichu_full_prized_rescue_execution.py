"""Full physical representative rescue chain for Harto Raichu.

Quick Ball -> Crobat V -> Dark Asset draws Computer Search -> K1 identifies
Alolan Raichu in Prize -> Computer Search selects Gladion -> Gladion retrieves
Alolan Raichu and cycles itself into Prize.
"""

from __future__ import annotations

from dataclasses import dataclass

from bench_state_kernel import BenchState
from discard_cost_witness import DiscardCandidate, DiscardSelection
from gladion_supporter_physical_transaction import (
    GladionSupporterOutcome,
    execute_gladion_supporter_physical,
)
from raichu_dark_asset_computer_followup_execution import (
    QuickDarkAssetComputerExecution,
    execute_quick_dark_asset_computer_gladion,
)
from trainer_search_transaction import TrainerSearchExecutionState


@dataclass(frozen=True)
class FullPrizedRaichuRescueExecution:
    computer_line: QuickDarkAssetComputerExecution
    gladion_outcomes: tuple[GladionSupporterOutcome, ...]


def execute_full_prized_raichu_rescue(
    state: TrainerSearchExecutionState,
    bench: BenchState,
    *,
    quick_discard_candidates: tuple[DiscardCandidate, ...],
    quick_discard_selection: DiscardSelection,
    computer_discard_candidates: tuple[DiscardCandidate, ...],
    computer_discard_selection: DiscardSelection,
) -> FullPrizedRaichuRescueExecution:
    """Execute the complete representative singleton Prize-recovery line."""

    computer_line = execute_quick_dark_asset_computer_gladion(
        state,
        bench,
        quick_discard_candidates=quick_discard_candidates,
        quick_discard_selection=quick_discard_selection,
        computer_discard_candidates=computer_discard_candidates,
        computer_discard_selection=computer_discard_selection,
    )

    computer = computer_line.computer
    gladion_outcomes = execute_gladion_supporter_physical(
        computer.physical_after,
        computer.after.budget,
        computer.after.channels,
        gladion_instance_id="private-gladion",
        selected_position=0,
    )

    if not gladion_outcomes:
        raise AssertionError("Gladion physical transition returned no outcomes")
    for outcome in gladion_outcomes:
        after = outcome.physical.physical_after
        if after.ledger.instance("prize-raichu").zone != "hand":
            raise AssertionError("Alolan Raichu was not recovered to hand")
        if after.ledger.instance("private-gladion").zone != "prize":
            raise AssertionError("played Gladion did not cycle into Prize")
        if not outcome.budget_after.supporter_used:
            raise AssertionError("Gladion did not consume the Supporter window")

    return FullPrizedRaichuRescueExecution(
        computer_line=computer_line,
        gladion_outcomes=gladion_outcomes,
    )
