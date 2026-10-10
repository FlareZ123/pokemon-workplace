# One physical Prize configuration, multiple observation-derived posteriors

## Question

Can an event-history-based epistemic model be synchronized with a **single realized physical set of card instances**, so that its strategic inferences are consistent with the cards that actually moved?

Yes, for the bounded Prize/top transitions under study.

## Integration

`tools/realized_prize_epistemic.py` connects:

- `PhysicalPrizeTop` from [observer_positioned_prize_truth](../observer_positioned_prize_truth/): exact unique card-instance IDs at named Prize positions and the current deck top, plus public visibility flags;
- `PrizeEpistemicTrace` from [prize_epistemic_trace](../prize_epistemic_trace/): a distribution over grouped physical worlds, with separate observation-event histories for actor and opponent;
- existing `PrizePositionTopBelief` / `ObserverPositionedPrizes` as read-only projections of each observer's current history-conditioned belief.

Every adapter state verifies that the precise **realized physical group-world and its observer observation histories** are still assigned positive mass. A transition that would make the observed history incompatible with the actual card-instance arrangement is rejected.

## Example

An exchangeable two-world prior has one physical A, one B and known top X. The realized arrangement happens to be:

`Prize0=physical-A, Prize1=physical-B, DeckTop=physical-X`.

The two players initially assign P(A at Prize0)=1/2.

1. A previously authorized **private Prize0 inspection** gives the actor P(A at Prize0)=1, while the opponent remains at 1/2.
2. The actor privately observes the top card X (as Arc Phone requires), then publicly selects Prize0 for the swap. With a documented policy of selecting slot0 at rates 4/5 when it contains A versus 1/5 when it contains B, the physical cards become `Prize0=X, Prize1=B, Top=A`. The actor knows P(Top=A)=1, and the opponent infers P(Top=A)=4/5.
3. An externally realized hidden shuffle exchanges physical Prize0 and Prize1. The material arrangement becomes `Prize0=B, Prize1=X, Top=A`. Both observers assign P(X at Prize1)=1/2 because the shuffle's actual permutation was hidden.
4. The second Prize position is publicly revealed as X. Both observers condition on the same observed identity and assign P(X at Prize1)=1; it becomes face up and unavailable for future face-down-only swaps.

The adapter exports each observer's conditioned posterior into the preexisting `ObserverPositionedPrizes` compatibility checker at successive stages, which independently requires positive mass on the material truth.

## Evidence

`results/realized_prize_epistemic/reproduce.py` reproduces each instance movement and conditional probability, ensures the two observer histories remain distinct, and checks failures for an impossible physical start, ineligible face-up swap, and invalid realized shuffle. The focused CI workflow executes this script.

This is a deterministic **witness** with an externally chosen realization of a uniformly randomized face-down Prize shuffle. Probabilities quantify the epistemic possibilities under that assumed shuffle law; a materialized simulator would sample the physical branch rather than choose a convenient permutation.

## Limits

This adapter still tracks only the Prize-zone positions and one deck-top instance, not a complete ordered 60-card deck, player's hand, discard, Prize-taking to hand, or KO timing. The physical instances are synthetic IDs and must be connected to the shared `IdentityLedger` in a full engine.

The private Prize inspection is stipulated to be authorized by an earlier card effect; the adapter does not adjudicate card legality or create such a card's play. A full producer must emit its correct observation events, and an ordinary Arc Phone play includes looking at the top card before the optional swap.

The actor policy is assumed for the test. Neither the policy nor the chosen physical arrangement is a statement about typical tournament play. The positive support invariant is necessary for consistency, while complete Bayesian common-prior reasoning depends on the supplied initial prior and faithful event transition model.

## Next work

The most valuable boundary to investigate is how drawing the exchanged top card changes observer knowledge and the conditional distribution of the **next** deck-top identity. That requires an explicitly conserved residual deck pool and forbids resetting a conditioned deck state to a naive independent hypergeometric prior.
