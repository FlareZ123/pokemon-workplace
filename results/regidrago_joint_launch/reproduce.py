"""Independent physical-card BFS versus exact category Prize/deal solver."""
from collections import Counter, deque
from fractions import Fraction
from itertools import combinations
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from tools.regidrago_joint_launch import Build, analyze, candidates


def physical_line_exists(
    hand: tuple[int, ...], deck: tuple[int, ...],
    cards: list[str], *, allow_compressor: bool = True
) -> bool:
    """Search exact individual-card Item transactions using physical zones."""
    start = (
        frozenset(hand), frozenset(deck),
        any(cards[i] == 'RV' for i in hand), False,
    )
    queue = deque([start])
    seen = {start}
    while queue:
        hand_ids, deck_ids, has_rv, has_dp_discarded = queue.popleft()
        if has_rv and has_dp_discarded:
            return True
        h = {
            name: [i for i in hand_ids if cards[i] == name]
            for name in ('VIP', 'QB', 'MT', 'BC', 'D', 'DP')
        }
        d = {
            name: [i for i in deck_ids if cards[i] == name]
            for name in ('RV', 'DP')
        }
        successors = []
        for item in h['VIP']:
            for target in d['RV']:
                successors.append((
                    hand_ids-{item}, deck_ids-{target}, True, has_dp_discarded,
                ))
        if allow_compressor:
            for item in h['BC']:
                for target in d['DP']:
                    successors.append((
                        hand_ids-{item}, deck_ids-{target}, has_rv, True,
                    ))
        for item_type in ('QB', 'MT'):
            for item in h[item_type]:
                for discard in h['D'] + h['DP']:
                    paid_hand = hand_ids-{item, discard}
                    paid_loaded = has_dp_discarded or cards[discard] == 'DP'
                    # Target-restricted searches permit choosing zero.
                    successors.append((
                        paid_hand, deck_ids, has_rv, paid_loaded,
                    ))
                    for target in d['RV']:
                        successors.append((
                            paid_hand, deck_ids-{target}, True, paid_loaded,
                        ))
                    if item_type == 'MT':
                        for target in d['DP']:
                            successors.append((
                                paid_hand | {target}, deck_ids-{target},
                                has_rv, paid_loaded,
                            ))
        for successor in successors:
            if successor not in seen:
                seen.add(successor)
                queue.append(successor)
    return False


def brute(build: Build, *, opener: int = 3, prizes: int = 2) -> dict[str, Fraction]:
    source = (
        [('RV', True)]*build.regidrago_v
        + [('BASIC', True)]*build.other_basics
        + [('DP', False)]*build.dragapult
        + [('VIP', False)]*build.vip
        + [('QB', False)]*build.quick_ball
        + [('MT', False)]*build.treasure
        + [('BC', False)]*build.compressor
        + [('D', False)]*build.safe
    )
    source += [('P', False)]*(build.total-len(source))
    assert len(source) == build.total
    tags = [name for name, _ in source]
    counts = Counter()
    worlds = 0
    for opening in combinations(range(build.total), opener):
        if not any(source[i][1] for i in opening):
            continue
        leftover = [i for i in range(build.total) if i not in opening]
        for prize in combinations(leftover, prizes):
            prize_set = set(prize)
            after = [i for i in leftover if i not in prize_set]
            for drawn in after:
                hand = (*opening, drawn)
                deck = tuple(i for i in after if i != drawn)
                held = Counter(tags[i] for i in hand)
                in_deck = Counter(tags[i] for i in deck)
                joint = physical_line_exists(hand, deck, tags)
                without_bc = physical_line_exists(
                    hand, deck, tags, allow_compressor=False,
                )
                rv = held['RV'] > 0 or (
                    in_deck['RV'] > 0 and (
                        held['VIP'] > 0 or (
                            held['QB']+held['MT'] > 0
                            and held['D']+held['DP'] > 0
                        )
                    )
                )
                dp = (
                    held['BC'] > 0 and in_deck['DP'] > 0
                ) or (
                    held['DP'] > 0 and held['QB']+held['MT'] > 0
                ) or (
                    in_deck['DP'] > 0 and held['MT'] > 0
                    and held['D'] > 0 and held['QB']+held['MT'] >= 2
                )
                events = {
                    'joint_any': joint,
                    'joint_bc': joint and not without_bc,
                    'joint_no_bc': without_bc,
                    'regidrago_access': rv,
                    'dragapult_discard': dp,
                    'joint_rv_start_held': joint and held['RV'] > 0,
                    'joint_dp_start_held': joint and held['DP'] > 0,
                    'joint_both_absent_start': (
                        joint and not held['RV'] and not held['DP']
                    ),
                }
                worlds += 1
                for key, yes in events.items():
                    if yes:
                        counts[key] += 1
    return {key: Fraction(counts[key], worlds) for key in events}


def verify() -> None:
    cases = (
        Build(regidrago_v=2, other_basics=2, dragapult=1, vip=1,
              quick_ball=1, treasure=1, compressor=1, safe=1, total=12),
        Build(regidrago_v=2, other_basics=2, dragapult=2, vip=0,
              quick_ball=1, treasure=1, compressor=1, safe=1, total=12),
        Build(regidrago_v=1, other_basics=2, dragapult=2, vip=1,
              quick_ball=2, treasure=1, compressor=0, safe=1, total=11),
        Build(regidrago_v=1, other_basics=2, dragapult=1, vip=1,
              quick_ball=1, treasure=2, compressor=1, safe=0, total=11),
    )
    for build in cases:
        exact = analyze(build, opener=3, prizes=2)
        physical = brute(build, opener=3, prizes=2)
        assert exact == physical, {
            key: (exact[key], physical[key]) for key in exact
            if exact[key] != physical[key]
        }
        print('PASS independent physical-card transaction oracle', build)
    for disposable in (0, 5, 10, 20, 30):
        rows = {
            name: analyze(build)
            for name, build in candidates(disposable).items()
        }
        assert rows['+Dragapult -VIP']['joint_any'] > rows['published']['joint_any']
        assert (
            rows['+Dragapult -VIP']['regidrago_access']
            < rows['published']['regidrago_access']
        )
        for metric in rows.values():
            assert metric['joint_no_bc']+metric['joint_bc'] == metric['joint_any']
            assert metric['joint_any'] <= metric['regidrago_access']
            assert metric['joint_any'] <= metric['dragapult_discard']
        print('PASS 60-card joint source+attacker access', disposable, {
            name: f"{100 * float(p['joint_any']):.9f}%"
            for name, p in rows.items()
        })
    print('PASS exact joint launch kernel and independent physical transactions')


if __name__ == '__main__':
    verify()
