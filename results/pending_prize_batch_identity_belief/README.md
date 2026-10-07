# Multi-Prize pending identity beliefs preserve per-card reveal order

## Question

Can observer-specific hidden-state correlations survive a simultaneous multi-Prize award when each exact pending card may later become public or remain hidden independently?

Yes. The pending batch must retain each selected Prize identity as its own latent variable.

Implementation: `tools/pending_prize_batch_identity_belief.py`  
Regression: `results/pending_prize_batch_identity_belief/reproduce.py`

## Motivation

Official Japanese Pokémon Card Q&A for Lost Block plus Billowing Smoke says that after a two-Prize Knock Out, the Prize-taking player looks at both Prize cards and may choose Lost Zone or discard separately for each card.

That ruling requires identity and destination decisions at per-card granularity after the simultaneous Prize selection.

The earlier one-pending belief result showed why public discard/Lost Zone entry can restore hidden correlations. This result extends the same idea to an exact batch identified by physical pending-instance IDs.

## Representation

`ObserverPendingPrizeBatchBeliefs` stores:

- an ordered tuple of exact pending instance IDs;
- one observer-relative probability distribution over top-deck group, remaining Prize groups, and pending-group tuple.

`stage_pending_prize_batch_for_observers()` removes several Prize positions together and can condition observers who learn the selected identities.

`resolve_pending_instance_visibility()` addresses a specific physical pending instance, conditions whichever observers see its identity at destination time, and removes only that latent variable.

After every pending card has resolved, `project_completed_batch()` returns to the ordinary observer-indexed top/Prize belief type.

## Correlation witness

The regression reuses the Arc Phone toy state.

The actor takes two exact pending cards whose true groups are X and B. The actor sees both. The opponent initially has:

- P(top=A)=1/2;
- P(first pending=X)=4/5;
- P(second pending=B)=1/2.

If B becomes public first, the opponent immediately infers top=A with probability 1, while X remains latent.

If X becomes public first, the opponent still has P(top=A)=1/2. Revealing B second then raises P(top=A) to 1.

When B instead enters the actor's hidden hand and only X becomes public, the opponent finishes at P(top=A)=1/2.

## Finding

The final posterior can depend on which pending identities become public, while intermediate posteriors can additionally depend on reveal order.

This is distinct from physical Prize-order choice. A simulator needs:

1. exact physical pending-instance identity;
2. observer-relative latent card-group identity;
3. destination visibility for each pending card;
4. sequential conditioning as those cards resolve.

## Scope

The module models one simultaneous batch. It does not yet attach destination effects or nested extra-Prize barriers directly to `PendingPrizeBatchOrder`.

Hidden-hand identity is marginalized after hand entry in this island. A fuller future model should preserve it if later hand revelation must update the same correlated belief state.
