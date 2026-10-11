"""SFT: exhaustive physical-instance validation of the Aichi G&H action menu."""
from __future__ import annotations

from collections import Counter
from itertools import combinations, product

from tools.aichi_gnh_discard_frontier import paid_gnh_states
from tools.aichi_post_gnh_prize_reset import Prepared
from tools.gnh_typed_search_frontier import (
    Action, SPECIAL_ENERGY, STADIUMS, TOOLS, options,
)


def canonical(cards: Counter[str]) -> tuple[tuple[str, int], ...]:
    return tuple(sorted((name, n) for name, n in cards.items() if n))


def physical_oracle(
    hand_cards: tuple[str, ...],
    deck_cards: tuple[str, ...],
    protected: frozenset[str],
) -> set[tuple[Action, tuple, tuple, tuple]]:
    """Enumerate distinct physical hand discard pairs and named deck picks."""
    answers = set()
    payments = [()] + list(combinations(range(len(hand_cards)), 2))
    for ids in payments:
        paid = tuple(sorted(hand_cards[i] for i in ids)) if ids else None
        if paid and any(name in protected for name in paid):
            continue
        held = [name for i, name in enumerate(hand_cards) if i not in ids]
        discard = [hand_cards[i] for i in ids]
        st = (None,) + tuple(i for i, c in enumerate(deck_cards) if c in STADIUMS)
        ts = (None,) if paid is None else (None,) + tuple(
            i for i, c in enumerate(deck_cards) if c in TOOLS)
        es = (None,) if paid is None else (None,) + tuple(
            i for i, c in enumerate(deck_cards) if c in SPECIAL_ENERGY)
        for picks in product(st, ts, es):
            fetched_ids = {i for i in picks if i is not None}
            fetched = [deck_cards[i] for i in picks if i is not None]
            survivors = [c for i, c in enumerate(deck_cards) if i not in fetched_ids]
            action = Action(
                paid,
                deck_cards[picks[0]] if picks[0] is not None else None,
                deck_cards[picks[1]] if picks[1] is not None else None,
                deck_cards[picks[2]] if picks[2] is not None else None,
            )
            answers.add((action, canonical(Counter(held + fetched)),
                         canonical(Counter(survivors)), canonical(Counter(discard))))
    return answers


def main() -> None:
    hand = ("Technical Machine: Evolution", "Jet Energy",
            "Guzma", "Karen", "Guzma")
    deck = ("Artazon", "Grand Tree", "Stealthy Hood", "Counter Gain",
            "Capture Energy", "Jet Energy", "Technical Machine: Evolution",
            "TechSlot1")
    state = Prepared(Counter(hand), Counter(deck), "Jirachi", (), True)
    total = state.hand + state.remaining
    for protected in (
        frozenset(), frozenset({"Guzma"}),
        frozenset({"Technical Machine: Evolution", "Karen"}),
    ):
        actual = options(state, protected)
        observed = {
            (out.action, canonical(out.hand), canonical(out.deck),
             canonical(out.discarded))
            for out in actual
        }
        reference = physical_oracle(hand, deck, protected)
        assert observed == reference, (protected, observed-reference, reference-observed)
        assert len(actual) == len(observed), "Distinct category line duplicated"
        for out in actual:
            assert out.hand + out.deck + out.discarded == total
            assert out.action.paid_with is None or len(out.action.paid_with) == 2
        print(f"PASS: independent labeled-card oracle with protection={sorted(protected)} "
              f"matches {len(actual)} category lines")

    old = paid_gnh_states(state)
    assert len(old) == 1 and old[0].paid_with is None
    new = options(state)
    witness = Action(("Guzma", "Karen"), "Artazon",
                     "Technical Machine: Evolution", "Jet Energy")
    assert any(out.action == witness for out in new)
    assert all(Action(p.paid_with, None, None, None) != witness
               for p in old)
    no_pay = [out for out in new if out.action.paid_with is None]
    assert all(out.action.tool is None and out.action.special_energy is None
               for out in no_pay)
    print("PASS: optional two-card payment is offered when required outputs are held")
    print("PASS: unpaid Supporter does not access Tool/Special-Energy channels")


if __name__ == "__main__":
    main()
