"""Restricted Arc Phone policy: every played Arc must exchange a Prize."""
from fractions import Fraction
from functools import lru_cache
from tools.arc_phone_deck_order_policy import arc_swap, draw, observe, optimize, exact_unknown_orders


@lru_cache(None)
def forced_swap(belief, arcs, shoes):
    if not belief[0][0][1] or not (arcs or shoes):
        return Fraction()
    groups = observe(belief, 0)
    options = [Fraction()]
    if arcs:
        value = Fraction()
        for _, (p, seen) in groups.items():
            choices = [forced_swap(arc_swap(seen, slot), arcs - 1, shoes)
                       for slot in range(len(seen[0][0][0]))]
            value += p * max(choices)
        options.append(value)
    if shoes:
        value = Fraction()
        for top, (p, seen) in groups.items():
            keep = Fraction(1) if top == 'T' else forced_swap(
                draw(seen, 1), arcs + (top == 'A'), shoes - 1 + (top == 'S'))
            if len(seen[0][0][1]) >= 2:
                discard = sum((q * (Fraction(1) if c == 'T' else forced_swap(
                    draw(b, 2), arcs + (c == 'A'), shoes - 1 + (c == 'S')))
                    for c, (q, b) in observe(seen, 1).items()), Fraction())
                keep = max(keep, discard)
            value += p * keep
        options.append(value)
    return max(options)


def compare(prizes, deck, arcs, shoes):
    belief = exact_unknown_orders(tuple(prizes), tuple(deck))
    return forced_swap(belief, arcs, shoes), optimize(belief, arcs, shoes)
