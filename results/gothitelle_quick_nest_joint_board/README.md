# Nest Ball as the second turn-one search for Gothitelle Bench assembly

This experiment extends the paid Quick Ball/ Sky Field two-turn setup line
with a **second Basic search from Nest Ball**, which puts its target
directly onto the Bench without requiring a discard payment.

- Engine: [`tools/gothitelle_quick_nest_joint_board.py`](../../tools/gothitelle_quick_nest_joint_board.py)
- Reproducer: [`reproduce.py`](reproduce.py)
- Comparison: [`gothitelle_two_quick_joint_board`](../gothitelle_two_quick_joint_board/)

## Grounding and timed objective

The bundled paper Expanded print `sv1-181` is a legal Item. Its
effect searches for a Basic Pokémon and puts it onto the Bench.
The search needs an open Bench position, present in each state
where a second Basic search is required in this experiment.

A legal seven-card opener and two subsequent natural turn draws
are modeled around six random Prizes. The first-turn hand must
contain Quick Ball and Sky Field; Quick Ball pays Sky Field into
discard. By first turn's end the player needs four ordinary Basic
Pokémon (one initial Active and three Bench) and Gothita (fourth
Bench). On the second turn the player must have Gothitelle and
Rare Candy to evolve Gothita, after its evolution window opens.

When one Basic is missing, Quick can find it. When two are
missing, a Nest Ball available during the first turn searches
the second Basic and puts it directly onto the Bench. Both
searched cards must remain unprized, and each leaves the
physical deck before the following natural draw.

The opponent's already-compatible Collapsed Stadium/Ninetales
Stadium-play lock is assumed, consistent with
[`gothitelle_teleport_two_turn_bridge`](../gothitelle_teleport_two_turn_bridge/).
The required two subsequent Bench entrants are also externally
provided. These assumptions prevent interpreting the results as
a full match or archetype setup probability.

## Exact illustrative access

Fixed 60-card disjoint pool: 3 Gothita, 2 Gothitelle,
4 Rare Candy, 8 other ordinary Basics, 4 Quick Ball,
2 Sky Field, and the indicated number of Nest Ball,
with filler adjusted accordingly.

| Nest Ball copies | Access per seven-card opener |
| ---: | ---: |
| 0 | 0.001573353% |
| 1 | 0.002480803% |
| 2 | 0.003374178% |
| 3 | 0.004253477% |
| 4 | **0.005118701%** |

At four Nest Ball copies, this is an additional **0.003545348
percentage points**, or **225.337% relative** to the single-Quick
baseline (3.253 times the baseline event probability).

| Four-Nest branch | Per-opening probability |
| --- | ---: |
| All four core Basics and Gothita naturally seen | 0.000020203% |
| Quick finds the fourth ordinary Basic | 0.001097614% |
| Quick finds Gothita | 0.000455535% |
| Quick + Nest find two ordinary Basics | 0.002141507% |
| Quick + Nest find Gothita and an ordinary Basic | 0.001403841% |

The two-search probabilities condition jointly on the Prize
composition of Gothita and ordinary Basics. Where one evolution
piece is missing, the turn-two chance uses its expected unprized
copies divided by the physical deck size after both searches.

## Search payment changes the probability geometry

For zero through four Nest Ball copies, the incremental
two-search event has a **constant negative second finite difference**
as a function of Nest count. The first eight observed cards can
contain either one or two Nest copies in a successful two-search
state, producing a quadratic inclusion-exclusion expression and
diminishing marginal gains.

The companion [two-Quick study](../gothitelle_two_quick_joint_board/)
requires a separately approved discardable card for the second
Quick Ball. Its successful eight-card prefixes leave room for
only one copy of that cost card, producing an exactly linear gain
as copies are substituted for filler.

The two Item search effects therefore produce materially
different marginal-access profiles in this narrowly defined
setup window.

## Verification

Two independent physical-ID exhaustive small-deck enumerations
reproduce all five branch masses. They enumerate exact opening
sets, random Prize subsets, first-turn card identities,
one or two unprized Basic search targets, and every possible
second-turn draw. A zero-Prize control and exact concavity
regressions provide additional checks.

The shared Prize-conditioned search computation is reused from
`gothitelle_two_quick_joint_board`, while this model supplies
the different Nest Ball access condition and direct-Bench
action class. The print's legal status and Item effect text are
asserted from `resources/cards/en/sv1.json`.

## Limitations

The model does not evaluate attacks, opposing Knock Outs,
other Trainers, early Item lock, evolutionary action costs beyond
the fixed Rare Candy window, or actual Basic on-entry Abilities.
Nest Ball placing a Basic directly onto the Bench differs
tactically from Quick Ball adding it to the hand, even though
both remove one unprized Basic from the draw deck. Those
differences require typed on-entry trigger and Bench action models.

This is a joint timed access calculation under a deliberately
restrictive set of action choices; it is not an empirical deck
consistency claim.

## Next research direction

Connect a direct-Bench search to ability-triggered
hand-to-Bench effects and compare those endpoints against
physical Quick Ball retrieval. Then evaluate opposing early
Bench contraction and named species dependencies.
