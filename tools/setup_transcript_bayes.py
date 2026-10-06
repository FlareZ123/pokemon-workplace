from __future__ import annotations

import argparse
import json
import math
import os
import tempfile
from itertools import product
from pathlib import Path
from typing import Any, Callable, Iterable, Sequence

KeepPolicy = Callable[[tuple[int, ...]], float]


def _choose(n: int, k: int) -> int:
    if k < 0 or k > n:
        return 0
    return math.comb(n, k)


def _validate(
    deck_size: int,
    forced_starters: int,
    tracked_group_sizes: Sequence[int],
    hand_size: int,
) -> tuple[int, ...]:
    groups = tuple(tracked_group_sizes)
    if deck_size <= 0:
        raise ValueError("deck_size must be positive")
    if forced_starters < 0 or any(size < 0 for size in groups):
        raise ValueError("card counts must be nonnegative")
    if forced_starters + sum(groups) > deck_size:
        raise ValueError("tracked counts exceed deck size")
    if not 0 <= hand_size <= deck_size:
        raise ValueError("hand_size must be between 0 and deck_size")
    return groups


def rejected_pattern_probability(
    deck_size: int,
    forced_starters: int,
    tracked_group_sizes: Sequence[int],
    keep_policy: KeepPolicy,
    pattern: Sequence[int],
    *,
    hand_size: int = 7,
) -> float:
    groups = _validate(deck_size, forced_starters, tracked_group_sizes, hand_size)
    counts = tuple(pattern)
    if len(counts) != len(groups):
        raise ValueError("pattern length must match tracked groups")
    if any(count < 0 or count > size for count, size in zip(counts, groups)):
        return 0.0
    filler = deck_size - forced_starters - sum(groups)
    filler_in_hand = hand_size - sum(counts)
    if not 0 <= filler_in_hand <= filler:
        return 0.0

    ways = _choose(filler, filler_in_hand)
    for size, count in zip(groups, counts):
        ways *= _choose(size, count)
    if ways == 0:
        return 0.0

    keep_probability = float(keep_policy(counts))
    if not 0.0 <= keep_probability <= 1.0:
        raise ValueError("keep_policy must return a value between 0 and 1")
    reject_probability = 1.0 - keep_probability
    return ways * reject_probability / _choose(deck_size, hand_size)


def rejection_probability(
    deck_size: int,
    forced_starters: int,
    tracked_group_sizes: Sequence[int],
    keep_policy: KeepPolicy,
    *,
    hand_size: int = 7,
) -> float:
    groups = _validate(deck_size, forced_starters, tracked_group_sizes, hand_size)
    total = 0.0
    ranges = [range(min(size, hand_size) + 1) for size in groups]
    for counts in product(*ranges):
        total += rejected_pattern_probability(
            deck_size,
            forced_starters,
            groups,
            keep_policy,
            counts,
            hand_size=hand_size,
        )
    return total


def acceptance_probability(
    deck_size: int,
    forced_starters: int,
    tracked_group_sizes: Sequence[int],
    keep_policy: KeepPolicy,
    *,
    hand_size: int = 7,
) -> float:
    return 1.0 - rejection_probability(
        deck_size,
        forced_starters,
        tracked_group_sizes,
        keep_policy,
        hand_size=hand_size,
    )


def group_seen_given_rejection(
    deck_size: int,
    forced_starters: int,
    tracked_group_sizes: Sequence[int],
    keep_policy: KeepPolicy,
    group_index: int,
    *,
    hand_size: int = 7,
) -> float:
    groups = tuple(tracked_group_sizes)
    if not 0 <= group_index < len(groups):
        raise ValueError("group_index out of range")
    rejected = rejection_probability(
        deck_size,
        forced_starters,
        groups,
        keep_policy,
        hand_size=hand_size,
    )
    if rejected == 0.0:
        raise ValueError("policy produces no revealed mulligans")

    seen = 0.0
    ranges = [range(min(size, hand_size) + 1) for size in groups]
    for counts in product(*ranges):
        if counts[group_index] <= 0:
            continue
        seen += rejected_pattern_probability(
            deck_size,
            forced_starters,
            groups,
            keep_policy,
            counts,
            hand_size=hand_size,
        )
    return seen / rejected


def group_ever_seen_before_acceptance(
    deck_size: int,
    forced_starters: int,
    tracked_group_sizes: Sequence[int],
    keep_policy: KeepPolicy,
    group_index: int,
    *,
    hand_size: int = 7,
) -> float:
    groups = tuple(tracked_group_sizes)
    rejected = rejection_probability(
        deck_size,
        forced_starters,
        groups,
        keep_policy,
        hand_size=hand_size,
    )
    accepted = 1.0 - rejected
    conditional_seen = group_seen_given_rejection(
        deck_size,
        forced_starters,
        groups,
        keep_policy,
        group_index,
        hand_size=hand_size,
    )
    reject_seen = rejected * conditional_seen
    return reject_seen / (accepted + reject_seen)


def transcript_likelihood(
    deck_size: int,
    forced_starters: int,
    tracked_group_sizes: Sequence[int],
    keep_policy: KeepPolicy,
    rejected_patterns: Iterable[Sequence[int]],
    *,
    hand_size: int = 7,
) -> float:
    groups = tuple(tracked_group_sizes)
    likelihood = acceptance_probability(
        deck_size,
        forced_starters,
        groups,
        keep_policy,
        hand_size=hand_size,
    )
    for pattern in rejected_patterns:
        likelihood *= rejected_pattern_probability(
            deck_size,
            forced_starters,
            groups,
            keep_policy,
            pattern,
            hand_size=hand_size,
        )
    return likelihood


def normalized_posterior(
    likelihoods: dict[str, float], priors: dict[str, float] | None = None
) -> dict[str, float]:
    if priors is None:
        priors = {name: 1.0 for name in likelihoods}
    if set(priors) != set(likelihoods):
        raise ValueError("priors and likelihoods must use the same names")
    weighted = {name: likelihoods[name] * priors[name] for name in likelihoods}
    total = sum(weighted.values())
    if total <= 0.0:
        raise ValueError("evidence has zero total likelihood")
    return {name: value / total for name, value in weighted.items()}


def build_examples() -> dict[str, Any]:
    deck_size = 60
    forced = 4
    groups = (2, 2, 4)

    decline_all = lambda counts: 0.0
    accept_doll = lambda counts: float(counts[1] > 0)
    accept_any_optional = lambda counts: float(counts[0] + counts[1] > 0)

    policies = {
        "decline_all_optional_only": decline_all,
        "accept_if_doll_present": accept_doll,
        "accept_any_optional_only": accept_any_optional,
    }

    policy_rows = {}
    for name, policy in policies.items():
        reject = rejection_probability(deck_size, forced, groups, policy)
        policy_rows[name] = {
            "rejection_probability": reject,
            "acceptance_probability": 1.0 - reject,
            "manectric_seen_given_rejection": group_seen_given_rejection(
                deck_size, forced, groups, policy, 0
            ),
            "doll_seen_given_rejection": group_seen_given_rejection(
                deck_size, forced, groups, policy, 1
            ),
            "diagnostic_x_seen_given_rejection": group_seen_given_rejection(
                deck_size, forced, groups, policy, 2
            ),
            "diagnostic_x_ever_seen_before_acceptance": group_ever_seen_before_acceptance(
                deck_size, forced, groups, policy, 2
            ),
        }

    count_posteriors = {}
    for k in (0, 1, 2, 3):
        likelihoods = {}
        for name, policy in {
            "decline_all": decline_all,
            "accept_any_optional": accept_any_optional,
        }.items():
            reject = rejection_probability(deck_size, forced, groups, policy)
            likelihoods[name] = reject**k * (1.0 - reject)
        count_posteriors[str(k)] = normalized_posterior(likelihoods)

    pattern = (1, 0, 0)
    pattern_likelihoods = {
        "decline_all": transcript_likelihood(
            deck_size, forced, groups, decline_all, (pattern,)
        ),
        "accept_any_optional": transcript_likelihood(
            deck_size, forced, groups, accept_any_optional, (pattern,)
        ),
    }

    return {
        "scope": "60-card setup transcript; 4 forced Basics; tracked groups are 2 Manectric, 2 Snorlax Doll, 4 unrelated diagnostic X",
        "policy_visibility": policy_rows,
        "mulligan_count_policy_posterior_equal_prior": count_posteriors,
        "revealed_pattern": {
            "pattern": list(pattern),
            "likelihoods": pattern_likelihoods,
            "posterior": normalized_posterior(pattern_likelihoods),
        },
    }


def atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lock_path = path.with_suffix(path.suffix + ".lock")
    with lock_path.open("a+b") as lock_file:
        if os.name == "nt":
            import msvcrt
            msvcrt.locking(lock_file.fileno(), msvcrt.LK_LOCK, 1)
        else:
            import fcntl
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
        tmp_path: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w", encoding="utf-8", dir=path.parent, delete=False
            ) as tmp_file:
                json.dump(payload, tmp_file, indent=2, ensure_ascii=False)
                tmp_file.write("\n")
                tmp_file.flush()
                os.fsync(tmp_file.fileno())
                tmp_path = Path(tmp_file.name)
            os.replace(tmp_path, path)
        finally:
            if tmp_path is not None and tmp_path.exists():
                tmp_path.unlink()


def main() -> None:
    parser = argparse.ArgumentParser(description="Exact Bayesian model of revealed setup transcripts.")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results/setup_transcript_bayes/model_examples.json"),
    )
    args = parser.parse_args()
    payload = build_examples()
    atomic_write_json(args.output, payload)
    print(json.dumps(payload, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
