"""Observer-relative evidence from a Peonia-seeded Greedy/Dream/Jirachi packet.

This test deliberately conditions on a stated *randomized* placement policy:
the three known packet identities are uniformly permuted among positions 0..2.
The actor learns their realized positions. The opponent knows the packet's
composition but not the permutation. The actor later selects exactly the two
positions containing Greedy Dice and Dream Ball to take as an attack award.

Conditional policies are essential: public selected positions leak information
about the placement, even when the cards remain face down.
"""

from __future__ import annotations

from itertools import permutations
from math import isclose, log2

from e31_peonia_seed_execution import initial_physical, play_peonia, run_seeded
from identity_materialization import assert_conserved
from observer_top_prize_beliefs import ObserverTopPrizeBeliefs
from prize_pending_batch_observer import (
    prepend_additional_prize_with_latent_observers,
    stage_prize_batch_with_latent_observers,
)
from prize_position_top_swap import PrizePositionTopBelief

GREEDY, DREAM, JIRACHI = "Greedy Dice", "Dream Ball", "Jirachi ◇"
GROUPS = (GREEDY, DREAM, JIRACHI)
CLASS_GROUPS = {
    "xy11-102": GREEDY,
    "swsh7-146": DREAM,
    "sm7-97": JIRACHI,
}
PHYSICAL_PACKET = (GREEDY, DREAM, JIRACHI, None)


def packet_beliefs() -> tuple[PrizePositionTopBelief, PrizePositionTopBelief]:
    """Posterior at the instant after a randomized, face-down Peonia exchange."""
    face_up = (False,) * 4
    actor = PrizePositionTopBelief(
        GROUPS, face_up, (((PHYSICAL_PACKET, None), 1.0),)
    )
    worlds = tuple(
        (((*arrangement, None), None), 1 / 6)
        for arrangement in permutations(GROUPS)
    )
    opponent = PrizePositionTopBelief(GROUPS, face_up, worlds)
    return actor, opponent


def public_pair_likelihood(belief: PrizePositionTopBelief, positions=(0, 1)):
    """Actor selects the two positions holding Greedy and Dream, in either order."""
    return {
        world: float(
            tuple(
                index for index, group in enumerate(world[0])
                if group in (GREEDY, DREAM)
            ) == positions
        )
        for world, _mass in belief.masses
    }


def independent_pair_likelihood(belief: PrizePositionTopBelief):
    """Control: choose one of the three two-slot pairs uniformly."""
    return {world: 1 / 3 for world, _mass in belief.masses}


def assert_near(actual: float, expected: float) -> None:
    assert isclose(actual, expected, rel_tol=0, abs_tol=1e-12), (
        actual, expected
    )


def run() -> dict[str, float]:
    before, board, physical = initial_physical()
    board, physical = play_peonia(board, physical)
    assert_conserved(before, board.ledger)
    assert physical.prize_instance_ids == (
        "greedy", "dream", "jirachi", "filler"
    )

    actor, opponent = packet_beliefs()
    assert_near(actor.probability_at(2, JIRACHI), 1)
    assert_near(opponent.probability_at(2, JIRACHI), 1 / 3)
    assert_near(opponent.probability_at(0, GREEDY), 1 / 3)

    independent = opponent.condition_on_public_world_choice(
        independent_pair_likelihood(opponent)
    )
    assert_near(independent.probability_at(2, JIRACHI), 1 / 3)

    chosen = opponent.condition_on_public_world_choice(
        public_pair_likelihood(opponent)
    )
    actor_chosen = actor.condition_on_public_world_choice(
        public_pair_likelihood(actor)
    )
    assert_near(chosen.probability_at(2, JIRACHI), 1)
    assert_near(chosen.probability_at(0, GREEDY), 1 / 2)
    assert_near(chosen.probability_at(1, DREAM), 1 / 2)
    assert len(chosen.masses) == 2
    assert len(actor_chosen.masses) == 1

    # The two positional beliefs now enter the shared physical/observer
    # pending Prize system. Both must give positive probability to truth.
    staged = stage_prize_batch_with_latent_observers(
        physical,
        ObserverTopPrizeBeliefs((
            ("actor", actor_chosen.as_existing_top_prize_joint()),
            ("opponent", chosen.as_existing_top_prize_joint()),
        )),
        actor_id="actor",
        positions=(0, 1),
        group_by_card_class=CLASS_GROUPS,
    )
    state = staged.after
    assert state.beliefs.pending_instance_ids == ("greedy", "dream")
    assert state.order.unresolved_batch_ids == ("greedy", "dream")
    observer = state.beliefs.belief_for("opponent")
    assert_near(observer.pending_probability(0, GREEDY), 1 / 2)
    assert_near(observer.pending_probability(1, DREAM), 1 / 2)
    assert_near(
        sum(
            mass for (_top, prizes, _pending), mass in observer.masses
            if prizes[0] == JIRACHI
        ),
        1,
    )

    # Under the heads branch Greedy chooses the now-known Jirachi slot.
    # The nested Prize becomes latent pending work for both observers.
    # Actual Jirachi Bench-entry and the following extra Prize are
    # separately checked by run_seeded; no inaccurate generic move to
    # the Bench is introduced here.
    nested = prepend_additional_prize_with_latent_observers(
        state, position=0
    )
    assert nested.beliefs.pending_instance_ids == (
        "jirachi", "greedy", "dream"
    )
    assert_near(
        nested.beliefs.belief_for("opponent").pending_probability(
            0, JIRACHI
        ),
        1,
    )
    try:
        nested.order.choose_next("dream")
    except ValueError as exc:
        assert "nested" in str(exc)
    else:
        raise AssertionError("original sibling bypassed nested Prize")

    assert run_seeded(heads=False) == (2, "Tapu Lele-GX")
    assert run_seeded(heads=True) == (4, JIRACHI)

    return {
        "observed_pair_probability": 1 / 3,
        "prior_jirachi_at_slot2": 1 / 3,
        "posterior_jirachi_at_slot2": 1.0,
        "posterior_greedy_at_slot0": 1 / 2,
        "information_gain_bits": log2(3),
        "conditional_expected_prizes": 3.0,
    }


if __name__ == "__main__":
    metrics = run()
    for key, value in metrics.items():
        print(f"{key}={value:.12g}")
    print("Peonia packet observer-choice regression passed")
