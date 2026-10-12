"""Source-backed paired Trifrost payment inversion through Super Rod and Crispin.

Regidrago VSTAR starts with one DDE attached; hand has another DDE,
Grass, both Fire copies, Super Rod and Crispin; deck has two DDE,
three Grass, zero Fire. An attachment then copied Trifrost consumes
the attached DDE and Basic. On the following turn, allow exactly
Super Rod, Crispin and one manual attachment, with no opponent response.
"""
from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from tools.energy_discard_solver import attack_cost_ready

DDE_TYPES = ("Grass", "Fire", "Water", "Lightning", "Psychic",
             "Fighting", "Darkness", "Metal", "Fairy", "Colorless")


@dataclass(frozen=True)
class Route:
    spent_basic: str
    after_attack_hand: dict[str, int]
    after_attack_discard: dict[str, int]
    rod_returned: str
    crispin_attached: str | None
    next_attached: dict[str, int]
    apex_ready: bool


def execute_route(chosen: str, *, prior_fire_discard: int = 0,
                  extra_fire_item_payment: bool = False) -> Route:
    if chosen not in ("Grass", "Fire") or not 0 <= prior_fire_discard <= 2:
        raise ValueError("Invalid Basic or prior Fire zone")
    hand = Counter({"DDE":1, "Grass":1, "Fire":2-prior_fire_discard})
    deck = Counter({"DDE":2, "Grass":3})
    discard = Counter({"Fire":prior_fire_discard})
    attached = Counter({"DDE":1})
    def conserve() -> None:
        for kind, expected in (("DDE",4),("Grass",4),("Fire",2)):
            assert hand[kind]+deck[kind]+discard[kind]+attached[kind] == expected
    conserve()
    if hand[chosen] == 0:
        raise ValueError("Chosen Basic not held")
    # An ordinary manual attachment this turn, then a copied attack
    # that discards every attached Energy.
    hand[chosen] -= 1
    attached[chosen] += 1
    discard.update(attached)
    attached.clear()
    after_hand = {k: hand[k] for k in ("DDE","Grass","Fire")}
    after_discard = {k: discard[k] for k in ("DDE","Grass","Fire")}

    # Optional payable Item discards a hand Fire before Super Rod.
    if extra_fire_item_payment:
        if hand["Fire"] == 0:
            raise ValueError("No Fire to pay extra Item")
        hand["Fire"] -= 1
        discard["Fire"] += 1

    # Next own turn: Super Rod returns one available Basic Energy to deck.
    rod = "Fire" if discard["Fire"] else "Grass" if discard["Grass"] else "none"
    if rod != "none":
        discard[rod] -= 1
        deck[rod] += 1
    # Crispin searches two different Basics when possible: place one
    # Fire in hand, attach the other Grass to Regidrago.
    crispin_attach = None
    if deck["Grass"] and deck["Fire"]:
        deck["Grass"] -= 1
        deck["Fire"] -= 1
        hand["Fire"] += 1
        attached["Grass"] += 1
        crispin_attach = "Grass"
    elif deck["Grass"] or deck["Fire"]:
        # One searched Basic goes into hand, leaving none to attach.
        kind = "Grass" if deck["Grass"] else "Fire"
        deck[kind] -= 1
        hand[kind] += 1

    # Normal next-turn attachment is still unused.
    hand["DDE"] -= 1
    attached["DDE"] += 1
    providers = [{"units":2,"types":list(DDE_TYPES)}]
    for kind in ("Grass","Fire"):
        providers.extend({"units":1,"types":[kind]} for _ in range(attached[kind]))
    ready = attack_cost_ready(providers,["Grass","Grass","Fire"])
    conserve()
    return Route(chosen,after_hand,after_discard,rod,crispin_attach,
                 {k:attached[k] for k in ("DDE","Grass","Fire")},ready)


def _card(root: Path, card_id: str) -> dict[str, Any]:
    path = root/"resources/cards/en"/f"{card_id.split('-')[0]}.json"
    return next(x for x in json.loads(path.read_text(encoding="utf-8"))
                if x["id"] == card_id)


def build(root: Path) -> dict:
    deck=json.loads((root/"results/regidrago_aichi_top10_playable/yoshioka_regidrago_2026.json").read_text(encoding="utf-8"))
    trainers={x["name"] for x in deck["groups"]["Trainer"]}
    assert {"Super Rod","Crispin"} <= trainers
    rod=_card(root,"sv2-188")
    crispin=_card(root,"sv7-133")
    kyurem=_card(root,"sv6pt5-47")
    drago=_card(root,"swsh12-136")
    dde=_card(root,"xy6-97")
    assert "Shuffle up to 3 in any combination of Pokémon and Basic Energy cards from your discard pile into your deck." in rod["rules"]
    assert "up to 2 Basic Energy cards of different types" in " ".join(crispin["rules"])
    assert "Attach the other to 1 of your Pokémon" in " ".join(crispin["rules"])
    assert "Discard all Energy from this Pokémon" in kyurem["attacks"][0]["text"]
    assert next(x for x in drago["attacks"] if x["name"]=="Apex Dragon")["cost"] == ["Grass","Grass","Fire"]
    assert "provides only 2 Energy at a time" in " ".join(dde["rules"])
    grass=execute_route("Grass")
    fire=execute_route("Fire")
    assert not grass.apex_ready and fire.apex_ready
    assert grass.crispin_attached is None and fire.crispin_attached == "Grass"
    assert grass.rod_returned == "Grass" and fire.rod_returned == "Fire"
    assert execute_route("Grass",prior_fire_discard=1).apex_ready
    assert execute_route("Grass",extra_fire_item_payment=True).apex_ready
    return {"source":deck["source"],
            "card_ids":["swsh12-136","sv6pt5-47","sv2-188","sv7-133","xy6-97"],
            "state":"DDE attached; hand another DDE, Grass, both Fire, Rod, Crispin; deck 2 DDE, 3 Grass, no Fire",
            "branches":[grass.__dict__,fire.__dict__],
            "controls":"Prior Fire in discard or an extra payable Fire-discard Item rescues Grass route",
            "scope":"Restricted one-opponent-cycle sequence; no match frequency"}


if __name__=="__main__":
    print(json.dumps(build(Path(".")),indent=2))
