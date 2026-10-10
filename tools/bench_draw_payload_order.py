"""Exact single-target hand survival under Crobat V and Dedenne-GX draw ordering.

A bounded, K0 information experiment: one target singleton was absent from
an already-known opening hand, and occupies one uniformly random remaining
position (natural draw, face-down Prize, or deck). The two support Basics are
retained in hand, a starting Active Basic has already been chosen, and any
prior hand reduction played only non-target cards without changing the deck.

No additional search, locks, Ability suppressors, recovery, or attack use is
modeled. The objective is a target copy in hand when the policy stops.
"""

from dataclasses import dataclass
from fractions import Fraction

POLICIES = (
    "dedenne_blind",
    "dedenne_stop",
    "crobat_only",
    "crobat_dedenne_forced",
    "crobat_dedenne_stop",
)


@dataclass(frozen=True)
class Outcome:
    target_in_hand: Fraction
    target_discarded: Fraction
    expected_bench_plays: Fraction
    expected_dedenne_uses: Fraction
    expected_draws: Fraction


@dataclass(frozen=True)
class _Path:
    found: bool
    discarded: bool
    bench_plays: int
    dedenne_uses: int
    drawn_cards: int


def _run_path(policy: str, *, hand_size: int, target_location: str,
              target_deck_index: int, deck_cards: int,
              bench_slots: int) -> _Path:
    """Execute one physical target position; other cards are inert filler."""
    if policy not in POLICIES:
        raise ValueError("unknown policy")
    found = target_location == "hand"
    discarded = False
    bench = 0
    dedenne = 0
    drawn = 0
    consumed = 0
    current_hand = hand_size

    def draw(count: int) -> None:
        nonlocal found, consumed, current_hand, drawn
        take = min(count, deck_cards - consumed)
        if target_location == "deck" and consumed <= target_deck_index < consumed + take:
            found = True
        consumed += take
        current_hand += take
        drawn += take

    def crobat() -> None:
        nonlocal bench, current_hand
        bench += 1
        current_hand -= 1
        draw(max(0, 6 - current_hand))

    def dedenne_play() -> None:
        nonlocal bench, current_hand, discarded, found, dedenne
        bench += 1
        dedenne += 1
        current_hand -= 1
        if found:
            discarded = True
            found = False
        current_hand = 0
        draw(6)

    if policy == "dedenne_blind":
        dedenne_play()
    elif policy == "dedenne_stop":
        if not found:
            dedenne_play()
    elif policy == "crobat_only":
        if not found:
            crobat()
    elif policy == "crobat_dedenne_forced":
        if bench_slots < 2:
            raise ValueError("two free Bench slots required")
        crobat()
        dedenne_play()
    else:
        if bench_slots < 2:
            raise ValueError("two free Bench slots required")
        if not found:
            crobat()
            if not found:
                dedenne_play()

    if bench > bench_slots:
        raise AssertionError("Bench overfilled")
    return _Path(found, discarded, bench, dedenne, drawn)


def analyze(*, hand_size: int = 5, deck_cards: int = 46,
            prizes: int = 6, natural_draws: int = 1,
            bench_slots: int = 2) -> dict[str, Outcome]:
    """Exact average over target locations without hidden-position clairvoyance.

    There is one target singleton among the natural_draws + prizes +
    deck_cards unseen cards. All draws are natural draws before the support
    decisions. For natural_draws > 1, this procedure assumes target was held
    and preserved if it appeared in any of those draws; the hand-size input is
    already after non-target payments. For the two-support staging policy,
    the decision to use Dedenne depends only on whether K is now in hand.
    """
    if min(deck_cards, prizes, natural_draws) < 0:
        raise ValueError("negative card count")
    if hand_size < 2 or hand_size < 3 and natural_draws:
        raise ValueError("two supports, plus room for a drawn target if needed")
    if bench_slots < 1 or bench_slots > 5:
        raise ValueError("Bench slots must be 1..5")
    total = natural_draws + prizes + deck_cards
    if total == 0:
        raise ValueError("no possible target position")
    cases = ([("hand", -1)] * natural_draws
             + [("prize", -1)] * prizes
             + [("deck", index) for index in range(deck_cards)])
    available = [p for p in POLICIES if bench_slots >= 2 or
                 not p.startswith("crobat_dedenne")]
    result = {}
    for policy in available:
        paths = [_run_path(policy, hand_size=hand_size,
                           target_location=zone, target_deck_index=index,
                           deck_cards=deck_cards, bench_slots=bench_slots)
                 for zone, index in cases]
        result[policy] = Outcome(*(
            Fraction(sum(getattr(p, field) for p in paths), total)
            for field in ("found", "discarded", "bench_plays",
                          "dedenne_uses", "drawn_cards")
        ))
    return result


def exact_closed_form(*, hand_size: int, deck_cards: int,
                      prizes: int, natural_draws: int = 1) -> dict[str, Fraction]:
    """Independent closed forms for successes when draw pool is ample.

    Assumes deck_cards >= max(0,7-hand_size) + 6.
    """
    a = max(0, 7 - hand_size)
    if deck_cards < a + 6:
        raise ValueError("closed form requires enough live deck cards")
    total = natural_draws + prizes + deck_cards
    return {
        "dedenne_blind": Fraction(6, total),
        "dedenne_stop": Fraction(natural_draws + 6, total),
        "crobat_only": Fraction(natural_draws + a, total),
        "crobat_dedenne_forced": Fraction(6, total),
        "crobat_dedenne_stop": Fraction(natural_draws + a + 6, total),
    }


if __name__ == "__main__":
    for h in (3, 4, 5, 6, 7):
        x = analyze(hand_size=h)
        print(f"h={h}: Dedenne stop={float(x['dedenne_stop'].target_in_hand):.6%}, "
              f"staged stop={float(x['crobat_dedenne_stop'].target_in_hand):.6%}, "
              f"extra Bench plays={float(x['crobat_dedenne_stop'].expected_bench_plays - x['dedenne_stop'].expected_bench_plays):.6f}")
