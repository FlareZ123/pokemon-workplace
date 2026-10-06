# Quick Ball -> Tapu Lele-GX -> Gladion: setup-trigger and discard realism

## Question

How realistic is the familiar Expanded connector:

Quick Ball -> Tapu Lele-GX -> Wonder Tag -> Gladion

once setup rules, Prize cards, Quick Ball's discard cost, and the requirement to play Tapu Lele-GX from the hand onto the Bench are modeled together?

This result finds two distinct reductions that a plain graph misses:

1. Quick Ball needs an acceptable discard card.
2. Tapu Lele-GX can be consumed by setup when it is the only starter in the accepted opening hand, preventing Wonder Tag from being preserved for the turn.

Implementation: tools/quick_ball_lele_access.py

Reproducer and exhaustive validation: results/quick_ball_lele_access/reproduce.py

## Modeled package

The baseline deck contains:

- 60 cards;
- 6 Prize cards;
- 7-card accepted opening hand;
- 12 setup-eligible starters total;
- exactly 1 Tapu Lele-GX among those starters;
- 11 other setup-eligible starters;
- 4 critical non-starter singletons;
- 2 non-starter Gladion copies;
- 4 Quick Ball copies;
- a variable pool of non-starter cards considered acceptable Quick Ball discards;
- all remaining cards as other non-starters.

The model conditions on at least one critical singleton being Prized, because that is the state where Gladion rescue matters.

Bench space, Items, Abilities, and Supporters are assumed available.

## Setup-trigger loss

Tapu Lele-GX's Wonder Tag requires the Pokémon to be played from the hand onto the Bench during the turn.

During setup, a player with at least one Basic Pokémon must choose an Active Pokémon before the game begins.

Therefore, when Tapu Lele-GX is the only setup-eligible starter in the accepted opening hand, it must be put into play for setup. It cannot be preserved in the hand and later manually Benched to trigger Wonder Tag.

When the opening contains Tapu Lele-GX plus another starter, the model assumes skilled play selects another starter as the Active Pokémon and leaves Tapu Lele-GX in the hand.

This creates a connector-specific interaction with mulligan conditioning. Tapu Lele-GX helps make the opening legal while sometimes losing the very hand-to-Bench trigger for which the deck included it.

## Access lines

Current-window Gladion access succeeds through any of three routes:

1. a Gladion copy is already in the accepted opening hand;
2. Tapu Lele-GX is preserved in the hand because another starter is available, then is manually Benched and Wonder Tag finds an unprized Gladion in the deck;
3. Tapu Lele-GX remains in the deck, Quick Ball is in the hand, an acceptable discard is available, and Wonder Tag can find an unprized Gladion after Quick Ball puts Tapu Lele-GX into the hand.

A Prized Tapu Lele-GX cannot satisfy routes 2 or 3.

If every unexposed Gladion is Prized, Wonder Tag cannot manufacture access to one.

## Quick Ball discard policy

The strict model counts only the explicitly designated disposable-card pool as valid Quick Ball fodder.

An optional policy also allows spare Quick Ball copies beyond the one being played to count as discardable.

This parallels the earlier discard-cost AMR work. The number of cards in hand is insufficient information by itself; the identities and strategic discardability of those cards matter.

## Main result

With four critical singletons, two Gladion, one Tapu Lele-GX, four Quick Ball, and 12 total starters:

| Dedicated disposable non-starters | Strict access | Spare Quick Ball copies may be discarded | Naive model that ignores setup-trigger loss |
| ---: | ---: | ---: | ---: |
| 4 | 38.626850% | 41.247915% | 41.540185% |
| 8 | 44.615074% | 46.372717% | 47.528410% |
| 12 | 48.569324% | 49.697934% | 51.482660% |
| 16 | 51.061415% | 51.748257% | 53.974751% |
| 20 | 52.543426% | 52.933980% | 55.456762% |
| 24 | 53.361937% | 53.565232% | 56.275273% |

All values are conditional on a valid opening and at least one modeled critical card being Prized.

## Finding 1: the discard gate is material

At only four dedicated disposable cards, the strict first-window access rate is **38.626850%**.

At 12 disposable cards it rises to **48.569324%**.

At 24 it reaches **53.361937%**.

The same nominal four Quick Ball copies therefore represent very different Gladion access depending on the hand's discardable composition.

This is a deck-specific version of the earlier Ultra Ball and Secret Box discard-payability result.

## Finding 2: spare search copies partly relieve the discard gate

Allowing extra Quick Ball copies to serve as discard fodder raises access by:

- **2.621066 percentage points** with 4 dedicated disposable cards;
- **1.757643 points** with 8;
- **1.128610 points** with 12;
- **0.686842 points** with 16;
- **0.390554 points** with 20;
- **0.203294 points** with 24.

Spare-copy discardability matters most when the dedicated disposable pool is small.

This remains a state-dependent assumption. A second Quick Ball can itself be valuable for another Basic Pokémon.

## Finding 3: ignoring setup-trigger loss adds a stable overestimate

Across every disposable-pool size in the table, pretending that an opening-hand Tapu Lele-GX is always available to fire Wonder Tag overstates access by **2.913336 percentage points**.

The effect is stable here because the setup event depends on starter composition, while the Quick Ball discard pool is a disjoint non-starter category.

This is a useful correction for first-turn simulators that condition on a valid Basic-containing opening but then treat every support Pokémon found in that opening as still available in the hand.

## Why this matters beyond Tapu Lele-GX

The same semantic issue can arise for other setup-eligible Basic Pokémon whose desirable Ability triggers when they are played from the hand onto the Bench during the turn.

A simulator needs to distinguish:

- a card drawn in the opening seven;
- a card left in the hand after setup choices;
- a card placed Active during setup;
- a card placed on the Bench during setup;
- a card later played from the hand onto the Bench.

All five states can originate from the same opening seven while having different trigger behavior.

## Relation to K0 and setup conditioning

The earlier valid-start Prize result showed that mulligan conditioning changes Prize priors.

This result shows a second consequence of setup conditioning: the accepted opening hand is not the same object as the actionable turn-one hand.

Some opening cards are moved into play before the game begins. Whether a specific card remains available for a trigger depends on the composition of the other starters and the player's setup choices.

That distinction belongs in any detailed K0 or first-turn model.

## Relation to AMR and connector domination

Even when the exact connector is mechanically live, it can still be strategically expensive.

Quick Ball consumes:

- itself;
- one discardable card;
- a Bench slot through Tapu Lele-GX.

Tapu Lele-GX also becomes a two-Prize board liability.

The model assumes those costs are acceptable. A deck optimizer should apply DCI, Bench contention, matchup risk, and competing Quick Ball targets before assigning full strategic value to the line.

## Validation

The reproducer exhaustively enumerates a small labeled deck over every accepted opening-hand subset and every disjoint Prize subset.

It checks four policy combinations:

- strict discard policy with setup-trigger loss;
- spare Quick Ball discard policy with setup-trigger loss;
- strict discard policy while deliberately ignoring setup-trigger loss;
- spare Quick Ball policy while deliberately ignoring setup-trigger loss.

The closed-form combinatorial result matches the exhaustive labeled enumeration to floating-point precision in all four cases.

## Limitations

The current model stops at the accepted opening seven.

It does not model an additional draw before the first usable Supporter window, going-first versus going-second Supporter timing, other draw effects, Pokémon search for Quick Ball itself, bounce/replay effects, Ability lock, Item lock, Bench saturation, or alternative support Pokémon.

Disposable cards are a binary DCI class. The model does not decide which real deck cards belong in that class.

Tapu Lele-GX is a singleton in the model. Other copy counts can be added later if a deck-specific question requires them.

## Next useful work

The strongest extension is to model the same line after one or more random draws and then compare it directly with the idealized clean-out model.

That will measure how much the clean-out abstraction overstates a real compound connector once its required target, discard fodder, setup-trigger preservation, and Prize topology are all represented.
