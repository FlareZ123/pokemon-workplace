# Physical instance truth and observer-specific Prize/top beliefs

## Question

How can a simulator carry separate player knowledge about face-down Prize positions while preserving one physical board truth during Arc Phone, private top-card peeks, face-down shuffling, and public Prize revelations?

The repository already has the foundation:

- `observer_prize_beliefs/`: player-indexed, count-only posterior updates;
- `prize_position_belief/` and `prize_slot_visibility/`: positional memory and visibility;
- `prize_top_swap_belief/`: a correlated Prize/top posterior after an acting-player swap;
- `prize_position_top_swap/`: finite joint priors and actor/opponent-specific evidence updates.

This result adds an explicit **physical-instance witness** and a consistency-checked multi-observer transition adapter. It uses source-grounded Arc Phone and face-down Prize behavior.

## Implementation

`tools/observer_positioned_prize_truth.py` has two immutable records:

- `PhysicalPrizeTop`: ordered exact card-instance IDs for Prize positions, one actual top-deck instance ID, face-up flags, and a map from physical instance IDs to strategic model groups. Multiple physical cards may map to the same group.
- `ObserverPositionedPrizes`: one physical truth and independently maintained `PrizePositionTopBelief` distributions indexed by observer.

Every valid adapter state checks that **each observer's posterior assigns positive probability to the actual grouped physical world** and agrees on public face-up geometry. An observer believing something incompatible with the physical truth is rejected. This is a necessary coherence invariant, rather than a complete proof that all observers' beliefs come from one common prior.

The adapter exposes:

- `peek_top(observer_id)` for private observations visible to only one participant;
- `swap(position, observed_choice_likelihoods=...)` for one public physical move and optional observer-specific policy-likelihood inference;
- `shuffle(sources)` for one realized hidden uniform face-down shuffle, represented as a physical permutation and as a marginalized distribution for observers;
- `reveal(position)` for a public reveal conditioned on physical identity, making that position face-up and ineligible for later face-down-only swaps.

The caller must sample the physical shuffle permutation uniformly if modeling a fair shuffle. The adapter accepts a realized permutation to make tests deterministic.

## Reproducible physical witness

Five distinct physical cards `A,B,F1,F2,F3` are grouped into modeled A, modeled B, and three filler instances. Start with:

- exact physical Prizes: `F1, B`;
- physical top card: `A`;
- both positions face down;
- both observers sharing the same exchangeable prior over ordered two-Prize/one-top deals.

After actor privately peeks top A:

- actor `P(top=A)=1`;
- opponent `P(top=A)=1/5`.

After actor swaps that top into Prize position zero:

- exact physical Prizes are `A, B`, actual top `F1`;
- actor `P(A at Prize0)=1`;
- opponent `P(A at Prize0)=1/5`.

Apply a realized hidden physical swap of the two Prize positions, interpreted as one outcome of a uniform shuffle. The actual Prizes become `B, A`, while:

- actor assigns `P(A at Prize1)=1/2`;
- opponent assigns `P(A at Prize1)=1/5`.

Reveal actual Prize position one. Both observers condition on public A and agree `P(A at Prize1)=1`; position one becomes face up, so a later Arc Phone-like face-down-only swap at that position is rejected.

The regression also rejects a prior that assigns zero probability to the actual top card, rejects an impossible physical permutation, checks an optional swap-policy likelihood update, and confirms exact instance movement.

## Finding

The following invariants can be maintained separately:

1. **Material identity:** exactly which physical card instance occupies each zone position.
2. **Observer knowledge:** which physical configurations are consistent with each participant's evidence.
3. **Public geometry:** which individual Prize positions are face up and eligible for a given effect.
4. **Action evidence:** what an opponent infers from the acting player's observable decisions.

This representation permits both players to disagree about hidden cards without creating inconsistent *physical* truth.

## Limits

- This is a small cross-zone adapter over the existing grouped information kernel. It does not synchronize the complete `IdentityLedger`, resolve a game turn, or implement the full deck order.
- The physical card instance IDs are synthetic and should be mapped to authoritative card-instance objects by a full simulation.
- A common physically possible world is a **necessary, insufficient** condition for coherent Bayesian beliefs. The adapter does not prove common-prior consistency or strategic common knowledge.
- Inferences from player choices require explicit likelihood assumptions. A player policy depending on other unmodeled hidden information cannot be compressed into top-group-only likelihoods without loss.
- A fair hidden shuffle must choose its realized permutation uniformly; the adapter does not supply randomness itself.
- This test is an information-state invariant and source-grounded transition witness, not a claim about competitive match win rates.

## Reproduction

`results/observer_positioned_prize_truth/reproduce.py` contains the deterministic witness and adversarial rejections. Its focused GitHub Actions workflow runs against the repository's shared state modules.
