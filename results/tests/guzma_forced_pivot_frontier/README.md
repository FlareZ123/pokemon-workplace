# Guzma forced-own-pivot tactical frontier

**Status:** Exact synthetic one-turn tactical analysis. Locally reproduced on 12 October 2026. No head-to-head match-win estimate. Source: tools/guzma_forced_pivot.py; independent regression: reproduce.py.

## Competitive relevance and card-text basis

The 2026 Aichi champion [Shadow Rider](../../decks/shadow-rider-calyrex/) uses one Guzma, while the runner-up [Vileplume control](../../decks/vileplume-control/) and fifth-place [Mew/Genesect](../../decks/mew-genesect/) each use two. Replacing Guzma by Boss's Orders changes the *own Active* movement, so opponent-target reachability alone does not determine the usefulness of the change. This research **does not recommend a swap**.

The regression confirms the English print texts in resources/cards/en:
- sm3-115 Guzma switches an opposing Benched Pokémon into Active; **if it does**, switches your own Active with a Benched Pokémon.
- swsh2-154 Boss's Orders switches an opposing Benched Pokémon into Active, without switching your own Active.
- sv1-194 Switch moves your own Active to the Bench and is an Item.

The supplied Advanced Player's Rulebook supports the Item/Supporter limits and switching mechanics (B-01, B-03, C-03, C-05).

## Explicit game model

One attacking turn. The opponent has exactly one Active and one Benched Pokémon, each worth 1, 2, or 3 Prizes. You have an Active and zero to five Benched Pokémon, respecting Bench capacity. Every own Pokémon has an arbitrary two-bit immediate KO-capability mask: able to KO the original opposing Active, the original opposing Bench, both, or neither.

Play zero or one held Supporter (Boss or Guzma), optionally sequence one held Switch Item before or after it if Items are legal, then make one attack. Track actual own and opposing Active indices. If Guzma successfully gusts, it must switch your own Active if you have a Bench target. Score the Prize value of an immediate KO, or zero for an attack incapable of KOing that target.

No attack-cost acquisition, Energy payment, normal Retreat, abilities, future opponent actions, damage persistence, refill, or strategic value of non-KO damage. This is a **conditional immediate Prize payoff**, not a match-win model. Every assignment of KO capability and Prize values is equally represented for enumeration and does not correspond to field frequency.

## Complete one-turn census without an alternative switch

| Own Pokémon | Boss better | Guzma better | Equal | Total |
| ---: | ---: | ---: | ---: | ---: |
| 1 | 0 | 0 | 36 | 36 |
| 2 | 24 | 24 | 96 | 144 |
| 3 | 48 | 144 | 384 | 576 |
| 4 | 96 | 672 | 1,536 | 2,304 |
| 5 | 192 | 2,880 | 6,144 | 9,216 |
| 6 | 384 | 11,904 | 24,576 | 36,864 |
| **Total** | **744** | **15,624** | **32,772** | **49,140** |

The difference may be three immediate Prizes. For own attack masks (2,0) and opponent Prize values (1,3), Boss yields 3 and Guzma 0: Guzma is forced to promote an own Bench Pokémon that cannot KO the valuable target. For masks (0,2) and the same opponent values, Boss yields 0 and Guzma 3: Guzma promotes the own ready attacker as part of the gust.

## Playable Switch equalizes the best payoff

Across **all 49,140** states, one freely playable Switch Item makes Boss and Guzma attain identical maximum immediate Prize payouts. Boss uses Switch to choose the preferred attacker; Guzma can use Switch before its mandatory own pivot to return the original attacker, or directly gust and promote a desired Bench attacker. When the held Switch is disabled by Item lock, results exactly match the no-Switch case.

A separate, algebraic closed-form oracle computes the maximum payout from reachable attacking Pokémon and checks every dynamic event-order answer. Both explicit three-Prize witnesses, exact histogram counts, held-but-Item-locked equivalence, and usable Switch equivalence are checked in reproduce.py.

Reproduce from the repository root: python -m results.tests.guzma_forced_pivot_frontier.reproduce

## Interpretation

Guzma's own-pivot effect has both constructive and destructive discrete tactical value, while availability of other switching actions changes the comparison. Real decks additionally constrain attack-readiness by Energy, active-dependent locks, other cards in hand, opponent decisions, and turn sequencing. A credible deck replacement study should model those constraints before judging the swap.
