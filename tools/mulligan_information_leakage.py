from __future__ import annotations

import argparse
import json
import math
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


@dataclass(frozen=True)
class MulliganModel:
    name: str
    forced_basics: int
    diagnostic_cards: int
    deck_size: int = 60
    hand_size: int = 7

    def __post_init__(self) -> None:
        if self.deck_size <= 0:
            raise ValueError("deck_size must be positive")
        if not 0 <= self.hand_size <= self.deck_size:
            raise ValueError("hand_size must be between 0 and deck_size")
        if not 0 <= self.forced_basics <= self.deck_size:
            raise ValueError("forced_basics must be between 0 and deck_size")
        if not 0 <= self.diagnostic_cards <= self.deck_size - self.forced_basics:
            raise ValueError("diagnostic_cards must fit outside the forced-Basic group")


def _ratio(numerator: int, denominator: int) -> float:
    return numerator / denominator


def mulligan_probability(model: MulliganModel) -> float:
    return _ratio(
        math.comb(model.deck_size - model.forced_basics, model.hand_size),
        math.comb(model.deck_size, model.hand_size),
    )


def acceptance_probability(model: MulliganModel) -> float:
    return 1.0 - mulligan_probability(model)


def expected_failed_mulligans(model: MulliganModel) -> float:
    reject = mulligan_probability(model)
    accept = 1.0 - reject
    return reject / accept


def rejected_hand_exact_diagnostic_probability(
    model: MulliganModel, diagnostic_count: int
) -> float:
    if diagnostic_count < 0 or diagnostic_count > model.hand_size:
        return 0.0
    if diagnostic_count > model.diagnostic_cards:
        return 0.0
    filler = model.deck_size - model.forced_basics - model.diagnostic_cards
    filler_needed = model.hand_size - diagnostic_count
    if filler_needed < 0 or filler_needed > filler:
        return 0.0
    favorable = math.comb(model.diagnostic_cards, diagnostic_count) * math.comb(
        filler, filler_needed
    )
    return _ratio(favorable, math.comb(model.deck_size, model.hand_size))


def conditional_diagnostic_count_given_mulligan(
    model: MulliganModel, diagnostic_count: int
) -> float:
    return rejected_hand_exact_diagnostic_probability(
        model, diagnostic_count
    ) / mulligan_probability(model)


def diagnostic_seen_given_mulligan(model: MulliganModel) -> float:
    no_diagnostic = conditional_diagnostic_count_given_mulligan(model, 0)
    return 1.0 - no_diagnostic


def ever_diagnostic_before_acceptance(model: MulliganModel) -> float:
    reject_without_diagnostic = rejected_hand_exact_diagnostic_probability(model, 0)
    reject_with_diagnostic = mulligan_probability(model) - reject_without_diagnostic
    return reject_with_diagnostic / (1.0 - reject_without_diagnostic)


def exact_mulligan_count_probability(model: MulliganModel, mulligans: int) -> float:
    if mulligans < 0:
        raise ValueError("mulligans must be nonnegative")
    reject = mulligan_probability(model)
    return reject**mulligans * (1.0 - reject)


def revealed_sequence_likelihood(
    model: MulliganModel, diagnostic_counts: Iterable[int]
) -> float:
    likelihood = acceptance_probability(model)
    for diagnostic_count in diagnostic_counts:
        likelihood *= rejected_hand_exact_diagnostic_probability(model, diagnostic_count)
    return likelihood


def normalized_posterior(
    likelihoods: dict[str, float], priors: dict[str, float] | None = None
) -> dict[str, float]:
    if priors is None:
        priors = {name: 1.0 for name in likelihoods}
    if set(priors) != set(likelihoods):
        raise ValueError("priors and likelihoods must use the same model names")
    weighted = {name: likelihoods[name] * priors[name] for name in likelihoods}
    total = sum(weighted.values())
    if total <= 0:
        raise ValueError("evidence has zero total likelihood")
    return {name: value / total for name, value in weighted.items()}


def posterior_from_mulligan_count(
    models: Iterable[MulliganModel], mulligans: int, priors: dict[str, float] | None = None
) -> dict[str, float]:
    model_list = list(models)
    likelihoods = {
        model.name: exact_mulligan_count_probability(model, mulligans)
        for model in model_list
    }
    return normalized_posterior(likelihoods, priors)


def posterior_from_revealed_sequence(
    models: Iterable[MulliganModel],
    diagnostic_counts: Iterable[int],
    priors: dict[str, float] | None = None,
) -> dict[str, float]:
    counts = tuple(diagnostic_counts)
    model_list = list(models)
    likelihoods = {
        model.name: revealed_sequence_likelihood(model, counts) for model in model_list
    }
    return normalized_posterior(likelihoods, priors)


def model_summary(model: MulliganModel) -> dict[str, Any]:
    return {
        "name": model.name,
        "deck_size": model.deck_size,
        "hand_size": model.hand_size,
        "forced_basics": model.forced_basics,
        "diagnostic_cards": model.diagnostic_cards,
        "mulligan_probability": mulligan_probability(model),
        "expected_failed_mulligans": expected_failed_mulligans(model),
        "diagnostic_seen_given_mulligan": diagnostic_seen_given_mulligan(model),
        "ever_diagnostic_before_acceptance": ever_diagnostic_before_acceptance(model),
    }


def build_examples() -> dict[str, Any]:
    density_models = [
        MulliganModel("4 Basics / 4 diagnostic", 4, 4),
        MulliganModel("8 Basics / 4 diagnostic", 8, 4),
        MulliganModel("12 Basics / 4 diagnostic", 12, 4),
        MulliganModel("1 Basic / 4 diagnostic", 1, 4),
    ]

    low_basic = MulliganModel("4-Basic candidate", 4, 4)
    high_basic = MulliganModel("12-Basic candidate", 12, 4)
    count_posteriors = {
        str(k): posterior_from_mulligan_count((low_basic, high_basic), k)
        for k in (0, 1, 2, 3, 5)
    }

    four_copy = MulliganModel("4-copy diagnostic", 4, 4)
    two_copy = MulliganModel("2-copy diagnostic", 4, 2)
    sequence_posteriors = {
        "one_mulligan_one_copy_then_accept": posterior_from_revealed_sequence(
            (four_copy, two_copy), (1,)
        ),
        "two_mulligans_one_copy_each_then_accept": posterior_from_revealed_sequence(
            (four_copy, two_copy), (1, 1)
        ),
        "one_mulligan_two_copies_then_accept": posterior_from_revealed_sequence(
            (four_copy, two_copy), (2,)
        ),
        "two_mulligans_zero_copies_then_accept": posterior_from_revealed_sequence(
            (four_copy, two_copy), (0, 0)
        ),
    }

    singleton = MulliganModel("4 Basics / singleton diagnostic", 4, 1)

    return {
        "scope": "stationary forced-Basic setup policy; 60-card deck and 7-card opening unless overridden",
        "density_examples": [model_summary(model) for model in density_models],
        "mulligan_count_bayes_equal_prior": {
            "candidates": [model_summary(low_basic), model_summary(high_basic)],
            "posterior_by_exact_failed_mulligans": count_posteriors,
        },
        "revealed_content_bayes_equal_prior": {
            "candidates": [model_summary(four_copy), model_summary(two_copy)],
            "posterior_by_sequence": sequence_posteriors,
        },
        "singleton_example": model_summary(singleton),
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
    parser = argparse.ArgumentParser(
        description="Exact mulligan-count and revealed-hand information model."
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results/mulligan_information_leakage/model_examples.json"),
    )
    args = parser.parse_args()
    payload = build_examples()
    atomic_write_json(args.output, payload)
    print(json.dumps(payload, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
