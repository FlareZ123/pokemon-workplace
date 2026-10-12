"""Compose Goodra coin gate with Dashing Pouch's actual Ultra Ball payment access.

Reuses two previously tested physical mechanics without a simplified hand model.
"""
from __future__ import annotations

from fractions import Fraction
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

from board_object_kernel import make_board, make_pokemon
from discard_cost_witness import DiscardCandidate, enumerate_discard_selections
from retreat_action_enumerator import enumerate_board_derived_retreat_actions
from retreat_goodra_coin_gate import normal_retreat_goodra_outcomes
from trainer_search_transaction import (
    TrainerSearchExecutionState, execute_trainer_retrieval_transaction,
)
from results.retreat_ultraball_payment_bridge.reproduce import (
    build_actor, DISCARD_CANDIDATES, ENERGY_CLASSES, SEARCH_PROFILE,
    TARGETS, RETRIEVAL,
)


def access_after_outcome(outcome, *, spare_hand: int) -> bool:
    zones = outcome.state.energy.zones
    candidates = DISCARD_CANDIDATES + (
        (DiscardCandidate("spare_fodder"),) if spare_hand else ()
    )
    choices = enumerate_discard_selections(zones, candidates, 2)
    for choice in choices:
        tx = execute_trainer_retrieval_transaction(
            TrainerSearchExecutionState(
                zones=zones, budget=outcome.state.unified.turn_budget,
            ),
            profile=SEARCH_PROFILE,
            action_card_class="ultra_ball",
            targets=TARGETS,
            retrieval_action=RETRIEVAL,
            discard_candidates=candidates,
            discard_selection=choice,
        )
        assert tx.after.zones.count("target_pokemon", "hand") == 1
        assert tx.after.zones.count("ultra_ball", "discard") == 1
        assert tx.after.budget.retreat_used
        assert not tx.after.budget.supporter_used
        for card in ("ultra_ball", "target_pokemon", *ENERGY_CLASSES):
            assert tx.after.zones.total(card) == zones.total(card)
        return True
    return False


def evaluate(*, spare_hand=0, goodra_count=1, suppress=False):
    actor = build_actor(spare_hand=spare_hand)
    source = tuple(
        make_pokemon(
            f"goodra{i}", "Goodra", print_id="me4-68",
            abilities_enabled=not suppress, tags=("Stage2",),
        )
        for i in range(goodra_count)
    )
    opponent = make_board(make_pokemon("other", "Other"), source)
    enumeration = enumerate_board_derived_retreat_actions(
        actor, opponent, base_retreat_cost=2,
    )
    assert len(enumeration.actions) == 2

    result = {}
    for action in enumeration.actions:
        paid = tuple(sorted(action.discard_energy_ids))
        branches = normal_retreat_goodra_outcomes(actor, opponent, action)
        assert sum((b.probability for b in branches), Fraction()) == 1
        result[paid] = sum(
            (outcome.probability for outcome in branches
             if access_after_outcome(outcome, spare_hand=spare_hand)),
            Fraction(),
        )
        for outcome in branches:
            assert outcome.state.unified.turn_budget.retreat_used
            if outcome.label == "tails":
                assert outcome.state.energy.zones == actor.energy.zones
                assert outcome.state.energy.board == make_board(
                    actor.energy.board.get("active"),
                    (actor.energy.board.get("pivot"),),
                    retreat_used=True,
                )
    return result


def main() -> None:
    minimal = ("dce",)
    overpayment = ("basic", "dce")
    one_goodra = evaluate()
    two_goodra = evaluate(goodra_count=2)
    no_goodra = evaluate(goodra_count=0)
    disabled = evaluate(suppress=True)
    one_spare = evaluate(spare_hand=1)
    two_spare = evaluate(spare_hand=2)

    assert one_goodra == {
        minimal: Fraction(0), overpayment: Fraction(1, 2),
    }
    assert two_goodra == one_goodra
    assert no_goodra == disabled == {
        minimal: Fraction(0), overpayment: Fraction(1),
    }
    assert one_spare == {
        minimal: Fraction(1, 2), overpayment: Fraction(1, 2),
    }
    assert two_spare == {
        minimal: Fraction(1), overpayment: Fraction(1),
    }
    print("Goodra + Dashing Pouch + paid Ultra Ball continuation: PASS")
    print({
        "unopposed_minimal_vs_overpayment": [str(x) for x in no_goodra.values()],
        "opposed_minimal_vs_overpayment": [str(x) for x in one_goodra.values()],
        "two_goodra_no_stack": two_goodra == one_goodra,
    })


if __name__ == "__main__":
    main()
