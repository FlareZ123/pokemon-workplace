"""Secret Box output-category dependency audit for Aichi Vileplume.

The existing paired Aichi first-turn model uses all four Secret Box output
categories. This module replays the same accepted opening, Prize, draw, and
Stellar Wish states while selectively enabling any subset of the Item, Tool,
Supporter, and Stadium outputs.

For every Secret-Box-only core success, it records the smallest output-category
subset that still reaches the Bunnelby + TM: Evolution + Jet Energy endpoint.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import random

from aichi_vileplume_secret_box import (
    BASE_DECK,
    SECRET_BOX_DECK,
    BOX_ALL_OUTPUTS,
    BOX_ITEM_OUTPUT,
    BOX_STADIUM_OUTPUT,
    BOX_SUPPORTER_OUTPUT,
    BOX_TOOL_OUTPUT,
    HAND_INDEX,
    STELLAR_TRAINERS,
    _compress_deck,
    _compress_hand,
    _core_possible,
    _raw_state,
    _state_succeeds,
)


OUTPUTS = (
    (BOX_ITEM_OUTPUT, "Item"),
    (BOX_TOOL_OUTPUT, "Tool"),
    (BOX_SUPPORTER_OUTPUT, "Supporter"),
    (BOX_STADIUM_OUTPUT, "Stadium"),
)


@dataclass(frozen=True)
class OutputDependencyResult:
    """Aggregate dependency geometry over paired incremental successes."""

    trials: int
    baseline_successes: int
    full_output_successes: int
    incremental_successes: int
    minimum_category_counts: tuple[int, ...]
    mask_success_counts: tuple[int, ...]
    minimal_mask_witness_counts: tuple[int, ...]
    unique_minimal_mask_counts: tuple[int, ...]
    indispensable_category_counts: tuple[int, ...]
    singleton_signature_counts: tuple[int, ...]
    singleton_route_count_counts: tuple[int, ...]
    item_failure_tag_call_deck_counts: tuple[int, ...]
    supporter_failure_gnh_deck_counts: tuple[int, ...]
    monotonicity_violations: int

    def mask_label(self, mask: int) -> str:
        names = [name for bit, name in OUTPUTS if mask & bit]
        return "+".join(names) if names else "none"


def _state_succeeds_with_mask(raw_state, output_mask: int) -> bool:
    """Replay the existing planner with a restricted Secret Box output mask."""

    hand, remaining, active, top_five = raw_state
    picks = [None]
    if active == "Jirachi":
        picks.extend(sorted(set(top_five) & STELLAR_TRAINERS))

    for pick in picks:
        candidate_hand = hand.copy()
        candidate_deck = remaining.copy()
        if pick is not None:
            candidate_hand[pick] += 1
            candidate_deck[pick] -= 1
            if candidate_deck[pick] == 0:
                del candidate_deck[pick]

        state = (
            _compress_hand(candidate_hand.elements()),
            _compress_deck(candidate_deck.elements()),
            False,
            False,
            False,
            active == "Bunnelby",
            active == "Fan Rotom",
        )
        if _core_possible(state, output_mask):
            return True

    return False


def analyze_output_dependencies(
    trials: int,
    *,
    seed: int = 20261007,
) -> OutputDependencyResult:
    """Audit all 16 Secret Box output subsets on paired incremental states."""

    rng = random.Random(seed)
    baseline_successes = 0
    full_output_successes = 0
    incremental_successes = 0
    minimum_category_counts = [0] * 5
    mask_success_counts = [0] * 16
    minimal_mask_witness_counts = [0] * 16
    unique_minimal_mask_counts = [0] * 16
    indispensable = [0] * len(OUTPUTS)
    singleton_signatures = [0] * 16
    singleton_route_counts = [0] * 5
    item_failure_tag_call_counts = [0] * 5
    supporter_failure_gnh_counts = [0] * 5
    monotonicity_violations = 0

    for _ in range(trials):
        while True:
            order = rng.sample(range(60), 60)
            baseline_state = _raw_state(BASE_DECK, order)
            if baseline_state is not None:
                break

        secret_state = _raw_state(SECRET_BOX_DECK, order)
        if secret_state is None:
            raise AssertionError("ACE SPEC substitution changed setup acceptance")

        baseline_ok = _state_succeeds(baseline_state)
        full_ok = _state_succeeds_with_mask(
            secret_state,
            BOX_ALL_OUTPUTS,
        )
        baseline_successes += int(baseline_ok)
        full_output_successes += int(full_ok)

        if baseline_ok or not full_ok:
            continue

        incremental_successes += 1
        outcomes = tuple(
            _state_succeeds_with_mask(secret_state, mask)
            for mask in range(16)
        )
        if not outcomes[BOX_ALL_OUTPUTS]:
            raise AssertionError("full-output state changed during audit")

        for mask, success in enumerate(outcomes):
            if success:
                mask_success_counts[mask] += 1

        successful_masks = [
            mask for mask, success in enumerate(outcomes) if success
        ]
        minimum = min(mask.bit_count() for mask in successful_masks)
        minimum_category_counts[minimum] += 1
        minimal_masks = [
            mask
            for mask in successful_masks
            if mask.bit_count() == minimum
        ]
        for mask in minimal_masks:
            minimal_mask_witness_counts[mask] += 1
        if len(minimal_masks) == 1:
            unique_minimal_mask_counts[minimal_masks[0]] += 1

        singleton_signature = 0
        for index, (bit, _name) in enumerate(OUTPUTS):
            if outcomes[bit]:
                singleton_signature |= bit
            if not outcomes[BOX_ALL_OUTPUTS ^ bit]:
                indispensable[index] += 1
        singleton_signatures[singleton_signature] += 1
        singleton_route_counts[singleton_signature.bit_count()] += 1

        if not outcomes[BOX_ITEM_OUTPUT]:
            item_failure_tag_call_counts[remaining["Tag Call"]] += 1
        if not outcomes[BOX_SUPPORTER_OUTPUT]:
            supporter_failure_gnh_counts[remaining["Guzma & Hala"]] += 1

        for mask, success in enumerate(outcomes):
            if not success:
                continue
            for superset in range(16):
                if mask & superset == mask and not outcomes[superset]:
                    monotonicity_violations += 1
                    break

    return OutputDependencyResult(
        trials=trials,
        baseline_successes=baseline_successes,
        full_output_successes=full_output_successes,
        incremental_successes=incremental_successes,
        minimum_category_counts=tuple(minimum_category_counts),
        mask_success_counts=tuple(mask_success_counts),
        minimal_mask_witness_counts=tuple(minimal_mask_witness_counts),
        unique_minimal_mask_counts=tuple(unique_minimal_mask_counts),
        indispensable_category_counts=tuple(indispensable),
        singleton_signature_counts=tuple(singleton_signatures),
        singleton_route_count_counts=tuple(singleton_route_counts),
        item_failure_tag_call_deck_counts=tuple(
            item_failure_tag_call_counts
        ),
        supporter_failure_gnh_deck_counts=tuple(
            supporter_failure_gnh_counts
        ),
        monotonicity_violations=monotonicity_violations,
    )


def main() -> None:
    result = analyze_output_dependencies(100_000)

    print(f"trials={result.trials}")
    print(f"baseline_successes={result.baseline_successes}")
    print(f"full_output_successes={result.full_output_successes}")
    print(f"incremental_successes={result.incremental_successes}")
    print(f"minimum_category_counts={result.minimum_category_counts}")
    print(
        "indispensable_category_counts="
        f"{dict((OUTPUTS[i][1], count) for i, count in enumerate(result.indispensable_category_counts))}"
    )
    print(f"monotonicity_violations={result.monotonicity_violations}")

    print("mask_success_counts:")
    for mask, count in enumerate(result.mask_success_counts):
        print(f"  {mask:02d} {result.mask_label(mask):28s} {count}")

    print("minimal_mask_witness_counts:")
    for mask, count in enumerate(result.minimal_mask_witness_counts):
        if count:
            print(f"  {mask:02d} {result.mask_label(mask):28s} {count}")


if __name__ == "__main__":
    main()
