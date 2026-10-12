"""Source-verified Lightning-unit and self-KO Prize gate for Hosoda Raichu.

A ceiling for one fully paid Electrode-GX Extra Energy Bomb into one non-Rule-Box
Alolan Raichu. It does not estimate the chance to assemble the cards in time.
"""
from __future__ import annotations

import json
from itertools import product
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
RESOURCES = ROOT / "resources" / "cards" / "en"
CAPACITY = (4, 4, 4)  # Reversal, Counter, Unit Energy LPM
ENERGY_CARDS_ATTACHED = 5
PACKET_DAMAGE = 30


def source_record(card_id: str) -> dict:
    set_id = card_id.rsplit("-", 1)[0]
    data = json.loads((RESOURCES / f"{set_id}.json").read_text(encoding="utf-8"))
    return next(row for row in data if row["id"] == card_id)


def prize_state(ours: int, opponents: int) -> bool | None:
    """Return whether conditional Energy is active AFTER Electrode-GX self-KO.

    None signals that the self-KO gives the opponent their final Prize cards.
    """
    if not (1 <= ours <= 6 and 1 <= opponents <= 6):
        raise ValueError("both players must have one to six Prize cards left")
    if opponents <= 2:
        return None
    return ours > opponents - 2


def lightning_units(reversal: int, counter: int, unit: int,
                    behind: bool) -> int:
    if min(reversal, counter, unit) < 0:
        raise ValueError("negative Energy card count")
    if reversal > 4 or counter > 4 or unit > 4:
        raise ValueError("outside actual 2026 deck supply")
    return 3 * reversal + 2 * counter + unit if behind else unit


def best_five_cards(behind: bool) -> tuple[int, tuple[int, int, int]]:
    """Maximize available Lightning units over five distinct attached cards."""
    candidates = (
        (lightning_units(r, c, u, behind), (r, c, u))
        for r, c, u in product(range(5), repeat=3)
        if r + c + u == ENERGY_CARDS_ATTACHED
    )
    return max(candidates, key=lambda result: result[0])


def verify() -> None:
    electrode = source_record("sm7-48")
    raichu = source_record("sm11-57")
    reversal = source_record("sv2-192")
    counter = source_record("sm4-100")
    unit = source_record("sm5-138")
    assert "opponent takes 2 Prize cards" in electrode["rules"][0]
    assert "attach 5 Energy cards from your discard pile" in electrode["abilities"][0]["text"]
    assert "this Pokémon is Knocked Out" in electrode["abilities"][0]["text"]
    assert "each Energy you discarded" in raichu["attacks"][0]["text"]
    assert "choose 1 of your opponent's Pokémon" in raichu["attacks"][0]["text"]
    assert "provides only 3 Energy at a time" in reversal["rules"][0]
    assert "Evolution Pokémon that doesn't have a Rule Box" in reversal["rules"][0]
    assert "provides only 2 Energy at a time" in counter["rules"][1]
    assert "isn't a Pokémon-GX or Pokémon-EX" in counter["rules"][1]
    assert "provides only 1 Energy at a time" in unit["rules"][1]
    assert "Lightning" in unit["rules"][1]

    assert best_five_cards(True) == (14, (4, 1, 0))
    assert best_five_cards(False)[0] == 4
    assert best_five_cards(False)[1][2] == 4
    assert prize_state(6, 6) is True
    assert prize_state(2, 6) is False
    assert prize_state(3, 4) is True
    assert prize_state(4, 6) is False
    assert prize_state(6, 2) is None
    assert prize_state(1, 1) is None
    assert max(lightning_units(*mix, True) for mix in product(range(5), repeat=3)
               if sum(mix) == 5) == 14
    assert all(
        (prize_state(o, p) is None if p <= 2
         else prize_state(o, p) == (o > p - 2))
        for o, p in product(range(1, 7), repeat=2)
    )

    print("PASS: source cards independently verify 2-Prize self-KO, 5 cards,")
    print("      3/2/1 conditional Lightning units and Electro Rain energy-unit text")
    print("PASS: tied 6-6 before self-KO -> 6-4 behind, 4 Reversal + Counter")
    print("      supplies 14 Lightning, at most 14*30=420 spread damage")
    print("PASS: if still not behind after self-KO, at most 4 Unit LPM")
    print("      supplies Lightning, at most 4*30=120 spread damage")
    print("PASS: opponent <=2 Prizes before self-KO -> game ends before attack")
    print("LIMIT: no attack/recovery/discount availability, damage prevention,")
    print("      complete-game success probability or matchup claim")


if __name__ == "__main__":
    verify()
