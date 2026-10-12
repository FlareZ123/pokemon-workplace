# Pinned Twinleaf: Night Watch chooses cards instead of enforcing random selection

## Executive finding

**The Aichi champion Shadow Rider deck is not yet semantically safe to evaluate unchanged in the pinned Twinleaf engine.** Its singleton `Trevenant & Dusknoir-GX` `smp-SM217` has Night Watch, which requires **two random cards** from the opponent's hand to be revealed and shuffled into the opponent's deck. The corresponding Twinleaf class for this exact promo print instead creates an **attacker-owned `ChooseCardsPrompt`** whose result accepts every legal two-card subset.

This is an **executable semantics discrepancy**, not merely a static string mismatch. The pinned real-class test is [`simulation/twinleaf/test-night-watch-randomness.cjs`](../../simulation/twinleaf/test-night-watch-randomness.cjs), run successfully in [manual CI 38244765490](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38244765490). Source revision: `3348ebdc898f175a2ed8f999133cd13d1afd01f5`. No upstream/vendor file was changed.

## Card text and engine evidence

The bundled full English card database for `smp-SM217` prints Night Watch:

> Choose 2 random cards from your opponent's hand. Your opponent reveals those cards and shuffles them into their deck.

The paper instruction creates a chance event. With a three-card opponent hand containing distinguishable card instances, each unordered pair should have probability **1/3** if the selection is uniformly random.

At the pinned upstream class [`trevenant-dusknoir-gx.ts`](https://github.com/twinleafgg/twinleafgg/blob/3348ebdc898f175a2ed8f999133cd13d1afd01f5/ptcg-server/src/sets/08-sun-and-moon/set-sun-and-moon-promos/trevenant-dusknoir-gx.ts), the Night Watch branch:

1. obtains the opposing hand and counts `min(2, hand length)`;
2. invokes `new ChooseCardsPrompt(player, ..., opponent.hand, ..., {min: n, max: n, isSecret: true})`, where `player` is the **attacker**;
3. transfers whichever selected cards the prompt returns from opposing hand to opposing deck.

In the pinned generic [`ChooseCardsPrompt`](https://github.com/twinleafgg/twinleafgg/blob/3348ebdc898f175a2ed8f999133cd13d1afd01f5/ptcg-server/src/game/store/prompts/choose-cards-prompt.ts), `isSecret` only affects sorting/display-related handling. `decode(indices)` returns cards at the supplied indices and `validate(cards)` allows any distinct valid subset of the requested size. Neither method samples a uniformly random subset.

## Live reducer regression

The SFT instantiates the pinned card's actual `TrevenantDusknoirGX` class, actual `AttackEffect`, actual player/hand objects, and `ChooseCardsPrompt`; it invokes the real card's `reduceEffect()` method on a controlled three-card opposing hand and captures the prompt.

Confirmed:

| Actual engine outcome | Witness |
| --- | --- |
| Attack is the exact SMP 217 Night Watch | card instance `set='SMP', setNumber='217'` and attack text contains `2 random cards` |
| Attacking player owns the generated prompt | `prompt.playerId === attacker.id` |
| Prompt targets the opponent's physical hand | `prompt.cards === defender.hand` |
| `isSecret` is set | `prompt.options.isSecret === true` |
| Any two of the three cards are accepted | `decode([0,1])`, `decode([0,2])`, `decode([1,2])` each `validate() === true` |
| Actual card instances are freely specified | the resulting IDs exactly equal the caller's selected indices |

The test exercises prompt creation and choice validation. It does **not** continue through the final hand-to-deck move, since that move would not change the demonstrated root cause. It also does **not** assert that the opponent's hidden hand identities become visible to the human attacker; that would require separately auditing client serialization and bot state-view restrictions.

## Competitive impact

A decision policy selecting indices deterministically receives a materially different outcome distribution from card text's random selection. On a three-card hand, such a policy can choose the same pair in every corresponding physical state rather than producing three equiprobable outcomes. If the bot has private information it ought not possess, the effect could be even more distorted.

The winning Shadow Rider deck's Trevenant & Dusknoir-GX is a card the engine **does instantiate** at the exact intended promo print. The initial print coverage scanner erroneously marked it missing due the `PR-SM` / `SMP` set-code and `SM217` / `217` collector-number differences; that identifier-level gap is being repaired separately in `simulation/twinleaf/print-coverage.cjs`.

Resolving print identity is therefore insufficient as a criterion for reliable competitive simulation. A headless Shadow Rider versus Regidrago match using the current engine must either avoid exercising Night Watch or mark outcomes involving the incorrect branch as semantically compromised.

## Recommended research-side repair

Use a version-pinned, reviewable hook **outside the Twinleaf submodule** to make Night Watch uniformly select `min(2, opponent.hand size)` physical cards from the opponent's hand without accepting a strategic player choice. The hook must shuffle those cards into the defender's own deck, preserve revelation semantics, keep a reproducible seeded RNG stream, and be tested at hand sizes 0, 1, 2 and at least 3. In particular, sample a uniformly random *unordered subset* without replacement.

Test against the exact physical choice frequencies over all pairs in a three-card hand, then integrate the hook into the research-side headless runner before trusting match-level outcomes. Changes to the pinned Twinleaf upstream revision must trigger a renewed hook compatibility test.

This finding alone does not prove a particular winner or deck is favored by the bug. It provides an experimentally witnessed reason to distinguish engine implementation coverage from rules-faithful behavior.
