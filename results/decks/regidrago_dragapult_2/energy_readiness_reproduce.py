"""SFT: physical Prize/turn draw oracle and both printed Regidrago 60s."""

from __future__ import annotations

import json
from fractions import Fraction
from itertools import combinations, permutations
from pathlib import Path

from tools.deck_validator import load_all_card_records
from tools.regidrago_two_turn_natural_energy import calculate


def brute(n: int, opener: int, prizes: int,
          starters: int, dde: int, energy: int) -> tuple[Fraction,Fraction]:
    cards = (("Starter",)*starters+("DDE",)*dde+("Basic",)*energy
             +("Other",)*(n-starters-dde-energy))
    eligible = winning = total = 0
    for open_ids in combinations(range(n),opener):
        unused = [i for i in range(n) if i not in open_ids]
        valid = any(cards[i]=="Starter" for i in open_ids)
        for prize_ids in combinations(unused,prizes):
            available = [i for i in unused if i not in prize_ids]
            for draw1,draw2 in permutations(available,2):
                total += 1
                if not valid:
                    continue
                eligible += 1
                seen = [cards[i] for i in open_ids]+[cards[draw1],cards[draw2]]
                if seen.count("DDE")>=1 and seen.count("DDE")+seen.count("Basic")>=2:
                    winning += 1
    return Fraction(eligible,total),Fraction(winning,eligible)


def main() -> None:
    checked = 0
    for n,opener,s,d,e in ((8,3,2,1,2),(9,3,3,2,1),
                           (10,3,3,2,2),(10,4,2,2,2)):
        expected = calculate(n,opener,s,d,e)
        for prizes in (0,1,2):
            got = brute(n,opener,prizes,s,d,e)
            assert got==(expected.accepted_opening,
                         expected.ready_given_valid_opening)
            checked += 1
    print(f"PASS: {checked} independently enumerated Prize/draw populations")

    root = Path(__file__).resolve().parents[3]
    baseline=json.loads((root/"results"/"competitive_deck_baselines"
                         /"regidrago_haruku_2026.json").read_text(encoding="utf-8"))
    variant=json.loads((Path(__file__).resolve().parent
                        /"candidate.json").read_text(encoding="utf-8"))
    records=load_all_card_records(root/"resources")
    for deck in (baseline,variant):
        cards=deck["cards"]
        starters=sum(c["quantity"] for c in cards
                     if records[c["print_id"]].is_basic_pokemon)
        dde=sum(c["quantity"] for c in cards if c["name"]=="Double Dragon Energy")
        basics=sum(c["quantity"] for c in cards
                   if c["name"] in ("Grass Energy","Fire Energy"))
        assert (starters,dde,basics)==(15,4,6)
        result=calculate(60,7,starters,dde,basics)
        assert result.accepted_opening==Fraction(172135,195054)
        assert result.ready_given_valid_opening==Fraction(
            1277933731,3913833495)
        assert result.ready_unconditional==Fraction(
            1277933731,4434942798)
    print("PASS: original and candidate both have 32.651714301%")
    print("natural turn-two compatible Energy source exposure after legal opener")
    print("LIMIT: excludes extra draw, search, Crispin acceleration and attacks")


if __name__=="__main__":
    main()
