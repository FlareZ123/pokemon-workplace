"""Single runnable verification of the named one-Mail access experiment."""
from collections import Counter
from math import isclose

from tools.iron_thorns_mail_frontier import (
    Result, augmented, deck, evaluate, experiment,
)


def test_rule_boundaries() -> None:
    assert len(deck(2, 1)) == len(deck(1, 2)) == 60
    assert Counter(deck(2, 1))["L"] == Counter(deck(1, 2))["L"] == 4

    hand = Counter({"L": 1, "D": 1})
    stock = Counter({"M": 1})
    assert evaluate(hand, stock) == Result(False, False)
    assert augmented(hand, stock, ("M", "O", "O", "O")) == Result(True, False)
    assert augmented(hand, stock, ("D", "O", "O", "O")) == Result(False, False)
    assert augmented(hand, stock, ("L", "O", "O", "O")) == Result(False, False)

    hand = Counter({"L": 1, "S": 2})
    stock = Counter({"G": 1, "M": 1, "D": 1})
    assert not evaluate(hand, stock).attack
    assert augmented(hand, stock, ("G", "O", "O", "O")).attack

    # An unplayed Mail is a hypothetical discard; a played Mail is not.
    hand = Counter({"L": 1, "S": 1, "G": 1})
    stock = Counter({"M": 1, "D": 1, "B": 1})
    assert evaluate(hand, stock).attack
    spent = hand.copy()
    left = stock.copy()
    spent["L"] -= 1
    spent["B"] += 1
    left["B"] -= 1
    assert evaluate(spent, left) == Result(False, True)
    assert augmented(hand, stock, ("B", "O", "O", "O")).attack

    hand = Counter({"L": 1})
    stock = Counter({"B": 1})
    assert evaluate(hand, stock) == Result(False, False)
    assert augmented(hand, stock, ("B", "O", "O", "O")) == Result(False, True)
    assert augmented(Counter(), stock, ("B", "O", "O", "O")) == Result(False, False)
    print("PASS: Mail target restrictions, spent-discard payment, and Beach fallback")


def verify() -> None:
    test_rule_boundaries()
    fields = (
        "base_attack", "base_fallback", "mail_attack", "mail_fallback",
        "mail_attack_gain", "mail_fallback_gain",
        "mail_attack_from_fallback", "used_mail_context",
    )
    expected = {
        "two_dce": (62732, 80791, 72537, 93207, 9805, 13440, 1024, 123507),
        "two_beach": (48826, 118597, 56208, 134947, 7382, 17759, 1409, 123507),
    }
    results = experiment(300_000, seed=20261014)
    for name, t in results.items():
        assert t.accepted == 300_000
        observed = tuple(getattr(t, field) for field in fields)
        assert observed == expected[name], (name, observed, expected[name])
        assert t.mail_attack_gain == t.mail_attack - t.base_attack
        assert (
            t.mail_fallback ==
            t.base_fallback + t.mail_fallback_gain - t.mail_attack_from_fallback
        )
    # Independent grouped exact model, published in the preceding result.
    exact_baseline = {
        "two_dce": (0.20953810534, 0.27046350616),
        "two_beach": (0.16293835803, 0.39657753910),
    }
    for name, (attack, fallback) in exact_baseline.items():
        t = results[name]
        assert isclose(t.base_attack / t.accepted, attack, abs_tol=0.002)
        assert isclose(t.base_fallback / t.accepted, fallback, abs_tol=0.002)
    print("PASS: deterministic paired physical trials agree with exact baseline "
          "within prespecified Monte Carlo tolerance")


if __name__ == "__main__":
    verify()
