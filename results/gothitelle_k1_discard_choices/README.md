# State-dependent Quick Ball discard costs and the value of K1 Prize information

## Question

The [paid adaptive Item model](../gothitelle_paid_adaptive_items/)
treats the cost of additional Quick Ball plays as a separate,
static pool of approved disposable cards.

What changes when *copies already held* can become safe discard
payments, and when an otherwise strategically protected Rare Candy
or Gothitelle must be discarded to cross a Basic-search threshold?

The first Quick Ball still discards Sky Field and searches the deck,
giving its controller full information on the remaining deck and,
by elimination, on the six Prize cards. Subsequent Quick Ball
payment decisions can therefore use **K1** information.

- New engine: [`tools/gothitelle_k1_discard_choices.py`](../../tools/gothitelle_k1_discard_choices.py)
- Exact baseline: [`gothitelle_paid_adaptive_items`](../gothitelle_paid_adaptive_items/)
- Independent labeled enumerator: [`reproduce.py`](reproduce.py)
- Prior theory: `resources/human_concepts.md`, especially state-dependent DCI/UDP and K0/K1

## Fixed setup and payment policy

Same hypothetical 60-card disjoint pool: Gothita3,
Gothitelle2, Rare Candy4, eight other ordinary Basics,
Quick Ball4, Sky Field2, Nest Ball4, Battle VIP Pass4,
approved-discard cards12, filler17.

A legal opening has an ordinary Basic as Active. Six Prize
cards are set. After one natural first-turn draw, the
player must establish four ordinary Basics (one Active
and three Bench) plus Gothita (fourth Bench), paying Sky
Field with one mandatory Quick Ball. Turn-two Rare Candy
and Gothitelle must be available after the next natural draw.

One additional Quick Ball can search one more Basic if its
discard cost can be paid. The model uses **only the
minimum number** of extra Quick Balls needed to attain
the Basic threshold after available Nest/VIP actions.

Payment priority in the exact narrow objective:

1. Use separately approved discard cards.
2. Also allow *safe surplus* from a second Sky Field,
   Gothita copies beyond the single necessary copy,
   ordinary Basics beyond four, duplicate Stage2/Candy
   cards while preserving one, and unused additional
   Quick Balls after paying for the required Quick plays.
3. When safe payments are short by exactly one, and both
   Stage2 and Candy are present, allow discarding the
   last retained copy of **one** evolution piece,
   accepting that the turn-two natural draw must
   replace that piece.

No Nest Ball or Battle VIP Pass is sacrificed to pay
an extra Quick. Trading a one- or two-Basic direct
search Item for one paid Quick search cannot increase
the Basic-search capacity in this fixed objective.

## Exact probabilities

| Payment policy | Two-turn access per seven-card attempt |
| --- | ---: |
| Approved-discard pool only | 0.069787404809% |
| Approved cards plus safe surplus | 0.070443459417% |
| Add critical evolution discard, committed without Prize information | 0.070643171862% |
| **Choose the critical discard using K1 information** | **0.070643235845%** |

The safe-surplus channel alone contributes **0.000656054608
percentage points**. Critical-payment risk adds another
**0.000199776428 percentage points** under K1.
Together they produce +0.000855831036 percentage
points over the earlier static-discard model, a
**1.226340% relative improvement**.

The K1-specific informational improvement over an
optimal *pre-search commitment* to discarding Stage2
or Candy is **0.000000063982776 percentage points**.
It is positive and extremely small in this population.

The hypothetical K0 commitment chooses whichever discard
type has higher *expected* turn-two replacement access,
marginalizing six hidden Prizes. The K1 line chooses after
inspecting the physical deck, using the actual counts of
unprized Gothitelle versus Rare Candy outs.
The value is small because four copies of Rare Candy
and two of Gothitelle produce a usually obvious
preferred target, with comparatively few Prize states
reversing that order.

## Mathematical method

Each seven-card category multiset and first-turn draw
category receives its exact multivariate hypergeometric
weight. The already-validated approved-only model
contributes its mass unchanged.

New states are counted **only** when the approved pool
alone cannot pay for the minimum extra Quick demand:

- If held safe surplus can supply the required costs,
  the probability of unprized Basic-search targets
  and one needed evolution-piece draw comes from the
  exact joint-Prize search kernel.
- If safe surplus falls short by one and both evolution
  pieces are initially present, Prize count states of
  Gothita, ordinary Basics, Stage2 and Rare Candy are
  summed jointly. The search target requirements must
  be physically satisfied before choosing the discard.
  K0 takes the maximum of expected Stage2/Candy
  replacement probabilities. K1 takes the expected
  maximum after each revealed Prize configuration.

All calculations use exact rational arithmetic.
The final draw denominator accounts for the number
of Basics actually removed from the deck.

## Validation

The independent SFT fully enumerates **physical card IDs**
for two different 16-card example populations. For each
observed opening hand and first-turn natural draw, it
enumerates all possible Prize sets and all physical
search targets, then evaluates every possible final draw.

The K0 reference groups all hidden Prize possibilities
for the same observed hand before choosing which
critical piece to discard. The K1 reference chooses
separately per Prize set. The baseline, safe-surplus,
K0 critical and K1 critical fractions each agree
exactly with the analytic result in both populations.
Quick Ball's paper Expanded legality and mandatory
one-card payment are checked from `swsh1-179`.

## Limitations and strategic interpretation

The finding formalizes **state-dependent DCI**:
a held redundant evolution card, extra Sky Field,
or surplus Basic can become expendable when a Quick
Ball payment unlocks a first-turn search. In a
rare state, sacrificing the sole held evolution
piece is still rational for the modeled objective,
because the board would otherwise remain incomplete.

The probabilities remain conditional on the
exogenous opposing Collapsed Stadium/Ninetales
structure, Gothita survival and two later Basic
entrants. The model suppresses attacks, opponent
disruption, and unrelated value of the discarded
cards. It also excludes optional extra Quick plays
whose only purpose would be deck thinning.

A general deck optimizer should evaluate
discardability at the **game-state and intended
continuation** level, rather than tagging cards
as permanently discardable or permanently protected.

## Next experiment

Investigate the value of an *optional* Quick Ball
search for an expendable Basic when all necessary
Basics are already present but one evolution piece
remains missing. It thins the deck without changing
Bench assembly, at the cost of revealing the deck
and consuming an unneeded Basic.
