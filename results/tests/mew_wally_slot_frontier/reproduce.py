"""Exact Wally/Tapu Lele slot frontier on the published 2026 Aichi Mew 60.

All rates are a restricted T1-going-second access endpoint, never match rates.
Reproduce: python results/tests/mew_wally_slot_frontier/reproduce.py
"""
from __future__ import annotations

import json
import sys
from datetime import date
from fractions import Fraction
from math import comb
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from results.competitive_deck_baselines.mew_genesect_reproduce import (
    ENERGY, POKEMON, PRINT_IDS, TRAINERS,
)
from results.tests.mew_wally_tapu_variant.reproduce import (
    exact, physical_oracle,
)
from tools.deck_legality_proof import adjudicate_deck
from tools.deck_validator import DeckEntry, load_all_card_records

# Each non-original option exchanges one or two Special Red Cards, with no
# other changes to the established English-print 60-card source baseline.
# Format: (Wally count, Tapu Lele-GX count).
FRONTIER = {
    "published_W1_L0": (1, 0),
    "one_Wally_one_Lele": (1, 1),
    "two_Wally_zero_Lele": (2, 0),
    "one_Wally_two_Lele": (1, 2),
    "two_Wally_one_Lele": (2, 1),
    "three_Wally_zero_Lele": (3, 0),
}

EXPECTED = {
    "published_W1_L0": (
        Fraction(167155400140607, 11575496365633200),
        Fraction(167155400140607, 11575496365633200),
    ),
    "one_Wally_one_Lele": (
        Fraction(636040115150563, 8681622274224900),
        Fraction(167155400140607, 11575496365633200),
    ),
    "two_Wally_zero_Lele": (
        Fraction(3611784934223, 130550710890600),
        Fraction(3611784934223, 130550710890600),
    ),
    "one_Wally_two_Lele": (
        Fraction(4419175629125911, 52089733645349400),
        Fraction(167155400140607, 11575496365633200),
    ),
    "two_Wally_one_Lele": (
        Fraction(207472683238253, 2367715165697700),
        Fraction(3611784934223, 130550710890600),
    ),
    "three_Wally_zero_Lele": (
        Fraction(276110269671017, 6945297819379920),
        Fraction(276110269671017, 6945297819379920),
    ),
}


def pool(wally: int, lele: int) -> tuple[int, ...]:
    assert wally >= 1 and lele >= 0 and wally + lele <= 3
    # Mew V, Genesect V, VMAX, Wally, DCE, VIP, Quick, Ultra, Lele,
    # all remaining prints combined (which include remaining Red Cards).
    out = (4, 4, 3, wally, 4, 3, 4, 4, lele, 33 - (wally - 1) - lele)
    assert sum(out) == 60
    return out


def validate_prints() -> None:
    pokemon = {**POKEMON, "Tapu Lele-GX": 1}
    trainers = dict(TRAINERS)
    trainers["Wally"] = 2
    trainers.pop("Special Red Card")
    cards = {**pokemon, **trainers, **ENERGY}
    assert (sum(pokemon.values()), sum(trainers.values()), sum(ENERGY.values())) == (15, 41, 4)
    manifest = json.loads(
        (ROOT / "results/decks/mew-genesect-wally2-tapu1/deck.json").read_text(encoding="utf-8")
    )
    assert manifest["as_of"] == "2026-10-13"
    assert {c["name"]: c["quantity"] for c in manifest["cards"]} == cards
    prints = {**PRINT_IDS, "Tapu Lele-GX": "sm2-60"}
    prints.pop("Special Red Card")
    assert {c["name"]: c["print_id"] for c in manifest["cards"]} == prints
    resources = ROOT / "resources"
    records = load_all_card_records(resources)
    assert sum(q for name, q in pokemon.items() if records[prints[name]].is_basic_pokemon) == 12
    proof = adjudicate_deck(
        [DeckEntry(prints[name], amount) for name, amount in cards.items()],
        resources, as_of=date(2026, 10, 13),
    )
    assert proof.construction.valid, proof.construction.issues
    assert proof.disposition == "eligible_snapshot", proof
    def card(print_id: str) -> dict:
        sid = print_id.rsplit("-", 1)[0]
        data = json.loads((resources / "cards/en" / f"{sid}.json").read_text(encoding="utf-8"))
        return next(c for c in data if c["id"] == print_id)
    assert "first turn" in " ".join(card("xy6-94")["rules"])
    assert "from your hand onto your Bench" in card("sm2-60")["abilities"][0]["text"]
    assert "put them onto your Bench" in " ".join(card("swsh8-225")["rules"])
    print("English-print paper Expanded snapshot proof PASS: 60 cards, 12 Basics")


def main() -> None:
    validate_prints()
    # Test changed multiplicities against the independent physical-card oracle,
    # not merely against a second application of the symbolic formula.
    toys = (
        ((1, 1, 1, 2, 1, 0, 1, 1, 1, 3), 3, 2),
        ((1, 1, 1, 1, 1, 0, 1, 1, 2, 3), 3, 2),
        ((2, 1, 1, 3, 1, 1, 1, 1, 0, 2), 4, 2),
    )
    for toy, hand, prizes in toys:
        assert exact(toy, hand, prizes) == physical_oracle(toy, hand, prizes)
        print(f"Independent labeled-card enumeration PASS N={sum(toy)}")

    observed = {}
    for label, (wally, lele) in FRONTIER.items():
        routes = exact(pool(wally, lele), 7, 6)
        unrestricted = sum(routes.values(), Fraction(0))
        # With persistent Wonder Tag suppression, only the naturally held
        # Wally route remains. No Stadium-removal assumption is required.
        blocked = routes["old"]
        assert (unrestricted, blocked) == EXPECTED[label], label
        observed[label] = (unrestricted, blocked)
        valid = 1 - Fraction(comb(60 - 11 - lele, 7), comb(60, 7))
        print(
            f"{label}: no_lock={float(unrestricted):.12%}; "
            f"Wonder_Tag_suppressed={float(blocked):.12%}; "
            f"valid_opening={float(valid):.12%}; exact={unrestricted}"
        )

    w2l1 = observed["two_Wally_one_Lele"]
    w1l2 = observed["one_Wally_two_Lele"]
    w3l0 = observed["three_Wally_zero_Lele"]
    assert w2l1[0] > w1l2[0] and w2l1[1] > w1l2[1]
    # Two-state mixture only, with blocker prevalence supplied externally.
    p = (w2l1[0] - w3l0[0]) / (w2l1[0] - w2l1[1])
    assert p == Fraction(4987144017417877, 6246593684973178)
    print(f"W2L1 vs W3L0 blocker-mixture crossover p={float(p):.12%}; exact={p}")
    print("CAVEAT: access-only, simplified ball payment, opponent-state frequency unknown")


if __name__ == "__main__":
    main()
