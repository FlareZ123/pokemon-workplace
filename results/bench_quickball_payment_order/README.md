# Quick Ball payments can make Bench-trigger ordering decisive

## Research question

Does modeling the current hand as a fixed set of discardable cards
underestimate the probability of executing two different hand-to-Bench
support Pokémon triggers? An already-used support can be picked up into hand
and then discarded to pay for a later Quick Ball, changing the set of legal
actions within the same turn.

This is a small **restricted action-model** experiment for paper Expanded:
[decision kernel](../../tools/bench_quickball_sequence.py),
[setup and Prize integration](../../tools/bench_quickball_access.py),
[reproduction](reproduce.py).

## Actual card-text anchors

The bundled card database contains:

- **Quick Ball** `swsh1-179`: an Item playable only after discarding one other hand card. It searches a Basic Pokémon into hand.
- **Super Scoop Up** `bw1-103`: an Item that flips a coin, and on heads puts one of your Pokémon plus attached cards into hand.
- **Scoop Up Cyclone** `bw10-95`: a deterministic pickup Item with the one-ACE-SPEC-per-deck limitation.
- **Tapu Lele-GX** `sm2-60` Wonder Tag and **Crobat V** `swsh3-104` Dark Asset: examples of abilities triggered specifically when played from hand onto the Bench.

The model keeps two separate singleton target Basics, their hand/deck/Bench/
discarded or unavailable locations, a bitmask of triggers already resolved,
one-use Quick Ball copies, other cards permissible for discard, and deterministic
or coin pickup Items.

**Important restrictions:** It treats trigger payloads as neutral; Crobat V
actually draws and another support such as Dedenne-GX may discard the hand,
so complete real-game sequencing is different. Any initial support Basic
forced to be the starting Active is treated as unavailable, even though a
sufficiently supported scoop/replacement line could potentially recover it.
Opening hand ordinary Basics are not automatically counted as discard fuel.
It excludes locks, attack timing, Bench-capacity-changing cards, search
failures unrelated to the two targets, recovery, Prize rescue, opponent turns,
and all other game objectives. The exact percentages apply only to the stated
restricted model; they are **not tournament win probabilities**.

## A concrete legal-action witness inside the model

Suppose support A is in hand and B is in deck. The player's one transactional
Bench slot is free, and the hand contains one Quick Ball and one Scoop Up
Cyclone, with no disposable filler.

A search-before-trigger solver declares the second target unreachable:
the only payment candidates appear protected. The finite-state planner finds:

`Play A from hand to Bench -> trigger A -> Scoop Up Cyclone returns A -> discard returned A to Quick Ball -> search B -> play B onto Bench -> trigger B.`

This achieves both distinct trigger entries while preserving the same single
physical Bench slot. Replacing deterministic Scoop Up Cyclone with one
Super Scoop Up makes the plan succeed on heads, probability `1/2`;
with two available Super Scoop Ups its probability is `3/4`.
The exact policy adapts to the first coin result.

The crucial state change is in the discard value of A. Before activation
the single copy is needed to satisfy the trigger objective; after activation
and successful pickup, the returned copy may be expendable. A coarse static
discard-capable index misses that timing.

## Exact opening/Prize calculation

For each grouped 7-card ordinary-Basic accepted opener, six hidden Prize
cards and a specified number of later random cards are drawn without
replacement. A target left on deck can be fetched by a Quick Ball; a target
Prized or irretrievably consumed as starting Active cannot. Each Quick Ball
requires one **different** physical hand card as payment. Direct-to-Bench
Items cannot cause the desired hand-origin trigger, but can themselves be
discarded to pay for Quick Ball if they are in hand.

At each grouped world we calculate:

- `payment_first`: the best success probability under a deliberately
  constrained policy that must execute all required Quick Ball searches
  before the first support enters the Bench. It may spend surplus Balls
  or pickup Items as discard payment;
- `adaptive`: the optimal stochastic within-turn action sequence,
  allowing support entry and pickup to create new discard opportunities.

An exact finite-state dynamic program maximizes a rational expected
success probability. It enumerates legal action branches, including every
possible payment source, both possible support orders, and heads/tails
for each Super Scoop Up. It uses a physical two-target state and `Fraction`
arithmetic. Hidden Prize sets are combinatorially marginalized without
granting a player information before the first deck search.

## 60-card sensitivity

Assume one A, one B, four ordinary Basic starters, four Quick Ball copies,
four Super Scoop Up copies, six Prizes, a seven-card opening, four later
uniform random cards, and four persistent core Bench occupants leaving one
transactional slot. Other 60-card slots are inert filler unless specified
as disposable. The extra random cards are a stipulated input rather than
a complete simulated draw engine.

All values condition on an accepted ordinary-Basic opening.

| Extra direct-Bench Items | Extra discardable filler | Search all first | Adaptive optimal | Ideal searches without payment |
| ---: | ---: | ---: | ---: | ---: |
| 0 | 0 | 1.508701% | **3.514291%** | 4.590978% |
| 0 | 2 | 2.052221% | **3.802451%** | 4.590978% |
| 2 | 0 | 2.052221% | **3.802451%** | 4.590978% |
| 4 | 0 | 2.534595% | **4.021786%** | 4.590978% |
| 4 | 2 | 2.953938% | **4.186583%** | 4.590978% |

The zero-extra-discard-stock scenario gains **2.005590 percentage points**
from optimal interleaving, compared with the payment-first policy. Relative
to the payment-first estimate, the adaptive probability is more than twice
as large. It remains below the ideal zero-payment upper benchmark,
demonstrating a real payment bottleneck in the restricted model.

Wrong-zone direct-to-Bench search Items can still contribute discard stock:
replacing two designated expendable cards with two such Items preserves
exact access in this model because both classes are identical payment
sources once in hand. This equivalence is specific to the two-trigger goal.

The ideal-search comparison is the prior
[double-trigger access model](../bench_double_trigger_release/), with
the same number of ordinary Basics, visible post-setup cards, and pickup
copies. It does not charge search payment.

## Independent verification

The reproducer enumerates **10,500 distinct labeled opening/Prize/draw
worlds**, using a ten-card physical deck with singleton A/B supports,
one ordinary Basic, two Quick Balls, two coin pickups, one direct-Bench
Item, one expendable card, and one filler. The oracle independently
constructs actual hand, starting Active, searchable deck, and all item
counts. It agrees exactly with the grouped model:

- search-before-trigger: `37/750`;
- adaptive optimum: `167/2625`.

Six separate exact small action-state witnesses verify pickup/pay sequencing
and coin probabilities. Five 60-card configurations satisfy
`payment_first <= adaptive <= zero-payment ideal`, and substituting
direct-Bench Items for equal quantities of disposable filler preserves the
result. The regression is run by GitHub Actions.

## Interpretation

Discardability changes *as a consequence of play*. A support copy can be
strategically protected while it is still needed for its unique Bench
trigger, and then become good Quick Ball payment after pickup.
Both the number of search connectors and their **time-dependent payment
sources** belong in an executable deck model.

The natural next layer is to execute support Abilities that mutate the
hand, then evaluate alternative orders and opposing Item/Ability locks.
A Dedenne-GX-like full-hand discard can destroy the next support or the
pickup Item, so the present order advantage may shrink or reverse when
real payloads and discard strategy are applied.
