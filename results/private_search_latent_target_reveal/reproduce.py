"""Reproduce latent private-search target revelation."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from private_search_latent_target_belief import (
    resolve_private_search_with_latent_target_for_observers,
    reveal_private_target_to_observers,
)
from private_search_target_belief import (
    resolve_private_search_target_shuffle_for_observers,
)
from prize_position_belief import PrizePositionBelief
from prize_slot_visibility import PrizeSlotVisibilityBelief


def close(actual: float, expected: float) -> None:
    assert abs(actual - expected) <= 1e-12, (actual, expected)


def main() -> None:
    positions = PrizePositionBelief(
        ("A", "B"),
        1,
        ((("A",), 0.2), (("B",), 0.2), ((None,), 0.6)),
    )
    prior = PrizeSlotVisibilityBelief.all_face_down(positions)
    pool = {"A": 1, "B": 1}
    uniform_policy = {
        (1, 0): {"B": 0.25, None: 0.75},
        (0, 1): {"A": 0.25, None: 0.75},
        (0, 0): {"A": 0.25, "B": 0.25, None: 0.50},
    }

    latent = resolve_private_search_with_latent_target_for_observers(
        (("actor", prior), ("opponent", prior)),
        actor_id="actor",
        actor_exact_prize_counts={"A": 0, "B": 0},
        actor_selected_target_group="A",
        pre_search_group_pool_counts=pool,
        pre_search_pool_size=5,
        target_probability_by_composition=uniform_policy,
    )
    actor = latent.belief_for("actor")
    opponent = latent.belief_for("opponent")

    close(actor.target_probability("A"), 1.0)
    close(actor.top_probability("A"), 0.0)
    close(actor.top_probability("B"), 1.0 / 3.0)
    close(actor.top_probability(None), 2.0 / 3.0)

    close(opponent.target_probability("A"), 0.2)
    close(opponent.target_probability("B"), 0.2)
    close(opponent.target_probability(None), 0.6)
    close(opponent.top_probability("A"), 0.2)
    close(opponent.top_probability("B"), 0.2)
    close(opponent.top_probability(None), 0.6)

    old_projection = resolve_private_search_target_shuffle_for_observers(
        (("actor", prior), ("opponent", prior)),
        actor_id="actor",
        actor_exact_prize_counts={"A": 0, "B": 0},
        actor_selected_target_group="A",
        pre_search_group_pool_counts=pool,
        pre_search_pool_size=5,
        target_probability_by_composition=uniform_policy,
    )
    projected = latent.project_hidden_target()
    assert projected.belief_for("actor").masses == old_projection.belief_for("actor").masses
    assert projected.belief_for("opponent").masses == old_projection.belief_for("opponent").masses

    revealed = reveal_private_target_to_observers(
        latent,
        observed_group="A",
        observer_ids=("opponent",),
    )
    after = revealed.belief_for("opponent")
    close(after.target_probability("A"), 1.0)
    close(after.top_probability("A"), 0.0)
    close(after.top_probability("B"), 0.25)
    close(after.top_probability(None), 0.75)
    close(after.prize_probability_at(0, "A"), 0.0)
    close(after.prize_probability_at(0, "B"), 0.25)
    close(after.prize_probability_at(0, None), 0.75)

    print("Private search latent-target reveal regressions passed")


if __name__ == "__main__":
    main()
