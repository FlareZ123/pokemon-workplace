"""Exact finite-world Peonia / Arc Phone / Trekking Shoes policy.

Models a single known-composition Prize group with unknown physical positions.
Full deck order is hidden. Inert filler cards F have no playable effects.

Peonia: inspect up to three selected physical Prize slots; take their cards,
then return the same number of cards from hand to those slots in chosen order.
Arc Phone: inspect deck top, optionally exchange it with one Prize slot.
Trekking Shoes: inspect deck top, take it or discard it and draw the next card.

One Peonia is available, plus a known A/S/F hand. Probability objective:
put the critical T singleton into hand during this sequence.
"""
from collections import Counter, defaultdict
from fractions import Fraction
from functools import lru_cache
from itertools import combinations, product

KINDS = "TASF"


def distinct_orders(items):
    """Enumerate each multiset permutation once, including long filler tails."""
    counts = Counter(items)

    def walk(prefix):
        if len(prefix) == len(items):
            yield tuple(prefix)
        else:
            for card in KINDS:
                if counts[card]:
                    counts[card] -= 1
                    prefix.append(card)
                    yield from walk(prefix)
                    prefix.pop()
                    counts[card] += 1

    return tuple(walk([]))


def normalize(worlds):
    total = sum(worlds.values(), Fraction())
    return tuple(sorted(
        ((world, mass / total) for world, mass in worlds.items() if mass),
        key=lambda entry: entry[0],
    ))


def initial(prizes, deck):
    prizes_orders = distinct_orders(prizes)
    deck_orders = distinct_orders(deck)
    weight = Fraction(1, len(prizes_orders) * len(deck_orders))
    return normalize({
        (prizes_order, deck_order): weight
        for prizes_order in prizes_orders
        for deck_order in deck_orders
    })


def observe(belief, choice):
    """Integer choice observes deck index; tuple choice observes Prize slots."""
    groups = defaultdict(lambda: defaultdict(Fraction))
    for (prizes, deck), weight in belief:
        seen = tuple(prizes[i] for i in choice) if isinstance(choice, tuple) else deck[choice]
        groups[seen][(prizes, deck)] += weight
    return tuple(
        (seen, sum(worlds.values(), Fraction()), normalize(worlds))
        for seen, worlds in sorted(groups.items(), key=lambda pair: str(pair[0]))
    )


def transform(belief, effect):
    outcomes = defaultdict(Fraction)
    for world, mass in belief:
        outcomes[effect(world)] += mass
    return normalize(outcomes)


def add_hand(hand, cards):
    counts = list(hand)
    for card in cards:
        counts[KINDS.index(card)] += 1
    return tuple(counts)


def remove_hand(hand, cards):
    counts = list(hand)
    for card in cards:
        idx = KINDS.index(card)
        counts[idx] -= 1
        if counts[idx] < 0:
            return None
    return tuple(counts)


@lru_cache(None)
def play_peonia(belief, hand):
    size = len(belief[0][0][0])
    best = Fraction()
    for quantity in range(1, min(3, size) + 1):
        for chosen in combinations(range(size), quantity):
            expectation = Fraction()
            for viewed, chance, conditioned in observe(belief, chosen):
                acquired = add_hand(hand, viewed)
                possibilities = []
                for returned in set(product(KINDS, repeat=quantity)):
                    remaining = remove_hand(acquired, returned)
                    if remaining is None:
                        continue
                    if remaining[0]:
                        score = Fraction(1)
                    else:
                        def replace(world):
                            slots, deck = world
                            new_slots = list(slots)
                            for index, card in zip(chosen, returned):
                                new_slots[index] = card
                            return (tuple(new_slots), deck)

                        updated = transform(conditioned, replace)
                        score = optimal(updated, remaining, False)
                    possibilities.append(score)
                expectation += chance * max(possibilities)
            best = max(best, expectation)
    return best


@lru_cache(None)
def optimal(belief, hand, peonia_available):
    """Bellman optimum for the exact player-observable belief state."""
    if hand[0]:
        return Fraction(1)
    deck_available = bool(belief[0][0][1])
    if not peonia_available and (not deck_available or (not hand[1] and not hand[2])):
        return Fraction()

    actions = [Fraction()]
    if peonia_available:
        actions.append(play_peonia(belief, hand))

    if hand[1] and deck_available:
        after = remove_hand(hand, "A")
        expected = Fraction()
        for _top, chance, conditioned in observe(belief, 0):
            choices = [optimal(conditioned, after, peonia_available)]
            for slot in range(len(conditioned[0][0][0])):
                def exchange(world):
                    prizes, deck = world
                    new_prizes = list(prizes)
                    new_prizes[slot] = deck[0]
                    return (tuple(new_prizes), (prizes[slot],) + deck[1:])

                exchanged = transform(conditioned, exchange)
                choices.append(optimal(exchanged, after, peonia_available))
            expected += chance * max(choices)
        actions.append(expected)

    if hand[2] and deck_available:
        after = remove_hand(hand, "S")
        expected = Fraction()
        for top, chance, conditioned in observe(belief, 0):
            taken = Fraction(1) if top == "T" else optimal(
                transform(conditioned, lambda world: (world[0], world[1][1:])),
                add_hand(after, top), peonia_available,
            )
            discarded = Fraction()
            if len(conditioned[0][0][1]) >= 2:
                without_top = transform(
                    conditioned, lambda world: (world[0], world[1][1:])
                )
                for next_card, draw_chance, seen in observe(without_top, 0):
                    discarded += draw_chance * (
                        Fraction(1) if next_card == "T" else optimal(
                            transform(seen, lambda world: (world[0], world[1][1:])),
                            add_hand(after, next_card), peonia_available,
                        )
                    )
            expected += chance * max(taken, discarded)
        actions.append(expected)

    return max(actions)


def compare(prizes, deck, arcs, shoes, filler_in_hand):
    """Return (Peonia-first optimum, unrestricted-timing optimum)."""
    belief = initial(tuple(prizes), tuple(deck))
    hand = (0, arcs, shoes, filler_in_hand)
    return play_peonia(belief, hand), optimal(belief, hand, True)
