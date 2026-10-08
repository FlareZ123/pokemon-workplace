"""Reproduce Prime Catcher own-switch timing and Bench occupancy geometry.

Run: python -m results.prime_catcher_order_geometry.reproduce
"""
from collections import Counter
from functools import lru_cache
from itertools import product

from tools.prime_catcher_order_geometry import OwnTurn, attack_witness


@lru_cache(None)
def independently_reachable(s: OwnTurn) -> bool:
    """Depth-first existential reachability with independently coded transitions."""
    if s.gusted and s.active_ready and not s.hand_ready:
        return True

    for i in range(len(s.hand_ready)):
        if len(s.bench_ready) < 5:
            h = s.hand_ready[:i] + s.hand_ready[i + 1 :]
            b = tuple(sorted((*s.bench_ready, s.hand_ready[i])))
            if independently_reachable(OwnTurn(
                s.active_ready, b, h, s.prime_ready, s.gusted, s.switches
            )):
                return True

    if s.prime_ready and not s.gusted:
        if not s.bench_ready and independently_reachable(OwnTurn(
            s.active_ready, (), s.hand_ready, False, True, s.switches
        )):
            return True
        for i, ready in enumerate(s.bench_ready):
            b = list(s.bench_ready)
            b[i] = s.active_ready
            if independently_reachable(OwnTurn(
                ready, tuple(sorted(b)), s.hand_ready, False, True, s.switches
            )):
                return True

    if s.switches:
        for i, ready in enumerate(s.bench_ready):
            b = list(s.bench_ready)
            b[i] = s.active_ready
            if independently_reachable(OwnTurn(
                ready, tuple(sorted(b)), s.hand_ready, s.prime_ready,
                s.gusted, s.switches - 1
            )):
                return True
    return False


def run():
    checked = 0
    count = Counter()
    for n in range(6):
        for bench in product((False, True), repeat=n):
            for active in (False, True):
                for switch_tokens in (0, 1):
                    s = OwnTurn(active, bench, switches=switch_tokens)
                    actual = attack_witness(s) is not None
                    assert actual == independently_reachable(s), s
                    checked += 1
                    if active and not switch_tokens:
                        count["ready_cases"] += 1
                        count["ready_wins"] += actual
                    if active and switch_tokens:
                        count["ready_switch_wins"] += actual
                    if not active and not switch_tokens:
                        count["unready_wins"] += actual

    assert count == {
        "ready_cases": 63,
        "ready_wins": 58,
        "ready_switch_wins": 63,
        "unready_wins": 57,
    }

    hand_count = Counter()
    for n in range(5):
        for bench in product((False, True), repeat=n):
            for hand_ready in (False, True):
                for switch_tokens in (0, 1):
                    s = OwnTurn(True, bench, (hand_ready,), switches=switch_tokens)
                    actual = attack_witness(s) is not None
                    assert actual == independently_reachable(s), s
                    checked += 1
                    hand_count[(hand_ready, switch_tokens, actual)] += 1
    assert hand_count == {
        (False, 0, True): 27,
        (False, 0, False): 4,
        (False, 1, True): 31,
        (True, 0, True): 31,
        (True, 1, True): 31,
    }
    assert checked == 376

    assert attack_witness(OwnTurn(True, ())) == ("Prime (no own Bench)",)
    assert attack_witness(OwnTurn(True, (False,))) is None
    assert attack_witness(OwnTurn(True, (True,))) is not None
    assert attack_witness(OwnTurn(False, (True,))) is not None
    assert attack_witness(OwnTurn(True, (False,), switches=1)) is not None

    s = OwnTurn(True, (), (False,))
    assert attack_witness(s, required_first="Prime") == (
        "Prime (no own Bench)", "Bench False"
    )
    assert attack_witness(s, required_first="Bench") is None
    print("Board geometries:", dict(count))
    print("Required-hand-Bench geometries:", dict(hand_count))
    print(f"PASS: {checked} states independently verified; "
          "mandatory-own-switch and Prime-before-Bench witnesses")


if __name__ == "__main__":
    run()
