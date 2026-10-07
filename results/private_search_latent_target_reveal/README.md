# Private unrestricted-search targets can remain latent until later revelation

## Question

Can the existing private unrestricted-search belief result preserve enough information to update the opponent if the exact searched hand card is revealed later?

Yes, by retaining the hidden target group as a latent variable instead of permanently marginalizing it.

Implementation: `tools/private_search_latent_target_belief.py`  
Regression: `results/private_search_latent_target_reveal/reproduce.py`

## Relationship to existing work

Agent38's `private_search_target_belief.py` correctly marginalizes the private target when producing the opponent's immediate post-search top/Prize belief. That is the right observable projection while the searched card remains hidden.

The new layer preserves the same target as latent evidence. Projecting the latent target away reproduces agent38's existing actor and opponent `TopPrizeJointBelief` masses exactly.

No existing transaction API is changed.

## Five-card witness

The regression reuses the published five-card model:

- singleton modeled groups A and B;
- three filler cards;
- one face-down Prize;
- one private searched target;
- one shuffled top;
- uniform hidden target selection among physically available deck cards.

Before later revelation, the opponent has:

- P(target=A)=1/5;
- P(target=B)=1/5;
- P(target=filler)=3/5;
- top marginal A=1/5, B=1/5, filler=3/5.

The actor's exact world has filler Prized and private target A, giving actor top probabilities A=0, B=1/3, filler=2/3.

## Later public reveal

When the exact private target A is later revealed to the opponent, the latent belief can condition on that same card identity.

The opponent then learns A was available in deck rather than Prized. Their posterior becomes:

- target A with probability 1;
- Prize A with probability 0;
- Prize B with probability 1/4;
- Prize filler with probability 3/4;
- top A with probability 0;
- top B with probability 1/4;
- top filler with probability 3/4.

Those updates cannot be reconstructed from the already-marginalized top/Prize belief alone because the target-to-hidden-state correlation has been discarded.

## Finding

Private movement and permanent information loss are separate operations.

A simulator may expose a marginalized observable belief to another player while retaining a latent exact-card variable internally. If a later public event reveals that card, the model can condition on the retained variable and recover the correct posterior.

## Scope

This result tracks one grouped private search target. It does not yet attach the latent variable to the exact materialized hand instance from the Computer Search transaction, nor does it model multiple private hand cards.

The natural next integration is to key the latent target to the materialized hand instance ID so card movement and observer evidence share the same physical referent.
