"""Exact learning of opposite search policies from print frequencies.

A forward policy chooses X when critical singleton A is Prized; a reverse
policy swaps X and Y. The finite-population hypergeometric model supplies the
conditional print frequencies and Prize posteriors for both policies.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from expanded_singleton_reveal_hypergeometric import (
    SingletonRevealProbabilities,
)


@dataclass(frozen=True)
class ExpandedPolicyBelief:
    forward_prior: Fraction
    print_signal: SingletonRevealProbabilities

    def __post_init__(self) -> None:
        if not 0 <= self.forward_prior <= 1:
            raise ValueError("forward policy prior must lie in [0,1]")

    def print_probability(self, observed_print: str) -> Fraction:
        alpha = self.forward_prior
        r = self.print_signal.probability_x_given_success
        if observed_print == "X":
            return alpha * r + (1 - alpha) * (1 - r)
        if observed_print == "Y":
            return alpha * (1 - r) + (1 - alpha) * r
        raise ValueError("print must be X or Y")

    def updated_by_print(self, observed_print: str) -> "ExpandedPolicyBelief":
        r = self.print_signal.probability_x_given_success
        forward_likelihood = (
            r if observed_print == "X"
            else 1 - r if observed_print == "Y"
            else None
        )
        if forward_likelihood is None:
            raise ValueError("print must be X or Y")
        evidence = self.print_probability(observed_print)
        if evidence == 0:
            raise ValueError("print has zero probability under model")
        return ExpandedPolicyBelief(
            self.forward_prior * forward_likelihood / evidence,
            self.print_signal,
        )

    def a_prized_posterior(self, observed_print: str) -> Fraction:
        """Retain the correlation between policy and hidden Prize membership."""
        alpha = self.forward_prior
        r = self.print_signal.probability_x_given_success
        q_x = self.print_signal.a_prized_given_x
        q_y = self.print_signal.a_prized_given_y
        if observed_print == "X":
            numerator = alpha * r * q_x + (1 - alpha) * (1 - r) * q_y
        elif observed_print == "Y":
            numerator = alpha * (1 - r) * q_y + (1 - alpha) * r * q_x
        else:
            raise ValueError("print must be X or Y")
        return numerator / self.print_probability(observed_print)

    def zero_one_accuracy(self, *, reveal_print: bool) -> Fraction:
        if not reveal_print:
            q = self.print_signal.a_prized_given_success
            return max(q, 1 - q)

        expectation = Fraction()
        for observed_print in ("X", "Y"):
            probability = self.print_probability(observed_print)
            if probability == 0:
                continue
            posterior = self.a_prized_posterior(observed_print)
            expectation += probability * max(posterior, 1 - posterior)
        return expectation

    def print_information_value(self) -> Fraction:
        return self.zero_one_accuracy(reveal_print=True) - self.zero_one_accuracy(
            reveal_print=False
        )

    def x_action_threshold(self) -> Fraction:
        """Forward prior above which the X print predicts A Prized (>1/2)."""
        r = self.print_signal.probability_x_given_success
        q_x = self.print_signal.a_prized_given_x
        q_y = self.print_signal.a_prized_given_y
        if not (0 < r < 1 and q_x > Fraction(1, 2) > q_y):
            raise ValueError("X/ Y probabilities do not straddle binary threshold")
        numerator = (1 - r) * (Fraction(1, 2) - q_y)
        denominator = r * (q_x - Fraction(1, 2)) + numerator
        return numerator / denominator
