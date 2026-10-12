# A prize-aware, typed Secret Box -> Quick Ball -> Basic Pokémon line

## Mechanism and scope

The [shared-hand Item quota result](../joint_item_payment/) demonstrates that an Item's presence and separately affordable payment can exaggerate reachable lines. This extension identifies and evaluates a **specific typed line** in the same hypothetical deck:

`Secret Box (discard 3 F) -> fetch Quick Ball from deck -> Quick Ball (discard 1 more F) -> fetch a Basic Pokémon from deck`.

This correctly distinguishes Secret Box's printed search domain (**one Item, Tool, Supporter and Stadium**) from Quick Ball's printed Basic Pokémon search domain. It requires a *total of four distinct safe filler cards* already held, with a Quick Ball and a Basic Pokémon each remaining in the unprized deck after initial setup. If Quick Ball is already payable from the hand, the longer route does not contribute a *new* Basic-search endpoint.

Printed, corpus-marked Expanded-legal anchors: Quick Ball `swsh1-179` (one discard), Ultra Ball `swsh9-150` (two discards; direct Pokémon search), Secret Box `sv6-163` (three discards; one ACE SPEC permitted). Restricted deck groups remain B12 starter Basics, Q4 Quick Ball, U4 Ultra Ball, S1 Secret Box, F8 designated safe filler and P31 protected. Initial seven-card hand must contain a Basic; one becomes Active, six Prizes are chosen uniformly and one ordinary turn draw is made going second. Exactly one Basic is placed, with extra Basics in hand protected. All meaningful strategic opportunity costs, Item lock, draw powers, other search connectors and future turns are outside the model.

**Direct Basic-search endpoint:** a held Quick Ball with at least one safe filler, or a held Ultra Ball with at least two, and at least one unprized Basic remaining in the deck.

**Secret bridge endpoint:** a held Secret Box with at least four safe filler, plus at least one Quick Ball and one Basic remaining in the unprized deck. A successful bridge is an *increment* only when the direct endpoint was unavailable from the initial hand.

## Exact conditional probabilities

| Discard-safe filler count | Direct Basic access | Additional Secret Box bridge | Combined |
| ---: | ---: | ---: | ---: |
| 4 | 18.536146% | 0.000424% | 18.536570% |
| 8 | **34.143020%** | **0.025236%** | **34.168255%** |
| 12 | 46.367985% | 0.149778% | 46.517763% |
| 20 | 61.329371% | 0.983321% | 62.312692% |
| 28 | 67.159183% | 2.558605% | 69.717788% |

In the benchmark F8 state, Secret Box is *individually* payable in **0.453336%** of Basic-valid starts from the [earlier quota study](../joint_item_payment/), but it contributes only **0.025236 percentage points** of additional immediate Basic Pokémon search through the concrete Quick Ball chain. This is largely the hand-budget consequence of paying four distinct discarded cards and competing against already available direct Balls.

A naive graph that treats Secret Box as immediate direct Basic search would instead mistake the larger [34.398664% any-Item payability](../joint_item_payment/) for this particular endpoint. The actual typed, prize-aware two-step endpoint here is **34.168255%**. The gap combines discarded-card quota, alternate source overlap, exact target categories and Prize constraints. It must not be interpreted as Secret Box's overall card value, since its primary multiaxis Trainer-search effects are not scored.

## Exact Prize-aware calculation

The [source solver](../../tools/secret_box_basic_bridge.py) conditions on each accepted opening category histogram, removes one Basic from hand into the Active Spot, then considers the marginal next natural draw. Conditional on that physical draw, **the six Prize cards are uniformly distributed among the remaining 52 unseen cards** (for this N=60, h=7 snapshot). This permits exact inventory feasibility without simulating all 6-card Prize placements in the large deck.

For `r` unseen cards of a target category among `M` unseen cards and `p` uniformly placed Prizes, the probability that **every** target copy is Prized is

\[
P(\text{all target copies Prized}) =
\frac{\binom{M-r}{p-r}}{\binom{M}{p}}
\]

when `r <= p`, and zero when `r > p`. The probability that both a Basic and Quick Ball remain in deck follows from inclusion-exclusion on those two disjoint categories. This treats information and physical inventories correctly, with no assumption of revealed Prizes.

An [independent labeled physical oracle](reproduce.py) enumerates legal small opening hands, each disjoint Prize allocation, and every possible next natural draw. It independently checks **all five** event probabilities, including nonzero bridge contributions, in three toy configurations. A 32-point protected-to-safe-filler sweep checks monotonicity and crosschecks against the prior three-Item gate. [Manually dispatched Windows CI](../../.github/workflows/validate-agent2-secret-box-basic-bridge.yml) verifies it without per-commit workflows.

## Interpretation and next steps

The bridge is a legal *candidate sequence* if all the stated conditions hold, but the study stops at acquiring a Basic. It does not prove an attacker is powered, evolved, safe from a lock, or worth prioritizing over Secret Box's other search outputs. A realistic evaluator should assign marginal value to the particular Basic target and benchmark the opportunity cost of consuming Secret Box and four fillers against competing Trainer-package actions. A future deck-specific step should replace the artificial F class with exact-print cards and state-dependent discard policy.
