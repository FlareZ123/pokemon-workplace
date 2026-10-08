"""Apply source-scoped hand-play restrictions to materialized paired gust.

The caller supplies already-active restrictions for the current player.
This adapter uses the established exact/residual permission projection.
"""
from collections.abc import Sequence

from tools.board_object_kernel import BoardState
from tools.card_action_metadata import CardActionMetadata
from tools.identity_materialization import IdentityLedger
from tools.paired_switch_identity_bridge import (
    MaterializedPairedSwitchTransaction, execute_materialized_paired_switch,
)
from tools.paired_switch_order_catalog import PairedSwitchProgram
from tools.source_scoped_action_restrictions import SourceScopedActionRestriction
from tools.source_scoped_channel_projection import (
    action_allowed, project_source_scoped_permissions,
)
from tools.turn_action_budget import TurnActionBudget


def execute_permissioned_paired_switch(
    ledger: IdentityLedger,
    player_board: BoardState,
    opponent_board: BoardState,
    turn_budget: TurnActionBudget,
    program: PairedSwitchProgram,
    metadata: CardActionMetadata,
    *,
    source_instance_ids: tuple[str, ...],
    opponent_promote_id: str | None,
    own_promote_id: str | None,
    active_restrictions: Sequence[SourceScopedActionRestriction] = (),
) -> MaterializedPairedSwitchTransaction | None:
    """Execute after checking exact print metadata and active locks."""
    required_kind = (
        "supporter"
        if program.name in {"Guzma", "Team Rocket's Giovanni"}
        else "item"
    )
    if metadata.name != program.name or metadata.card_kind != required_kind:
        raise ValueError("source print metadata does not match paired-switch program")

    projected = project_source_scoped_permissions(active_restrictions)
    if not action_allowed(projected, metadata.attempt("hand")):
        return None

    return execute_materialized_paired_switch(
        ledger, player_board, opponent_board, turn_budget, program,
        source_instance_ids=source_instance_ids,
        opponent_promote_id=opponent_promote_id,
        own_promote_id=own_promote_id,
        item_play_allowed=True,
    )
