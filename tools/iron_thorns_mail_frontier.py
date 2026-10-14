"""Paired physical opening study: one Trainers' Mail in two Iron Thorns variants.

This measures a named early-access endpoint under optimistic card selection.
It does not simulate games, estimate match wins, or model multi-turn draw.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from math import sqrt
import random
from typing import NamedTuple


class Result(NamedTuple):
    attack: bool
    beach: bool


BASE_COUNTS = {"I": 4, "T": 2, "G": 2, "M": 1, "S": 8, "L": 4}


def deck(dce: int, beach: int) -> list[str]:
    counts = dict(BASE_COUNTS, D=dce, B=beach)
    counts["O"] = 60 - sum(counts.values())
    assert counts["O"] >= 0 and sum(counts.values()) == 60
    return [name for name, copies in counts.items() for _ in range(copies)]


def evaluate(hand: Counter[str], stock: Counter[str]) -> Result:
    """Reproduce the prior strict paid-discard named attack and Beach endpoints.

    The four Trainers' Mail belong to the assumed safe 12 only while in hand;
    the other eight safe cards are four Crushing Hammer, two Enhanced Hammer,
    and two Camping Gear. DCI acceptability is hypothetical, not guaranteed.
    """
    gh = bool(hand["G"] or (hand["T"] and stock["G"]))
    m = bool(hand["M"] or stock["M"])
    d = bool(hand["D"] or stock["D"])
    free = bool(
        (hand["M"] and hand["D"]) or (hand["D"] and gh and m)
    )
    paid = bool(
        not hand["D"] and gh and m and d and hand["S"] + hand["L"] >= 2
    )
    if free or paid:
        return Result(True, False)
    return Result(False, bool(hand["B"] or (gh and stock["B"])))


def augmented(
    hand: Counter[str], stock: Counter[str], top4: tuple[str, ...]
) -> Result:
    """Best of skipping Mail or one Mail revealing G, T, M, or B.

    This best-outcome choice sees otherwise hidden Prize/deck contents.
    It is an optimistic restricted-action envelope, not a practical K0 policy.
    Trainers' Mail cannot reveal Energy or other Trainers' Mail.
    """
    best = evaluate(hand, stock)
    if not hand["L"] or best.attack:
        return best
    for category in set(top4).intersection({"G", "T", "M", "B"}):
        hh = hand.copy()
        dd = stock.copy()
        hh["L"] -= 1
        hh[category] += 1
        dd[category] -= 1
        assert dd[category] >= 0
        v = evaluate(hh, dd)
        if v.attack:
            return v
        if v.beach:
            best = v
    return best


@dataclass
class Tally:
    accepted: int = 0
    base_attack: int = 0
    base_fallback: int = 0
    mail_attack: int = 0
    mail_fallback: int = 0
    mail_attack_gain: int = 0
    mail_fallback_gain: int = 0
    mail_attack_from_fallback: int = 0
    used_mail_context: int = 0

    def add(self, baseline: Result, with_mail: Result, held_mail: bool) -> None:
        self.accepted += 1
        self.base_attack += int(baseline.attack)
        self.base_fallback += int(baseline.beach)
        self.mail_attack += int(with_mail.attack)
        self.mail_fallback += int(with_mail.beach)
        self.mail_attack_gain += int(with_mail.attack and not baseline.attack)
        self.mail_fallback_gain += int(
            with_mail.beach and not baseline.beach and not baseline.attack
        )
        self.mail_attack_from_fallback += int(with_mail.attack and baseline.beach)
        self.used_mail_context += int(held_mail)

    def summary(self) -> dict[str, str]:
        fields = (
            "base_attack", "base_fallback", "mail_attack", "mail_fallback",
            "mail_attack_gain", "mail_fallback_gain", "mail_attack_from_fallback",
            "used_mail_context",
        )
        return {
            name: f"{getattr(self, name) / self.accepted:.9%}"
            for name in fields
        }


def experiment(accepted_target: int, seed: int = 20261014) -> dict[str, Tally]:
    """Draw paired ordered physical positions, conditioning on Basic-valid seven.

    positions[:7] are opening, [7:13] six Prizes, [13] first going-second draw,
    [14:18] top four after that draw. Card positions align across the two 60s;
    the sole substitution is DCE for Tropical Beach.
    """
    rng = random.Random(seed)
    decks = {"two_dce": deck(2, 1), "two_beach": deck(1, 2)}
    inventories = {k: Counter(v) for k, v in decks.items()}
    tally = {k: Tally() for k in decks}
    attempts = 0
    while tally["two_dce"].accepted < accepted_target:
        attempts += 1
        positions = rng.sample(range(60), 18)
        if not any(decks["two_dce"][p] == "I" for p in positions[:7]):
            continue
        for name, cards in decks.items():
            opening = Counter(cards[p] for p in positions[:7])
            prizes = Counter(cards[p] for p in positions[7:13])
            first_draw = cards[positions[13]]
            top4 = tuple(cards[p] for p in positions[14:18])
            h = opening.copy()
            h["I"] -= 1
            h[first_draw] += 1
            stock = inventories[name] - opening - prizes - Counter({first_draw: 1})
            baseline = evaluate(h, stock)
            mail = augmented(h, stock, top4)
            assert mail.attack or not baseline.attack
            assert not (mail.attack and mail.beach)
            assert baseline.attack or not mail.attack or h["L"] > 0
            tally[name].add(baseline, mail, bool(h["L"]))
    print(
        f"seed={seed} accepted={accepted_target} attempts={attempts}"
        " (seven-card opener contains Iron)"
    )
    for name, t in tally.items():
        print(f"{name}: {t.summary()}")
        p = t.mail_attack_gain / t.accepted
        width = 1.96 * sqrt(p * (1 - p) / t.accepted)
        print(
            "  attack-gain 95% normal Monte Carlo interval: "
            f"{p - width:.9%} .. {p + width:.9%}"
        )
    return tally


if __name__ == "__main__":
    experiment(300_000)
