# Exact Prize knowledge is non-monotonic

## Question

Once a player has learned the exact Prize composition, can a simulator safely treat that knowledge as permanent?

No. Legal Expanded effects can mutate the Prize zone using identities that the player does not fully observe. Exact composition knowledge can therefore become uncertain again.

Implementation: `tools/prize_knowledge_transitions.py`

Reproducer: `results/prize_knowledge_nonmonotonic/reproduce.py`

## Stronger state principle

Exact Prize knowledge is a property of the current information state.

It is not a permanent achievement attached to the game after the first full deck inspection.

For a one-card replacement of the Prize set, exact composition knowledge is preserved when the identities of both:

- the card leaving the Prize zone;
- the card entering the Prize zone

are known.

If either identity is unknown, the resulting Prize composition generally becomes uncertain unless the complete resulting set is inspected again.

## Finding 1: Arc Phone can turn exact composition into a multi-state posterior

Arc Phone `swsh11-152` reads, in the bundled card data:

`Look at the top card of your deck. You may switch that card with 1 of your face-down Prize cards. (The cards stay face down.)`

Suppose the player previously acquired exact Prize composition by inspecting the remaining deck.

The player therefore knows the set of six Prize identities, while a deck inspection alone does not reveal which identity occupies which face-down Prize position.

Arc Phone reveals the incoming top-deck card.

If the player switches it with a chosen face-down Prize position, the identity leaving the Prize zone can be any of the six known Prize cards under the ordinary unknown-position assumption.

When all six identities are treated as physically distinct, the resulting Prize set has six possible states.

A uniform six-state posterior has:

`log2(6) = 2.584962501 bits`

of entropy.

Exact composition knowledge has become uncertain again.

If duplicate card identities collapse some outcomes together, the strategic uncertainty can be smaller. The exact physical-card state still has six possible outgoing copies.

## Finding 2: full Prize redeals can create very large uncertainty

Rotom Dex `sm1-131` says:

`After counting your Prize cards, shuffle them into your deck. Then, take that many cards from the top of your deck and put them face down as your Prize cards.`

Naganadel-GX `sm6-56` has the **Stinger-GX** attack:

`Both players shuffle their Prize cards into their decks. Then, each player puts the top 3 cards of their deck face down as their Prize cards.`

These effects randomize a new Prize set from a combined pool.

If the player knew every card identity in a combined pool of size `M` before a six-card redeal, but did not know the new randomized order, the number of possible physical Prize sets becomes:

`C(M, 6)`

For a representative `M = 52` state:

`C(52, 6) = 20,358,520`

possible physical six-card Prize sets.

If all are equiprobable and physically distinct, that support has:

`24.279129350 bits`

of entropy.

The exact number of strategically distinct states can be smaller because repeated card identities merge equivalent compositions. The important result is qualitative and structural: a full redeal can expand a one-state exact belief into a very large posterior.

## Finding 3: top-card swaps can degrade knowledge even when the incoming identity is known

The Arc Phone example shows that knowing the incoming card is insufficient.

The outgoing face-down Prize identity also matters.

Mr. Mime `det1-11` has **Pantomime**:

`When you play this Pokémon from your hand onto your Bench during your turn, you may switch 1 of your face-down Prize cards with the top card of your deck.`

Unlike Arc Phone, Pantomime does not first reveal the top card.

If neither the incoming top-deck identity nor the selected Prize position's identity is known, the posterior can broaden in both directions.

Opponent effects can create the same problem. Galarian Mr. Rime's **Shuffle Dance** can switch one of the opponent's face-down Prize cards with the top card of that opponent's deck.

An information model therefore has to process Prize-zone mutations from both players.

## Finding 4: some Prize replacements preserve exactness

Prize-zone mutation does not automatically destroy information.

Examples from the same card pool show the opposite case.

Gladion first lets the player look at all face-down Prize cards, then takes one and places the visible Gladion card into the remaining Prize set.

The identities removed and inserted are known, so the resulting composition remains exact even though the remaining cards are shuffled face down.

Beast Ball and Hisuian Heavy Ball similarly inspect all face-down Prizes before a possible known-card exchange.

A replacement can therefore preserve exact composition while destroying identity-to-position knowledge.

Those are different information variables.

## Composition knowledge versus position knowledge

A stronger model should distinguish at least:

- exact Prize **composition**;
- mapping from card identities to physical Prize **positions**;
- uncertainty over composition;
- uncertainty over positions.

A full deck search can reveal composition by elimination while leaving position mapping unknown.

Town Map turns all Prize cards face up, revealing both composition and the identity at each physical Prize position.

Gladion reveals all face-down identities and then shuffles the remaining Prizes, preserving composition while removing useful position mapping.

Arc Phone can turn exact-composition/unknown-position knowledge into uncertain composition by using one of those unknown positions as the outgoing card.

This distinction affects later targeted Prize interactions.

## K1 should be a recurrent information state

The earlier K0/K1 terminology is useful as shorthand for whether exact Prize composition is known.

The card pool shows that the transition graph can contain:

`uncertain -> exact -> uncertain -> exact`

rather than only:

`uncertain -> exact`

Examples:

- full deck search acquires exact composition;
- Arc Phone can make composition uncertain again;
- a later full deck search can restore exact composition;
- Town Map can instead reveal every remaining Prize directly.

The exact-information flag should therefore be recomputed after relevant zone mutations.

## Validation

The reproducer:

- verifies the bundled texts of Arc Phone, Rotom Dex, Naganadel-GX Stinger-GX, and Mr. Mime Pantomime;
- checks that a known-incoming/unknown-outgoing six-Prize swap has six possible physical resulting sets;
- checks the `log2(6)` uniform entropy calculation;
- verifies `C(52,6) = 20,358,520` for a representative six-card redeal;
- tests the composition-preservation rule for known and unknown incoming/outgoing identities.

## Limitations

The entropy examples use physically distinct cards and uniform states.

Strategic information often cares about card names, functional variants, or line-relevant groups rather than physical copies. Duplicate identities can reduce the effective uncertainty.

Deck-order knowledge can also change the result. If another effect has revealed the incoming top card, Pantomime's uncertainty is smaller. If a player somehow knows the identity at the chosen Prize position, Arc Phone can preserve exact composition.

The rules around a specific interaction still need to be represented in the underlying state engine. This result provides the information-state requirement.

## Next useful work

The natural next step is a general Prize-belief transition kernel.

Instead of a boolean `K1` flag, it should maintain a probability distribution over line-relevant Prize compositions and update that distribution for:

- full deck inspection;
- full Prize inspection;
- partial Prize inspection;
- known-card Prize swaps;
- unknown-card Prize swaps;
- full Prize redeals;
- taking Prize cards;
- adding cards to the Prize zone.

That kernel can then feed the belief-aware line-selection model already developed in this research thread.
