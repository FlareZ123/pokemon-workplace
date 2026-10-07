"""Reproduce unified-state composition regressions."""

from __future__ import annotations

from dataclasses import replace
import json
from math import comb, isclose
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from bench_state_kernel import BenchResident, BenchState  # noqa: E402
from prize_belief_kernel import PrizeBelief  # noqa: E402
from unified_state_kernel import (  # noqa: E402
    Zone,
    active_tool_protects,
    apply_lock,
    attack_ready,
    attach_dce_to_active,
    attach_tool_to_active,
    change_bench_capacity,
    gladion_access_probability,
    make_state,
    play_tapu_lele_from_hand,
    play_thunder_mountain,
    shortest_gladion_line,
    suppress_active_tool_effect,
)


def _assert_close(actual: float, expected: float) -> None:
    if not isclose(actual, expected, rel_tol=0.0, abs_tol=1e-12):
        raise AssertionError(f"{actual} != {expected}")


def _gladion_base(**kwargs: object):
    return make_state(
        {
            "Quick Ball": Zone.HAND.value,
            "Fodder": Zone.HAND.value,
            "Tapu Lele-GX": Zone.DECK.value,
            "Gladion": Zone.DECK.value,
        },
        **kwargs,
    )


def _full_bench_gladion_base():
    residents = tuple(
        BenchResident(
            name=f"Core {index}",
            role="core",
            retention_value=10.0 + index,
        )
        for index in range(5)
    )
    locations = {
        "Quick Ball": Zone.HAND.value,
        "Fodder": Zone.HAND.value,
        "Tapu Lele-GX": Zone.DECK.value,
        "Gladion": Zone.DECK.value,
    }
    locations.update({resident.name: Zone.BENCH.value for resident in residents})
    return make_state(
        locations,
        bench=BenchState(capacity=5, residents=residents),
    )


def main() -> None:
    expected_line = [
        "Quick Ball -> Tapu Lele-GX to hand",
        "Play Tapu Lele-GX from hand; Wonder Tag -> Gladion",
        "Play Gladion",
    ]

    baseline = _gladion_base()
    result = shortest_gladion_line(baseline)
    assert result is not None
    assert result[0] == expected_line

    # The same nominal access graph can fail at four different mechanical layers.
    assert shortest_gladion_line(apply_lock(baseline, "item")) is None
    assert shortest_gladion_line(apply_lock(baseline, "supporter")) is None
    assert shortest_gladion_line(
        replace(baseline, abilities_allowed=False)
    ) is None
    full_bench = _full_bench_gladion_base()
    assert shortest_gladion_line(full_bench) is None

    # Direct deck-to-Bench placement reaches Lele but never emits the hand-play
    # condition required for Wonder Tag.
    nest = make_state(
        {
            "Nest Ball": Zone.HAND.value,
            "Tapu Lele-GX": Zone.DECK.value,
            "Gladion": Zone.DECK.value,
        }
    )
    assert shortest_gladion_line(nest) is None

    # Item lock and Tool play remain separate channels.
    tool_base = make_state(
        {
            "Iron Thorns ex": Zone.ACTIVE.value,
            "Stealthy Hood": Zone.HAND.value,
        },
        active_name="Iron Thorns ex",
        active_tags=frozenset({"Lightning", "Basic"}),
    )
    item_locked_tool = apply_lock(tool_base, "item")
    hood_attached = attach_tool_to_active(
        item_locked_tool,
        card="Stealthy Hood",
    )
    assert hood_attached is not None
    assert hood_attached.active_tool_name == "Stealthy Hood"
    assert active_tool_protects(hood_attached)

    # Tool identity must survive composition. A generic attached-Tool boolean
    # is insufficient because only Stealthy Hood grants this protection.
    choice_base = make_state(
        {
            "Iron Thorns ex": Zone.ACTIVE.value,
            "Choice Band": Zone.HAND.value,
        },
        active_name="Iron Thorns ex",
        active_tags=frozenset({"Lightning", "Basic"}),
    )
    choice_attached = attach_tool_to_active(
        choice_base,
        card="Choice Band",
    )
    assert choice_attached is not None
    assert choice_attached.active_tool_name == "Choice Band"
    assert not active_tool_protects(choice_attached)

    hood_suppressed = suppress_active_tool_effect(hood_attached)
    assert hood_suppressed.active_pokemon.tool_attached
    assert not hood_suppressed.active_pokemon.tool_effect_enabled
    assert not active_tool_protects(hood_suppressed)

    trainer_locked_tool = apply_lock(tool_base, "trainer")
    assert attach_tool_to_active(
        trainer_locked_tool,
        card="Stealthy Hood",
    ) is None

    # The same state owns card zones, attachment bandwidth, lock channels, and
    # the typed Energy summary passed to the exact Energy solver.
    energy = make_state(
        {
            "Iron Thorns ex": Zone.ACTIVE.value,
            "Double Colorless Energy": Zone.HAND.value,
            "Thunder Mountain Prism Star": Zone.HAND.value,
        },
        active_name="Iron Thorns ex",
        active_tags=frozenset({"Lightning", "Basic"}),
    )
    assert not attack_ready(energy, ("L", "C", "C"))

    dce_attached = attach_dce_to_active(energy)
    assert dce_attached is not None
    assert not attack_ready(dce_attached, ("L", "C", "C"))

    attack_state = play_thunder_mountain(dce_attached)
    assert attack_state is not None
    assert attack_ready(attack_state, ("L", "C", "C"))

    special_energy_locked = apply_lock(energy, "special_energy_play")
    assert attach_dce_to_active(special_energy_locked) is None

    stadium_locked = apply_lock(dce_attached, "stadium")
    assert play_thunder_mountain(stadium_locked) is None

    # Dynamic Bench contraction changes both Bench residency and canonical zones.
    cores = tuple(
        BenchResident(
            name=f"Stable Core {index}",
            role="core",
            retention_value=20.0 + index,
        )
        for index in range(4)
    )
    contraction_locations = {
        resident.name: Zone.BENCH.value
        for resident in cores
    }
    contraction_locations.update(
        {
            "Tapu Lele-GX": Zone.HAND.value,
            "Gladion": Zone.DECK.value,
        }
    )
    contraction = make_state(
        contraction_locations,
        bench=BenchState(capacity=5, residents=cores),
    )
    lele_transition = play_tapu_lele_from_hand(contraction)
    assert len(lele_transition) == 1
    with_lele = lele_transition[0][1]
    assert len(with_lele.bench.residents) == 5
    assert with_lele.zone("Tapu Lele-GX") == Zone.BENCH.value

    contracted, discarded = change_bench_capacity(
        with_lele,
        new_capacity=4,
    )
    assert [resident.name for resident in discarded] == ["Tapu Lele-GX"]
    assert contracted.zone("Tapu Lele-GX") == Zone.DISCARD.value
    assert len(contracted.bench.residents) == 4

    # Belief-weighted reachability composes uncertain Prize state with the same
    # deterministic planner. Both singleton cards must be outside six Prizes.
    belief = PrizeBelief.from_hypergeometric(
        {
            "lele": 1,
            "gladion": 1,
        },
        pool_size=53,
        prize_count=6,
    )
    singleton_groups = {
        "lele": "Tapu Lele-GX",
        "gladion": "Gladion",
    }
    access_probability = gladion_access_probability(
        baseline,
        belief,
        singleton_groups,
    )
    expected_probability = comb(51, 6) / comb(53, 6)
    _assert_close(access_probability, expected_probability)

    _assert_close(
        gladion_access_probability(
            apply_lock(baseline, "item"),
            belief,
            singleton_groups,
        ),
        0.0,
    )
    _assert_close(
        gladion_access_probability(
            full_bench,
            belief,
            singleton_groups,
        ),
        0.0,
    )

    exact_unprized = PrizeBelief.from_exact(
        {"lele": 0, "gladion": 0},
        prize_count=6,
    )
    exact_lele_prized = PrizeBelief.from_exact(
        {"lele": 1, "gladion": 0},
        prize_count=6,
    )
    _assert_close(
        gladion_access_probability(
            baseline,
            exact_unprized,
            singleton_groups,
        ),
        1.0,
    )
    _assert_close(
        gladion_access_probability(
            baseline,
            exact_lele_prized,
            singleton_groups,
        ),
        0.0,
    )

    print(
        json.dumps(
            {
                "baseline_gladion_line": result[0],
                "baseline_prize_weighted_access": access_probability,
                "expected_two_singleton_unprized": expected_probability,
                "item_lock_access": 0.0,
                "full_bench_access": 0.0,
                "tool_attach_under_item_lock": True,
                "non_hood_tool_grants_stealthy_hood_protection": False,
                "tool_effect_after_suppression": False,
                "volt_cyclone_ready_after_dce_and_thunder_mountain": True,
                "contraction_discards": [
                    resident.name for resident in discarded
                ],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
