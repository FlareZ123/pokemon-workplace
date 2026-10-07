# K0 discard-reacquisition information bias

## Question

How much can a search planner overstate discard-and-reacquire lines when it knows the sampled Prize allocation before the player has searched the deck?

The effect appears when a card pays its discard cost before its search reveals the remaining deck. Secret Box, Ultra Ball, and the optional paid branch of Guzma & Hala all have relevant cost-before-search structure in the bundled card text.

This result isolates the information timing problem from DCI scoring. The endpoint-critical cards are symmetric, each has one replacement copy somewhere in the unknown deck-plus-Prize pool, and the search line has a compatible output for every discarded class whose replacement remains in the deck.

Implementation: `tools/k0_discard_reacquisition_bias.py`  
Regression: `results/k0_discard_reacquisition_bias/reproduce.py`

## Rules and information boundary

Secret Box `sv6-163` says it can be used only after discarding three other cards from hand, followed by the deck search. Ultra Ball likewise discards before searching. Guzma & Hala's optional two-card discard is declared when the Supporter is played, and the resulting Tool and Special Energy access is part of the later deck search.

The Advanced Player's Rulebook requires Trainer instructions to be followed in their written order. A full deck search exposes the remaining deck contents to the searcher, which can establish exact Prize composition by elimination when the list is known.

This creates a timing boundary. A first discard-before-search decision can occur under K0. A later discard decision after a full deck search can occur under K1.

## Exact symmetric model

Let:

- `U` be the current unknown deck-plus-Prize pool size;
- `P` be the number of Prize cards;
- `m` be the number of endpoint-critical discard candidates;
- `d` be the number of those critical classes that must be discarded;
- each critical class have exactly one replacement copy in the unknown pool.

A fixed symmetric K0 policy succeeds when none of its `d` selected replacements are Prized:

`C(U-d, P) / C(U, P)`.

An informed K1 policy can choose which classes to discard after learning the Prize composition. If `k` of the `m` replacement copies are Prized, the line remains feasible when at least `d` replacements are still in deck. Its success probability is:

`sum[k=0..m-d] C(m,k) C(U-m,P-k) / C(U,P)`.

The difference measures the value of information for this isolated discard choice. It also measures the optimistic bias of a planner that leaks exact hidden Prize placement into the pre-search decision.

## First-turn 52-card benchmark

After an accepted seven-card opening hand and the first draw, a player can have 52 own cards split between the deck and six face-down Prizes before any full deck search.

For two critical candidates with one replacement copy each, suppose only two cheap filler cards remain to pay a three-card Secret Box cost. One of the two critical cards must therefore be discarded.

| Candidate classes | Forced critical discards | Blind K0 success | Informed K1/oracle success | Information gap |
| ---: | ---: | ---: | ---: | ---: |
| 2 | 1 | 88.461538% | 98.868778% | **10.407240 pp** |
| 2 | 2 | 78.054299% | 78.054299% | 0.000000 pp |
| 3 | 1 | 88.461538% | 99.909502% | 11.447964 pp |
| 3 | 2 | 78.054299% | 96.787330% | **18.733032 pp** |

The second row has no information value because both critical candidates are forced discards. Prize knowledge changes decisions only when a choice exists.

## Aichi Secret Box counterexample

The regression constructs two local Aichi states with the same observable K0 hand:

- Secret Box;
- one TM: Evolution;
- one Artazon;
- one Jet Energy;
- two ordinary filler cards.

The payment must use both fillers plus either TM: Evolution or Artazon. Each endpoint-critical class has one replacement copy in the unknown pool.

In hidden world A, the replacement TM is in deck and the replacement Artazon is Prized. The successful payment discards TM and preserves Artazon.

In hidden world B, the replacement Artazon is in deck and the replacement TM is Prized. The successful payment discards Artazon and preserves TM.

The current `aichi_vileplume_secret_box._core_possible` recursion succeeds in both hidden worlds. The regression then fixes the Secret Box discard choice before exposing the deck state. Each fixed K0 choice fails in one of the two worlds.

This occurs because `_raw_state` removes sampled Prize cards from the exact `remaining` deck, and `_core_possible` receives those exact deck counts while it enumerates the Secret Box discard payment. The planner can therefore condition a pre-search discard choice on hidden Prize placement.

## Interpretation

The result identifies a policy-information leak rather than a card-rule error. Exact physical truth is useful for simulation, while legal decision policy must be restricted to information available to the player at that point.

For discard-before-search connectors, an exact planner should either carry an observer belief state through the cost decision or group hidden physical states that share the same player observation and require one common policy choice across that group.

The same distinction helps interpret transient DCI. A required copy can be highly discardable at K1 when its replacement is visibly in deck. The identical hand at K0 can carry measurable replacement risk.

## Scope and limitations

The 52-card benchmark is a local conditional model. It does not claim that the published Aichi first-turn probability is overstated by 10.407240 percentage points.

Several concrete states already reach K1 before later discard decisions. Tag Call searches the deck before a Guzma & Hala obtained through Tag Call is played. A Secret Box search also establishes full deck information before a later Guzma & Hala payment. Those later decisions do not have the same K0 uncertainty.

Jirachi's Stellar Wish creates partial deck information without revealing the full deck. A binary K0/K1 abstraction cannot fully represent that case. The repository's observer-belief kernels are the appropriate foundation for a future full correction.

## Validation

The reproducer includes:

- exact closed-form assertions for the 52-card benchmark;
- exhaustive labeled Prize enumeration on small decks;
- the two-world Aichi counterexample;
- fixed-choice regressions showing that the required Secret Box discard flips with hidden Prize placement.

## Next useful work

The next step is a belief-constrained Aichi policy audit. It should identify every first full-deck inspection, partition pre-inspection states by the player's observable information, and compare the current omniscient upper bound with the best policy shared across each observation-equivalence class.

That experiment would quantify the actual deck-level effect instead of only the local conditional gap.
