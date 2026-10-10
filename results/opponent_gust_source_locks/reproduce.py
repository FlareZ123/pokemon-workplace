"""Independent physical source-arrival deadline oracle and no-lock regression."""
from fractions import Fraction
from itertools import combinations, permutations
from tools.opponent_source_lock_schedule import win_probability, initial_win_probability
from tools.multisource_opponent_gust_race import win_probability as prior
from tools.gust_copy_opening_access import at_least_one, choose


def ordered_physical_oracle(basics, bosses, counters, prizes, boss_lock, counter_lock,
                            total=10, hand_size=3):
    """Exact labeled opening/Prize/two ordered natural draws, independent solver."""
    cards = tuple(range(total))
    boss = set(range(basics, basics + bosses))
    counter = set(range(basics + bosses, basics + bosses + counters))
    winning = trials = 0
    for opening in combinations(cards, hand_size):
        hand = set(opening)
        if not any(card < basics for card in hand):
            continue
        remaining = tuple(card for card in cards if card not in hand)
        for prize_cards in combinations(remaining, prizes):
            drawable = tuple(card for card in remaining if card not in prize_cards)
            for first, second in permutations(drawable, 2):
                trials += 1
                visible_first = hand | {first}
                visible_second = visible_first | {second}
                early_boss = bool(visible_first & boss)
                later_boss = bool(visible_second & boss)
                later_counter = bool(visible_second & counter)
                # Witness: Counter cannot be used on reply 1 due to Prize gate.
                opponent_wins = (
                    (early_boss and 1 not in boss_lock)
                    or (later_boss and 2 not in boss_lock)
                    or (later_counter and 2 not in counter_lock)
                )
                winning += not opponent_wins
    return Fraction(winning, trials)


def verify():
    toy = 0
    regimes = (((), ()), ((), (2,)), ((2,), ()), ((2,), (2,)))
    for basics in (2, 3):
        for count in (1, 2, 3):
            for bosses in range(count + 1):
                counters = count - bosses
                for prizes in (1, 2):
                    for blocked_b, blocked_c in regimes:
                        observed = initial_win_probability(
                            1, (1, 1, 3), 2, (2, 2), 1, 1, 3,
                            basics, bosses, counters, blocked_b, blocked_c,
                            total=10, hand_size=3, prize_count=prizes)
                        expected = ordered_physical_oracle(
                            basics, bosses, counters, prizes, blocked_b, blocked_c)
                        assert observed == expected
                        toy += 1
    assert toy == 144

    # Reproduce the earlier unrestricted source state engine.
    cases = 0
    boards = ((3, (3,)), (2, (2, 2)), (1, (2, 3)), (1, (1, 3, 3)))
    for oa, ob in ((1, (1,)), (1, (1, 2)), (1, (1, 1, 3))):
        for ea, eb in boards:
            for ep in (2, 3, 4):
                for hb in range(3):
                    for hc in range(3):
                        observed = win_probability(oa, ob, ea, eb, 1, 1, 6, ep,
                                                   hb, hc, 0, 0, 0, 0, (), ())
                        expected = prior(oa, ob, ea, eb, 1, 1, 6, ep,
                                         hb, hc, 0, 0, 0)
                        assert observed == expected
                        cases += 1
    assert cases == 324

    # Independently derive special first-/second-reply visibility formulas.
    analytic = 0
    for basics in (4, 8, 12, 16, 20):
        for bosses in range(5):
            counters = 4 - bosses
            valid = choose(60, 7) - choose(60 - basics, 7)
            no_gust = choose(56, 7) - choose(56 - basics, 7)
            for blocked_b, blocked_c in regimes:
                actual = initial_win_probability(
                    1, (1, 1, 3), 2, (2, 2), 1, 1, 3,
                    basics, bosses, counters, blocked_b, blocked_c)
                if not blocked_b and not blocked_c:
                    expected = 1 - at_least_one(basics, 4, 2)
                elif blocked_c and not blocked_b:
                    expected = 1 - at_least_one(basics, bosses, 2)
                elif blocked_b and not blocked_c:
                    expected = (Fraction(no_gust, valid) * Fraction(49, 53)
                                * Fraction(52 - counters, 52))
                else:
                    expected = 1 - at_least_one(basics, bosses, 1)
                assert actual == expected
                analytic += 1
    assert analytic == 100
    print(f'PASS: {toy} ordered physical two-draw oracles, '
          f'{cases} unrestricted solver parity checks, '
          f'{analytic} independent four-source deadline formula checks')


if __name__ == '__main__':
    verify()
