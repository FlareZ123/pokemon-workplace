# Joint probability of the first-turn Quick Ball and Sky Field payload

## Research question

How frequently can one first-turn Quick Ball both discard Sky Field and
establish Gothita in time for turn-two Rare Candy into Gothitelle, with
Gothitelle's Teleport Room later retrieving the same Stadium from discard?

The deterministic physical play and timing witness is already proved in
[`gothitelle_teleport_two_turn_bridge`](../gothitelle_teleport_two_turn_bridge/).
This result measures the **joint card-access event** under an explicitly
simplified random-draw policy. It does not multiply independently estimated
setup and downstream-access probabilities.

- Engine: [`tools/gothitelle_dual_use_joint_access.py`](../../tools/gothitelle_dual_use_joint_access.py)
- Independent labeled SFT: [`reproduce.py`](reproduce.py)

## Population and turn policy

Example 60-card disjoint partition:

| Category | Copies |
| --- | ---: |
| Gothita | 3 |
| Gothitelle (Teleport Room) | 2 |
| Rare Candy | 4 |
| Other opening-capable Basic Pokémon | 8 |
| Quick Ball | 4 |
| Sky Field | 2 |
| Other filler | 37 |

Starting seven-card hand must contain Gothita or another Basic for a legal
opening. Six Prizes are selected uniformly from the remaining cards.
The player draws one natural card on turn one, and one on turn two.
The event requires **both Quick Ball and Sky Field in the observed first
eight cards**. Quick Ball is played on turn one **paying Sky Field**.

If Gothita is among the first eight cards, it is established on the Bench
and Quick Ball may choose zero targets in its restricted Basic search after
paying its mandatory discard. Otherwise Quick Ball must retrieve an
unprized Gothita from the physical deck and establish it on turn one.

Turn two succeeds if Rare Candy and Gothitelle are in the hand after the
natural draw. The turn-two draw is from a deck of 46 physical cards without
search, or 45 after a successful Gothita search. We marginalize Prizes
exactly. A single last draw cannot acquire both missing evolution pieces.

The end-to-end **board** assumptions remain exogenous: a suitable Bench
slot must be available on turn one, Gothita must survive, Collapsed
Stadium must be in play with a compatible history, and the opponent's
Barrier Shrine or an equivalent restraint must make the later discard
payload strategically relevant. The two additional required Basics are
assumed available. Their access and the pre-existing board are **not**
sampled from the 60-card population.

## Exact results

| Observed path | Per seven-card opening attempt |
| --- | ---: |
| First-turn Gothita naturally available | 0.196035720% |
| First-turn Gothita found by Quick Ball | 0.346314745% |
| **Combined joint access** | **0.542350465%** |
| **Combined, conditional on legal opener** | **0.697486125%** |

The searched-Gothita branch is distinct from the natural branch, so their
masses sum without double counting.

Sensitivity with the other category counts held constant, changing filler
to preserve 60 cards:

| Sky Field copies | Joint access per opening attempt |
| ---: | ---: |
| 1 | 0.280918692% |
| 2 | 0.542350465% |
| 3 | 0.785290118% |

These values estimate **card access for this one line**, not deck
consistency, matchup win probability, or the marginal benefit of adding
Sky Field to an actual deck. Opportunity cost, alternative search,
Supporters, Item lock, and other strategic routes remain excluded.

## Method and validation

For each seven-card category multiset we weight its exact multivariate
hypergeometric mass, then enumerate the category of the first-turn draw.
Marginalizing random Prizes permits treating that draw as exchangeable
among the 53 initially unseen cards. The subsequent paid Gothita search
requires an unprized copy, so the model explicitly sums the number of
Gothita in Prizes. Conditional on that count, the remaining Prizes are
exchangeable among other categories. If a Stage 2 or Candy is missing,
its expected surviving copies are divided by the **post-search** physical
deck size of 45, preserving the search/draw dependence.

Two independent labeled-exhaustive cases enumerate opening sets,
Prize subsets, first-turn draw identities, a chosen physical Gothita
search target, and all second-turn draws. They match the exact category
formula, including a case where Prizes change searchability. A no-Prize
variant and exact 60-card Fraction regression add independent controls.

Printed-card checks use the bundled paper Expanded pool: Gothita
`xy3-39`, Gothitelle `xy3-41`, Rare Candy `sv1-191`,
Quick Ball `swsh1-179` and Sky Field `xy6-89`. Rules grounding for
turn-one evolution restrictions and searching comes from the provided
Advanced Player's Rulebook.

## Strategic interpretation

The same early Quick Ball has a delayed resource role when the selected
discarded card becomes the only viable route to a Stadium under a
Stadium-from-hand lock. Exact joint access for the tight dual-use
sequence is well below one percent in this illustrative population,
showing why a deterministic legal line should not be mistaken for a
likely opening sequence.

This result provides the joint access missing from the prior
[`gothitelle_quick_ball_first_turn`](../gothitelle_quick_ball_first_turn/)
and [`teleport_same_pool_policy`](../teleport_same_pool_policy/) models.
It remains a bounded, source-grounded combinatorial result.

## Next experiment

Jointly sample the actual board-establishment requirements and access
to the two later Basic entrants, then admit alternative action lines
(direct Stadium removal, search/discard Items, opponent disruption).
Keep physical Prize/search accounting and turn-specific policy intact.
