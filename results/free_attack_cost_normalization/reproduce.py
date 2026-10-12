"""Single-file regression for the source snapshot's two fake Free Energy tokens."""

from collections import Counter
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from free_attack_energy_normalizer import (  # noqa: E402
    normalized_attack_cost,
    normalized_converted_energy_cost,
)

printed = {
    card["id"]: card
    for path in sorted((ROOT / "resources" / "cards" / "en").glob("*.json"))
    for card in json.loads(path.read_text(encoding="utf-8"))
}

sentinel = []
for card in printed.values():
    for attack in card.get("attacks", []):
        if "Free" in attack["cost"]:
            sentinel.append((card["id"], card["name"], attack["name"]))
            assert attack["cost"] == ["Free"], (card["id"], attack)
            assert attack["convertedEnergyCost"] == 1, (card["id"], attack)
            assert normalized_attack_cost(attack) == ()
            assert normalized_converted_energy_cost(attack) == 0

assert set(sentinel) == {
    ("sv8pt5-4", "Budew", "Itchy Pollen"),
    ("me1-71", "Tyrogue", "Pow-Pow Punching"),
}, sentinel

budew_old = next(a for a in printed["sv8pt5-4"]["attacks"]
                 if a["name"] == "Itchy Pollen")
budew_new = next(a for a in printed["me2pt5-16"]["attacks"]
                 if a["name"] == "Itchy Pollen")
assert budew_old["text"] == budew_new["text"]
assert budew_new["cost"] == []
assert budew_new["convertedEnergyCost"] == 0
assert normalized_attack_cost(budew_old) == normalized_attack_cost(budew_new)
assert normalized_converted_energy_cost(budew_old) == 0
assert normalized_converted_energy_cost(budew_new) == 0

ordinary = next(a for a in printed["swsh12-136"]["attacks"]
                if a["name"] == "Apex Dragon")
assert normalized_attack_cost(ordinary) == ("Grass", "Grass", "Fire")
assert normalized_converted_energy_cost(ordinary) == 3

print("PASS: printed 0-Energy sentinel audit over", len(printed), "records.")
for card_id, name, attack in sorted(sentinel):
    print(f"  {card_id}: {name} / {attack}: source CEC 1 -> normalized 0")
print("PASS: same-effect Budew reprints converge; ordinary Apex Dragon remains [G,G,F].")
