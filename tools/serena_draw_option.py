"""State-adaptive Serena gust-versus-discard-and-draw in a Prize endgame.

Each turn begins with one draw from a finite deck containing Boss, Serena,
and filler cards. One Supporter may be played: Boss gusts any Benched Pokemon,
Serena gusts a Pokemon V, or Serena discards 1..3 hand cards and draws until
the hand has 5 cards. Discard choices can include Boss/Serena, so this model
does not silently treat every hand card as low-value discard fuel.

An attack KOs one target, closes the turn, and the defender chooses the next
Active adversarially. For Serena's private draws, promotion cannot depend
on which exact cards were drawn. All attacks are one-hit KOs; six Prizes win.
"""
from fractions import Fraction
from functools import lru_cache
from math import comb
from tools.typed_gust_target_minimax import Target


@lru_cache(None)
def draw_outcomes(
    deck_boss: int,
    deck_serena: int,
    deck_filler: int,
    draw_count: int,
) -> tuple[tuple[int, int, int, Fraction], ...]:
    total = deck_boss + deck_serena + deck_filler
    if not 0 <= draw_count <= total:
        raise ValueError("Draw count exceeds remaining deck size")
    outcomes = []
    for bosses in range(min(deck_boss, draw_count) + 1):
        for serenas in range(min(deck_serena, draw_count - bosses) + 1):
            fillers = draw_count - bosses - serenas
            if not 0 <= fillers <= deck_filler:
                continue
            likelihood = Fraction(
                comb(deck_boss, bosses)
                * comb(deck_serena, serenas)
                * comb(deck_filler, fillers),
                comb(total, draw_count),
            )
            outcomes.append((bosses, serenas, fillers, likelihood))
    return tuple(outcomes)


@lru_cache(None)
def expected_attacks(
    active: Target,
    bench: tuple[Target, ...],
    hand_boss: int,
    hand_serena: int,
    hand_filler: int,
    deck_boss: int,
    deck_serena: int,
    deck_filler: int,
    prizes_needed: int = 6,
    enable_serena_draw: bool = True,
    protect_gust_resources: bool = False,
) -> Fraction:
    """Expected attack turns from before a turn's mandatory natural draw."""
    remaining = deck_boss + deck_serena + deck_filler
    if remaining <= 0:
        raise ValueError("Experiment requires a nonempty deck on each turn")
    total = Fraction()
    if deck_boss:
        total += Fraction(deck_boss, remaining) * _after_natural_draw(
            active, bench, hand_boss + 1, hand_serena, hand_filler,
            deck_boss - 1, deck_serena, deck_filler,
            prizes_needed, enable_serena_draw, protect_gust_resources,
        )
    if deck_serena:
        total += Fraction(deck_serena, remaining) * _after_natural_draw(
            active, bench, hand_boss, hand_serena + 1, hand_filler,
            deck_boss, deck_serena - 1, deck_filler,
            prizes_needed, enable_serena_draw, protect_gust_resources,
        )
    if deck_filler:
        total += Fraction(deck_filler, remaining) * _after_natural_draw(
            active, bench, hand_boss, hand_serena, hand_filler + 1,
            deck_boss, deck_serena, deck_filler - 1,
            prizes_needed, enable_serena_draw, protect_gust_resources,
        )
    return total


@lru_cache(None)
def _after_natural_draw(
    active: Target,
    bench: tuple[Target, ...],
    hand_boss: int,
    hand_serena: int,
    hand_filler: int,
    deck_boss: int,
    deck_serena: int,
    deck_filler: int,
    prizes_needed: int,
    enable_serena_draw: bool,
    protect_gust_resources: bool,
) -> Fraction:
    """Select no Supporter, targeted gust, or the full Serena draw mode."""
    return min(
        cost for _description, cost in action_values(
            active, bench, hand_boss, hand_serena, hand_filler,
            deck_boss, deck_serena, deck_filler,
            prizes_needed, enable_serena_draw, protect_gust_resources,
        )
    )


def action_values(
    active: Target,
    bench: tuple[Target, ...],
    hand_boss: int,
    hand_serena: int,
    hand_filler: int,
    deck_boss: int,
    deck_serena: int,
    deck_filler: int,
    prizes_needed: int = 6,
    enable_serena_draw: bool = True,
    protect_gust_resources: bool = False,
) -> tuple[tuple[str, Fraction], ...]:
    """After-draw conditional choices and their continuation value."""
    def attack(
        target: Target,
        remaining: tuple[Target, ...],
        b: int,
        s: int,
        f: int,
    ) -> Fraction:
        if target.prizes >= prizes_needed or not remaining:
            return Fraction(1)
        return Fraction(1) + max(
            expected_attacks(
                promoted, remaining[:i] + remaining[i + 1:],
                b, s, f, deck_boss, deck_serena, deck_filler,
                prizes_needed - target.prizes, enable_serena_draw,
                protect_gust_resources
            )
            for i, promoted in enumerate(remaining)
        )

    options = [("attack_active", attack(active, bench, hand_boss, hand_serena, hand_filler))]
    for i, target in enumerate(bench):
        new_bench = tuple(sorted((active,) + bench[:i] + bench[i + 1:]))
        if hand_boss:
            options.append((
                f"boss_gust_{target.prizes}{'_V' if target.is_pokemon_v else '_nonV'}",
                attack(target, new_bench, hand_boss - 1, hand_serena, hand_filler),
            ))
        if hand_serena and target.is_pokemon_v:
            options.append((
                f"serena_gust_{target.prizes}V",
                attack(target, new_bench, hand_boss, hand_serena - 1, hand_filler),
            ))

    if hand_serena and enable_serena_draw:
        # Serena is played first, leaving (hand_serena-1) other copies.
        other_serenas = hand_serena - 1
        for discarded_boss in range(
            1 if protect_gust_resources else min(3, hand_boss) + 1
        ):
            for discarded_serena in range(
                1 if protect_gust_resources else min(3 - discarded_boss, other_serenas) + 1
            ):
                for discarded_filler in range(
                    min(3 - discarded_boss - discarded_serena, hand_filler) + 1
                ):
                    discard_count = (
                        discarded_boss + discarded_serena + discarded_filler
                    )
                    if discard_count == 0:
                        continue
                    b = hand_boss - discarded_boss
                    s = other_serenas - discarded_serena
                    f = hand_filler - discarded_filler
                    draw_count = max(0, 5 - (b + s + f))
                    if draw_count == 0:
                        # Dominated by keeping the Serena and attacking Active.
                        continue
                    remaining_deck = deck_boss + deck_serena + deck_filler
                    if draw_count > remaining_deck:
                        # All experimental initial states have enough deck;
                        # exclude truncated-draw states outside this model.
                        continue
                    if active.prizes >= prizes_needed or not bench:
                        options.append(("serena_draw", Fraction(1)))
                        continue

                    outcomes = draw_outcomes(
                        deck_boss, deck_serena, deck_filler, draw_count
                    )
                    future = max(
                        sum(
                            (
                                likelihood * expected_attacks(
                                    promoted,
                                    bench[:i] + bench[i + 1:],
                                    b + got_boss, s + got_serena,
                                    f + got_filler,
                                    deck_boss - got_boss,
                                    deck_serena - got_serena,
                                    deck_filler - got_filler,
                                    prizes_needed - active.prizes,
                                    enable_serena_draw, protect_gust_resources,
                                )
                                for got_boss, got_serena, got_filler, likelihood in outcomes
                            ),
                            Fraction(),
                        )
                        for i, promoted in enumerate(bench)
                    )
                    options.append((
                        f"serena_draw_discard_{discarded_boss}_boss_"
                        f"{discarded_serena}_serena_{discarded_filler}_filler",
                        Fraction(1) + future,
                    ))
    return tuple(options)
