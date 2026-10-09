# Reciprocal gust creates an exposed-Bench liability

## Question

Does putting an additional Pokemon on our Bench ever hurt our chance to force a six-Prize win, even if that Pokemon costs nothing to deploy and expands our promotion choices?

The earlier [two-sided race](../two_sided_gust_race/) treated the opponent as attacking only our natural Active. This extension gives the opponent zero, one, or two unrestricted, already-available **Boss's Orders** gust tokens. Its answer is conditional: adding a Benched Pokemon is harmless in this model when opposing gust is absent, yet it can expose a game-ending Prize target when opposing Boss is available.

## Rules-grounded abstract game

Each player has a fixed board. Pokemon are labeled only by their 1/2/3-Prize KO reward; every announced attack one-hit KOs its selected Active. We use one of three starting two-gust inventories: 2 Counter Catchers, 1 Boss plus 1 Counter, or 2 Bosses. Counter remains subject to own remaining Prizes > opposing remaining Prizes.

The opposing player can use at most one Boss each attacking turn, choosing any of our Benched Pokemon to gust and KO. Both sides select their own new Active after suffering a KO. The opponent can instead end its turn without attacking, as permitted by Advanced Player's Rulebook A-01. No new Pokemon or resources are acquired between attacks. The opponent's currently available Boss tokens are consumed upon use. Immediate victory occurs when either player takes its final Prize or knocks out the other's final Pokemon.

This is a deliberately bounded, perfect-information game. Its 1/2/3-Prize labels represent existing Pokémon properties abstractly, without attack costs, HP, Abilities or Bench-slot competition.

## A small actionable counterexample

Both players start with six Prize cards remaining. The **opponent has two Prizes remaining**, an Active worth three Prizes, a Benched three-Prizer, and one Boss's Orders. We have an Active worth one Prize, a Benched one-Prizer, and two Counter Catchers.

- **Do not Bench an additional two-Prize Pokemon:** We can force the win in two attacks. Knock Out a three-Prizer with Counter Catcher, and KO the remaining three-Prizer next attack. The opponent's one Boss can only expose a one-Prize Pokemon, so cannot take both remaining Prizes in its reply.
- **Bench an additional two-Prize Pokemon:** The opponent can use Boss's Orders on that newly exposed two-Prizer and KO it on its reply, taking both final Prizes before our second attack. Under this abstract combat model, we cannot force the win.

If the opponent has no Boss, the additional two-Prizer does not remove our forced win. This reversal isolates the opponent's target-selection geometry rather than any deck-space or Bench-capacity cost.

## Exact exhaustive census

For each baseline own Active worth 1 or 2 and eight own Bench configurations, add one 1-, 2-, or 3-Prize Pokemon. Evaluate every pairing with 146 opposing board classes, opponent remaining Prizes 2..6, and each of three attacker gust inventories. There are **105,120 baseline-to-expanded-board comparisons per opposing Boss budget**.

| Opponent Boss tokens | Adding Bench reduced our forced win | Adding Bench improved our forced win | No change |
| ---: | ---: | ---: | ---: |
| 0 | 0 | 15,467 | 89,653 |
| 1 | 4,914 | 10,378 | 89,828 |
| 2 | 6,286 | 7,558 | 91,276 |

The zero-harm result with no opposing gust has a structural explanation. The extra Benched Pokemon is never forcibly selected by the opponent and adds a promotion choice for us. We can emulate any old winning policy while ignoring that extra body. Opponent gust introduces an additional targeted action, breaking the simulation relation. The extra pokemon's Prize value becomes an offensive option for the opponent.

These are **uniformly enumerated structural comparisons**, with repeated baseline states under different add-card choices and inventories. They are not metagame frequencies or a deck-construction ranking.

## Independent validation

The two-sided mutual-gust solver lives in [tools/two_sided_mutual_gust.py](../../tools/two_sided_mutual_gust.py). Its independent fixed-deadline oracle [reproduce.py](reproduce.py) checks **26,280** initial states and playing-permission conditions. For all cases with zero opposing Boss, **13,140** comparisons match the prior [two-sided gust race](../two_sided_gust_race/) implementation exactly.

The reproducer additionally checks all **315,360** Bench-addition comparisons across zero, one and two opposing Boss tokens and asserts the small counterexample. Source comparison follows the natural nesting: with identical target scopes, two unrestricted Boss tokens are at least as strong as one Boss plus one Counter, which is at least as strong as two Counters.

Run from repository root: `python -m results.mutual_gust_bench_liability.reproduce`.

## Limits and next questions

A realistic Pokemon added to the Bench can also contribute attack readiness, draw Abilities or evolution targets, and can consume a scarce Bench slot. Opponent gust may face Item lock, Supporter lock, target-specific protections, and card-acquisition deadlines. Attacks can take multiple hits or fail to secure a Knock Out. Extending this result requires typed, resource-aware attack and Bench states, plus an actual opponent policy under partial information.

The constructive mechanism is still an important warning for a general deck or board optimizer: **extra visible liabilities can convert the opponent's gust resource into a terminal action**, even when the extra Pokemon provides a defensive spare.
