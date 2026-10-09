"""Independent labeled-index oracle for the mixed-class two-discard theorem."""

from fractions import Fraction
from itertools import permutations
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from mixed_random_discard_likelihood import mixed_class_two_discard_inference


def labeled_oracle(a: int, b: int, tagged: str, sequence: tuple[str, str]):
    hand = [tagged] + ["A"] * a + ["B"] * b
    ordered = tuple(permutations(range(len(hand)), 2))
    matches = tuple(
        indexes for indexes in ordered
        if tuple(hand[i] for i in indexes) == sequence
    )
    if not ordered:
        return Fraction(0), Fraction(0)
    return (
        Fraction(len(matches), len(ordered)),
        Fraction(sum(0 not in pair for pair in matches), len(ordered)),
    )


def main():
    checked = 0
    for a in range(6):
        for b in range(6):
            if a + b + 1 < 2:
                continue
            likelihood_a, surviving_a = labeled_oracle(a, b, "A", ("A", "B"))
            likelihood_b, surviving_b = labeled_oracle(a, b, "B", ("A", "B"))
            assert labeled_oracle(a, b, "A", ("B", "A")) == (
                likelihood_a, surviving_a,
            )
            assert labeled_oracle(a, b, "B", ("B", "A")) == (
                likelihood_b, surviving_b,
            )

            for prior in (
                Fraction(0), Fraction(1, 4), Fraction(2, 7),
                Fraction(1, 2), Fraction(1),
            ):
                evidence = prior * likelihood_a + (1 - prior) * likelihood_b
                if not evidence:
                    try:
                        mixed_class_two_discard_inference(a, b, prior_tag_a=prior)
                    except ValueError:
                        pass
                    else:
                        raise AssertionError("impossible observation was accepted")
                    continue
                exact_p = prior * likelihood_a / evidence
                exact_survival = (
                    prior * surviving_a + (1 - prior) * surviving_b
                ) / evidence
                output = mixed_class_two_discard_inference(
                    a, b, prior_tag_a=prior,
                )
                assert output.likelihood_tag_a == likelihood_a
                assert output.likelihood_tag_b == likelihood_b
                assert output.posterior_tag_a == exact_p
                assert output.posterior_tag_survives == exact_survival
                checked += 1

    for k in range(1, 6):
        prior = Fraction(2, 7)
        output = mixed_class_two_discard_inference(
            k, k, prior_tag_a=prior,
        )
        assert output.posterior_tag_a == prior
        assert output.posterior_tag_survives == Fraction(k, k + 1)

    left_heavy = mixed_class_two_discard_inference(
        2, 1, prior_tag_a=Fraction(2, 7),
    )
    assert left_heavy.posterior_tag_a == Fraction(3, 13)
    assert left_heavy.posterior_tag_survives == Fraction(7, 13)

    right_heavy = mixed_class_two_discard_inference(
        1, 2, prior_tag_a=Fraction(2, 7),
    )
    assert right_heavy.posterior_tag_a == Fraction(8, 23)
    assert right_heavy.posterior_tag_survives == Fraction(14, 23)

    print(f"Independent labeled-pair regression checked {checked} policies")
    print("Equal known counts cancel the mixed-discard information exactly")
    print("Unequal counts retain a nonunit likelihood ratio")


if __name__ == "__main__":
    main()
