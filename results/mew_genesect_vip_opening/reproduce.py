"""Exact Mew/Genesect first-turn Battle VIP Pass setup frontier.

The event is limited to natural first draw, naturally held Basics, and one
naturally held Battle VIP Pass. It excludes every other search/draw Ability,
Trainer card, Energy attachment, evolution, and opponent interaction.
"""

from __future__ import annotations

from fractions import Fraction
from itertools import combinations
from math import comb
from random import Random


def category_counts(vip: int) -> tuple[int, ...]:
    """Mew V, Genesect V, other Basic, Battle VIP Pass, other non-Basic."""
    assert vip in (3, 4)
    return 4, 4, 3, vip, 49 - vip


def vectors(total: int, caps: tuple[int, ...]):
    if not caps:
        if total == 0:
            yield ()
        return
    for n in range(min(total, caps[0]) + 1):
        for tail in vectors(total - n, caps[1:]):
            yield (n, *tail)


def outcome(
    visible: tuple[int, ...],
    prizes: tuple[int, ...],
    counts: tuple[int, ...],
    required_genesect: int,
) -> tuple[bool, bool, bool]:
    """Return direct success, added VIP-only success, combined success."""
    mew, genesect, _, vip, _ = visible
    direct = mew >= 1 and genesect >= required_genesect
    missing_mew = max(0, 1 - mew)
    missing_genesect = max(0, required_genesect - genesect)
    use_vip = (
        vip >= 1
        and missing_mew + missing_genesect <= 2
        and counts[0] - visible[0] - prizes[0] >= missing_mew
        and counts[1] - visible[1] - prizes[1] >= missing_genesect
    )
    return direct, use_vip and not direct, direct or use_vip


def exact(
    counts: tuple[int, ...],
    required_genesect: int,
    *,
    hand_size: int = 7,
    prize_size: int = 6,
) -> dict[str, Fraction]:
    """Enumerate disjoint physical hand/Prize/draw categories exactly.

    First draw is the single extra visible card after the opening hand. For an
    eight-card visible set with one Basic, exactly seven of its eight choices
    of last-drawn card leave a valid seven-card opening hand. For two or more
    Basics all eight possible last-draw choices are valid.
    """
    assert len(counts) == 5 and required_genesect in (1, 2, 3)
    total_cards = sum(counts)
    exposed = hand_size + 1
    assert prize_size <= total_cards - exposed
    masses = [0, 0, 0, 0]
    for visible in vectors(exposed, counts):
        n_basics = sum(visible[:3])
        if n_basics == 0:
            continue
        valid_last_draws = exposed if n_basics >= 2 else hand_size
        weight_visible = valid_last_draws
        for count, seen in zip(counts, visible):
            weight_visible *= comb(count, seen)
        remaining = tuple(c - v for c, v in zip(counts, visible))
        for prizes in vectors(prize_size, remaining):
            weight = weight_visible
            for count, taken in zip(remaining, prizes):
                weight *= comb(count, taken)
            direct, vip_only, union = outcome(
                visible, prizes, counts, required_genesect
            )
            masses[0] += weight
            masses[1] += weight * direct
            masses[2] += weight * vip_only
            masses[3] += weight * union
    total, direct, vip_only, union = masses
    assert direct + vip_only == union
    denom = exposed * comb(total_cards, exposed) * comb(
        total_cards - exposed, prize_size
    )
    assert Fraction(total, denom) == 1 - Fraction(
        comb(total_cards - sum(counts[:3]), hand_size),
        comb(total_cards, hand_size),
    )
    return {
        "valid_hand": Fraction(total, denom),
        "direct": Fraction(direct, total),
        "vip_only": Fraction(vip_only, total),
        "combined": Fraction(union, total),
    }


def physical_oracle(
    counts: tuple[int, ...], required_genesect: int, *,
    hand_size: int, prize_size: int
) -> dict[str, Fraction]:
    """Independently enumerate labeled hand, Prize, and draw allocations."""
    deck = tuple(i for i, copies in enumerate(counts) for _ in range(copies))
    all_ids = tuple(range(len(deck)))
    masses = [0, 0, 0, 0]
    for hand in combinations(all_ids, hand_size):
        if not any(deck[i] <= 2 for i in hand):
            continue
        rest = tuple(i for i in all_ids if i not in hand)
        for prizes in combinations(rest, prize_size):
            leftover = tuple(i for i in rest if i not in prizes)
            prize_counts = tuple(sum(deck[i] == category for i in prizes)
                                 for category in range(5))
            for next_card in leftover:
                visible = (*hand, next_card)
                visible_counts = tuple(sum(deck[i] == category for i in visible)
                                       for category in range(5))
                direct, vip_only, union = outcome(
                    visible_counts, prize_counts, counts, required_genesect
                )
                masses[0] += 1
                masses[1] += direct
                masses[2] += vip_only
                masses[3] += union
    return dict(zip(("valid_worlds", "direct", "vip_only", "combined"),
                    (masses[0], *(Fraction(k, masses[0]) for k in masses[1:]))))


def simulated(counts: tuple[int, ...], required_genesect: int, *,
              seed: int, trials: int) -> tuple[float, int]:
    deck = tuple(i for i, copies in enumerate(counts) for _ in range(copies))
    rng = Random(seed)
    good = valid = 0
    for _ in range(trials):
        sample = rng.sample(deck, len(deck))
        if not any(c <= 2 for c in sample[:7]):
            continue
        valid += 1
        prize_counts = tuple(sample[7:13].count(c) for c in range(5))
        visible_counts = tuple((sample[:7] + sample[13:14]).count(c)
                               for c in range(5))
        good += outcome(visible_counts, prize_counts, counts, required_genesect)[2]
    return good / valid, valid


def assert_legal_deck_variants() -> None:
    from datetime import date
    from pathlib import Path
    from results.competitive_deck_baselines.mew_genesect_reproduce import (
        ENERGY, POKEMON, PRINT_IDS, TRAINERS, verify,
    )
    from tools.deck_legality_proof import adjudicate_deck
    from tools.deck_validator import DeckEntry

    verify()
    root = Path(__file__).resolve().parents[2]
    for vip_count in (3, 4):
        card_counts = {**POKEMON, **TRAINERS, **ENERGY}
        card_counts["Battle VIP Pass"] = vip_count
        card_counts["Special Red Card"] = 5 - vip_count
        assert sum(card_counts.values()) == 60
        assert all(0 < n <= 4 for n in card_counts.values())
        assert sum(POKEMON.values()) == 14
        assert sum(ENERGY.values()) == 4
        entries = [DeckEntry(PRINT_IDS[name], n) for name, n in card_counts.items()]
        proof = adjudicate_deck(entries, root / "resources", as_of=date(2026, 10, 12))
        assert proof.construction.valid, proof.construction.issues
        assert proof.disposition == "eligible_snapshot", proof.disposition
        print(f"Exact-print VIP={vip_count} legal snapshot: {proof.disposition}")


def self_test() -> None:
    # Independent labeled physical oracle, 12 distinct card instances.
    tiny = (2, 2, 1, 1, 6)
    for target in (1, 2):
        expected = exact(tiny, target, hand_size=3, prize_size=2)
        oracle = physical_oracle(tiny, target, hand_size=3, prize_size=2)
        for key in ("direct", "vip_only", "combined"):
            assert expected[key] == oracle[key], (key, expected[key], oracle[key])
        print(f"Physical {target}-Genesect toy oracle: {oracle['valid_worlds']} valid worlds, all metrics agree")
    for target in (2, 3):
        baseline = exact(category_counts(3), target)
        expanded = exact(category_counts(4), target)
        assert baseline["direct"] == expanded["direct"]
        assert expanded["combined"] > baseline["combined"]
        assert baseline["valid_hand"] == expanded["valid_hand"]
        print(f"Mew V + {target} Genesect V; first natural draw, conditional on Basic-valid opener:")
        for name, result in (("published VIP3", baseline), ("legal +VIP/-Red VIP4", expanded)):
            print(f"  {name}: direct={float(result['direct']):.9%}, "
                  f"VIP only={float(result['vip_only']):.9%}, "
                  f"union={float(result['combined']):.9%}")
        difference = expanded["combined"] - baseline["combined"]
        print(f"  Difference: {float(difference)*100:.9f} percentage points")
        for vip in (3, 4):
            estimated, accepted = simulated(category_counts(vip), target, seed=20261012, trials=100000)
            truth = float(exact(category_counts(vip), target)["combined"])
            assert abs(estimated - truth) < 0.006, (vip, target, accepted, estimated, truth)
            print(f"  100000-seed Monte Carlo VIP{vip}: {estimated:.9%}, accepted {accepted}")


if __name__ == "__main__":
    self_test()
    assert_legal_deck_variants()
