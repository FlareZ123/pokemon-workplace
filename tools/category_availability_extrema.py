"""Sharp exact expectations under fixed marginal binary resource availability.

For four categories, a joint distribution over 16 availability masks is
constrained by five equalities: total mass and four Bernoulli marginals.
Linear objectives attain extrema at basic feasible solutions with at most
five supported masks. Enumerate all five-column bases exactly.
"""

from fractions import Fraction
from itertools import combinations
from numbers import Rational
from typing import Sequence


def _linear_solve(
    matrix: list[list[Fraction]],
    rhs: tuple[Fraction, ...],
) -> tuple[Fraction, ...] | None:
    size = len(rhs)
    augmented = [
        row.copy() + [value] for row, value in zip(matrix, rhs)
    ]
    for pivot_index in range(size):
        pivot_row = next(
            (
                i for i in range(pivot_index, size)
                if augmented[i][pivot_index]
            ),
            None,
        )
        if pivot_row is None:
            return None
        augmented[pivot_index], augmented[pivot_row] = (
            augmented[pivot_row], augmented[pivot_index]
        )
        scale = augmented[pivot_index][pivot_index]
        augmented[pivot_index][pivot_index:] = [
            x / scale for x in augmented[pivot_index][pivot_index:]
        ]
        for i in range(size):
            if i == pivot_index:
                continue
            multiple = augmented[i][pivot_index]
            if multiple:
                augmented[i][pivot_index:] = [
                    a - multiple * b
                    for a, b in zip(
                        augmented[i][pivot_index:],
                        augmented[pivot_index][pivot_index:],
                    )
                ]
    return tuple(row[-1] for row in augmented)


def sharp_expectation_bounds(
    subset_values: Sequence[Rational],
    category_marginals: Sequence[Rational],
) -> tuple[
    tuple[Fraction, dict[int, Fraction]],
    tuple[Fraction, dict[int, Fraction]],
]:
    """Min/max expectations and achieving mask-probability witnesses.

    Four output categories are encoded by bits 1,2,4,8. The supplied
    marginals constrain each bit's probability of being enabled;
    arbitrary correlations are permitted. All calculations are exact.
    """
    if len(subset_values) != 16 or len(category_marginals) != 4:
        raise ValueError("exactly four availability categories are required")
    probs = tuple(Fraction(p) for p in category_marginals)
    if any(p < 0 or p > 1 for p in probs):
        raise ValueError("marginal probability outside [0,1]")

    target = (Fraction(1), *probs)
    scores = tuple(Fraction(x) for x in subset_values)
    least: tuple[Fraction, dict[int, Fraction]] | None = None
    greatest: tuple[Fraction, dict[int, Fraction]] | None = None

    for support in combinations(range(16), 5):
        columns = tuple(
            (Fraction(1),)
            + tuple(Fraction(bool(mask & (1 << bit))) for bit in range(4))
            for mask in support
        )
        matrix = [
            [columns[col][row] for col in range(5)]
            for row in range(5)
        ]
        mass = _linear_solve(matrix, target)
        if mass is None or any(x < 0 for x in mass):
            continue
        distribution = {
            mask: weight
            for mask, weight in zip(support, mass)
            if weight
        }
        objective = sum(
            (scores[mask] * weight for mask, weight in distribution.items()),
            Fraction(0),
        )
        if least is None or objective < least[0]:
            least = (objective, distribution)
        if greatest is None or objective > greatest[0]:
            greatest = (objective, distribution)

    if least is None or greatest is None:
        raise AssertionError("valid Bernoulli marginals must be feasible")
    return least, greatest
