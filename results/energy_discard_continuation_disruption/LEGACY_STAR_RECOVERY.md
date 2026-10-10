# Legacy Star rescues the greedy Dragon Impact discard, at an action cost

## Research question

Does a one-card Double Dragon Energy discard actually prevent Regidrago VSTAR from ever using Apex Dragon again?

**No.** The same Regidrago VSTAR has a once-per-game VSTAR Power, **Legacy Star**, that can recover the discarded DDE. The distinction is the cost in subsequent scarce actions needed to restore attack readiness.

## Printed source

Regidrago VSTAR `swsh12-136`, in the bundled card database, has:

- **Apex Dragon**, attack cost Grass/Grass/Fire, copies a Dragon Pokémon attack from the discard pile.
- **Legacy Star**, a VSTAR Power: discard the top seven cards of the deck, then put up to two cards from discard into hand. Only one VSTAR Power may be used in a game.

The earlier [Dragon Impact continuation witness](../energy_discard_continuation_frontier/) assumes Regidrago VSTAR has DDE, Basic Grass, and two Basic Fire Energy before copying Salamence ex's attack and discarding two Energy units.

## Minimal recovery paths

Assume a deck containing at least seven inert cards before using Legacy Star, no additional Energy card in hand, no Item/Ability/attack locks, an available manual Energy attachment next turn, no intervening opponent action, and no other Energy acquisition options.

| First attack payment | Immediately next-Apex-ready? | With Legacy Star unused | With VSTAR Power already consumed |
| --- | --- | --- | --- |
| Discard DDE (one card) | No | **Yes**, by Legacy Star retrieving DDE followed by manual attach | No modeled recovery route |
| Discard Grass and Fire (two cards) | Yes | Yes, without spending VSTAR Power or hand attachment | Yes |
| Discard both Fire (two cards) | Yes | Yes, without spending VSTAR Power or hand attachment | Yes |

Therefore the one-card discard can be rescued mechanically, yet the rescue consumes **the once-per-game VSTAR Power and the normal hand attachment for the turn**. Both scarce resources remain available after the two-Basic-card payment. Legacy Star's seven-card deck mill and selection of another card create additional opportunity costs that this minimal model leaves unvalued.

This also explains why the previous exact result should be read as *post-payment Energy readiness*, with a subsequent-action qualification.

## Reproduction

`tools/energy_discard_legacy_star_recovery.py` verifies the Regidrago ability text by exact print, enumerates the source-backed four irredundant payments, and checks successful or blocked recovery under four resource regimes: all prerequisites present, VSTAR Power spent, manual attachment spent, and Ability suppressed.

Run `python -m tools.energy_discard_legacy_star_recovery` at the repository root.

## Limits

The model represents the recovery line with one specifically discarded DDE. Legacy Star can access any card in discard, and other draws, search effects, Supporters, and attachments might provide alternative routes. A real deck may contain several DDE, other attached Energy, or active lock/Stadium effects. Subsequent attacks, opponent Knock Outs, prize taking, and win probability are not simulated.

The tactical point is the **opportunity cost of restoration**. Merely marking the one-card payment "recoverable" can obscure its resource commitments.
