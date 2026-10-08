# Gust Prize-race value persists with damage carryover

## Question

The exact one-hit gust minimax result identifies complementarity and timing option value. Does the phenomenon disappear when opponents may survive one attack and retain damage after being switched to the Bench?

## Model

`tools/durable_gust_minimax.py` assigns each opposing Pokemon two attributes: `(prizes_awarded_on_KO, attacks_remaining_to_KO)`. Rewards are 1, 2, or 3; durability is 1 or 2 hits. Every attack removes exactly one hit, and damage persists when switching a surviving target out. A target that survives remains Active. When it is Knocked Out, the defending player chooses the promotion that maximizes the attacking player's remaining number of attack turns.

A gust token changes the selected target from the Active Pokemon to a Benched Pokemon and switches the old Active onto the Bench, consuming one available Supporter-like gust on that attack turn. Multiple gusts require different turns.

The attacker wins when it has taken six Prizes or Knocked Out the last opposing Pokemon. No Pokemon are newly Benched. The defender has no voluntary retreat, switching, healing or attack actions, and the attacker has no target-specific energy constraints. These exclusions make the result a finite combinatorial tactical model.

Relevant source evidence is the advanced manual: A-03 / C-03 / C-05 describe switching and retention of damage counters; A-01 describes attack-turn closure; D and E describe KO and endgame resolution. The deck database supplies the card-text basis for Boss's Orders as the archetypal gust Supporter.

## Enumeration and exact results

Enumerate every multiset of two to four opposing Pokemon drawn from the six categories `(Prize value in {1,2,3}, hits in {1,2})`, with total available Prizes at least six, and every distinct starting Active category. This produces **390 structural initial board classes**.

| Attacks saved versus zero gusts | One gust | Two gusts |
| --- | ---: | ---: |
| 0 | 224 | 122 |
| 1 | 94 | 105 |
| 2 | 56 | 126 |
| 3 | 12 | 30 |
| 4 | 4 | 7 |
| **Total** | **390** | **390** |

The second gust has a strictly larger marginal attack-count saving than the first in **107** classes. Forcing the first gust onto a Benched target immediately, instead of preserving the timing choice, worsens the minimax attack count in **141** classes.

All counts are uniform counts of mathematically distinct board classes. No claims about their frequency in tournament play follow.

## Witness A: complementarity survives two-hit targets

Opponent Active `(1 Prize, 2 hits)`, Bench `(1 Prize, 2 hits)`, `(3 Prizes, 2 hits)`, `(3 Prizes, 2 hits)`.

| Gust access | Minimax attacks |
| ---: | ---: |
| 0 | 8 |
| 1 | 8 |
| 2 | 4 |

The defending player can otherwise keep two-hit one-Prize targets in front. Two separate gust actions switch in the two three-Prize Pokemon, and each survives its first hit while remaining Active for the follow-up knockout. Four attacks take six Prizes. One gust cannot ensure that outcome.

## Witness B: saving a single gust swings four attack turns

Opponent Active `(3 Prizes, 1 hit)`, Bench `(1 Prize, 2 hits)`, `(1 Prize, 2 hits)`, `(3 Prizes, 1 hit)`.

The minimax attack counts for zero, one and two gusts are **(6, 2, 2)**. With one gust the attacker should KO the starting Active for three Prizes without spending a Supporter, then gust the other one-hit three-Prize target next turn. If the gust is forced onto the Benched three-Prize target first, the defender can promote a two-hit one-Prize Pokemon and the favorable two-attack win disappears.

This illustrates how apparent material availability can be dominated by an immediate attack that preserves the targeted-switch option for a later turn.

## Independent validation

`results/durable_gust_minimax/reproduce.py` uses a separate Boolean finite-horizon oracle to test the shortest guaranteed winning deadline for each board and 0/1/2 gust tokens: **1,170 state/budget comparisons**. It also checks exact reduction to the original one-hit solver for all **117** eligible one-hit state/budget cases with up to four Pokemon.

Histograms, complementarity counts, eager-use regret, and both witnesses are asserted. The recursion strictly decreases the total number of hits remaining, establishing finite termination.

Reproduce: `python results/durable_gust_minimax/reproduce.py`.

## Limits and next directions

The key structural effects survive this normalized persistent-damage extension, although the class counts are sensitive to state-space definitions. This does not quantify how often a deck can KO a Pokémon VMAX in one or two attacks or whether Boss's Orders can be searched at the necessary turn.

Further models should make defender switches and healing decisions explicit, connect gust availability to `tools/stochastic_gust_draw.py`, distinguish damage from attack effects, and include turn-specific damage/Energy constraints. A physically realistic target-exposure model should also allow new Bench entries and the opponent's own attacks.
