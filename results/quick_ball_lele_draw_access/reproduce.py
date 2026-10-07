from itertools import combinations
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from quick_ball_lele_draw_access import draw_window_gladion_access_probability as exact


def brute(mode):
    kinds = {
        "C1":"c","C2":"c","R":"r","L":"l","Q":"q",
        "D":"d","S1":"s","S2":"s","F1":"f","F2":"f",
    }
    cards = tuple(kinds)
    good = total = 0
    for hand_t in combinations(cards, 3):
        hand = set(hand_t)
        other_starters = sum(kinds[x] == "s" for x in hand)
        if "L" not in hand and other_starters == 0:
            continue
        rest = [x for x in cards if x not in hand]
        for prize_t in combinations(rest, 2):
            prize = set(prize_t)
            if not any(kinds[x] == "c" for x in prize):
                continue
            deck = [x for x in rest if x not in prize]
            for draw_t in combinations(deck, 2):
                draw = set(draw_t)
                total += 1
                seen = hand | draw
                r_hand = "R" in seen
                r_deck = "R" in deck and "R" not in draw
                l_draw = "L" in draw
                l_keep = "L" in hand and (mode == "ignore_setup" or other_starters > 0)
                l_hand = l_draw or l_keep
                l_deck = "L" in deck and "L" not in draw
                q_hand = "Q" in seen
                d_hand = "D" in seen
                lele = l_hand and r_deck
                if mode == "clean_qb":
                    q_line = q_hand and r_deck
                else:
                    q_line = q_hand and l_deck and r_deck
                    if mode in {"strict", "ignore_setup"}:
                        q_line = q_line and d_hand
                good += bool(r_hand or lele or q_line)
    return good / total


small = dict(
    deck_size=10, prize_count=2, opening_hand_size=3,
    other_starters=2, critical_nonstarter=2, rescue_nonstarter=1,
    quick_ball_copies=1, disposable_nonstarter=1, later_random_draws=2,
)
for mode in ("strict", "no_discard", "clean_qb", "ignore_setup"):
    a = exact(**small, mode=mode)
    b = brute(mode)
    assert abs(a-b) < 1e-12, (mode, a, b)

base = dict(
    deck_size=60, prize_count=6, other_starters=11,
    critical_nonstarter=4, rescue_nonstarter=2, quick_ball_copies=4,
    disposable_nonstarter=12, later_random_draws=0,
)
assert abs(exact(**base, mode="strict") - 0.48569324497) < 1e-11
assert abs(exact(**base, mode="ignore_setup") - 0.51482660076) < 1e-11

one = {**base, "later_random_draws":1}
locked = exact(**one, mode="strict", abilities_allowed=False)
full = exact(**one, mode="strict", bench_available=False)
assert abs(locked-full) < 1e-15
assert abs(locked-0.24265474753) < 1e-11

for draws in (0,1,2,3,5,8,12):
    row = {**base, "later_random_draws":draws}
    print(draws, *(f"{m}={exact(**row, mode=m):.9%}"
        for m in ("strict","no_discard","clean_qb","ignore_setup")))
print("validation passed")
