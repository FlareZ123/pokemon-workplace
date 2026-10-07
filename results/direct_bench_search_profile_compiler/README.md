# Direct-to-Bench Basic-Pokémon search compiler

## Question

Can a common family of deck-search effects that put Basic Pokémon directly onto the Bench be compiled from the bundled card text without conflating them with reveal-to-hand search effects?

Yes, for a deliberately narrow literal family.

Implementation: `tools/direct_bench_search_profile_compiler.py`  
Regression: `results/direct_bench_search_profile_compiler/reproduce.py`

## Why this deserves a separate semantic island

The existing Trainer-search compilers intentionally model searches whose payload moves from deck to hand. That destination is strategically meaningful. A searched Basic Pokémon in hand can later be played from hand, while a Pokémon put directly onto the Bench enters through a different game transition.

The advanced rulebook also gives direct Bench placement its own capacity semantics in C-11: a search-to-Bench attack can resolve while the Bench is full and then fail to place anything, whereas a Trainer card or Ability with that effect cannot be used with a full Bench. If fewer slots remain than the effect could fill, only the available number of Pokémon can be placed.

For those reasons, changing the destination on an existing hand-search profile would erase real rules and AMR constraints.

## Conservative syntax

The compiler accepts only effects whose complete search body is one of these shapes:

- `Search your deck for a Basic Pokémon and put it onto your Bench. Then, shuffle your deck.`
- `Search your deck for N Basic Pokémon and put them onto your Bench. ...`
- `Search your deck for up to N Basic Pokémon and put them onto your Bench. ...`

Both current `Then, shuffle your deck.` wording and the older `Shuffle your deck afterward.` wording are recognized.

The current semantic island covers:

- Pokémon attacks whose entire attack text is the direct-Bench search body;
- Trainer cards whose one search rule is the direct-Bench body, allowing only generic Item/Supporter reminder text and at most one literal play condition.

The profile preserves source kind, action class, attack name and Energy cost when applicable, maximum search units, whether `up to` was explicit, and a simple Trainer play condition.

## Snapshot coverage

Against the current effectively legal paper-Expanded card snapshot, the compiler emits **101 print-level profiles across 76 unique card names**.

| Source | Maximum | Explicit `up to` | Profiles |
| --- | ---: | --- | ---: |
| Attack | 1 | no | 40 |
| Attack | 2 | no | 6 |
| Attack | 2 | yes | 42 |
| Attack | 3 | yes | 7 |
| Trainer | 1 | no | 5 |
| Trainer | 2 | yes | 1 |

The Trainer profiles are five Nest Ball prints plus Battle VIP Pass.

Battle VIP Pass retains its separate first-turn play condition rather than compiling into an unrestricted two-Basic search.

## Historical wording boundary

Three older Emolga prints provide a useful regression boundary. Their Call for Family attack says to search for `2 Basic Pokémon` rather than `up to 2`, and uses the older shuffle wording. The compiler records a maximum of two while preserving `explicit_up_to=False` and the printed one-Colorless attack cost.

The distinction remains available to downstream rules logic even though hidden-zone deck-search rules can separately affect how many matching cards are actually found.

## Deliberate exclusions

Several strategically important neighboring cards are excluded because their selectors or additional effects require semantics beyond this island:

- Buddy-Buddy Poffin: HP predicate;
- Professor Oak's Setup: distinct-type constraint;
- Dream Ball: Prize-origin play timing and unrestricted Pokémon selector;
- Single Strike Style Mustard: style predicate plus conditional draw;
- Furisode Girl: optional switch after placement;
- Precious Trolley: unbounded `any number` output;
- Egg Incubator: coin gate and alternate Trainer destination.

These are candidates for separate validated compilers or richer selector support.

## Strategic consequence

A search graph that collapses `deck -> hand` and `deck -> Bench` into the same “access to Basic Pokémon” edge is mechanically lossy.

Direct Bench placement consumes Bench capacity immediately, can be barred by full-Bench Trainer/Ability rules, and does not constitute playing that Pokémon from the hand. Hand-search routes can preserve a later choice of whether and when to commit a Bench slot and may enable effects that specifically trigger from hand play.

The compiler therefore treats destination and source action class as first-class metadata rather than incidental text.

## Validation

The deterministic reproducer checks:

- 101 total profiles across 76 names;
- the exact source/maximum/`up to` breakdown above;
- all five Nest Ball print IDs;
- Battle VIP Pass's exact first-turn condition;
- the older fixed-two Emolga wording and attack cost;
- deliberate exclusion of representative nearby semantic families.

## Limits

This result compiles text into a direct-Bench search profile. It does not yet execute the profile against the canonical physical board/identity state.

In particular, downstream execution still needs to combine:

- exact searchable target copies in deck;
- current Bench capacity;
- source-specific full-Bench legality;
- exact card materialization from deck into an in-play board object;
- action-window costs such as ending the turn after an attack;
- hand-play trigger suppression for direct placement;
- deck shuffle and observer-relative information effects.

A useful next step is a conserved direct-Bench executor that materializes selected Basic Pokémon into `StackBoardMaterialState` and regression-tests Nest Ball against a full Bench and a hand-trigger Pokémon.
