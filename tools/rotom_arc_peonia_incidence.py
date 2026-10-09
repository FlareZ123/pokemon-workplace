"""Exact union of Arc/Peonia raw topdeck and top-five-Item repacking."""
import json
from pathlib import Path
from fractions import Fraction
from itertools import combinations, permutations
from math import comb

from tools.peonia_arc_opening_incidence import exact_event


def choose(n, k):
    return comb(n, k) if 0 <= k <= n else 0


def with_top_five(starters=12, arcs=4, peonias=2, arrangers=4,
               disposable=None, total=60, opening=7, prizes=6):
    """P(A/P/F hand and T on top OR R hand and T among next five)."""
    # R denotes top-five arranging Items, up to four Rotom Phone plus
    # four Pokédex. Their later deck-tail effects differ; this narrow
    # event only needs them to put an observed target T on top.
    if disposable is None:
        disposable = total - starters - arcs - peonias - arrangers - 1
    protected = total-starters-arcs-peonias-arrangers-1-disposable
    if min(starters, arcs, peonias, arrangers, disposable, protected) < 0:
        raise ValueError("Invalid category counts")
    if total-opening-prizes-1 < 1:
        raise ValueError("No deck card remains after turn draw")

    base = exact_event(starters,arcs,peonias,disposable,total,opening)
    if not arrangers:
        return base

    valid = Fraction(choose(total,opening)-choose(total-starters,opening),
                     choose(total,opening))
    seen = opening+1
    exposure_with_rotom = Fraction()
    for b in range(1,min(starters,seen)+1):
        for a in range(1,min(arcs,seen-b)+1):
            for p in range(1,min(peonias,seen-b-a)+1):
                for r in range(1,min(arrangers,seen-b-a-p)+1):
                    for f in range(1,min(disposable,seen-b-a-p-r)+1):
                        o = seen-b-a-p-r-f
                        if not 0 <= o <= protected:
                            continue
                        ways = (choose(starters,b)*choose(arcs,a)
                                *choose(peonias,p)*choose(arrangers,r)
                                *choose(disposable,f)*choose(protected,o))
                        opener_factor = Fraction(opening,seen) if b == 1 else 1
                        exposure_with_rotom += (
                            Fraction(ways,choose(total,seen))*opener_factor
                        )

    # Arc alone covers deck position 1 (base). Holding Rotom additionally
    # covers positions 2..5 with T placed on top by its look-and-select Item.
    extra_positions = min(5,total-opening-prizes-1)-1
    return (base + exposure_with_rotom/valid
            * Fraction(extra_positions,total-opening-1))


def with_rotom(starters=12, arcs=4, peonias=2, rotoms=4,
               disposable=None, total=60, opening=7, prizes=6):
    """Convenience name when all top-five Items are Rotom Phone."""
    return with_top_five(starters,arcs,peonias,rotoms,
                         disposable,total,opening,prizes)


def labeled_oracle(starters=2, arcs=1, peonias=1, rotoms=1,
                   disposable=4, opening=4, prizes=1):
    """Independent physical setup, Prize, turn-draw and deck-order oracle."""
    cards = ("B"*starters+"A"*arcs+"P"*peonias+"R"*rotoms
             +"T"+"F"*disposable)
    n = len(cards)
    numerator = denominator = 0
    for first in combinations(range(n),opening):
        if not any(cards[i] == "B" for i in first):
            continue
        pool = [i for i in range(n) if i not in first]
        for prize in combinations(pool,prizes):
            after_prize = [i for i in pool if i not in prize]
            for turn_draw in after_prize:
                hand = [cards[i] for i in (*first,turn_draw)]
                ready = all(x in hand for x in "APF")
                has_rotom = "R" in hand
                rest = [i for i in after_prize if i != turn_draw]
                for order in permutations(rest):
                    top = [cards[i] for i in order]
                    denominator += 1
                    if ready and (
                        top[0] == "T" or (
                            has_rotom and "T" in top[:5]
                        )
                    ):
                        numerator += 1
    return Fraction(numerator,denominator)



def assert_card_text():
    """Pin the precise print text supporting the modeled source transitions."""
    root = Path(__file__).resolve().parent.parent / "resources" / "cards" / "en"
    specs = (
        ("swsh35", "swsh35-64", "Rotom Phone", "Item",
         "Look at the top 5 cards of your deck, choose 1 of them"),
        ("xy12", "xy12-82", "Pokédex", "Item",
         "Look at the top 5 cards of your deck and put them back in any order."),
        ("swsh11", "swsh11-152", "Arc Phone", "Item",
         "You may switch that card with 1 of your face-down Prize cards."),
        ("swsh6", "swsh6-149", "Peonia", "Supporter",
         "Put up to 3 Prize cards into your hand."),
    )
    for set_id, card_id, name, subtype, passage in specs:
        records = json.loads((root / (set_id + ".json")).read_text(encoding="utf-8"))
        card = next(x for x in records if x["id"] == card_id)
        assert card["name"] == name
        assert subtype in card["subtypes"]
        assert card["legalities"]["expanded"] == "Legal"
        assert passage in card["rules"][0]



def run():
    assert_card_text()
    values = (
        Fraction(345378629,215366137272),
        Fraction(20123651,8973589053),
        Fraction(4260227,1506056904),
        Fraction(362395607,107683068636),
        Fraction(830344565,215366137272),
    )
    for copies,expected in enumerate(values):
        actual = with_rotom(rotoms=copies)
        assert actual == expected,(copies,actual,expected)
        print(f"Rotom={copies}: {actual} = {float(actual):.9%}")
    # Two different legally named Items each allow four copies, so a
    # top-five selector family can contain 4 Rotom Phone + 4 Pokédex.
    assert with_top_five(arrangers=8) == Fraction(105799951,19578739752)
    print(f"4 Rotom + 4 Pokédex = {float(with_top_five(arrangers=8)):.9%}")
    for f,expected in (
        (4,Fraction(7,150)),
        (5,Fraction(305,8568)),
    ):
        calculated = with_rotom(starters=2,arcs=1,peonias=1,
                                rotoms=1,disposable=f,
                                total=6+f,opening=4,prizes=1)
        counted = labeled_oracle(disposable=f)
        assert calculated == counted == expected,(f,calculated,counted)
        print(f"Independent labeled microdeck F={f}: {counted}")
    print("Rotom union probabilities and labeled oracles passed.")


if __name__ == "__main__":
    run()
