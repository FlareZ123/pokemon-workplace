# Coarsened public search reveals require a latent selected-target class

## Question

A searcher privately inspects their deck, chooses a particular Pokémon printing, and reveals a card. Suppose an opponent model retains only the coarse name of that reveal even though the simulator tracks distinct exact print classes. Can the simulator remove the actor's known selected class from the opponent's deck pool and still obtain a correct name-only posterior?

In general, no. The opponent does not know which exact print was selected under that deliberately coarse observation. The selected print must remain a **latent variable** correlated with Prize composition and the next shuffled top card.

## Model

This is a controlled abstraction study. A real Pokémon card reveal shows the card, and the physical printing is normally observable. The name-only channel represents a computationally coarsened observation, not a claim that an opponent physically cannot see the print.

Let `s` be a hidden ordered Prize state, `t` the exact physical target group, and `o=f(t)` its projected public label. After observing `o` and completing the search-and-shuffle, the joint posterior is proportional to

`P(s) × P(t | s) × 1[f(t)=o] × P(next_top | s,t)`.

The last factor depends on which exact target was removed from deck. Therefore it must be evaluated **inside** the mixture over target classes.

Implementation: `tools/revealed_target_coarsening.py`.

The new layer reuses `condition_on_revealed_search_target` for Bayesian conditioning of the public label, then invokes `post_private_search_with_latent_target` after renormalizing the eligible target policy inside each Prize composition. The existing `LatentPrivateTargetJointBelief` representation retains the selected exact group until a later full-identity observation.

## Exact witness

Revisit the previously validated six-card pool: important singleton A, two distinct Pikachu prints (`Xa`, `Xb`), and three fillers. Two ordered Prizes are random. The searcher favors Xa when A is Prized and Xa is available; otherwise Xb when available, then Xa if needed. Both Prized means no search.

The actor's exact world has A and a filler in Prizes. The actor chooses Xa and sees the full deck; its next-top distribution is:

- P(top=A) = 0;
- P(top=Xb) = 1/3;
- P(top=filler) = 2/3.

A name-only opponent sees "Pikachu" and thus excludes the 1/15 initial Prize worlds with both prints Prized. They retain the exact selected target as latent:

- P(selected=Xa) = 1/2;
- P(selected=Xb) = 1/2;
- **P(A Prized) = 5/14**;
- **P(top=A) = 3/14**.

If this model later learns the exact print, conditioning its retained latent target yields:

| Later revealed target | P(A Prized) | P(top=A) |
| --- | ---: | ---: |
| Xa | 4/7 | 1/7 |
| Xb | 1/7 | 2/7 |

These match the independently enumerated 84-branch exact search/top oracle in `tools/revealed_print_information.py`.

## Failure mode avoided

The existing one-target hidden Trainer bridge knows the actor's exact selected physical target group. It passes that group to the ordinary reveal/shuffle belief updater, which subtracts one fixed target class from every observer's pool.

That is correct when all observers receive that exact target observation. If the modeled public label collapses Xa and Xb to the same name, subtracting Xa from every opponent world incorrectly leaks the actor's private selected printing. In worlds where Xa was Prized but Xb was selected, the fixed Xa subtraction can even make the observer's Prize belief incompatible with the remaining pool.

The new coarsening kernel subtracts Xa or Xb **conditionally on each possible world and latent selected target**. It can project away the latent identity for immediate top/Prize predictions, while retaining it for a later reveal or print-specific decision.

## Validation and scope

- Kernel: `tools/revealed_target_coarsening.py`
- Regression: `results/revealed_target_coarsening/reproduce.py`
- Workflow: `.github/workflows/validate-revealed-target-coarsening.yml`

The regression builds the full position-aware 30-ordered-Prize prior, checks actor K1 and opponent coarsened beliefs, conditions on each exact printing, and matches six posterior probabilities against independent physical branch enumeration. It also checks that an actor cannot select a target ruled out by its own supplied policy and that every policy target has a public-label projection.

The model assumes known target-choice probabilities conditional on Prize composition and a single searched target. It does not generate the policy from gameplay utility, reconcile unknown decks, or represent partial print features (artwork, language, gameplay-variant equivalence). No empirical opponent behavior is inferred.

## Next steps

Integrate this latent coarsened-label projection with the full physical Trainer search bridge under an explicitly declared observation channel. The actor's exact physical target should remain materialized, while each observer's belief represents only what their selected observation namespace reveals. Then test when coarsening is decision-sufficient for an opponent response, using a controlled utility model.
