from __future__ import annotations

import itertools
import math
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from setup_transcript_bayes import (  # noqa: E402
    acceptance_probability,
    build_examples,
    group_ever_seen_before_acceptance,
    group_seen_given_rejection,
    normalized_posterior,
    rejected_pattern_probability,
    rejection_probability,
    transcript_likelihood,
)


def exhaustive_rejected_patterns(
    deck_size: int,
    forced: int,
    groups: tuple[int, ...],
    hand_size: int,
    keep_policy,
) -> dict[tuple[int, ...], float]:
    cards = [("F", 0)] * forced
    for group_index, size in enumerate(groups):
        cards.extend(("G", group_index) for _ in range(size))
    cards.extend(("X", 0) for _ in range(deck_size - forced - sum(groups)))

    denominator = math.comb(deck_size, hand_size)
    weights: Counter[tuple[int, ...]] = Counter()
    for indices in itertools.combinations(range(deck_size), hand_size):
        hand = [cards[i] for i in indices]
        if any(kind == "F" for kind, _ in hand):
            continue
        counts = tuple(
            sum(kind == "G" and index == group_index for kind, index in hand)
            for group_index in range(len(groups))
        )
        reject_weight = 1.0 - float(keep_policy(counts))
        weights[counts] += reject_weight
    return {pattern: weight / denominator for pattern, weight in weights.items() if weight}


def assert_close(actual: float, expected: float, tol: float = 1e-12) -> None:
    if not math.isclose(actual, expected, rel_tol=tol, abs_tol=tol):
        raise AssertionError(f"{actual} != {expected}")


def main() -> None:
    small_groups = (2, 1, 2)
    selective = lambda counts: float(counts[1] > 0)
    brute = exhaustive_rejected_patterns(11, 2, small_groups, 3, selective)
    exact = {}
    for pattern in itertools.product(*(range(size + 1) for size in small_groups)):
        probability = rejected_pattern_probability(
            11, 2, small_groups, selective, pattern, hand_size=3
        )
        if probability:
            exact[pattern] = probability
    if set(brute) != set(exact):
        raise AssertionError((set(brute), set(exact)))
    for pattern in brute:
        assert_close(brute[pattern], exact[pattern])
    assert_close(
        sum(exact.values()),
        rejection_probability(11, 2, small_groups, selective, hand_size=3),
    )
    assert_close(
        1.0 - sum(exact.values()),
        acceptance_probability(11, 2, small_groups, selective, hand_size=3),
    )

    groups = (2, 2, 4)
    decline_all = lambda counts: 0.0
    accept_doll = lambda counts: float(counts[1] > 0)
    accept_any = lambda counts: float(counts[0] + counts[1] > 0)

    assert_close(
        group_seen_given_rejection(60, 4, groups, decline_all, 0),
        0.23636363636363633,
    )
    assert_close(
        group_seen_given_rejection(60, 4, groups, decline_all, 1),
        0.23636363636363633,
    )
    assert_close(group_seen_given_rejection(60, 4, groups, accept_doll, 1), 0.0)
    assert_close(group_seen_given_rejection(60, 4, groups, accept_any, 0), 0.0)
    assert_close(group_seen_given_rejection(60, 4, groups, accept_any, 1), 0.0)

    assert_close(
        group_seen_given_rejection(60, 4, groups, decline_all, 2),
        0.4231370306842005,
    )
    assert_close(
        group_seen_given_rejection(60, 4, groups, accept_doll, 2),
        0.4360017833935703,
    )
    assert_close(
        group_seen_given_rejection(60, 4, groups, accept_any, 2),
        0.4496444731738849,
    )
    assert_close(
        group_ever_seen_before_acceptance(60, 4, groups, decline_all, 2),
        0.3887644501857918,
    )
    assert_close(
        group_ever_seen_before_acceptance(60, 4, groups, accept_doll, 2),
        0.2696824545970048,
    )
    assert_close(
        group_ever_seen_before_acceptance(60, 4, groups, accept_any, 2),
        0.19244961978239736,
    )

    pattern = (1, 0, 0)
    likelihoods = {
        "decline_all": transcript_likelihood(
            60, 4, groups, decline_all, (pattern,)
        ),
        "accept_any": transcript_likelihood(
            60, 4, groups, accept_any, (pattern,)
        ),
    }
    posterior = normalized_posterior(likelihoods)
    assert likelihoods["decline_all"] > 0.0
    assert_close(likelihoods["accept_any"], 0.0)
    assert_close(posterior["decline_all"], 1.0)

    payload = build_examples()
    assert payload["policy_visibility"]
    print("All setup transcript Bayes checks passed.")
    print(
        "Diagnostic X conditional visibility, decline/selective/accept-any:",
        *(
            f"{100 * group_seen_given_rejection(60, 4, groups, p, 2):.9f}%"
            for p in (decline_all, accept_doll, accept_any)
        ),
    )


if __name__ == "__main__":
    main()
