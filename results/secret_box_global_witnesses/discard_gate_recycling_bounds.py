"""Exact DCI-threshold sensitivity for rare Aichi Secret Box output witnesses.

Select d of 11 physical nonBasic filler cards as acceptable to discard;
the other 11-d are protected. This is a hypothetical statewise DCI rule,
not a classification of those real cards' long-game utility.

Supporter certificate: three safe cards pay Secret Box; the two-card
Guzma & Hala fee may then use residual safe cards and freshly fetched
TM: Evolution / Artazon if an unprized second copy can be re-searched.
This happens *after* Box's legal deck inspection, avoiding K0 foresight.

Tool+Stadium certificate: three safe cards pay Secret Box; no second
discard cost is required. Exact probability masses condition on a valid
Basic-containing opening, physical Prizes and the natural first draw.
"""
from collections import Counter
from fractions import Fraction
from itertools import combinations
from math import comb
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
from aichi_vileplume_secret_box import BASE_DECK
from aichi_vileplume_als import DECK_COUNTS

FILLER_NAMES = {
    "Guzma", "Cassius", "Karen", "Plumeria", "Gladion", "Faba",
    "Lusamine", "Peonia", "Team Yell's Cheer", "Bellelba & Brycen-Man",
}
FILLERS = tuple(i for i, name in enumerate(BASE_DECK) if name in FILLER_NAMES)
assert len(FILLERS) == 11
A = 1 - Fraction(comb(46, 7), comb(60, 7))
DENOMINATOR = comb(60, 7) * comb(53, 6) * 47 * A


def usable_pair(pair, necessary):
    prized = Counter(BASE_DECK[i] for i in pair)
    return all(prized[name] < DECK_COUNTS[name] for name in necessary)


def extra_pair_counts(fixed_names, forced_prize_name, exposure, supporter):
    """Independently enumerate 48 eligible physical identities for two Prizes."""
    occupied = set(exposure)
    for name in fixed_names:
        i = next(i for i in range(60)
                 if BASE_DECK[i] == name and i not in occupied)
        occupied.add(i)
    for _ in range(4):
        i = next(i for i in range(60)
                 if BASE_DECK[i] == forced_prize_name and i not in occupied)
        occupied.add(i)
    assert len(occupied) == 12
    pool = set(range(60)) - occupied
    assert len(pool) == 48
    necessary = (
        ("Technical Machine: Evolution", "Jet Energy", "Artazon", "Bunnelby")
        if supporter else
        ("Technical Machine: Evolution", "Artazon", "Bunnelby")
    )
    counts = Counter()
    for pair in combinations(sorted(pool), 2):
        if not usable_pair(pair, necessary):
            continue
        if supporter:
            names = (BASE_DECK[pair[0]], BASE_DECK[pair[1]])
            recyclable = (
                ("Technical Machine: Evolution" not in names)
                + ("Artazon" not in names)
            )
            for safe in range(7):
                if safe >= 3 and safe - 3 + recyclable >= 2:
                    counts[safe] += 1
        else:
            for safe in range(3, 6):
                counts[safe] += 1
    return counts


def safe_exposure_count(disposable, size, minimum):
    """Independent physical 11-label enumeration of safe opening/draw stock."""
    safe = set(FILLERS[:disposable])
    return sum(
        len(exposure)
        for exposure in combinations(FILLERS, size)
        if len(safe.intersection(exposure)) >= minimum
    )


def coefficient(disposable, supporter):
    size = 6 if supporter else 5
    total = 0
    for safe in range(3, size + 1):
        choose = comb(disposable, safe) * comb(11 - disposable, size - safe) \
            if safe <= disposable and size - safe <= 11 - disposable else 0
        pair_count = {3: 944, 4: 1120, 5: 1124, 6: 1124}[safe] \
            if supporter else 1125
        total += size * choose * pair_count
    return total


def main():
    # A canonical exposure with all actual pair choices verifies recyclable
    # payment routing counts without using any closed-form pair assumptions.
    s_pairs = extra_pair_counts(
        ("Oddish", "Grand Tree"), "Tag Call",
        FILLERS[:6], True,
    )
    t_pairs = extra_pair_counts(
        ("Oddish", "Grand Tree", "Jet Energy"), "Guzma & Hala",
        FILLERS[:5], False,
    )
    assert [s_pairs[k] for k in range(7)] == [0, 0, 0, 944, 1120, 1124, 1124]
    assert [t_pairs[k] for k in range(6)] == [0, 0, 0, 1125, 1125, 1125]

    for d in range(12):
        # Independent labeled-card exhaustive opener/draw oracle, even before
        # considering later recycled payment opportunities.
        s_exposure_ge5 = safe_exposure_count(d, 6, 5)
        t_exposure_ge3 = safe_exposure_count(d, 5, 3)
        assert s_exposure_ge5 == 6 * sum(
            comb(d, j) * comb(11-d, 6-j)
            for j in (5, 6) if j <= d and 6-j <= 11-d
        )
        assert t_exposure_ge3 == 5 * sum(
            comb(d, j) * comb(11-d, 5-j)
            for j in (3, 4, 5) if j <= d and 5-j <= 11-d
        )
        s = Fraction(
            DECK_COUNTS["Oddish"] * coefficient(d, True), 1
        ) / DENOMINATOR
        t = Fraction(
            DECK_COUNTS["Oddish"] * DECK_COUNTS["Jet Energy"]
            * coefficient(d, False), 1
        ) / DENOMINATOR
        assert 0 <= s <= Fraction(843, 48561235923200)
        assert 0 <= t <= Fraction(225, 7769797747712)
        if d == 3:
            assert s == Fraction(59, 33385849697200)
            assert t == Fraction(75, 42733887612416)
        if d == 11:
            assert s == Fraction(843, 48561235923200)
            assert t == Fraction(225, 7769797747712)
        print("disposable", d, "supporter_certificate", s, float(s),
              "tool_stadium_certificate", t, float(t))

    # Monotone in the number of hypothetical safe physical cards.
    assert all(
        coefficient(d, True) <= coefficient(d+1, True)
        and coefficient(d, False) <= coefficient(d+1, False)
        for d in range(11)
    )
    print("DCI-aware recyclable search-output payment certificates passed.")


if __name__ == "__main__":
    main()
