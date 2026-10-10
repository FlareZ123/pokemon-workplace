"""Physical 60-card identity certificate for Secret Box/Guzma & Hala recycling.

Conserves card instances and protected opening fillers throughout Box's
pre-search discard and the later G&H cost. The canonical Aichi opening
is deliberately narrow; target is Bunnelby benched with TM Evolution
and Jet Energy held, exactly as in the source first-turn planner.
"""
from dataclasses import dataclass
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
from aichi_vileplume_secret_box import SECRET_BOX_DECK

FILLERS = ("Guzma", "Cassius", "Karen", "Faba", "Plumeria", "Lusamine")

@dataclass
class Zones:
    hand: set[int]
    deck: set[int]
    prizes: set[int]
    active: set[int]
    bench: set[int]
    stadium: set[int]
    discard: set[int]

    def check(self):
        parts = (self.hand, self.deck, self.prizes, self.active,
                 self.bench, self.stadium, self.discard)
        assert sum(map(len, parts)) == 60
        assert set.union(*parts) == set(range(60))

def labels(indices):
    return tuple(sorted(SECRET_BOX_DECK[i] for i in indices))

def fetch(name, source):
    index = next((i for i in sorted(source)
                  if SECRET_BOX_DECK[i] == name), None)
    assert index is not None, name
    source.remove(index)
    return index

def transfer(i, a, b, z):
    getattr(z, a).remove(i)
    getattr(z, b).add(i)
    z.check()

def run(extra_prizes, disposable, expected):
    remaining = set(range(60))
    opening = [fetch(n, remaining) for n in
               ("Oddish", "Secret Box", *FILLERS[:5])]
    prizes = {fetch(n, remaining) for n in
              (("Tag Call",) * 4 + tuple(extra_prizes))}
    draw = fetch(FILLERS[5], remaining)
    z = Zones(set(opening[1:] + [draw]), remaining, prizes,
              {opening[0]}, set(), set(), set())
    z.check()
    filler_ids = opening[2:] + [draw]
    safe = set(filler_ids[:disposable])
    protected = set(filler_ids[disposable:])

    if disposable < 3:
        assert not expected and protected <= z.hand
        return False

    box = next(i for i in z.hand if SECRET_BOX_DECK[i] == "Secret Box")
    transfer(box, "hand", "discard", z)
    box_pay = set(filler_ids[:3])
    for i in box_pay:
        transfer(i, "hand", "discard", z)
    assert box_pay <= safe  # payment chosen before any deck inspection
    assert all(SECRET_BOX_DECK[i] != "Tag Call" for i in z.deck)
    for name in ("Technical Machine: Evolution", "Guzma & Hala", "Artazon"):
        i = fetch(name, z.deck)
        z.hand.add(i)
        z.check()

    supporter = next(i for i in z.hand
                     if SECRET_BOX_DECK[i] == "Guzma & Hala")
    transfer(supporter, "hand", "discard", z)
    payment = sorted(safe - box_pay)
    for name in ("Technical Machine: Evolution", "Artazon"):
        if any(SECRET_BOX_DECK[i] == name for i in z.deck):
            payment.append(next(i for i in z.hand if SECRET_BOX_DECK[i] == name))
    if len(payment) < 2:
        assert not expected and protected <= z.hand
        return False
    payment = payment[:2]
    for i in payment:
        transfer(i, "hand", "discard", z)

    # G&H's optional two-card payment enables its Tool + Special Energy
    # searches; Stadium search is available even without that payment.
    for name in ("Artazon", "Technical Machine: Evolution", "Jet Energy"):
        if not any(SECRET_BOX_DECK[i] == name for i in z.hand):
            i = fetch(name, z.deck)
            z.hand.add(i)
            z.check()
    artazon = next(i for i in z.hand if SECRET_BOX_DECK[i] == "Artazon")
    transfer(artazon, "hand", "stadium", z)
    bunnelby = fetch("Bunnelby", z.deck)
    z.bench.add(bunnelby)
    z.check()
    assert expected and protected <= z.hand
    assert ("Jet Energy" in labels(z.hand)
            and "Technical Machine: Evolution" in labels(z.hand))
    assert len(z.discard) == 7
    print("prizes:", extra_prizes, "disposable:", disposable,
          "Box cost:", labels(box_pay),
          "G&H cost:", labels(payment),
          "preserved:", labels(protected),
          "payload:", labels(z.hand))
    return True

def main():
    assert not run(("Pidgeotto", "Gloom"), 2, False)
    assert run(("Pidgeotto", "Gloom"), 3, True)
    assert not run(("Technical Machine: Evolution", "Gloom"), 3, False)
    assert run(("Technical Machine: Evolution", "Gloom"), 4, True)
    assert not run(("Technical Machine: Evolution", "Artazon"), 4, False)
    assert run(("Technical Machine: Evolution", "Artazon"), 5, True)
    print("Named physical Secret Box payment witnesses passed.")

if __name__ == "__main__":
    main()
