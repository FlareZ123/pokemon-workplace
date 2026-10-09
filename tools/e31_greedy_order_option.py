"""Exact tiny decision model for Prize-origin E-31 order and prize-position knowledge.

This is a deliberately controlled four-Prize terminal scenario, not a complete
Pokemon TCG gameplay simulator. Every branch is enumerated with exact Fractions.
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from fractions import Fraction
from itertools import product

GREEDY = "Greedy Dice"
DREAM = "Dream Ball"
JIRACHI = "Jirachi Prism Star"
FILLER = "Filler"
TARGET = "Dream Ball target"


@dataclass(frozen=True)
class Outcome:
    prize_count: int
    bench_newcomer: str
    prize_sequence: tuple[str, ...]
    pending_sequence: tuple[str, ...]

    @property
    def terminal(self) -> bool:
        return self.prize_count == 4


def resolve(
    *,
    order: tuple[str, str],
    remaining_prizes: tuple[str, str],
    greedy_heads: bool,
    selected_prize_position: int,
    use_jirachi: bool,
) -> Outcome:
    """Resolve effects one by one, prepending new Prizes before older siblings.

    One Active and four Benched Pokemon are assumed to exist, leaving one
    open Bench slot. A legal Dream Ball search target exists in the deck.
    """
    if set(order) != {GREEDY, DREAM} or len(order) != 2:
        raise ValueError("the award must contain Greedy Dice and Dream Ball")
    if set(remaining_prizes) != {JIRACHI, FILLER}:
        raise ValueError("remaining Prizes must be Jirachi and filler")
    if selected_prize_position not in (0, 1):
        raise ValueError("selected Prize position must be 0 or 1")

    waiting = list(order)
    prizes = list(remaining_prizes)
    award = list(order)
    handled: list[str] = []
    newcomer = ""

    while waiting:
        card = waiting.pop(0)
        handled.append(card)
        if card == GREEDY:
            if greedy_heads and prizes:
                extra = prizes.pop(selected_prize_position)
                award.append(extra)
                waiting.insert(0, extra)
        elif card == DREAM:
            if not newcomer:
                newcomer = TARGET
        elif card == JIRACHI:
            if use_jirachi and not newcomer:
                newcomer = JIRACHI
                if prizes:
                    extra = prizes.pop(0)
                    award.append(extra)
                    waiting.insert(0, extra)
        elif card != FILLER:
            raise AssertionError("unsupported Prize effect")

    if len(set(award)) != len(award):
        raise AssertionError("Prize cards were awarded twice")
    if len(award) + len(prizes) != 4:
        raise AssertionError("Prize conservation failed")
    if not newcomer:
        raise AssertionError("the open Bench slot was never used")
    return Outcome(len(award), newcomer, tuple(award), tuple(handled))


def expectation(
    *, order: tuple[str, str],
    known_positions: bool,
    target_value: Fraction,
    use_jirachi: bool,
) -> tuple[Fraction, dict[tuple[int, str], Fraction]]:
    """Enumerate both Prize layouts and both coin faces, exactly 1/4 each.

    Composition-only: card identities are known, but slots are exchangeable.
    Position-known: the exact face-down slot of Jirachi is known beforehand.
    Ordinary first deck search alone does not establish positional knowledge.
    """
    scores = Fraction(0)
    distribution: dict[tuple[int, str], Fraction] = defaultdict(Fraction)
    for jirachi_position, heads in product((0, 1), (False, True)):
        layout = (JIRACHI, FILLER) if jirachi_position == 0 else (FILLER, JIRACHI)
        selected = jirachi_position if known_positions else 0
        result = resolve(
            order=order,
            remaining_prizes=layout,
            greedy_heads=heads,
            selected_prize_position=selected,
            use_jirachi=use_jirachi,
        )
        weight = Fraction(1, 4)
        distribution[(result.prize_count, result.bench_newcomer)] += weight
        scores += weight * (
            result.prize_count + target_value * (result.bench_newcomer == TARGET)
        )
    return scores, dict(distribution)


def optimal_value(*, order: tuple[str, str], known_positions: bool,
                  target_value: Fraction) -> tuple[Fraction, bool]:
    """Optimize the only consequential optional trigger, Jirachi's Ability."""
    choices = (
        (expectation(order=order, known_positions=known_positions,
                     target_value=target_value, use_jirachi=use)[0], use)
        for use in (False, True)
    )
    return max(choices, key=lambda pair: pair[0])


def exact_regressions() -> None:
    early = (GREEDY, DREAM)
    late = (DREAM, GREEDY)
    for v in (Fraction(0), Fraction(1, 3), Fraction(1, 2),
              Fraction(1), Fraction(3, 2), Fraction(4)):
        base = Fraction(5, 2) + v
        extra = max(Fraction(0), 1 - v)
        assert optimal_value(order=late, known_positions=False,
                             target_value=v)[0] == base
        assert optimal_value(order=late, known_positions=True,
                             target_value=v)[0] == base
        assert optimal_value(order=early, known_positions=False,
                             target_value=v)[0] == base + extra / 4
        assert optimal_value(order=early, known_positions=True,
                             target_value=v)[0] == base + extra / 2

    expected = {
        (False, early): {(2, TARGET): Fraction(1, 2),
                         (3, TARGET): Fraction(1, 4),
                         (4, JIRACHI): Fraction(1, 4)},
        (True, early): {(2, TARGET): Fraction(1, 2),
                        (4, JIRACHI): Fraction(1, 2)},
        (False, late): {(2, TARGET): Fraction(1, 2),
                        (3, TARGET): Fraction(1, 2)},
        (True, late): {(2, TARGET): Fraction(1, 2),
                       (3, TARGET): Fraction(1, 2)},
    }
    for (k1, order), wanted in expected.items():
        _, dist = expectation(order=order, known_positions=k1,
                              target_value=Fraction(0), use_jirachi=True)
        assert dist == wanted, (k1, order, dist)

    # Early Greedy can reproduce the entire Dream-first distribution by
    # declining Jirachi and then using the still-open Bench slot for Dream.
    for k1 in (False, True):
        _, early_decline = expectation(order=early, known_positions=k1,
                                       target_value=Fraction(0), use_jirachi=False)
        _, late_play = expectation(order=late, known_positions=k1,
                                   target_value=Fraction(0), use_jirachi=True)
        assert early_decline == late_play

    print("Exact E-31 order / positional-information regressions passed")
    for k1, label in ((False, "composition-only"), (True, "position-known")):
        value, dist = expectation(order=early, known_positions=k1,
                                  target_value=Fraction(0), use_jirachi=True)
        terminal = sum(p for (n, _), p in dist.items() if n == 4)
        print(f"{label}: Greedy-first expected Prizes={value}; "
              f"P(take all four)={terminal}; outcomes={dist}")
    print("Dream-first expected Prizes=5/2; P(take all four)=0")


if __name__ == "__main__":
    exact_regressions()
