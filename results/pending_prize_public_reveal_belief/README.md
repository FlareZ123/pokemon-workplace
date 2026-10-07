# Public redirected Prize cards can restore hidden correlations

## Question

If a taken face-down Prize card is privately observed by the taking player, then redirected to a public zone such as discard or the Lost Zone, should the other player's hidden-state belief be updated by that revealed identity?

Yes. Marginalizing the removed Prize identity immediately can destroy correlations that later public evidence should recover.

Implementation: `tools/pending_prize_identity_belief.py`  
Regression: `results/pending_prize_public_reveal_belief/reproduce.py`

## Rules boundary

Pokémon's official glossary states that discard piles are face up and may be inspected at any time. It also describes Lost Zone cards as face up and out of play. The Japanese official Q&A separately confirms that an opponent's Lost Zone cards may be checked.

Sources:

- https://www.pokemon.com/us/play-pokemon/about/pokemon-tcg-glossary
- https://www.pokemon-card.com/rules/faq/search.php?freeword=%E3%83%AD%E3%82%B9%E3%83%88%E3%82%BE%E3%83%BC%E3%83%B3&regulation_sidebar_form=XY

Therefore a Prize redirected by Billowing Smoke or Lost Block eventually exposes its identity to both players, even though the card began face down and the taker learned it privately.

## Failure mode in immediate marginalization

The existing observer-removal helper has two legitimate operations:

- condition an observer who sees the Prize identity, then remove the slot;
- marginalize the identity for an observer who does not see it.

The second operation becomes lossy if that same identity can later become public.

The regression uses the repository's existing Arc Phone toy state. After a public optional swap, taking the second Prize and privately observing group B makes the actor certain the top card is A. The opponent stays at P(top=A)=1/2 if the taken identity remains hidden.

If the B card then goes to discard or Lost Zone, the opponent sees B. Because the removed Prize identity was correlated with the post-swap top card, correct conditioning raises the opponent to P(top=A)=1.

If B instead enters the actor's hidden hand, the opponent correctly remains at 1/2.

## Representation

`PendingPrizeJointBelief` retains one removed Prize identity as a latent random variable alongside the joint top/remaining-Prize state.

`stage_one_pending_prize_for_observers()` conditions observers who know the identity while retaining the same latent variable for observers who do not.

`resolve_single_pending_visibility()` conditions on any destination-time observations, then removes the latent pending variable.

`destination_visibility()` currently recognizes:

- `hand`: identity remains private to the taking player;
- `discard`: identity is public;
- `lost_zone`: identity is public.

## Scope

This is a one-pending-card semantic island. Multi-card pending queues, hidden-hand tracking after hand entry, and later reveals from other hidden zones require a broader observer-relative zone model.

The key result is narrower: removing a physical Prize slot does not imply that its identity can be forgotten immediately. When a later transition can reveal that same card, its identity remains relevant evidence for correlated hidden state.

## Architectural implication

Physical disappearance from a hidden zone and information-state disappearance are different events.

A robust observer model should retain latent identity until the card reaches an information boundary where either its identity becomes public, remains privately known in another hidden zone, or can safely be marginalized because no modeled future observation depends on it.
