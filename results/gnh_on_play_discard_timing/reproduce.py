"""Phase-regression for Guzma & Hala's pre-Stadium-search discard.

Official Pokemon Japan Q&A: decide whether to discard 2 cards at the
moment the Supporter is played, before inspecting the deck for Stadium.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from itertools import combinations


@dataclass(frozen=True)
class State:
    hand: tuple[str, ...]
    deck: tuple[str, ...]
    knows_deck: bool = False
    supporter_spent: bool = False
    events: tuple[str, ...] = ()


def take(cards: tuple[str, ...], card: str) -> tuple[str, ...]:
    if card not in cards:
        raise ValueError(f"Card absent from required zone: {card}")
    result = list(cards)
    result.remove(card)
    return tuple(result)


def tag_call_one(state: State, target: str) -> State:
    if not target.startswith("tag:"):
        raise ValueError("Tag Call target must be TAG TEAM")
    hand = take(state.hand, "item:Tag Call")
    deck = take(state.deck, target)
    return replace(state, hand=hand + (target,), deck=deck,
                   knows_deck=True,
                   events=state.events + ("Tag Call:play", "Tag Call:search", "K1"))


def first_match(cards: tuple[str, ...], prefix: str) -> str | None:
    return next((card for card in cards if card.startswith(prefix)), None)


def guzma_hala(state: State, payment: tuple[str, ...] = ()) -> State:
    if state.supporter_spent:
        raise ValueError("Ordinary Supporter window already consumed")
    if len(payment) not in (0, 2) or len(set(payment)) != len(payment):
        raise ValueError("Payment requires two distinct physical cards")
    hand = take(state.hand, "tag:Guzma & Hala")
    deck = state.deck
    events = list(state.events) + ["G&H:play"]
    # The on-play payment is committed before the first deck search.
    for card in payment:
        hand = take(hand, card)
        events.append("G&H:discard:" + card)
    events.append("G&H:search:stadium")
    stadium = first_match(deck, "stadium:")
    if stadium is not None:
        deck = take(deck, stadium)
        hand += (stadium,)
    events.append("K1")
    if payment:
        for category in ("tool:", "special-energy:"):
            events.append("G&H:search:" + category)
            found = first_match(deck, category)
            if found is not None:
                deck = take(deck, found)
                hand += (found,)
    events.append("G&H:shuffle")
    return State(hand, deck, knows_deck=True, supporter_spent=True,
                 events=tuple(events))


def main() -> None:
    deck = ("stadium:Artazon", "tool:TM Evolution", "special-energy:Jet")
    insufficient = State(("tag:Guzma & Hala", "other:filler"), deck)
    try:
        guzma_hala(insufficient, ("other:filler", "stadium:Artazon"))
        raise AssertionError("Post-search Stadium used to pay pre-search cost")
    except ValueError as exc:
        assert "absent" in str(exc)

    only_stadium = guzma_hala(insufficient)
    assert "stadium:Artazon" in only_stadium.hand
    assert "tool:TM Evolution" not in only_stadium.hand
    assert only_stadium.events == (
        "G&H:play", "G&H:search:stadium", "K1", "G&H:shuffle")
    assert only_stadium.knows_deck and only_stadium.supporter_spent

    paid = guzma_hala(
        State(("tag:Guzma & Hala", "other:A", "other:B"), deck),
        ("other:A", "other:B"),
    )
    assert paid.events.index("G&H:discard:other:B") < paid.events.index("K1")
    assert {"stadium:Artazon", "tool:TM Evolution", "special-energy:Jet"} <= set(paid.hand)

    with_tag = State(
        ("tag:Guzma & Hala", "item:Tag Call", "other:F"),
        ("tag:Bellelba & Brycen-Man",) + deck,
    )
    preview = tag_call_one(with_tag, "tag:Bellelba & Brycen-Man")
    assert preview.knows_deck and not preview.supporter_spent
    informed = guzma_hala(preview, ("other:F", "tag:Bellelba & Brycen-Man"))
    assert informed.events.index("K1") < informed.events.index("G&H:play")
    assert "tool:TM Evolution" in informed.hand

    checks = 0
    for count in range(4):
        original = State(("tag:Guzma & Hala",) + tuple(
            f"other:{i}" for i in range(count)), deck)
        for choice in [()] + list(combinations(original.hand[1:], 2)):
            outcome = guzma_hala(original, choice)
            assert outcome.events.index("G&H:search:stadium") > max(
                (i for i, event in enumerate(outcome.events)
                 if event.startswith("G&H:discard:")), default=-1)
            assert outcome.events.index("K1") > outcome.events.index("G&H:search:stadium")
            checks += 1
    print(f"PASS: {checks} exhaustive on-play payment choices")
    print("PASS: Stadium fetched by G&H cannot fund the optional discard")
    print("PASS: earlier Tag Call search supplies K1 before G&H payment")


if __name__ == "__main__":
    main()
