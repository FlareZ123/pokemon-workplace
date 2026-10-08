# Serena: a Supporter mode is a choice between tactical gust and future draw access

## Source card and strategic problem

Serena `swsh12-164` is an Expanded-legal Supporter with two modes:

- Discard one to three cards from hand, then draw until the hand has five cards.
- Switch one opposing Benched Pokémon V with its Active Pokémon.

The first mode requires an actual hand discard. Both modes spend the only ordinary Supporter action that turn. Boss's Orders can gust any opposing Benched Pokémon but offers no card-draw alternative.

Previous `results/typed_gust_target_minimax/` treated Serena only as a Pokémon V-restricted gust. This experiment adds its exact draw-to-five mode and studies when drawing for a later Boss can make an otherwise inert Serena valuable.

## State and transitions

`tools/serena_draw_option.py` models a finite deck with three card categories: Boss, Serena and inert filler. It tracks physical counts of those card categories in the hand and deck. An opposing board has one-hit KO targets with 1, 2 or 3 Prize rewards and a Pokémon V eligibility flag. A normal draw happens at the beginning of every attacking turn.

After the draw the player chooses among:

- Attack the Active without playing a Supporter.
- Spend Boss to gust any opposing Benched Pokémon, then attack.
- Spend Serena to gust a Benched Pokémon V, then attack.
- Spend Serena in draw mode: remove Serena from hand, choose a nonempty set of up to three cards from the remaining hand to discard, then draw **exactly the missing number to five cards**, followed by an attack on the unchanged Active.

The discard choices include Boss or other Serena copies. They are enumerated instead of assuming that every hand card is disposable. Hypergeometric sampling of Boss/Serena/filler after the discard is exact. No further Supporter is played that turn, even when a newly drawn Boss appears.

An attack ends the turn. The defender chooses a replacement Active after a KO to maximize the player's expected future attack count. Serena draw identities remain private at that promotion decision: the defender chooses one promotion based on the aggregate distribution rather than seeing every drawn identity.

The model is a bounded continuation. It assumes the opposing board is already established, with no damage carryover, opponent attacks, additional Bench Pokémon, Item effects or Prize-card refill. All tested draw piles have at least 20 cards, enough for the limited planning horizon.

## A sharp draw-mode witness

Opponent Active **3-Prize non-V**, Bench **1-Prize non-V and 3-Prize non-V**. The player holds one Serena, zero Boss and zero filler cards, with **20 unknown deck cards** containing one or two Boss copies and inert fillers.

Serena's gust mode has no target, so the player can KO the Active three-Prize Pokémon naturally and try to draw Boss in time for a second KO on the following turn.

| Boss copies in 20-card deck | Serena draw mode enabled | Serena restricted to gust only | Expected attacks saved by draw mode |
| ---: | ---: | ---: | ---: |
| 1 | 53/20 = 2.650000 | 29/10 = 2.900000 | 1/4 = 0.250000 |
| 2 | 229/95 = 2.410526 | 533/190 = 2.805263 | 15/38 = 0.394737 |

When the first natural draw is a filler, Serena may discard that filler and draw five fresh cards. The newly drawn Boss cannot be played immediately because Serena consumed the Supporter action, but it becomes available for the next attack turn.

This witness admits an independently verifiable formula. With B Boss copies among 20 cards, the chance of failing to see Boss through the first two natural draws, absent Serena draw, is `C(20-B, 2) / C(20, 2)`. With Serena's five additional cards, an optimal two-attack route has an opportunity to expose seven total cards and the failure probability becomes `C(20-B, 7) / C(20, 7)`.

Accordingly:

`E[attacks without Serena draw] = 2 + C(20-B,2)/C(20,2)`

`E[attacks with Serena draw] = 2 + C(20-B,7)/C(20,7)`.

These are exact for this named witness with B=1 or B=2.

## Corpus-wide conditional study

All 582 V/non-V structural boards from `results/typed_gust_target_minimax/` were evaluated with one Serena in hand, no Boss in hand, twenty deck cards, and one or two Boss cards inside that draw pile.

| Boss copies in 20-card deck | Board geometries improved by enabling Serena draw | Maximum improvement in expected attacks |
| ---: | ---: | ---: |
| 1 | 105/582 | 1/2 |
| 2 | 120/582 | 29/38 |

The remaining board geometries have the same optimum with or without Serena's draw mode. This is a uniform structural state census, not a metagame-weighted deck analysis.

The alternate mode has a real opportunity cost. On a board with Active **1-Prize non-V**, Bench **1-Prize non-V, 3-Prize non-V, 3-Prize Pokémon V**, the initial Serena gust targeting the V preserves the possibility of Boss attacking the non-V three-Prize target later. Drawing with Serena on the first turn cannot achieve the same two-attack Prize route. In this specific state, enabling Serena draw does not change the optimum for 0, 1, 2, or 3 Boss copies in a 20-card draw pile.

## Verification

`results/serena_draw_option/reproduce.py` checks the exact one- and two-Boss formulas against the dynamic program; it checks that Serena requires a nonempty actual discard to access draw mode, verifies multivariate draw probabilities sum to one, and runs **1,164 model comparisons** over all 582 boards at Boss counts one and two, comparing both Serena modes versus gust mode alone.

The local after-draw state with a Serena, one filler card, and one Boss among nineteen deck cards has expected values `51/19` if Serena discards the filler to draw five and `56/19` if it attacks without using Serena. The distinction is asserted explicitly.

The exact computations use rational arithmetic and have no sampling error. Run from repository root: `python results/serena_draw_option/reproduce.py`.

## Interpretation and boundaries

Serena can be a future gust **access enabler** on a board with no current Pokémon V target, since its discard-draw mode can find Boss in time for the following attack. It may instead be the unique immediately legal gust source when a Pokémon V target must be hit now. Its value depends on actual hand size and disposable cards, future draw-pile composition, available action windows, and target geometry.

The study omits Supporter recovery, multiple other Supporters, opponent disruption, prize-taking into hand, search paths, and live Energy requirements. It models a local hand after setup rather than a full opening-seven draw, and cannot rank decklists without a realistic distribution of reachable hands.
