"""Independent Boolean deadline oracle for Boss and Serena target eligibility."""
from collections import Counter
from functools import lru_cache
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from tools.trainer_gust_catalog import CATEGORIES
from tools.typed_gust_target_minimax import (
    Target, enumerate_boards, forced_first_gust, minimum_attacks
)


@lru_cache(None)
def guaranteed_win(a, bench, bosses, serenas, need, turns):
    if need <= 0:
        return True
    if turns <= 0:
        return False
    choices = [(a, bench, bosses, serenas)]
    for i in range(len(bench)):
        target = bench[i]
        future_bench = tuple(sorted([a] + [x for j, x in enumerate(bench) if i != j]))
        if bosses:
            choices.append((target, future_bench, bosses - 1, serenas))
        if serenas and target.is_pokemon_v:
            choices.append((target, future_bench, bosses, serenas - 1))

    for target, remaining, next_bosses, next_serenas in choices:
        if target.prizes >= need or not remaining:
            return True
        if all(
            guaranteed_win(
                promoted, remaining[:j] + remaining[j + 1:],
                next_bosses, next_serenas, need - target.prizes, turns - 1
            )
            for j, promoted in enumerate(remaining)
        ):
            return True
    return False


def main():
    assert CATEGORIES["Boss's Orders"].target_scope == "any"
    assert CATEGORIES["Serena"].target_scope == "pokemon_v_family"
    assert "supporter" in CATEGORIES["Serena"].gates
    assert "draw_alternative" in CATEGORIES["Serena"].gates

    boards = tuple(enumerate_boards())
    assert len(boards) == 582
    differences = Counter()
    mixed_differences = Counter()
    statuses = Counter()
    strict_dominated = 0
    narrow_reach = 0
    tests = 0
    for a, bench in boards:
        for b in range(3):
            for s in range(3):
                result = minimum_attacks(a, bench, b, s, 6)
                oracle = next(
                    t for t in range(1, len(bench) + 2)
                    if guaranteed_win(a, bench, b, s, 6, t)
                )
                assert result == oracle, (a, bench, b, s, result, oracle)
                tests += 1
        boss_two = minimum_attacks(a, bench, 2, 0)
        mixed = minimum_attacks(a, bench, 1, 1)
        serena_two = minimum_attacks(a, bench, 0, 2)
        assert boss_two <= mixed <= serena_two
        differences[serena_two - boss_two] += 1
        mixed_differences[mixed - boss_two] += 1
        statuses[
            minimum_attacks(a, bench, 1, 0) == minimum_attacks(a, bench, 0, 1)
        ] += 1

        for v_target in sorted({t for t in bench if t.is_pokemon_v}):
            boss_first = forced_first_gust(a, bench, 1, 1, "boss", v_target)
            serena_first = forced_first_gust(a, bench, 1, 1, "serena", v_target)
            assert boss_first is not None and serena_first is not None
            assert serena_first <= boss_first, (a, bench, v_target)
            strict_dominated += int(serena_first < boss_first)
            narrow_reach += 1

    assert tests == 5238
    assert differences == {0:374, 1:178, 2:30}
    assert mixed_differences == {0:527, 1:51, 2:4}
    assert statuses == {True:475, False:107}
    assert strict_dominated == 118

    a = Target(1, False)
    bench = (Target(1, False), Target(3, False), Target(3, True))
    assert minimum_attacks(a, bench, 1, 1) == 2
    assert forced_first_gust(a, bench, 1, 1, "serena", Target(3, True)) == 2
    assert forced_first_gust(a, bench, 1, 1, "boss", Target(3, True)) == 4

    print("PASS:", tests, "independent deadline/game-tree comparisons")
    print("Two Serena versus two Boss:", dict(sorted(differences.items())))
    print("Boss + Serena versus two Boss:", dict(sorted(mixed_differences.items())))
    print("One Serena versus one Boss equal:", statuses[True], "of", len(boards))
    print("Strict waste of broad gust when V-restricted gust also applies:",
          strict_dominated, "of", narrow_reach, "forced source/target pairs")


if __name__ == "__main__":
    main()
