"""SFT: K0 posterior, explicit Mail commitment, and paired opening evidence."""
from __future__ import annotations

from collections import Counter
from itertools import product
from math import comb
import random

from tools.iron_thorns_mail_frontier import deck, evaluate
from tools.iron_thorns_mail_k0 import choose_after_mail, experiment, k0_action

KEYS = ("G", "M", "D", "B")


def slow_posterior_choice(dce: int, hand: Counter[str], top4: tuple[str, ...]) -> str:
    """Independent Prize-count hypergeometric oracle, no inclusion-exclusion."""
    inventory = Counter(deck(dce, 3 - dce))
    revealed = Counter(top4)
    unknown = inventory - hand - Counter({"I": 1}) - revealed
    assert sum(unknown.values()) == 48
    candidates = [""] + [x for x in ("M", "G", "T", "B") if revealed[x]]
    scored = {c: [0, 0] for c in candidates}
    other = 48 - sum(unknown[k] for k in KEYS)
    for prized in product(*(range(min(6, unknown[k]) + 1) for k in KEYS)):
        remainder = 6 - sum(prized)
        if not 0 <= remainder <= other:
            continue
        weight = comb(other, remainder)
        for category, count in zip(KEYS, prized):
            weight *= comb(unknown[category], count)
        prizes = Counter(dict(zip(KEYS, prized)))
        available = inventory - hand - Counter({"I": 1}) - prizes
        for choice in candidates:
            h = hand.copy()
            stock = available.copy()
            h["L"] -= 1
            if choice:
                h[choice] += 1
                stock[choice] -= 1
            event = evaluate(h, stock)
            scored[choice][0] += weight * int(event.attack)
            scored[choice][1] += weight * int(event.beach)
    return max(candidates, key=lambda c: (scored[c][0], scored[c][1], -candidates.index(c)))


def verify() -> None:
    rng = random.Random(300419)
    compared = 0
    for dce in (1, 2):
        cards = deck(dce, 3 - dce)
        for _ in range(800):
            places = rng.sample(range(60), 18)
            opening = Counter(cards[i] for i in places[:7])
            if not opening["I"]:
                continue
            hand = opening.copy()
            hand["I"] -= 1
            hand[cards[places[13]]] += 1
            if not hand["L"]:
                continue
            peek = tuple(sorted(cards[i] for i in places[14:18]))
            fast = choose_after_mail(
                dce,
                tuple(sorted((k, v) for k, v in hand.items() if v > 0)),
                peek,
            )
            slow = slow_posterior_choice(dce, hand, peek)
            assert fast == slow, (dce, hand, peek, fast, slow)
            compared += 1
    assert compared >= 150
    print("PASS: posterior inclusion-exclusion matches separate multivariate "
          "hypergeometric choice on", compared, "physical worlds")

    # One-Mail can spend the sole second safe G&H payment.
    hand = Counter({"L": 1, "S": 1, "G": 1, "O": 4})
    stock = Counter({"M": 1, "D": 2, "B": 1, "O": 42})
    assert evaluate(hand, stock).attack
    top4 = ("B", "O", "O", "O")
    assert not k0_action(hand, stock, top4, 2, False).attack
    assert k0_action(hand, stock, top4, 2, True).attack
    print("PASS: visible-hand payment-preserving precommitment")

    expected = {
        2: (62732, 80791, 58093, 106118, 72537, 93200, 72537, 93207, 14444, 0, 9805, 9805),
        1: (48826, 118597, 42027, 148990, 56208, 134934, 56208, 134947, 14181, 0, 7382, 7382),
    }
    fields = (
        "baseline_attack", "baseline_beach", "always_attack", "always_beach",
        "preserve_attack", "preserve_beach", "oracle_attack", "oracle_beach",
        "always_lost_attack", "preserve_lost_attack",
        "always_new_attack", "preserve_new_attack",
    )
    totals = experiment(300_000, seed=20261014)
    for variant, tally in totals.items():
        assert tally.samples == 300_000
        actual = tuple(getattr(tally, name) for name in fields)
        assert actual == expected[variant], (variant, actual, expected[variant])
        assert tally.preserve_attack == tally.oracle_attack
        assert tally.preserve_lost_attack == 0
        assert tally.always_lost_attack > 14_000
    print("PASS: fixed-seed paired 60-card K0, oracle and damage-by-overplaying counts")


if __name__ == "__main__":
    verify()
