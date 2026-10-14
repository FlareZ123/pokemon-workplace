"""K0-visible Trainers' Mail selection and paid-discard preservation.

Companion to iron_thorns_mail_frontier.py. The policy commits to Mail using
only the visible hand, then chooses from its top four using the exact posterior
over six unknown Prize cards. Only named setup resources are valued.
No game win rates, opponent decisions or subsequent draws are modeled.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from functools import lru_cache
from math import comb
import random

from tools.iron_thorns_mail_frontier import Result, augmented, deck, evaluate

KEYS = ("G", "M", "D", "B")
REVEAL_TARGETS = ("M", "G", "T", "B")


def _endpoint(hand: Counter[str], deck_available: dict[str, bool]) -> tuple[int, int]:
    """Same strict access rule as the physical model, with stock presence bits."""
    gh = bool(hand["G"] or (hand["T"] and deck_available["G"]))
    mountain = bool(hand["M"] or deck_available["M"])
    dce = bool(hand["D"] or deck_available["D"])
    free = bool((hand["M"] and hand["D"]) or (hand["D"] and gh and mountain))
    paid = bool(
        not hand["D"] and gh and mountain and dce
        and hand["S"] + hand["L"] >= 2
    )
    attack = free or paid
    fallback = bool(not attack and (hand["B"] or (gh and deck_available["B"])))
    return int(attack), int(fallback)


@lru_cache(maxsize=None)
def choose_after_mail(
    dce_count: int, hand_state: tuple[tuple[str, int], ...],
    revealed_four: tuple[str, ...],
) -> str:
    """Posterior-optimal revealed target for attack-first lexicographic utility.

    The player knows exact starting deck counts, their hand, one Active Iron
    Thorns and the four revealed cards, but not the six Prizes. Among 48 other
    physical cards, six are equally likely to be Prized. For each G/M/D/B
    category, the only relevant hidden question is whether *all* unseen
    copies were Prized. Inclusion-exclusion obtains the exact joint mass
    of these four binary events over all C(48,6) configurations.
    """
    inventory = Counter(deck(2, 1) if dce_count == 2 else deck(1, 2))
    hand = Counter(dict(hand_state))
    revealed = Counter(revealed_four)
    unseen = inventory - hand - Counter({"I": 1}) - revealed
    assert sum(unseen.values()) == 48

    counts = tuple(unseen[k] for k in KEYS)
    all_absent_mass = []
    for mask in range(16):
        required = sum(counts[i] for i in range(4) if mask & (1 << i))
        all_absent_mass.append(
            comb(48 - required, 6 - required) if required <= 6 else 0
        )

    exact_mass = []
    for mask in range(16):
        complement = 15 ^ mask
        amount = 0
        for add in range(16):
            if add & ~complement:
                continue
            sign = -1 if add.bit_count() % 2 else 1
            amount += sign * all_absent_mass[mask | add]
        assert amount >= 0
        exact_mass.append(amount)
    assert sum(exact_mass) == comb(48, 6)

    candidates = [""] + [name for name in REVEAL_TARGETS if revealed[name]]
    expected = []
    for candidate in candidates:
        after = hand.copy()
        after["L"] -= 1
        if candidate:
            after[candidate] += 1
        shown_remaining = revealed.copy()
        if candidate:
            shown_remaining[candidate] -= 1

        attack_mass = fallback_mass = 0
        for mask, probability_numerator in enumerate(exact_mass):
            if not probability_numerator:
                continue
            access = {
                name: bool(shown_remaining[name] or not (mask & (1 << i)))
                for i, name in enumerate(KEYS)
            }
            attack, fallback = _endpoint(after, access)
            attack_mass += probability_numerator * attack
            fallback_mass += probability_numerator * fallback
        expected.append((attack_mass, fallback_mass))

    choice_index = max(
        range(len(candidates)),
        key=lambda i: (expected[i][0], expected[i][1], -i),
    )
    return candidates[choice_index]


def k0_action(
    hand: Counter[str], stock: Counter[str], top4: tuple[str, ...],
    dce_count: int, preserve_payment: bool,
) -> Result:
    """Visible-hand Mail commitment followed by posterior Trainer selection.

    Always-commit: play one Mail whenever held unless the hand already has
    Thunder Mountain and DCE.
    Preserve-payment: additionally skip Mail when DCE is missing, exactly two
    hypothetical disposable cards remain, and G&H or Tag Call is held.
    The pre-commitment sees neither the hidden Prize allocation nor top four.
    """
    if not hand["L"] or (hand["M"] and hand["D"]):
        return evaluate(hand, stock)
    if (
        preserve_payment and not hand["D"]
        and hand["S"] + hand["L"] == 2
        and (hand["G"] or hand["T"])
    ):
        return evaluate(hand, stock)

    choice = choose_after_mail(
        dce_count,
        tuple(sorted((name, count) for name, count in hand.items() if count > 0)),
        tuple(sorted(top4)),
    )
    h = hand.copy()
    d = stock.copy()
    h["L"] -= 1
    if choice:
        h[choice] += 1
        d[choice] -= 1
    return evaluate(h, d)


@dataclass
class Tally:
    samples: int = 0
    baseline_attack: int = 0
    baseline_beach: int = 0
    always_attack: int = 0
    always_beach: int = 0
    preserve_attack: int = 0
    preserve_beach: int = 0
    oracle_attack: int = 0
    oracle_beach: int = 0
    always_lost_attack: int = 0
    preserve_lost_attack: int = 0
    always_new_attack: int = 0
    preserve_new_attack: int = 0

    def add(self, baseline: Result, always: Result,
            preserved: Result, oracle: Result) -> None:
        self.samples += 1
        self.baseline_attack += int(baseline.attack)
        self.baseline_beach += int(baseline.beach)
        self.always_attack += int(always.attack)
        self.always_beach += int(always.beach)
        self.preserve_attack += int(preserved.attack)
        self.preserve_beach += int(preserved.beach)
        self.oracle_attack += int(oracle.attack)
        self.oracle_beach += int(oracle.beach)
        self.always_lost_attack += int(baseline.attack and not always.attack)
        self.preserve_lost_attack += int(baseline.attack and not preserved.attack)
        self.always_new_attack += int(always.attack and not baseline.attack)
        self.preserve_new_attack += int(preserved.attack and not baseline.attack)

    def summary(self) -> dict[str, float]:
        return {
            name: 100 * getattr(self, name) / self.samples
            for name in self.__dataclass_fields__ if name != "samples"
        }


def experiment(accepted_target: int = 300_000, seed: int = 20261014) -> dict[int, Tally]:
    """Paired physical 60-card Prize/opening/top-four experiment."""
    rng = random.Random(seed)
    variants = {2: deck(2, 1), 1: deck(1, 2)}
    inventory = {k: Counter(cards) for k, cards in variants.items()}
    tallies = {k: Tally() for k in variants}
    attempts = 0

    while tallies[2].samples < accepted_target:
        attempts += 1
        slots = rng.sample(range(60), 18)
        if not any(variants[2][i] == "I" for i in slots[:7]):
            continue
        for dce, cards in variants.items():
            opening = Counter(cards[i] for i in slots[:7])
            prizes = Counter(cards[i] for i in slots[7:13])
            first_draw = cards[slots[13]]
            top4 = tuple(cards[i] for i in slots[14:18])
            hand = opening.copy()
            hand["I"] -= 1
            hand[first_draw] += 1
            stock = inventory[dce] - opening - prizes - Counter({first_draw: 1})
            baseline = evaluate(hand, stock)
            always = k0_action(hand, stock, top4, dce, False)
            preserved = k0_action(hand, stock, top4, dce, True)
            oracle = augmented(hand, stock, top4)
            assert not (always.attack and always.beach)
            assert not (preserved.attack and preserved.beach)
            assert not (preserved.attack and not oracle.attack)
            tallies[dce].add(baseline, always, preserved, oracle)

    print(
        f"seed={seed}, accepted={accepted_target}, attempts={attempts}, "
        f"posterior cache={choose_after_mail.cache_info()}"
    )
    for dce, result in tallies.items():
        print(f"{dce} DCE: {result.summary()}")
    return tallies


if __name__ == "__main__":
    experiment()
