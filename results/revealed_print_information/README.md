# Public search reveals can carry print-level Bayesian information

## Question

Does conditioning an opponent only on the **name** of a revealed searched Pokémon preserve all information that the actual public reveal could convey?

No, even when the revealed printings have the same deck-building name. A searcher can choose between two distinct legal printings using private post-search knowledge. Seeing the selected printing can signal that private information.

## Concrete card-pool grounding

The bundled paper-Expanded card pool records two legal Basic Pokémon named Pikachu:

- `xy1-42`, with Nuzzle and Quick Attack;
- `swsh7-49`, with Energize and Electro Ball.

Their names are identical and their printed attacks differ. A Quick Ball search reveals the actual selected Basic Pokémon to the opponent, so a model capable of representing the disclosed card should retain the printing/variant information when it matters.

This result uses a six-card **toy hidden pool**, not a valid standalone sixty-card deck or an empirical metagame estimate. It isolates how public target selection changes an observer's posterior.

## Exact six-card experiment

The initial unknown deck-plus-Prize pool contains a singleton strategic card A, one copy of each Pikachu print, and three distinct filler card instances. Two ordered Prize slots are sampled uniformly, leaving four cards in deck. The searching player fully inspects the deck and executes one deliberately synthetic target-selection policy:

1. If A is Prized and the `xy1-42` Pikachu is available, take that print.
2. Otherwise take `swsh7-49` if available.
3. Otherwise take `xy1-42` if available.
4. If both are Prized, do not search.

The policy is a controlled behavioral hypothesis. The player's private K1 information makes the chosen printing informative; no claim is made that this would be an optimal Pokémon line.

Across `C(6,2)=15` equiprobable unordered Prize worlds:

- 7 choose `xy1-42`;
- 7 choose `swsh7-49`;
- 1 has both Pikachu prints Prized and chooses no target.

Each successful search leaves three deck cards. Enumerating ordered Prize positions and every possible post-shuffle top gives 84 labeled branches.

## Exact opponent posteriors

Condition on a successful search for a Pikachu. Compare what the opponent can infer using only the common name against using the actual revealed print.

| Public observation | P(A is Prized) | P(shuffled top is A) |
| --- | ---: | ---: |
| Name "Pikachu" only | **5/14** | **3/14** |
| Print `xy1-42` | **4/7** | **1/7** |
| Print `swsh7-49` | **1/7** | **2/7** |

The print channel gives **0.151835501362 bits** of additional information about the binary event "A is Prized", conditional on knowing that a Pikachu was selected. This value follows from binary entropy and is computed on the exact enumerated distribution.

The two printed-card conditional probabilities average to the name-only probability, since each print has 7 of the 14 successful initial worlds. The name-only projection irreversibly merges behaviorally distinct observations.

## Why this matters for simulation

The earlier single-target hidden-search bridge now protects against a contradictory public observation by requiring its supplied observation name to agree with the materialized card name. That is useful for its existing name-level abstraction.

A later, print-aware bridge should derive the public observation **from the materialized instance's trusted print/variant class**, rather than accepting an arbitrary unrelated string or assuming the name is always sufficient. The `card_identity.py` and `card_class_namespace.py` research provides explicit print, conservative variant, and name identity relations.

Print-specific evidence is potentially valuable for identifying protected tech choices, recognizing an archetype, and predicting which singletons are missing from the searcher's accessible deck. Its actual strategic importance depends on the opponent's beliefs about the searcher's policy and the real matchup.

## Reproduction

- Kernel: `tools/revealed_print_information.py`
- Regression: `results/revealed_print_information/reproduce.py`
- CI: `.github/workflows/validate-revealed-print-information.yml`

The regression checks the two exact legal Pikachu records and their differing attacks; independently counts the 15 unordered Prize configurations; enumerates 84 ordered-Prize and shuffled-top branches; checks all rational posteriors; verifies the entropy result; and rejects impossible selected prints or zero-probability observations.

## Limits and next work

The observation model assumes the opponent can distinguish the revealed physical print. It does not assume they correctly know the player's private target-selection policy; the Bayesian numbers are conditional on the stated policy. It uses distinct physical instances with a uniform initial Prize law and does not include mulligans, deck-building copy limits, lock effects, discard payments, or opponent actions.

The next integration is an explicit public observation token compiled from a physically materialized card with a declared identity namespace. That token should be validated against print- or variant-level target-selection policies. A controlled comparison could then show when name-level coarsening is decision-sufficient and when it changes the best opposing response.
