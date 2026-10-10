"""Reproduce positioned Prize/top-card swap results against labeled deals."""

from collections import Counter, defaultdict
from itertools import permutations
from math import isclose
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from prize_position_top_swap import PrizePositionTopBelief


def close(actual: float, expected: float) -> None:
    assert isclose(actual, expected, abs_tol=1e-12), (actual, expected)


def main() -> None:
    # Exact labeled independent oracle: 5P3 = 60 ordered physical deals.
    pool = ("A", "B", "F1", "F2", "F3")
    deals = tuple(permutations(pool, 3))
    assert len(deals) == 60

    base = PrizePositionTopBelief.from_pool(
        {"A": 1, "B": 1}, pool_size=5, prize_count=2
    )
    close(base.probability_at(0, "A"), 1 / 5)
    close(base.probability_group_prized("A"), 2 / 5)

    # Arc Phone: player sees deck-top A, opponent does not.
    actor = base.observe_top("A").swap_face_down_with_top(0)
    opponent = base.swap_face_down_with_top(0)
    assert actor.face_up == opponent.face_up == (False, False)
    close(actor.probability_at(0, "A"), 1)
    close(actor.probability_at(1, "A"), 0)
    close(actor.probability_group_prized("A"), 1)
    close(actor.probability_top("B"), 1 / 4)
    close(actor.probability_at(1, "B"), 1 / 4)
    close(opponent.probability_at(0, "A"), 1 / 5)
    close(opponent.probability_group_prized("A"), 2 / 5)

    # Enumerate the original labeled physical worlds independently of the
    # grouped without-replacement prior implementation.
    actor_oracle = defaultdict(float)
    opponent_oracle = defaultdict(float)
    for p0, p1, top in deals:
        assert Counter((p0, p1, top)) == Counter((top, p1, p0))
        after = tuple(c if c in ("A", "B") else None for c in (top, p1, p0))
        world = ((after[0], after[1]), after[2])
        opponent_oracle[world] += 1 / 60
        if top == "A":
            actor_oracle[world] += 1 / 12

    for oracle, actual in ((actor_oracle, actor), (opponent_oracle, opponent)):
        assert set(oracle) == {world for world, _ in actual.masses}
        for world, mass in actual.masses:
            close(oracle[world], mass)

    # Adversarial cross-check against the pre-existing agent41 joint kernel.
    # That kernel starts from a Prize-position prior and a known incoming top;
    # the new kernel supplies the prior by conditioning a fully joint random deal.
    from prize_position_belief import PrizePositionBelief
    from prize_slot_visibility import PrizeSlotVisibilityBelief
    from prize_top_swap_belief import swap_known_top_with_face_down_prize

    old_prior_masses = defaultdict(float)
    for (prizes, _), mass in base.observe_top("A").masses:
        old_prior_masses[prizes] += mass
    old_prior = PrizePositionBelief(
        ("A", "B"), 2, tuple(old_prior_masses.items())
    )
    old_joint = swap_known_top_with_face_down_prize(
        PrizeSlotVisibilityBelief.all_face_down(old_prior),
        position=0,
        incoming_group="A",
    )
    bridged = actor.as_existing_top_prize_joint()
    old_masses = dict(old_joint.masses)
    assert set(old_masses) == {w for w, _ in bridged.masses}
    for world, mass in bridged.masses:
        close(mass, old_masses[world])
    roundtrip = PrizePositionTopBelief.from_existing_top_prize_joint(bridged)
    assert dict(roundtrip.masses).keys() == dict(actor.masses).keys()
    for world, mass in roundtrip.masses:
        close(mass, dict(actor.masses)[world])

    # Composition is insufficient: swap target position zero vs one.
    other_position = base.observe_top("A").swap_face_down_with_top(1)
    first = dict(actor.composition_masses())
    second = dict(other_position.composition_masses())
    assert first.keys() == second.keys()
    for counts in first:
        close(first[counts], second[counts])
    close(other_position.probability_at(0, "A"), 0)
    close(other_position.probability_at(1, "A"), 1)

    # Gladion-style shuffle destroys position certainty, not membership
    # certainty. The opponent's exchangeable distribution remains unchanged.
    shuffled = actor.shuffle_face_down_positions()
    close(shuffled.probability_at(0, "A"), 1 / 2)
    close(shuffled.probability_at(1, "A"), 1 / 2)
    close(shuffled.probability_group_prized("A"), 1)
    for state, mass in shuffled.composition_masses():
        close(mass, first[state])
    close(opponent.shuffle_face_down_positions().probability_at(0, "A"), 1 / 5)

    # Outgoing deck top is correlated with the remaining Prize.
    observed_outgoing_b = actor.observe_top("B")
    close(observed_outgoing_b.probability_at(1, "B"), 0)
    close(observed_outgoing_b.probability_at(0, "A"), 1)

    # Compatibility projections intentionally forget position and correlations.
    count_only = actor.collapse_to_prize_belief()
    assert count_only.groups == actor.groups
    assert count_only.prize_count == actor.prize_count
    for state, mass in count_only.masses:
        close(mass, first[state])
    visibility = actor.collapse_to_visibility_belief()
    assert visibility.face_up_count == 0
    for state, mass in visibility.face_down.masses:
        close(mass, first[state])

    # Publicly revealed Prize stays ineligible for face-down-only swaps.
    public = opponent.reveal_prize(0, "A")
    close(public.probability_face_down_group("A"), 0)
    assert public.face_up == (True, False)
    visible = public.collapse_to_visibility_belief()
    assert visible.face_up_group_count("A") == 1
    assert visible.face_down.prize_count == 1
    try:
        public.swap_face_down_with_top(0)
    except ValueError:
        pass
    else:
        raise AssertionError("accepted swapping a face-up Prize")

    # A second swap at the same position reverses the physical operation.
    twice = actor.swap_face_down_with_top(0)
    peek = base.observe_top("A")
    assert dict(twice.masses).keys() == dict(peek.masses).keys()
    for world, mass in twice.masses:
        close(mass, dict(peek.masses)[world])

    try:
        actor.observe_top("A")
    except ValueError:
        pass
    else:
        raise AssertionError("accepted impossible incoming-card observation")

    # Larger practical combinatorics: seven known nonPrize cards, 53 unseen,
    # six Prize positions, unique A and B, and exactly one deck top.
    larger = PrizePositionTopBelief.from_pool(
        {"A": 1, "B": 1}, pool_size=53, prize_count=6
    )
    assert len(larger.masses) == 57
    known = larger.observe_top("A").swap_face_down_with_top(3)
    unknown = larger.swap_face_down_with_top(3)
    close(known.probability_at(3, "A"), 1)
    close(known.probability_group_prized("B"), 5 / 52)
    close(known.probability_top("B"), 1 / 52)
    close(unknown.probability_at(3, "A"), 1 / 53)
    close(unknown.probability_group_prized("A"), 6 / 53)

    # A joint physical swap preserves all grouped identities.
    for (before, _), (after, _) in zip(base.masses, opponent.masses):
        assert Counter((*before[0], before[1])) == Counter((*after[0], after[1]))

    print("Prize/top position oracle passed: 60 labeled deals; 12 private A-top deals")
    print("Actor P(A at chosen position)=1; opponent=1/5, P(A Prized)=2/5")


if __name__ == "__main__":
    main()
