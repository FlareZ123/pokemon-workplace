"""Exact first-turn Mew VMAX Wally launch: +Tapu Lele-GX, -Special Red Card.

A deliberately restricted paper Expanded counterfactual, not match win rate.
Reproduce: python results/tests/mew_wally_tapu_variant/reproduce.py
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from datetime import date
from fractions import Fraction
from itertools import combinations
from math import comb
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from results.competitive_deck_baselines.mew_genesect_reproduce import (
    POKEMON, TRAINERS, ENERGY, PRINT_IDS,
)
from results.tests.mew_wally_first_attack.reproduce import (
    opening_counts, probability_all_prized,
)
from tools.deck_legality_proof import adjudicate_deck
from tools.deck_validator import DeckEntry, load_all_card_records

# Mew, Genesect, VMAX, Wally, DCE, VIP, Quick, Ultra, Tapu Lele, other.
# One non-Basic Special Red Card becomes a Basic Tapu Lele-GX.
VARIANT = (4, 4, 3, 1, 4, 3, 4, 4, 1, 32)
ROUTES = ("old", "lele_held", "lele_searched")
BASELINE = Fraction(167155400140607, 11575496365633200)


def survive(deck_size: int, prizes: int, targets: list[int]) -> Fraction:
    """Inclusion-exclusion: every required card category has a deck survivor."""
    result = Fraction(0)
    for size in range(len(targets) + 1):
        for subset in combinations(targets, size):
            result += (-1 if size % 2 else 1) * probability_all_prized(
                deck_size, prizes, sum(subset)
            )
    return result


def exact(pool: tuple[int, ...], hand: int, prizes: int) -> dict[str, Fraction]:
    n = sum(pool)
    output = {key: Fraction(0) for key in ROUTES}
    for initial, ways in opening_counts(pool, hand):
        if not initial[0]:
            continue  # Mew V must be Active before the natural draw.
        for k, copies in enumerate(pool):
            remaining = copies - initial[k]
            if not remaining:
                continue
            held = list(initial)
            held[k] += 1
            if not held[4]:  # DCE must be attachable from hand.
                continue
            if held[3]:
                if not (held[1] or held[5] or held[6] or held[7]):
                    continue
                targets = [pool[2] - held[2]]
                if not held[1]:
                    targets.append(pool[1] - held[1])
                key = "old"
            else:
                lele_ball = 0 if held[8] else 1
                gene_ball = 0 if (held[1] or held[5]) else 1
                if held[6] + held[7] < lele_ball + gene_ball:
                    continue
                targets = [pool[2] - held[2], pool[3] - held[3]]
                if lele_ball:
                    targets.append(pool[8] - held[8])
                if not held[1]:
                    targets.append(pool[1] - held[1])
                key = "lele_held" if held[8] else "lele_searched"
            chance = survive(n - hand - 1, prizes, targets)
            output[key] += Fraction(ways * remaining, comb(n, hand) * (n - hand)) * chance
    return output


def executable_route(held: Counter, deck: Counter) -> str | None:
    """Independent physical-hand/deck acceptance predicate for toy oracle."""
    if not (held[0] and held[4] and deck[2]):
        return None
    if held[3]:
        if held[1] or (deck[1] and (held[5] or held[6] or held[7])):
            return "old"
        return None
    if not deck[3]:
        return None
    tapu_search = 0 if held[8] else 1
    gene_search = 0 if (held[1] or held[5]) else 1
    if held[6] + held[7] < tapu_search + gene_search:
        return None
    if tapu_search and not deck[8]:
        return None
    if not held[1] and not deck[1]:
        return None
    return "lele_held" if held[8] else "lele_searched"


def physical_oracle(pool: tuple[int, ...], hand: int, prizes: int):
    cards = tuple(k for k, copies in enumerate(pool) for _ in range(copies))
    n = len(cards)
    hits = Counter()
    denominator = comb(n, hand) * comb(n - hand, prizes) * (n - hand - prizes)
    for chosen in combinations(range(n), hand):
        initial = set(chosen)
        if not any(cards[i] == 0 for i in initial):
            continue
        remaining = set(range(n)) - initial
        for prize in combinations(sorted(remaining), prizes):
            hidden = set(prize)
            for draw in remaining - hidden:
                held = Counter(cards[i] for i in initial | {draw})
                deck = Counter(cards[i] for i in remaining - hidden - {draw})
                route = executable_route(held, deck)
                if route is not None:
                    hits[route] += 1
    return {name: Fraction(hits[name], denominator) for name in ROUTES}


def verify_cards() -> None:
    pokemon = {**POKEMON, "Tapu Lele-GX": 1}
    trainers = {**TRAINERS, "Special Red Card": 1}
    energy = dict(ENERGY)
    prints = {**PRINT_IDS, "Tapu Lele-GX": "sm2-60"}
    assert (sum(pokemon.values()), sum(trainers.values()), sum(energy.values())) == (15, 41, 4)
    all_copies = {**pokemon, **trainers, **energy}
    assert sum(all_copies.values()) == 60
    manifest = json.loads(
        (ROOT / "results" / "decks" /
         "mew-genesect-tapu-wally-counterfactual" / "deck.json")
        .read_text(encoding="utf-8")
    )
    assert manifest["as_of"] == "2026-10-12"
    assert {
        entry["name"]: entry["quantity"] for entry in manifest["cards"]
    } == all_copies
    assert {
        entry["name"]: entry["print_id"] for entry in manifest["cards"]
    } == prints
    resources = ROOT / "resources"
    records = load_all_card_records(resources)
    basic = 0
    for name, copies in all_copies.items():
        record = records[prints[name]]
        assert record.name == name, (name, record.name)
        basic += copies if record.is_basic_pokemon else 0
    assert basic == 12
    proof = adjudicate_deck(
        [DeckEntry(prints[name], copies) for name, copies in all_copies.items()],
        resources,
        as_of=date(2026, 10, 12),
    )
    assert proof.construction.valid, proof.construction.issues
    assert proof.disposition == "eligible_snapshot"
    def card(printed: str):
        set_id = printed.rsplit("-", 1)[0]
        values = json.loads((resources / "cards" / "en" / f"{set_id}.json").read_text(encoding="utf-8"))
        return next(c for c in values if c["id"] == printed)
    assert "from your hand onto your Bench" in card("sm2-60")["abilities"][0]["text"]
    assert "Supporter" in card("sm2-60")["abilities"][0]["text"]
    assert "put it into your hand" in " ".join(card("swsh1-179")["rules"])
    assert "put it onto your Bench" in " ".join(card("swsh8-225")["rules"]) or "put them onto your Bench" in " ".join(card("swsh8-225")["rules"])
    assert "excluding Pokémon-EX" in " ".join(card("xy6-94")["rules"])
    print("LEGALITY PASSED: 15 Pokémon / 41 Trainers / 4 Energy, 12 Basics")


def main():
    verify_cards()
    for pool, hand, prizes in (
        ((1, 1, 1, 1, 1, 0, 1, 0, 1, 4), 3, 2),
        ((2, 2, 2, 1, 1, 1, 1, 1, 1, 1), 4, 2),
    ):
        assert exact(pool, hand, prizes) == physical_oracle(pool, hand, prizes)
        print("Labeled-card exhaustive independent oracle PASSED N=", sum(pool))
    routes = exact(VARIANT, 7, 6)
    assert routes["old"] == BASELINE
    expected = {
        "lele_held": Fraction(11605751320981, 992185402768560),
        "lele_searched": Fraction(1929826608427, 40951048463325),
    }
    for name, value in expected.items():
        assert routes[name] == value
    total = sum(routes.values())
    assert total == Fraction(636040115150563, 8681622274224900)
    valid = 1 - Fraction(comb(48, 7), comb(60, 7))
    for name, rate in routes.items():
        print(f"{name}: {float(rate):.12%}, exact={rate}")
    print(f"new total: {float(total):.12%}, exact={total}")
    print(f"baseline total: {float(BASELINE):.12%}")
    print(f"incremental access: {float(total - BASELINE):.12%}")
    print(f"valid opening: {float(valid):.12%}")
    print(f"conditional valid opening: {float(total / valid):.12%}")


if __name__ == "__main__":
    main()
