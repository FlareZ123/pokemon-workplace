"""Exact limited Regidrago Legacy Star launch with Item-search payment and Prize zones."""
from dataclasses import dataclass
from fractions import Fraction
from itertools import product
from math import comb


@dataclass(frozen=True)
class Window:
    safe: int = 0
    first_item: bool = True
    second_item: bool = True
    guzma: int = 2
    others: int = 11
    v: int = 4
    star: int = 3
    vip: int = 3
    quick: int = 3
    treasure: int = 3
    total: int = 60


def choose(n: int, k: int) -> int:
    return comb(n, k) if 0 <= k <= n else 0


def solve(w: Window, opening: int = 7, prizes: int = 6) -> dict[str, Fraction]:
    """Conditional accepted-opening event and mutually related route counts.

    The action policy spends designated discardable 'safe' filler only. On T1:
    use held V, otherwise VIP, paid Quick, paid Treasure; then optionally
    prefetch VSTAR with paid Treasure. T2 draws one card; if VSTAR remains
    absent and Items are legal, paid Treasure can fetch it from deck.
    """
    assert min(w.__dict__.values()) >= 0
    assert opening > 0 and opening + prizes + 2 <= w.total
    rest = (w.total - w.others - w.v - w.star - w.guzma -
            w.vip - w.quick - w.treasure - w.safe)
    assert rest >= 0
    groups = (w.others, w.v, w.star, w.guzma, w.vip,
              w.quick, w.treasure, w.safe, rest)
    seen = opening + 1
    numerator = {
        "guzma_t1": 0,
        "v_t1": 0,
        "star_t2": 0,
        "prefetch_t1": 0,
        "search_t2": 0,
    }
    total_weight = 0

    sizes = [range(min(n, seen) + 1) for n in groups[:-1]]
    for picks in product(*sizes):
        filler = seen - sum(picks)
        if filler < 0 or filler > rest:
            continue
        hand = (*picks, filler)
        basics = hand[0] + hand[1]
        # Eight seen cards have seven or eight permissible T1-draw labels
        # when exactly one or multiple Basics are present, respectively.
        valid_last = seen if basics >= 2 else seen - 1 if basics == 1 else 0
        if not valid_last:
            continue
        hand_weight = valid_last
        for n, k in zip(groups, hand):
            hand_weight *= choose(n, k)

        unseen_v = w.v - hand[1]
        unseen_star = w.star - hand[2]
        other_unseen = w.total - seen - unseen_v - unseen_star
        for pv in range(min(unseen_v, prizes) + 1):
            for ps in range(min(unseen_star, prizes - pv) + 1):
                prize_non = prizes - pv - ps
                prizeways = (choose(unseen_v, pv) * choose(unseen_star, ps) *
                             choose(other_unseen, prize_non))
                if not prizeways:
                    continue
                weight = hand_weight * prizeways
                total_weight += weight
                if not hand[3]:
                    continue
                numerator["guzma_t1"] += weight
                vdeck = unseen_v - pv
                sdeck = unseen_star - ps

                # VIP direct Bench placement has no discard payment.
                held_t = hand[6]
                held_d = hand[7]
                vready = hand[1] > 0
                if not vready and w.first_item and vdeck:
                    if hand[4]:
                        vready = True
                        vdeck -= 1
                    elif hand[5] and held_d:
                        vready = True
                        vdeck -= 1
                        held_d -= 1
                    elif held_t and held_d:
                        vready = True
                        vdeck -= 1
                        held_t -= 1
                        held_d -= 1
                if not vready:
                    continue
                numerator["v_t1"] += weight

                shand = hand[2]
                prefetched = False
                if not shand and sdeck and w.first_item and held_t and held_d:
                    held_t -= 1
                    held_d -= 1
                    sdeck -= 1
                    shand += 1
                    prefetched = True
                if prefetched:
                    numerator["prefetch_t1"] += weight
                if shand:
                    numerator["star_t2"] += weight
                    continue
                if not sdeck:
                    continue
                if w.second_item and held_t and held_d:
                    numerator["star_t2"] += weight
                    numerator["search_t2"] += weight
                    continue

                # Non-V/non-VSTAR Prize draws are exchangeable conditional
                # on just the V and VSTAR Prize counts. Integrate their
                # source identity exactly rather than treating Prizes as deck.
                deck_n = (w.total - seen - prizes -
                          (unseen_v - pv - vdeck) -
                          (unseen_star - ps - sdeck))
                assert deck_n > 0
                non_source_deck = other_unseen - prize_non
                p_star = Fraction(sdeck, deck_n)
                p_t = (Fraction((w.treasure - hand[6]) * non_source_deck,
                                other_unseen * deck_n)
                       if other_unseen else Fraction(0))
                p_d = (Fraction((w.safe - hand[7]) * non_source_deck,
                                other_unseen * deck_n)
                       if other_unseen else Fraction(0))
                probability = p_star
                if w.second_item:
                    if held_t and not held_d:
                        probability += p_d
                    elif held_d and not held_t:
                        probability += p_t
                assert 0 <= probability <= 1
                numerator["star_t2"] += weight * probability
                if w.second_item and (held_t or held_d):
                    numerator["search_t2"] += weight * (probability - p_star)
    assert total_weight > 0
    result = {key: Fraction(value, total_weight)
              for key, value in numerator.items()}
    assert (result["star_t2"] <= result["v_t1"] <= result["guzma_t1"] <= 1)
    return result
