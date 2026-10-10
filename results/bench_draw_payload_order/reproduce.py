"""Independent physical-list regression for the staged Crobat/Dedenne oracle."""
from __future__ import annotations

from fractions import Fraction
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from bench_draw_payload_order import POLICIES, analyze, exact_closed_form  # noqa: E402


def physical_oracle(policy: str, *, target_zone: str, target_index: int,
                    hand_size: int, deck_size: int,
                    prize_known: bool = False) -> tuple[bool, bool, int, int, int]:
    """Replay literal hand, discard pile, Bench and ordered deck lists."""
    hand = ["C", "D"]
    if target_zone == "hand":
        hand.append("K")
    hand += [f"h{i}" for i in range(hand_size - len(hand))]
    deck = ["K" if i == target_index and target_zone == "deck" else f"d{i}"
            for i in range(deck_size)]
    bench: list[str] = []
    discard: list[str] = []
    drawn = 0
    dedenne_uses = 0

    def play_support(name: str) -> None:
        nonlocal drawn, dedenne_uses
        hand.remove(name)
        bench.append(name)
        if name == "C":
            n = max(0, 6 - len(hand))
        else:
            dedenne_uses += 1
            discard.extend(hand)
            hand.clear()
            n = 6
        draw = deck[:n]
        del deck[:n]
        hand.extend(draw)
        drawn += len(draw)

    if prize_known and target_zone == "prize" and policy in (
            "dedenne_stop", "crobat_only", "crobat_dedenne_stop"):
        return False, False, 0, 0, 0

    if policy == "dedenne_blind":
        play_support("D")
    elif policy == "dedenne_stop":
        if "K" not in hand:
            play_support("D")
    elif policy == "crobat_only":
        if "K" not in hand:
            play_support("C")
    elif policy == "crobat_dedenne_forced":
        play_support("C")
        play_support("D")
    elif policy == "crobat_dedenne_stop":
        if "K" not in hand:
            play_support("C")
            if "K" not in hand:
                play_support("D")
    else:
        raise ValueError(policy)
    return "K" in hand, "K" in discard, len(bench), dedenne_uses, drawn


def exact_by_physical_positions(*, hand_size: int, deck_size: int,
                                prizes: int, natural_draws: int = 1,
                                prize_known: bool = False):
    locations = ([("hand", -1)] * natural_draws
                 + [("prize", -1)] * prizes
                 + [("deck", i) for i in range(deck_size)])
    result = {}
    for policy in POLICIES:
        values = [physical_oracle(policy, target_zone=loc, target_index=i,
                                  hand_size=hand_size, deck_size=deck_size,
                                  prize_known=prize_known)
                  for loc, i in locations]
        result[policy] = tuple(Fraction(sum(x[j] for x in values), len(values))
                               for j in range(5))
    return result


def validate() -> None:
    for deck in (6, 7, 10, 46):
        for hand in (3, 4, 5, 6, 7, 8):
            for known in (False, True):
                p = dict(hand_size=hand, deck_cards=deck, prizes=2,
                         natural_draws=1, prize_known=known)
                actual = analyze(**p)
                oracle = exact_by_physical_positions(
                    hand_size=hand, deck_size=deck, prizes=2, prize_known=known)
                for policy in POLICIES:
                    x = actual[policy]
                    assert (x.target_in_hand, x.target_discarded,
                            x.expected_bench_plays, x.expected_dedenne_uses,
                            x.expected_draws) == oracle[policy], (p, policy, x)
                if deck >= max(0, 7 - hand) + 6:
                    closed = exact_closed_form(
                        hand_size=hand, deck_cards=deck, prizes=2)
                    assert all(actual[k].target_in_hand == v
                               for k, v in closed.items())

    main = analyze(hand_size=5, deck_cards=46, prizes=6, natural_draws=1)
    assert main["dedenne_blind"].target_in_hand == Fraction(6, 53)
    assert main["dedenne_stop"].target_in_hand == Fraction(7, 53)
    assert main["crobat_only"].target_in_hand == Fraction(3, 53)
    assert main["crobat_dedenne_forced"].target_in_hand == Fraction(6, 53)
    assert main["crobat_dedenne_forced"].target_discarded == Fraction(3, 53)
    assert main["crobat_dedenne_stop"].target_in_hand == Fraction(9, 53)
    assert main["crobat_dedenne_stop"].target_discarded == 0
    assert main["crobat_dedenne_stop"].expected_bench_plays == Fraction(102, 53)
    assert main["crobat_dedenne_stop"].expected_dedenne_uses == Fraction(50, 53)
    assert main["crobat_dedenne_stop"].expected_draws == Fraction(404, 53)
    assert list(analyze(bench_slots=1)) == list(POLICIES[:3])
    prize_known = analyze(hand_size=5, prize_known=True)
    assert all(prize_known[k].target_in_hand == main[k].target_in_hand
               for k in POLICIES)
    assert prize_known["dedenne_stop"].expected_bench_plays == Fraction(46, 53)
    assert prize_known["crobat_dedenne_stop"].expected_bench_plays == Fraction(90, 53)
    assert prize_known["crobat_dedenne_stop"].expected_dedenne_uses == Fraction(44, 53)
    print("Physical-position oracle, closed-form identities, and benchmark passed.")
    print("h | Dedenne conditional | Crobat->Dedenne conditional | gain | extra Bench")
    for h in (3, 4, 5, 6, 7):
        out = analyze(hand_size=h)
        d = out["dedenne_stop"]
        s = out["crobat_dedenne_stop"]
        print(f"{h} | {float(d.target_in_hand):.6%} | {float(s.target_in_hand):.6%} | "
              f"{float(s.target_in_hand-d.target_in_hand):.6%} | "
              f"{float(s.expected_bench_plays-d.expected_bench_plays):.6f}")


if __name__ == "__main__":
    validate()
