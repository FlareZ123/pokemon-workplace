# Harto Miki Raichu/Electrode: exact K0 Quick Ball discard policy

## Question

Before Quick Ball searches the deck, should Harto Miki's Raichu/Electrode player discard a visible Gladion or a conservative disposable card when both are available?

This is an information-state decision. Alolan Raichu is not visible yet, so the player does not know whether it remains in the deck or is among the six Prize cards. The discard is paid before Quick Ball exposes the deck.

The two choices preserve different future resources:

- discarding Gladion preserves discard stock for Ultra Ball or Computer Search;
- discarding a Special-Energy/Giratina-like disposable preserves Gladion for immediate Prize rescue if the search reveals Raichu is Prized.

Implementation: `tools/raichu_k0_discard_policy.py`  
Independent labeled regression: `results/raichu_k0_discard_policy/reproduce.py`

## Observable branch

The exact model keeps the same Harto package as the preceding agent2 work:

- 1 Alolan Raichu;
- 2 Gladion;
- 3 Ultra Ball;
- 1 Computer Search;
- 1 Forest Seal Stone;
- 2 Crobat V;
- 2 Quick Ball;
- 11 conservative disposable non-starters;
- Giratina as one disposable starter;
- 13 other setup-eligible Basic Pokémon.

After a valid seven-card opening, setup, and one ordinary draw, the pre-search observable branch requires:

- Alolan Raichu is not visible;
- Quick Ball is in the action hand;
- at least one Gladion is in hand;
- at least one conservative disposable is in hand.

Nothing in that branch conditions on the hidden Prize composition or whether a Crobat V actually survives in the deck.

The branch occurs in **3.616756%** of valid-opening states, or **3.257891%** before valid-opening conditioning.

Because the singleton Raichu is absent from the eight visible opening/draw cards, its conditional Prize probability is exactly **6/52 = 11.538462%**.

## Continuation model

The two candidate policies are evaluated over the exact same hidden worlds.

After paying Quick Ball, the model attempts to search a deck-resident Crobat V. If both Crobat V copies are unavailable, this narrow continuation fails. That happens in **4.343047%** of branch states.

When the Crobat search succeeds it establishes K1. The continuation then credits same-turn Alolan Raichu access through:

- Gladion in hand when Raichu is Prized;
- Forest Seal Stone on the searched Crobat V;
- Ultra Ball when Raichu remains in deck and its two-card payment is live;
- Computer Search with its two-card payment;
- one-card Dark Asset exposure;
- Dark Asset drawing a disposable card that activates an otherwise unpayable held Ultra Ball or Computer Search.

The Supporter window remains open until Gladion is actually played.

## Fixed policies

If the player always chooses one payment whenever the branch occurs:

| Pre-search payment policy | Same-turn Raichu access |
| --- | ---: |
| Always discard Gladion | **28.050472%** |
| Always discard a disposable | **25.868810%** |

The first fixed policy wins on average because Raichu is much more likely to remain in deck than to be Prized. Preserving discard stock keeps the two-card search channel realistic in those common deck-resident worlds.

The second policy is still strategically important because it preserves direct Gladion rescue in the rarer Prize worlds.

## Exact optimal K0 policy

There are **1,331** distinct modeled visible observations after preserving Active identity and action-hand category counts.

A simple rule matches the exact optimal observation-consistent action in every one of them:

1. If at least two Gladion are visible, discard a Gladion.
2. Otherwise, if Forest Seal Stone is visible, discard a disposable.
3. Otherwise, if at least three conservative disposables are visible, discard a disposable.
4. Otherwise, if Ultra Ball or Computer Search is visible, discard Gladion.
5. Otherwise, discard a disposable.

This rule uses only information available before Quick Ball resolves.

Its exact same-turn success is **32.988189%**.

That is:

- **+4.937717 percentage points** over always discarding Gladion;
- **+7.119379 points** over always discarding a disposable.

By branch probability mass, the optimal K0 policy chooses:

- discard Gladion: **28.949682%**;
- discard a disposable: **67.568228%**;
- either choice is tied: **3.482090%**.

The fixed Gladion-discard policy therefore wins the fixed-policy comparison even though the optimal state-dependent K0 policy discards a disposable in most visible states. The smaller set of connector-rich observations where Gladion should be discarded carries enough strategic value to reverse the fixed-policy average.

## Why the visible rule has this shape

When two Gladion are visible, discarding one preserves another copy while keeping all conservative discard stock.

Forest Seal Stone changes the tradeoff because the searched Crobat V supplies its physical host. With Forest Seal already visible, the deck-resident target can be searched without a two-card payment, while preserving Gladion covers the Prize-resident target.

Three or more disposable cards also make Gladion preservation cheap. After spending one disposable on Quick Ball, at least two remain, so Ultra Ball or Computer Search can still pay their modeled cost.

The difficult boundary is one visible Gladion, fewer than three disposables, no Forest Seal Stone, and a visible Ultra Ball or Computer Search. In those states, preserving the disposable stock can be more important because it keeps the two-card connector live or one Dark Asset disposable draw away from live.

## Information-privileged oracle

A policy allowed to see the hidden Prize state before choosing the Quick Ball payment reaches **36.909665%**.

The legal optimal K0 policy reaches 32.988189%, leaving a **3.921476-point** information advantage.

This is a concrete deck-specific example where observation-consistent policy optimization matters even after the best visible-state rule is found.

It also complements the Aichi Secret Box K0 audit elsewhere in the repository. That clean Secret Box subset happened to have enough payment slack that hidden-state privilege produced no measured advantage. The Harto Raichu branch has a real tradeoff because one candidate payment protects Prize rescue while the other protects connector payability.

## Evidence and validation

The 60-card result is an exact combinatorial expectation.

The engine:

1. conditions on a valid setup hand;
2. integrates one ordinary draw;
3. groups the six hidden Prize cards exactly;
4. keeps each visible observation separate;
5. evaluates both discard actions on every hidden physical world;
6. averages each action across worlds sharing the same observation;
7. selects the better action only after that observation-level averaging.

That last step prevents sampled Prize truth from leaking into the pre-search decision.

The reproducer independently enumerates a labeled 15-card toy deck over every valid opening, ordinary draw, disjoint Prize set, Quick Ball payment, Crobat search, and Dark Asset top card. It matches the grouped engine for state mass, observable branch mass, target-Prize mass, Crobat-search failures, both fixed policies, the optimal K0 policy, and the hidden-state oracle.

## Limits

This is still a narrow same-turn Raichu-access endpoint.

It omits other Basic draw engines, alternative Quick Ball outputs when Crobat is unavailable, Bench contention, lock effects, VSTAR opportunity cost, evolution readiness, Electrode-GX setup, later turns, ordinary Prize-taking, and richer state-dependent discard values among the twelve conservative candidates.

The visible rule is exact only for this modeled package and endpoint. It should be treated as evidence that K0 discard policy can be compressed into interpretable state features, not as a universal Raichu rule.

## Next useful work

Two continuations are especially valuable.

First, replace the binary conservative-disposable class with identity-aware payments. The visible rule should then choose among individual Special Energy, Giratina, Gladion, and other candidate cards according to continuation value rather than only choosing between two classes.

Second, add an alternative Quick Ball output when Crobat V is unavailable or strategically dominated. That would turn the current failed-search branch into an allocation problem rather than a terminal failure.
