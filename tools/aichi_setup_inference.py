from __future__ import annotations

import argparse
import json
import math
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any



VILEPLUME_NONBASIC_COUNTS: dict[str, int] = {
    "Pidgeotto": 2,
    "Pidgeot ex": 2,
    "Gloom": 2,
    "Vileplume": 2,
    "Vileplume-GX": 1,
    "Herdier": 2,
    "Stoutland": 1,
    "Guzma & Hala": 4,
    "Guzma": 2,
    "Cassius": 1,
    "Karen": 1,
    "Plumeria": 1,
    "Gladion": 1,
    "Faba": 1,
    "Lusamine": 1,
    "Bellelba & Brycen-Man": 1,
    "Peonia": 1,
    "Team Yell's Cheer": 1,
    "Tag Call": 4,
    "Stealthy Hood": 3,
    "Technical Machine: Evolution": 2,
    "Counter Gain": 1,
    "Artazon": 2,
    "Grand Tree": 1,
    "Capture Energy": 2,
    "Jet Energy": 2,
    "Memory Energy": 1,
    "Grass Energy": 1,
}

KAZUMA_IRON_NONBASIC_COUNTS: dict[str, int] = {
    "Plumeria": 4,
    "Guzma": 3,
    "Guzma & Hala": 2,
    "Team Flare Grunt": 2,
    "Lusamine": 2,
    "Cynthia & Caitlin": 1,
    "Team Skull Grunt": 1,
    "Faba": 1,
    "Eri": 1,
    "Sidney": 1,
    "Gladion": 1,
    "Lillie's Determination": 1,
    "Team Rocket's Handiwork": 1,
    "Crushing Hammer": 4,
    "Trainers' Mail": 3,
    "VS Seeker": 3,
    "Tag Call": 2,
    "Enhanced Hammer": 2,
    "Camping Gear": 2,
    "Palace Book": 1,
    "Captivating Poké Puff": 1,
    "Echoing Horn": 1,
    "Megaton Blower": 1,
    "Handheld Fan": 1,
    "Tool Jammer": 1,
    "Palace Belt": 1,
    "Tropical Beach": 1,
    "Player's Ceremony": 1,
    "Thunder Mountain ♢": 1,
    "Wondrous Labyrinth ♢": 1,
    "Speed Lightning Energy": 4,
    "Capture Energy": 2,
    "Spiky Energy": 1,
    "Double Colorless Energy": 1,
}

RYOYA_IRON_NONBASIC_COUNTS: dict[str, int] = {
    "Plumeria": 4,
    "Lusamine": 2,
    "Guzma & Hala": 2,
    "Guzma": 2,
    "Sidney": 2,
    "Eri": 2,
    "Team Flare Grunt": 2,
    "Cynthia & Caitlin": 1,
    "Bellelba & Brycen-Man": 1,
    "Team Skull Grunt": 1,
    "Faba": 1,
    "N": 1,
    "Lillie's Determination": 1,
    "Gladion": 1,
    "Xerosic's Machinations": 1,
    "Trainers' Mail": 4,
    "VS Seeker": 3,
    "Nest Ball": 2,
    "Tag Call": 2,
    "Enhanced Hammer": 2,
    "Palace Book": 2,
    "Heavy Ball": 1,
    "Megaton Blower": 1,
    "Handheld Fan": 2,
    "Tool Jammer": 1,
    "Player's Ceremony": 2,
    "Thunder Mountain ♢": 1,
    "Wondrous Labyrinth ♢": 1,
    "Speed Lightning Energy": 4,
    "Double Colorless Energy": 3,
    "Capture Energy": 1,
}

KOHEI_IRON_NONBASIC_COUNTS: dict[str, int] = {
    "Plumeria": 4,
    "Guzma": 3,
    "Team Flare Grunt": 2,
    "Guzma & Hala": 2,
    "Lusamine": 2,
    "Faba": 1,
    "Cynthia & Caitlin": 1,
    "Eri": 1,
    "Sidney": 1,
    "Team Skull Grunt": 1,
    "Team Rocket's Handiwork": 1,
    "Peonia": 1,
    "Lillie's Determination": 1,
    "Crushing Hammer": 4,
    "VS Seeker": 3,
    "Trainers' Mail": 2,
    "Camping Gear": 2,
    "Tag Call": 2,
    "Enhanced Hammer": 1,
    "Captivating Poké Puff": 1,
    "Target Whistle": 1,
    "Field Blower": 1,
    "Megaton Blower": 1,
    "Palace Belt": 2,
    "Handheld Fan": 1,
    "Tool Jammer": 1,
    "Tropical Beach": 2,
    "Player's Ceremony": 1,
    "Thunder Mountain ♢": 1,
    "Wondrous Labyrinth ♢": 1,
    "Speed Lightning Energy": 4,
    "Capture Energy": 2,
    "Spiky Energy": 1,
    "Double Colorless Energy": 1,
}


def shared_name_copy_counts(
    left_counts: dict[str, int],
    right_counts: dict[str, int],
) -> tuple[int, int]:
    shared_names = set(left_counts) & set(right_counts)
    return (
        sum(left_counts[name] for name in shared_names),
        sum(right_counts[name] for name in shared_names),
    )


def left_copies_shared_with_family(
    left_counts: dict[str, int],
    right_family: tuple[dict[str, int], ...],
) -> int:
    right_names: set[str] = set()
    for counts in right_family:
        right_names.update(counts)
    return sum(
        copies for name, copies in left_counts.items() if name in right_names
    )


if sum(VILEPLUME_NONBASIC_COUNTS.values()) != 46:
    raise AssertionError("Vileplume non-Basic transcription must total 46 cards")
for _iron_counts in (
    KAZUMA_IRON_NONBASIC_COUNTS,
    RYOYA_IRON_NONBASIC_COUNTS,
    KOHEI_IRON_NONBASIC_COUNTS,
):
    if sum(_iron_counts.values()) != 56:
        raise AssertionError("Iron Thorns non-Basic transcription must total 56 cards")


@dataclass(frozen=True)
class ExactListCandidate:
    name: str
    forced_basics: int
    common_nonbasic_cards: int
    deck_size: int = 60
    hand_size: int = 7


def _choose(n: int, k: int) -> int:
    if k < 0 or k > n:
        return 0
    return math.comb(n, k)


def mulligan_probability(candidate: ExactListCandidate) -> float:
    return _choose(
        candidate.deck_size - candidate.forced_basics,
        candidate.hand_size,
    ) / _choose(candidate.deck_size, candidate.hand_size)


def acceptance_probability(candidate: ExactListCandidate) -> float:
    return 1.0 - mulligan_probability(candidate)


def common_only_mulligan_probability(candidate: ExactListCandidate) -> float:
    return _choose(
        candidate.common_nonbasic_cards,
        candidate.hand_size,
    ) / _choose(candidate.deck_size, candidate.hand_size)


def common_only_given_mulligan(candidate: ExactListCandidate) -> float:
    return common_only_mulligan_probability(candidate) / mulligan_probability(candidate)


def unique_name_exposed_before_acceptance(candidate: ExactListCandidate) -> float:
    reject = mulligan_probability(candidate)
    common_only = common_only_mulligan_probability(candidate)
    unique_reject = reject - common_only
    return unique_reject / (1.0 - common_only)


def exact_count_classification_accuracy(
    left: ExactListCandidate,
    right: ExactListCandidate,
    *,
    left_prior: float = 0.5,
    right_prior: float = 0.5,
    tolerance: float = 1e-15,
) -> float:
    if not math.isclose(left_prior + right_prior, 1.0):
        raise ValueError("priors must sum to 1")
    left_reject = mulligan_probability(left)
    right_reject = mulligan_probability(right)
    left_accept = 1.0 - left_reject
    right_accept = 1.0 - right_reject

    accuracy = 0.0
    k = 0
    while True:
        left_joint = left_prior * left_reject**k * left_accept
        right_joint = right_prior * right_reject**k * right_accept
        accuracy += max(left_joint, right_joint)
        remaining = (
            left_prior * left_reject ** (k + 1)
            + right_prior * right_reject ** (k + 1)
        )
        if remaining < tolerance:
            return accuracy
        k += 1


def unique_content_classification_accuracy(
    left: ExactListCandidate,
    right: ExactListCandidate,
    *,
    left_prior: float = 0.5,
    right_prior: float = 0.5,
    tolerance: float = 1e-18,
) -> float:
    if not math.isclose(left_prior + right_prior, 1.0):
        raise ValueError("priors must sum to 1")

    left_unique = unique_name_exposed_before_acceptance(left)
    right_unique = unique_name_exposed_before_acceptance(right)
    accuracy = left_prior * left_unique + right_prior * right_unique

    left_common = common_only_mulligan_probability(left)
    right_common = common_only_mulligan_probability(right)
    left_accept = acceptance_probability(left)
    right_accept = acceptance_probability(right)

    k = 0
    while True:
        left_joint = left_prior * left_common**k * left_accept
        right_joint = right_prior * right_common**k * right_accept
        accuracy += max(left_joint, right_joint)
        remaining = (
            left_prior * (1.0 - left_unique) * left_common ** (k + 1)
            + right_prior * (1.0 - right_unique) * right_common ** (k + 1)
        )
        if remaining < tolerance:
            return accuracy
        k += 1



def family_unique_content_classification_accuracy(
    left: ExactListCandidate,
    right_variants: tuple[ExactListCandidate, ...],
    *,
    left_prior: float = 0.5,
    right_prior: float = 0.5,
    tolerance: float = 1e-18,
) -> float:
    if not right_variants:
        raise ValueError("at least one right-side variant is required")
    if not math.isclose(left_prior + right_prior, 1.0):
        raise ValueError("priors must sum to 1")

    right_weight = 1.0 / len(right_variants)
    left_unique = unique_name_exposed_before_acceptance(left)
    right_unique = sum(
        right_weight * unique_name_exposed_before_acceptance(variant)
        for variant in right_variants
    )
    accuracy = left_prior * left_unique + right_prior * right_unique

    left_common = common_only_mulligan_probability(left)
    left_accept = acceptance_probability(left)
    right_common = tuple(
        common_only_mulligan_probability(variant)
        for variant in right_variants
    )
    right_accept = tuple(
        acceptance_probability(variant)
        for variant in right_variants
    )

    k = 0
    while True:
        left_joint = left_prior * left_common**k * left_accept
        right_joint = right_prior * sum(
            right_weight * common**k * accepted
            for common, accepted in zip(right_common, right_accept)
        )
        accuracy += max(left_joint, right_joint)
        if max(left_joint, right_joint) < tolerance and k > 0:
            return accuracy
        k += 1

def posterior_left_after_exact_mulligans(
    left: ExactListCandidate,
    right: ExactListCandidate,
    mulligans: int,
    *,
    left_prior: float = 0.5,
    right_prior: float = 0.5,
) -> float:
    if mulligans < 0:
        raise ValueError("mulligans must be nonnegative")
    left_likelihood = (
        mulligan_probability(left) ** mulligans * acceptance_probability(left)
    )
    right_likelihood = (
        mulligan_probability(right) ** mulligans * acceptance_probability(right)
    )
    left_joint = left_prior * left_likelihood
    right_joint = right_prior * right_likelihood
    return left_joint / (left_joint + right_joint)


def build_aichi_examples() -> dict[str, Any]:
    vile_kazuma_common, kazuma_vile_common = shared_name_copy_counts(
        VILEPLUME_NONBASIC_COUNTS,
        KAZUMA_IRON_NONBASIC_COUNTS,
    )
    vileplume = ExactListCandidate(
        "Takahiro Ando Vileplume Control",
        forced_basics=14,
        common_nonbasic_cards=vile_kazuma_common,
    )
    iron_thorns = ExactListCandidate(
        "Kazuma Kashi Iron Thorns",
        forced_basics=4,
        common_nonbasic_cards=kazuma_vile_common,
    )

    equal_count_accuracy = exact_count_classification_accuracy(
        vileplume, iron_thorns
    )
    equal_content_accuracy = unique_content_classification_accuracy(
        vileplume, iron_thorns
    )

    iron_count_maps = (
        KAZUMA_IRON_NONBASIC_COUNTS,
        RYOYA_IRON_NONBASIC_COUNTS,
        KOHEI_IRON_NONBASIC_COUNTS,
    )
    vileplume_vs_iron_family = ExactListCandidate(
        "Takahiro Ando Vileplume Control vs Iron family",
        forced_basics=14,
        common_nonbasic_cards=left_copies_shared_with_family(
            VILEPLUME_NONBASIC_COUNTS,
            iron_count_maps,
        ),
    )
    iron_family = tuple(
        ExactListCandidate(
            name,
            4,
            shared_name_copy_counts(
                VILEPLUME_NONBASIC_COUNTS,
                counts,
            )[1],
        )
        for name, counts in zip(
            (
                "Kazuma Kashi Iron Thorns",
                "Ryoya Fujii Iron Thorns",
                "Kohei Hamamichi Iron Thorns",
            ),
            iron_count_maps,
        )
    )
    family_content_accuracy = family_unique_content_classification_accuracy(
        vileplume_vs_iron_family,
        iron_family,
    )

    return {
        "scope": (
            "Exact published 2026 CL Aichi Open League lists: "
            "runner-up Vileplume Control vs sixth-place Iron Thorns"
        ),
        "candidate_definitions": {
            vileplume.name: {
                "forced_basics": vileplume.forced_basics,
                "nonbasic_cards": vileplume.deck_size - vileplume.forced_basics,
                "common_name_nonbasic_copies": vileplume.common_nonbasic_cards,
                "mulligan_probability": mulligan_probability(vileplume),
                "common_only_given_mulligan": common_only_given_mulligan(vileplume),
                "unique_name_exposed_before_acceptance": (
                    unique_name_exposed_before_acceptance(vileplume)
                ),
            },
            iron_thorns.name: {
                "forced_basics": iron_thorns.forced_basics,
                "nonbasic_cards": iron_thorns.deck_size - iron_thorns.forced_basics,
                "common_name_nonbasic_copies": iron_thorns.common_nonbasic_cards,
                "mulligan_probability": mulligan_probability(iron_thorns),
                "common_only_given_mulligan": common_only_given_mulligan(iron_thorns),
                "unique_name_exposed_before_acceptance": (
                    unique_name_exposed_before_acceptance(iron_thorns)
                ),
            },
        },
        "iron_thorns_family_robustness": {
            "iron_variants": [
                {
                    "name": variant.name,
                    "forced_basics": variant.forced_basics,
                    "common_name_nonbasic_copies_with_vileplume": (
                        variant.common_nonbasic_cards
                    ),
                }
                for variant in iron_family
            ],
            "vileplume_common_name_nonbasic_copies_with_family": (
                vileplume_vs_iron_family.common_nonbasic_cards
            ),
            "equal_prior_unique_content_classification_accuracy": (
                family_content_accuracy
            ),
        },
        "equal_prior": {
            "posterior_iron_thorns_by_exact_mulligans": {
                str(k): 1.0
                - posterior_left_after_exact_mulligans(vileplume, iron_thorns, k)
                for k in range(6)
            },
            "count_only_classification_accuracy": equal_count_accuracy,
            "count_only_value_over_50_50": equal_count_accuracy - 0.5,
            "unique_content_classification_accuracy": equal_content_accuracy,
            "unique_content_value_over_50_50": equal_content_accuracy - 0.5,
            "increment_over_count_only": (
                equal_content_accuracy - equal_count_accuracy
            ),
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
                mode="w",
                encoding="utf-8",
                dir=path.parent,
                delete=False,
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
        description="Exact setup inference between two published Aichi lists."
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results/aichi_setup_inference/model_examples.json"),
    )
    args = parser.parse_args()
    payload = build_aichi_examples()
    atomic_write_json(args.output, payload)
    print(json.dumps(payload, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
