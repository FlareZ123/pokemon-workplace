# Public search revelations, hidden Prizes, and opponent-policy inference

## Purpose

This synthesis connects several exact computational results about publicly revealed Pokémon in **paper Expanded**, with a focus on the difference between the physical card selected, the evidence seen by an observer, the searcher's hidden information, and the response that evidence justifies.

The program grew from a concrete simulator failure: it was possible to physically search for card X and report public observation Y to the opponent's Bayesian updater. Fixing this exposed a broader question about what identity the public reveal conveys, and how a sophisticated observer should reason when the searched print is evidence about the searcher's K1-dependent decisions.

**Status:** Verified mathematical toy models, typed single-card physical Quick Ball transactions, and local card-pool provenance checks. The results are **not empirical win-rate estimates or opponent behavior measurements**.

## Core model

Let:

- `P`: hidden ordered Prize-card configuration;
- `H`: searching player's target-selection policy hypothesis;
- `T`: actual physically selected print or target class;
- `O=f(T)`: the modeled public observation, such as card name or exact print ID;
- `D`: post-search shuffled deck-top card;
- `S`: the pre-search observable board, deck counts and available action resources.

A useful observer posterior factors along these lines:

`Pr(P,H,T,D | O,S) ∝ Pr(P,H | S) Pr(T | P,H,S) 1[f(T)=O] Pr(D | P,T,S)`.

This is a modeling factorization, not a claim that an opponent's behavior is perfectly known. The selection likelihood may be uncertain and should stay in the posterior if the policy hypothesis is not identified.

It has three operational implications:

1. **Physical truth must ground public evidence.** In a revealed search, the reported print/name cannot disagree with the actual materialized card.
2. **An observer learns only the chosen information projection.** If their model intentionally merges two prints under one card name, they cannot be given the actor's exact selected print through deck-pool subtraction.
3. **Preserve correlations for later learning.** Print identity may reveal facts about opponent policy even if it currently reveals nothing about A's Prize status. Later knowledge of policy or previously hidden Prize status can make old observations informative.

## What exact observations preserve

Pokémon print ID, gameplay variant, and deck-building name have distinct uses. The existing [card_identity_resolution](../card_identity_resolution/) study records **1,289 of 3,392** Expanded-scope card names with more than one conservative gameplay variant. For example, legal `xy1-42` Pikachu has Nuzzle and Quick Attack, whereas legal `swsh7-49` Pikachu has Energize and Electro Ball.

The physical Quick Ball bridge now optionally chooses a public observation namespace. A name-level reveal projects both printings to "Pikachu"; exact-print mode derives `xy1-42` or `swsh7-49` from the materialized card. An optional source-catalog validator checks that a caller-supplied print/name pair exists and is effectively legal in paper Expanded.

A deliberate *name-only model* is a lossy observation of an actually revealed card. It is suitable for analyzing approximation error; it should not be presented as the literal physical visibility of a card whose print can be seen.

## The exact six-card witness

Start with A, two different singleton Pikachu prints, and three filler cards. Two Prize positions are random; the player searches the deck, then chooses the target according to a K1-dependent policy: take old Pikachu if A is Prized and old is accessible, otherwise take new if accessible, then old fallback. If both are Prized, the search has no target. All subsequent numbers condition on a successful search.

The 15 unordered Prize placements yield seven old-print selections, seven new-print selections, and one unavailable-target failure. There are 84 equally weighted ordered-Prize and possible shuffled-top branches after the successful searches.

| Public information under this known policy | Pr(A Prized) | Pr(next top=A) |
| --- | ---: | ---: |
| "Pikachu" name only | 5/14 | 3/14 |
| Old print `xy1-42` | 4/7 | 1/7 |
| New print `swsh7-49` | 1/7 | 2/7 |

The print adds **0.151835501362 bits** of Shannon information about A's Prize status beyond the name. For an equal-reward decision that predicts A Prized or unprized, the best name-only accuracy is 9/14 and print-aware accuracy is 5/7: **1/14** extra correct predictions. This is an abstract endpoint with well-defined payoffs, not a simulation of a real attack.

## Unknown policies change the inference

Introduce a reverse policy, which swaps the old and new print preferences. If the observer assigns the forward and reverse policies equal 1/2 probability in the six-card witness:

- old and new prints each still appear in half of successful searches;
- observing the print alone gives Pr(A Prized)=5/14 for either print;
- observing the policy alone also leaves the same Pr(A Prized);
- jointly knowing print and policy recovers 4/7 or 1/7 posteriors.

Neither print alone nor policy alone improves the equal-reward binary decision: both yield accuracy 9/14. The **joint** observation yields 5/7. The two evidence channels are complementary.

Let `a` denote the prior probability of forward policy. In this six-card toy:

`Pr(A Prized | old) = (1+3a)/7`, and `Pr(A Prized | new) = (4-3a)/7`.

The print's extra decision value is exactly

`max(0,(6a-5)/14,(1-6a)/14)`.

It is zero for **1/6 ≤ a ≤ 5/6**, even when print information is positive in Shannon terms. At `a=3/4`, there are approximately 0.03649 bits about A in the revealed print, but neither print changes the correct action of the equal-reward binary predictor.

## What changes at a real six-Prize pool size

Now condition on 52 unknown deck-plus-Prize cards after eight cards have left a 60-card deck, with six randomly face-down Prizes, and on all three singleton identities A/old/new still belonging to the 52-card unknown pool. Use the same deterministic target-choice policy and normalize over successful searches.

The exact hypergeometric model yields:

| Evidence | Pr(A Prized) |
| --- | ---: |
| Only name "Pikachu" | 11/95 = 11.578947% |
| Old print | **10/19 = 52.631579%** |
| New print | **1/76 = 1.315789%** |

Old print occurs in only 1/5 of successful searches. The rare old-print observation is strongly diagnostic, while the average equal-reward binary decision gain is **1/95 ≈ 1.052632 percentage points**.

The posterior of A after X has a general finite-population form for `U` unknown cards and `P` Prizes:

`Pr(A Prized | X) = (U-2)/(2U-P-3)`,

which exceeds 1/2 for all admissible `P>1` under this exact selection policy.

The exact companion Y posterior is

`Pr(A Prized | Y) = P(P-1)/[P(P-1)+(U-2)(U-P-1)]`.

These are mathematical consequences of the chosen rule and the hypergeometric Prize population. Nothing here establishes that real players follow this preference.

## Policy learning depends on deck-size geometry

In the six-card toy, forward and reverse policies both select each print with frequency 1/2. Repeated print observations alone cannot tell those policies apart, regardless of sample count.

In the conditional 52-card six-Prize pool, forward selects old with probability **1/5** and new with **4/5**, while reverse swaps the frequencies. With a fixed persistent policy and independent games, every observed new-print search multiplies the odds in favor of forward by **4**. From a 1/2 prior, four successive new-print observations lead to posterior forward **256/257**.

Under the 52-card model the equal-reward binary action threshold is **74/75** confidence in forward. Three prior new-print reveals give 64/65, below threshold. Four give 256/257, above threshold. The next game's print-dependent response then gains **182/24415 ≈ 0.7454 percentage points** over ignoring print.

This connects hand/deck population geometry with opponent policy identifiability. A model that only monitors Prize status while ignoring what repeated target choices imply about the opponent's policy can miss this inter-game learning channel.

## Chronology and physical correctness

A proper simulator must respect when information becomes available:

- An Item's discard payment may occur **before** the deck search, so the cost choice cannot use knowledge first obtained by that search. The separate [k0_discard_reacquisition_bias](../k0_discard_reacquisition_bias/) study documents a substantial numerical bias from clairvoyant pre-search decisions.
- A successful deck search may privately reveal K1 Prize composition to the searcher.
- The searched target becomes a public physical card and creates evidence for opponents. It must be bound to the materialized card's actual identity.
- If the observer's declared observation model coarsens multiple possible target prints to one name, the exact target remains latent in their joint belief. The model should marginalize only for current queries while retaining the target correlation for future reveals.
- Later public knowledge of a past game's Prize status must be conditioned **incrementally**. Multiplying by the full print-plus-Prize event after having already used the print evidence double counts that print. A controlled asymmetric test produces the false posterior 10/11 instead of the correct 4/5 when this error is made.

The materialized, legality-aware Quick Ball experiment conserves all physical card classes and verifies positive observer support for the actual post-search Prize/top state. Its trusted print resolver rejects invented IDs, wrong names, and effectively banned prints.

## Reusable tested components

| Question | Implementation | Validated study |
| --- | --- | --- |
| Public print/name tokens from physical cards | `tools/revealed_target_identity.py` | [trainer_search_hidden_state_bridge](../trainer_search_hidden_state_bridge/) |
| Source-backed Expanded print identity and legality | `tools/trusted_print_reveal.py` | [trusted_print_reveal](../trusted_print_reveal/) |
| Exact Quick Ball and K1/public target event | `tools/trainer_search_hidden_state_bridge.py` | [trainer_search_hidden_state_bridge](../trainer_search_hidden_state_bridge/) |
| Latent selected print under coarse name | `tools/revealed_target_coarsening.py` | [revealed_target_coarsening](../revealed_target_coarsening/) |
| Material search with coarse observer | `tools/revealed_search_coarse_physical_bridge.py` | [revealed_search_coarse_physical_bridge](../revealed_search_coarse_physical_bridge/) |
| Exact print-specific posterior and entropy | `tools/revealed_print_information.py` | [revealed_print_information](../revealed_print_information/) |
| Observation-consistent decision payoff | `tools/observation_policy_envelope.py` | [revealed_print_decision_value](../revealed_print_decision_value/) |
| Unknown opponent choice policy | `tools/latent_search_policy_belief.py` | [latent_search_policy_information](../latent_search_policy_information/) |
| Prior sensitivity and action thresholds | `tools/latent_search_policy_belief.py` | [search_policy_prior_thresholds](../search_policy_prior_thresholds/) |
| Learning from repeated events & deferred evidence | `tools/search_policy_session_learning.py` | [sequential_search_policy_learning](../sequential_search_policy_learning/) |
| Exact deck-size/Prize combinatorics | `tools/expanded_singleton_reveal_hypergeometric.py` | [expanded_singleton_reveal_hypergeometric](../expanded_singleton_reveal_hypergeometric/) |
| Scaled opponent policy identifiability | `tools/expanded_policy_identifiability.py` | [expanded_policy_identifiability](../expanded_policy_identifiability/) |

All linked computational studies have passed their own regression workflows. See each source README for counts, assumptions, test scripts, CI identifiers and limitations.

## Open questions and research priorities

1. **Real archetype policies.** Replace the synthetic Pikachu print preference with target-selection behavior on a measured Expanded deck and matchup, preserving the full K0/K1 chronology.
2. **Decision-conditional utility.** Replace binary Prize guessing with a legal response action menu including gust, Item lock, Supporter contention, energy, and exact tactical Prize targets. The relevant statistic becomes the value of information for the legal decision, not a global entropy gain.
3. **Policy uncertainty.** Infer or constrain opponent behavior using actual legal search alternatives, observed prior turns, and repeat-match evidence. Avoid treating a deterministic hypothetical chooser as universal competitive play.
4. **General visibility compiler.** Derive observer-specific public information from source-backed materialized print instances for any revealed target count and destination, including deck-to-Bench and multi-target searches. Avoid free-form strings whose relationship to card identity is unverifiable.
5. **Full physical posterior coupling.** Preserve the same physical object across future movements while allowing observers to forget selected-print details only when the actual observation channel hides them.
6. **K0 payment policies.** Constrain pre-search discard decisions to observation-equivalent states and compare them against clairvoyant search policies, while letting post-search choices use K1 when allowed.

The strongest invariant is structural: **a simulator may know a hidden physical truth that no player knows yet, and may carry more card-level detail than a chosen observer abstraction. Policies and belief updates must use only information available to the player at the relevant moment.**
