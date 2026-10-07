"""Reproduce exact Battle Compressor and VS Seeker access to Gladion."""

from __future__ import annotations

from functools import lru_cache
from itertools import combinations
from math import isclose
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from compressor_vs_seeker_gladion import compressor_seeker_rescue_success


def pct(x: float) -> str:
    return f"{100*x:.6f}%"


def _remove(values: tuple[int, ...], value: int) -> tuple[int, ...]:
    out = list(values)
    out.remove(value)
    return tuple(sorted(out))


@lru_cache(maxsize=None)
def _labeled_future(
    cards: tuple[str, ...],
    turns: int,
    critical_prizes: tuple[int, ...],
    hand: tuple[int, ...],
    prizes: tuple[int, ...],
    deck: tuple[int, ...],
    discard: tuple[int, ...],
) -> float:
    if not critical_prizes:
        return 1.0
    if turns == 0 or not deck:
        return 0.0
    total = 0.0
    for drawn in deck:
        total += _labeled_after_draw(
            cards,
            turns,
            critical_prizes,
            tuple(sorted(hand + (drawn,))),
            prizes,
            _remove(deck, drawn),
            discard,
        )
    return total / len(deck)


def _labeled_after_draw(
    cards: tuple[str, ...],
    turns: int,
    critical_prizes: tuple[int, ...],
    hand: tuple[int, ...],
    prizes: tuple[int, ...],
    deck: tuple[int, ...],
    discard: tuple[int, ...],
) -> float:
    states = {(hand, deck, discard)}
    compressor = next((i for i in hand if cards[i] == "B"), None)
    deck_gladion = next((i for i in deck if cards[i] == "G"), None)
    if compressor is not None and deck_gladion is not None:
        states.add((
            _remove(hand, compressor),
            _remove(deck, deck_gladion),
            tuple(sorted(discard + (compressor, deck_gladion))),
        ))

    expanded = set(states)
    for h, d, x in states:
        seeker = next((i for i in h if cards[i] == "V"), None)
        discard_gladion = next((i for i in x if cards[i] == "G"), None)
        if seeker is not None and discard_gladion is not None:
            expanded.add((
                tuple(sorted(_remove(h, seeker) + (discard_gladion,))),
                d,
                tuple(sorted(_remove(x, discard_gladion) + (seeker,))),
            ))

    best = 0.0
    for h, d, x in expanded:
        best = max(
            best,
            _labeled_future(cards, turns - 1, critical_prizes, h, prizes, d, x),
        )
        gladion = next((i for i in h if cards[i] == "G"), None)
        if gladion is None:
            continue
        critical = critical_prizes[0]
        next_hand = list(h)
        next_hand.remove(gladion)
        next_hand.append(critical)
        next_prizes = list(prizes)
        next_prizes.remove(critical)
        next_prizes.append(gladion)
        best = max(
            best,
            _labeled_future(
                cards,
                turns - 1,
                critical_prizes[1:],
                tuple(sorted(next_hand)),
                tuple(sorted(next_prizes)),
                d,
                x,
            ),
        )
    return best


def labeled_small_case(turns: int = 2) -> tuple[float, float]:
    cards = ("S", "S", "S", "C", "C", "G", "B", "V", "O", "O")
    indices = tuple(range(10))
    opening = 3
    prize_count = 2
    accepted = 0
    total_prize_states = 0
    critical_states = 0
    success_sum = 0.0

    for hand in combinations(indices, opening):
        if not any(cards[i] == "S" for i in hand):
            continue
        accepted += 1
        remaining = tuple(i for i in indices if i not in hand)
        for prizes in combinations(remaining, prize_count):
            total_prize_states += 1
            critical = tuple(sorted(i for i in prizes if cards[i] == "C"))
            if not critical:
                continue
            critical_states += 1
            deck = tuple(i for i in remaining if i not in prizes)
            _labeled_future.cache_clear()
            success_sum += _labeled_future(
                cards,
                turns,
                critical,
                tuple(sorted(hand)),
                tuple(sorted(prizes)),
                tuple(sorted(deck)),
                (),
            )

    assert total_prize_states == accepted * 21
    return critical_states / total_prize_states, success_sum / critical_states


def main() -> None:
    packages = [(0, 0), (1, 0), (0, 1), (1, 1), (2, 2), (4, 4)]
    results = {}
    for b, v in packages:
        results[(b, v)] = []
        for turns in range(1, 5):
            literal = compressor_seeker_rescue_success(
                60,
                6,
                starter_cards=12,
                critical_starter=0,
                critical_nonstarter=4,
                gladion_copies=1,
                compressor_copies=b,
                vs_seeker_copies=v,
                rescue_turns=turns,
            )
            naive = compressor_seeker_rescue_success(
                60,
                6,
                starter_cards=12,
                critical_starter=0,
                critical_nonstarter=4,
                gladion_copies=1,
                compressor_copies=b,
                vs_seeker_copies=v,
                rescue_turns=turns,
                played_to_discard=True,
            )
            assert isclose(literal.state_mass, 1.0, rel_tol=0.0, abs_tol=1e-12)
            assert isclose(naive.state_mass, 1.0, rel_tol=0.0, abs_tol=1e-12)
            assert naive.conditional_success_probability + 1e-15 >= literal.conditional_success_probability
            results[(b, v)].append((
                literal.conditional_success_probability,
                naive.conditional_success_probability,
            ))

    for turn in range(4):
        no_chain = results[(0, 0)][turn][0]
        assert isclose(results[(1, 0)][turn][0], no_chain, rel_tol=0.0, abs_tol=1e-12)
        assert isclose(results[(0, 1)][turn][0], no_chain, rel_tol=0.0, abs_tol=1e-12)

    assert results[(1, 1)][0][0] > results[(0, 0)][0][0]

    category_small = compressor_seeker_rescue_success(
        10,
        2,
        starter_cards=3,
        critical_starter=0,
        critical_nonstarter=2,
        gladion_copies=1,
        compressor_copies=1,
        vs_seeker_copies=1,
        opening_hand_size=3,
        rescue_turns=2,
    )
    labeled_any, labeled_success = labeled_small_case(2)
    assert isclose(category_small.any_critical_prized, labeled_any, rel_tol=0.0, abs_tol=1e-12)
    assert isclose(category_small.conditional_success_probability, labeled_success, rel_tol=0.0, abs_tol=1e-12)

    print("compressor_vs_seeker_gladion: all assertions passed")
    for package, row in results.items():
        print("B,V", package)
        for turn, (literal, naive) in enumerate(row, 1):
            print(turn, pct(literal), pct(naive), f"gap={100*(naive-literal):.6f}pp")


if __name__ == "__main__":
    main()
