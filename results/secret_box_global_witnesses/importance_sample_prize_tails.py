"""Conditionally sample rare Prize layouts that naive Monte Carlo misses.

For each specified non-Basic Prize set, sample a uniformly random complete
60-card permutation conditional on those exact cards lying in the six Prize
positions and the seven-card starting hand containing a Basic Pokémon.

Compare the same physical order for the Grand Tree and Secret Box decks.
Weight conditional state frequencies by independently derived exact Prize
event probabilities; these estimates remain first-turn-core model outputs.
"""

from collections import Counter
from fractions import Fraction
from pathlib import Path
import random
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))

from accepted_opening_prize_probabilities import (
    fixed_nonbasic_prized_given_valid_opener,
)
from aichi_vileplume_als import BASICS
from aichi_secret_box_output_dependencies import _state_succeeds_with_mask
from aichi_vileplume_secret_box import (
    BASE_DECK, SECRET_BOX_DECK,
    _raw_state, _state_succeeds,
)


PRIZE_EVENTS = (
    ("four_tag_call", ("Tag Call",) * 4),
    ("four_guzma_hala", ("Guzma & Hala",) * 4),
    (
        "six_other_tool_stadium",
        ("Stealthy Hood",) * 3 + ("Counter Gain",)
        + ("Artazon",) * 2,
    ),
)

ALL_BASICS = sum(BASE_DECK.count(name) for name in BASICS)


def forced_indices(named_cards: tuple[str, ...]) -> tuple[int, ...]:
    """Select unique physical instances of each forced Prize identity."""
    pool = list(enumerate(BASE_DECK))
    result = []
    for name in named_cards:
        match = next(
            (index for index, card in pool if card == name), None
        )
        if match is None:
            raise ValueError(f"forced Prize identity missing: {name}")
        result.append(match)
        pool = [(index, card) for index, card in pool if index != match]
    assert len(result) == len(set(result))
    assert all(BASE_DECK[i] not in BASICS for i in result)
    return tuple(result)


def conditioned_order(
    rng: random.Random,
    required: tuple[int, ...],
) -> tuple[int, ...]:
    """Rejection sample valid opening uniformly given fixed Prize slots."""
    remaining = [
        i for i in range(60) if i not in required
    ]
    while True:
        rng.shuffle(remaining)
        extras = remaining[:6-len(required)]
        non_prizes = remaining[6-len(required):]
        # Shuffle non-Prize positions separately for an unbiased opener.
        rng.shuffle(non_prizes)
        if not any(BASE_DECK[i] in BASICS for i in non_prizes[:7]):
            continue
        prize_order = list(required) + extras
        rng.shuffle(prize_order)
        order = tuple(non_prizes[:7] + prize_order + non_prizes[7:])
        assert len(order) == len(set(order)) == 60
        return order


def sample_case(label: str, named: tuple[str, ...], trials: int) -> dict:
    rng = random.Random(20261010 + len(named) * 17 + len(label))
    required = forced_indices(named)
    exact_event = fixed_nonbasic_prized_given_valid_opener(
        cards=60, basics=ALL_BASICS, opening=7,
        prizes=6, forced_nonbasic=len(required),
    )
    totals = Counter()

    for _ in range(trials):
        order = conditioned_order(rng, required)
        assert set(required).issubset(set(order[7:13]))
        baseline = _raw_state(BASE_DECK, order)
        secret = _raw_state(SECRET_BOX_DECK, order)
        assert baseline is not None and secret is not None
        if _state_succeeds(baseline):
            totals["baseline_success"] += 1
            continue
        if not _state_succeeds_with_mask(secret, 15):
            continue
        totals["incremental"] += 1
        required_mask = 0
        for bit in (1, 2, 4, 8):
            if not _state_succeeds_with_mask(secret, 15 ^ bit):
                totals[f"requires_{bit}"] += 1
                required_mask |= bit
        totals[f"requirement_signature_{required_mask}"] += 1

    joint_incremental = exact_event * Fraction(
        totals["incremental"], trials
    )
    return {
        "event": label,
        "forced_cards": named,
        "accepted_trials": trials,
        "exact_event_probability": str(exact_event),
        "incremental_conditional": totals["incremental"],
        "conditional_signatures": dict(sorted(totals.items())),
        "estimated_unconditional_incremental": str(joint_incremental),
        "estimated_per_million_accepted": float(
            joint_incremental * 1_000_000
        ),
    }


def main(trials: int = 20_000) -> None:
    assert len(BASE_DECK) == len(SECRET_BOX_DECK) == 60
    assert ALL_BASICS == 14
    for label, names in PRIZE_EVENTS:
        result = sample_case(label, names, trials)
        print(result)
        assert result["accepted_trials"] == trials
        assert result["incremental_conditional"] >= 0
    print("Conditional rare-Prize sampling checks passed.")


if __name__ == "__main__":
    main()
