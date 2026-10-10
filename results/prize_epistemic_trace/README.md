# Observation-derived information partitions for Prize choices

## Question

Can we construct a player's permitted information set from **the sequence of observations they actually received**, rather than asking a simulator's policy code to supply world-specific hidden knowledge?

A finite-state prototype can. It represents a probability distribution over hidden physical Prize/top states, with a separate observation history for each player in each possible world.

## Context

Earlier results:

- [Prize top/position joint beliefs](../prize_position_top_swap/) represent hidden physical positions and the one-card deck top.
- [Selected-slot signaling](../prize_position_choice_signaling/) demonstrates Bayes' rule under a stated hidden-world-dependent choice likelihood.
- [Choice-policy admissibility](../prize_choice_policy_information/) proves that a physical-world-dependent policy is invalid when it distinguishes worlds the actor cannot observe.

This result changes how the information set is obtained: it is now **derived from recorded observation events**.

## Finite epistemic trace

`tools/prize_epistemic_trace.py` carries the group-valued physical world `(ordered Prize positions, deck top)`, its probability mass, and one observation history per observer.

The modeled event sequence includes:

1. `private_peek`: the designated observer records the actual Prize-position or top-card group in each possible world. Other players receive a public notice that an inspection occurred, with its identity hidden.
2. `select_and_swap`: the actor selects a face-down physical position according to a stochastic policy keyed **only by its recorded observation history**. The public choice is Bayesian evidence for everyone. The selected Prize identity and top card exchange.
3. `hidden_shuffle`: the eligible face-down positions are uniformly permuted in the belief distribution; all players observe only that a shuffle happened.
4. `public_reveal`: the observed card identity is conditioned across all worlds, face-up status changes, and all observers record the same public result.

The core information-set admissibility condition is enforced by construction: any two worlds sharing the actor's recorded history necessarily use the same choice distribution. That eliminates the most direct form of accidental omniscience in the preceding world-likelihood interface.

## Independent two-world experiment

Initially, the deck top is publicly known X and two face-down Prize positions contain A and B in either order with equal prior probability.

### History 1: private position inspection

The actor privately inspects Prize0, via an assumed source-authorized effect. Its private history becomes either `Prize0=A` or `Prize0=B`. The opponent only knows that an inspection occurred.

The actor chooses Prize0 for the subsequent Arc Phone-style swap with probabilities 4/5 when it saw A, and 1/5 when it saw B.

The opponent observes this choice. Its probability that the new deck top is the outgoing A becomes **4/5**. The privately informed actor remains certain of which card went to the top in each of its information sets.

An independent exact-`Fraction` two-world Bayes oracle confirms the 4/5 posterior.

### History 2: no inspection

With no private inspection recorded, both worlds share the actor's empty history. The actor can select Prize0 at any fixed probability, including 3/4, but the choice law must be identical across the two hidden mappings.

Observing the slot selection leaves the opponent's probability for outgoing A at **1/2**. Attempting to pass a policy that distinguishes the two unobserved physical worlds is rejected.

### Continuing the same trace

After the informed swap, uniformly shuffling both face-down Prize positions reduces the actor's probability of X occupying a particular slot to **1/2**. The actor retains its previously learned outgoing deck-top identity despite losing Prize-position knowledge.

A subsequent public reveal of X in position 1 makes both observers certain that position 1 contains X and marks it face up. Further swaps restricted to face-down Prize positions correctly reject position 1.

## Findings

- Observable action selection depends on the **actor's information history**.
- A public event can change an opponent's posterior even when it reveals no physical card identity.
- An actor's knowledge can remain richer than the opponent's after a swap.
- A hidden shuffle can erase current position knowledge without erasing the historical observation or necessarily changing knowledge of the outgoing deck top.
- Public reveals refine all observers' beliefs, conditional on the same actual outcome.

## Limits

This is a **small, grouped, finite-world information model**, not a full Pokémon simulator. The example stipulates that some legal previous effect permits the private position inspection; it does not implement that source card or check its legality/timing. The Arc Phone-like step operates after whatever prior source-authorized top peek is required; that card action is abstracted.

Important epistemic assumptions:

- The complete initial finite world support and prior probabilities are supplied by the caller.
- Private and public events are faithfully recorded; missing or misstated observations can still make the derived partition wrong.
- The acting player's choice policy may depend on previous observation labels. Other strategic resources (hand, lock, Supporter use) are outside the model.
- Hidden shuffle uses uniform permutations; an actual physical branch must be sampled and coupled with shared card-instance truth in a complete game engine.
- Observation histories retain public action markers but no full game chronology or cards beyond one deck top.
- Probabilities are Python floats except for independent regression-oracle comparisons to `Fraction`.

## Reproduction

`results/prize_epistemic_trace/reproduce.py` checks both histories, the independent rational posterior, shuffle and reveal continuations, actor/opponent disagreements, and invalid policy/reveal rejection. The associated focused GitHub Actions workflow runs it against the shared source module.

**Next:** compose the event-trace information partition with the [physical-instance observer bridge](../observer_positioned_prize_truth/), then investigate posterior consistency and hidden deck-top draw effects over multiple decisions.
