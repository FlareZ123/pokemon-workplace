"""Exact multi-copy non-Basic access after a Basic-valid opening and Prize split."""
from fractions import Fraction
from math import comb


def choose(n, k):
    """Binomial coefficient with zero for out-of-range event counts."""
    return comb(n, k) if 0 <= k <= n else 0


def source_count_distribution(basics, sources, replies, total=60,
                              hand_size=7, prize_count=6):
    """PMF for non-Basic source copies seen in hand plus first k draws.

    Conditions on the initial hand containing one or more Basic Pokemon.
    There are exactly `sources` interchangeable source cards in the deck.
    """
    if not (1 <= basics <= total and 0 <= sources <= total-basics):
        raise ValueError('invalid Basic/source composition')
    if not (0 < hand_size < total and 0 <= prize_count <= total-hand_size
            and 0 <= replies <= total-hand_size-prize_count):
        raise ValueError('invalid hand/Prize/draw counts')
    accepted = choose(total, hand_size)-choose(total-basics, hand_size)
    denominator = accepted*choose(total-hand_size,replies)
    fillers=total-basics-sources
    counts=[0]*(sources+1)
    for j in range(min(sources,hand_size)+1):
        for b in range(1,min(basics,hand_size-j)+1):
            ways_hand=(choose(sources,j)*choose(basics,b)*
                       choose(fillers,hand_size-j-b))
            for d in range(min(replies,sources-j)+1):
                ways_draw=(choose(sources-j,d)*
                           choose(total-hand_size-sources+j,replies-d))
                counts[j+d]+=ways_hand*ways_draw
    result=tuple(Fraction(x,denominator) for x in counts)
    assert sum(result)==1
    return result


def at_least_one(basics,sources,replies,total=60,hand_size=7,prize_count=6):
    """Shortcut closed form for one or more accessible source copies."""
    if not (1 <= basics <= total and 0 <= sources <= total-basics):
        raise ValueError('invalid Basic/source composition')
    if not (0 < hand_size < total and 0 <= prize_count <= total-hand_size
            and 0 <= replies <= total-hand_size-prize_count):
        raise ValueError('invalid hand/Prize/draw counts')
    accepted=choose(total,hand_size)-choose(total-basics,hand_size)
    valid_source_free=choose(total-sources,hand_size)-choose(total-sources-basics,hand_size)
    miss_after=Fraction(choose(total-hand_size-sources,replies),
                        choose(total-hand_size,replies))
    return 1-Fraction(valid_source_free,accepted)*miss_after
