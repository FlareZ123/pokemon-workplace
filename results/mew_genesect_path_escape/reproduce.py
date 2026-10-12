"""Exact 2026 Aichi Mew/Genesect Path escape access and toy oracle."""

from __future__ import annotations

import json
import sys
from collections import Counter
from datetime import date
from fractions import Fraction
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from results.competitive_deck_baselines.mew_genesect_reproduce import (
    POKEMON, TRAINERS, ENERGY, PRINT_IDS,
)
from tools.deck_legality_proof import adjudicate_deck
from tools.deck_validator import DeckEntry
from tools.mew_path_escape_frontier import EscapeFrontier, exact_escape_frontier


def physical_oracle(
    genesect: int, other_basics: int, outs: int, mails: int, filler: int,
    *,
    hand_size: int, prizes: int, reach: int,
) -> EscapeFrontier:
    """Independently enumerate every labeled legal hand/Prize/draw world."""

    cards = (
        ["G"]*genesect + ["B"]*other_basics + ["O"]*outs +
        ["M"]*mails + ["R"]*filler
    )
    n = len(cards)
    worlds = 0
    gene = 0
    direct = 0
    total = Fraction(0)
    gene_direct = 0
    gene_total = Fraction(0)

    for hand in combinations(range(n), hand_size):
        if not any(cards[i] in {"G", "B"} for i in hand):
            continue
        hand_set = set(hand)
        after_hand = tuple(i for i in range(n) if i not in hand_set)
        for prize in combinations(after_hand, prizes):
            prize_set = set(prize)
            undrawn = tuple(i for i in after_hand if i not in prize_set)
            for draw in undrawn:
                worlds += 1
                visible = hand + (draw,)
                seen_gene = any(cards[i] == "G" for i in visible)
                seen_out = any(cards[i] == "O" for i in visible)
                mail_count = sum(cards[i] == "M" for i in visible)
                if seen_gene:
                    gene += 1
                if seen_out:
                    direct += 1
                    if seen_gene:
                        gene_direct += 1
                    success = Fraction(1)
                elif mail_count:
                    deck = tuple(i for i in undrawn if i != draw)
                    top_sets = tuple(combinations(deck, reach))
                    misses = sum(
                        not any(cards[i] == "O" for i in top)
                        for top in top_sets
                    )
                    success = 1-Fraction(misses, len(top_sets))**mail_count
                else:
                    success = Fraction(0)
                total += success
                if seen_gene:
                    gene_total += success

    return EscapeFrontier(
        Fraction(gene, worlds),
        Fraction(direct, worlds),
        total/worlds,
        Fraction(gene_direct, worlds),
        gene_total/worlds,
    )


def verify_prints() -> None:
    expected = {
        "swsh8-185": ("Genesect V", "Fusion Strike Pokémon in play"),
        "swsh6-148": ("Path to the Peak", "have no Abilities"),
        "xy6-89": ("Sky Field", "8 Pokémon on his or her Bench"),
        "sm2-125": ("Field Blower", "Stadium cards"),
        "swsh11-162": ("Lost Vacuum", "another card from your hand"),
        "xy6-92": ("Trainers' Mail", "top 4 cards of your deck"),
    }
    for print_id, (name, signature) in expected.items():
        set_id = print_id.rsplit("-", 1)[0]
        source = json.loads(
            (ROOT/"resources"/"cards"/"en"/(set_id+".json"))
            .read_text(encoding="utf-8")
        )
        printed = next(c for c in source if c["id"] == print_id)
        assert printed["name"] == name
        text = " ".join(
            printed.get("rules", []) +
            [a.get("text", "") for a in printed.get("abilities", [])]
        )
        assert signature in text, (print_id, text)
        if print_id == "swsh8-185":
            assert any(a["name"] == "Fusion Strike System" for a in printed["abilities"])

    assert POKEMON["Genesect V"] == 4
    assert TRAINERS["Sky Field"] == 2
    assert TRAINERS["Path to the Peak"] == 2
    assert TRAINERS["Field Blower"] == 1
    assert TRAINERS["Lost Vacuum"] == 1
    assert TRAINERS["Trainers' Mail"] == 3
    assert sum(POKEMON.values()) == 14
    assert sum(ENERGY.values()) == 4
    assert sum(TRAINERS.values()) == 42


def verify_legal_swap() -> None:
    counts: Counter[str] = Counter({**POKEMON, **TRAINERS, **ENERGY})
    for candidate in (False, True):
        current = counts.copy()
        if candidate:
            current["Sky Field"] += 1
            current["Path to the Peak"] -= 1
        assert sum(current.values()) == 60
        entries = [DeckEntry(PRINT_IDS[name], qty) for name, qty in current.items()]
        proof = adjudicate_deck(entries, ROOT/"resources", as_of=date(2026, 10, 12))
        assert proof.construction.valid, proof.construction.issues
        assert proof.disposition == "eligible_snapshot", proof.disposition


def run() -> None:
    for args in (
        (2, 1, 2, 2, 3),
        (1, 2, 1, 2, 4),
        (0, 2, 3, 1, 4),
        (2, 2, 0, 2, 4),
    ):
        params = dict(zip(("genesect", "other_basics", "outs", "mails", "filler"), args))
        exact = exact_escape_frontier(
            **params, opening_hand=3, prizes=2, mail_reach=2,
        )
        oracle = physical_oracle(
            *args, hand_size=3, prizes=2, reach=2,
        )
        assert exact == oracle, (args, exact, oracle)

    verify_prints()
    verify_legal_swap()

    # The Aichi source has 11 starting Basics: four Genesect and seven others.
    outs_without_vacuum = TRAINERS["Sky Field"] + TRAINERS["Field Blower"]
    for vacuum_payable in (False, True):
        extra = int(vacuum_payable)
        baseline_outs = outs_without_vacuum + extra
        candidate_outs = baseline_outs + 1
        old = exact_escape_frontier(
            genesect=4, other_basics=7, outs=baseline_outs,
            mails=3, filler=60-11-baseline_outs-3,
        )
        new = exact_escape_frontier(
            genesect=4, other_basics=7, outs=candidate_outs,
            mails=3, filler=60-11-candidate_outs-3,
        )
        assert old.genesect_visible == new.genesect_visible
        assert new.combined > old.combined
        assert new.conditional_on_genesect > old.conditional_on_genesect
        print({
            "vacuum_assumed_payable": vacuum_payable,
            "source_outs": (baseline_outs, candidate_outs),
            "baseline_counter_access_pct": round(float(old.combined)*100, 9),
            "candidate_counter_access_pct": round(float(new.combined)*100, 9),
            "delta_percentage_points": round(float(new.combined-old.combined)*100, 9),
            "conditional_genesect_baseline_pct": round(
                float(old.conditional_on_genesect)*100, 9
            ),
            "conditional_genesect_candidate_pct": round(
                float(new.conditional_on_genesect)*100, 9
            ),
        })

    print("PASS: four labeled-physical toy oracles, exact 60-card solver, paper snapshot construction")


if __name__ == "__main__":
    run()
