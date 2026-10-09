# Battle VIP Pass changes the attainable first-turn Bench assembly

## Research question

How much does a first-turn **Battle VIP Pass** improve the unusually
tight Quick Ball/Sky Field/Gothitelle sequence when four ordinary
Basic Pokémon plus Gothita must be established on the first turn?

Battle VIP Pass `swsh8-225` is a legal paper Expanded Item that
searches for up to two Basic Pokémon and puts them directly onto
the Bench. It can only be used during the player's **first turn**.
Unlike Nest Ball, one copy can fill **two** missing Bench positions.

- Exact model: [`tools/gothitelle_quick_vip_joint_board.py`](../../tools/gothitelle_quick_vip_joint_board.py)
- Independent physical-label SFT: [`reproduce.py`](reproduce.py)
- Comparators: [`gothitelle_core_board_joint_access`](../gothitelle_core_board_joint_access/), [`gothitelle_quick_nest_joint_board`](../gothitelle_quick_nest_joint_board/)

## Population and rules

The same disjoint hypothetical 60-card deck includes 3 Gothita,
2 Gothitelle, 4 Rare Candy, 8 other ordinary Basics, 4 Quick Ball,
2 Sky Field, zero to four Battle VIP Pass, and filler.

The player must begin with an ordinary Basic in their legal
seven-card opening hand. Six random Prize cards are selected,
then the player draws once during their first turn.

The objective is to have four ordinary Basics (one Active,
three Bench) and Gothita (fourth Bench) established by
the end of turn one, with Quick Ball used that turn to
**discard Sky Field**. Quick Ball can find one missing
Basic. When at least two are missing, Battle VIP Pass must be
accessible on the first turn and can search the other one
or two missing Basics. All search targets must remain unprized.

The second own-turn natural draw must leave both Rare Candy
and Gothitelle accessible for immediate Stage 2 evolution.
All searched Basics leave the physical deck before this draw.

As in the [earlier physical witness](../gothitelle_teleport_two_turn_bridge/),
the opponent's Collapsed Stadium and Stadium-from-hand lock
are exogenous premises. The later two Basic entrants,
Gothita survival, Item/Ability lock suppression, and all
alternative draw/search engines remain outside the model.

## Exact 60-card probabilities

| Battle VIP Pass copies | Two-turn access per initial seven-card attempt |
| ---: | ---: |
| 0 | 0.001573353% |
| 1 | 0.011259277% |
| 2 | 0.020614944% |
| 3 | 0.029645393% |
| 4 | **0.038355665%** |

For four VIP Pass copies, the access probability is **24.3783
times** the one-Quick baseline and **7.4932 times**
the earlier four-Nest variant (0.005118701%). This is
a comparison of alternate filler-substitution populations
under the identical action window. It is no claim about
actual meta-optimal deck inclusions.

The four VIP branch decomposition is:

| Basic searches needed | Per-opening event probability |
| ---: | ---: |
| 0, all Basics naturally present | 0.000020203% |
| 1, solved using Quick Ball | 0.001553150% |
| 2, solved using Quick Ball plus VIP Pass | 0.003545348% |
| 3, one Quick Ball plus a two-Basic VIP Pass | **0.033236964%** |

The three-missing-Basic branch dominates this very specific
opening objective. It captures hands with few naturally
drawn ordinary Basics that become playable once a two-target
direct-Bench search is available.

## Mathematical method

The seven-card category multisets are weighted with an exact
multivariate hypergeometric distribution, and the first-turn
natural draw is integrated by exchangeability.

For each observed first-eight state, the model determines the
counts of missing Gothita and ordinary Basics. Up to one
Quick Ball search and two VIP Pass searches are permitted.
The model separately sums the **joint Prize distribution**
for both Basic categories and verifies that each required
searched card remains in the physical deck.

If one of Rare Candy/Gothitelle is still missing, its
expected unprized copies are divided by the post-search
physical deck size. The marginal cases with no search use
the correct one-draw denominator without a search.

Two independent exhaustive regressions with 12 and 13
distinctly labeled cards enumerate complete opening sets,
Prize subsets, first-turn draws, physical search targets,
and possible turn-two draws, matching all four analytic
branch fractions exactly. A no-Prize variant, first-turn
card-availability checks and the precise bundled VIP Pass
text/legality checks are included.

## Strategic interpretation and boundaries

The **maximum number of Basic targets per Item play** and
the **turn at which the Item remains legal** are discrete
properties with measurable effects on opening viability.
A scalar measure of search connectivity misses both.

This study remains narrow. It assumes all required missing
Basics have been classified as functional, eligible targets.
It does not model on-entry Abilities, the opponent's decisions,
future Prize recovery, timing after the first turn, or the
cost of using deck slots for cards that become inert
after the first turn.

A practical next comparison should jointly model **Quick Ball,
Nest Ball, and VIP Pass in the same 60-card population**, with
an adaptive selection policy and explicit in-hand Item access,
to prevent mistakenly adding alternative strategy probabilities
that share the same successful opening states.
