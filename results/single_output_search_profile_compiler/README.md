# Single-output revealed Trainer search compiler

## Question

Can ordinary one-target Trainer searches such as Quick Ball be compiled from the bundled card text into the same `CompiledTrainerSearchProfile` representation used by the existing search transaction engine?

Yes, for a narrow literal family.

Implementation: `tools/single_output_search_profile_compiler.py`

Regression: `results/single_output_search_profile_compiler/reproduce.py`

## Why a separate compiler

The existing `trainer_search_profile_compiler.py` intentionally covers a validated multi-output semantic island.

This result leaves that parser unchanged.

The new compiler handles a different literal family:

- Item or Supporter;
- exactly one deck-search clause;
- exactly one searched card;
- explicit reveal;
- destination is hand;
- explicit following shuffle;
- target label already understood by the typed target allocator;
- no unmodeled effect text.

This separation reduces the chance that adding common Ball-style search wording changes the behavior of the existing multi-output compiler.

## Conservative syntax

The accepted search sentence has the structural form:

`Search your deck for a/an <supported selector>, reveal it, and put it into your hand. Then, shuffle your deck.`

The target selector must already compile through `selector_from_label()`.

Examples of supported labels include:

- Pokémon;
- Basic Pokémon;
- Evolution Pokémon;
- Trainer card;
- Basic Energy card;
- supported typed Pokémon or Energy labels.

The parser also recognizes two simple discard-cost forms:

- a play/use condition requiring another card or N other cards to be discarded;
- older wording that discards N cards and performs the search only if that discard occurred.

Generic Item/Supporter reminder text and an ACE SPEC deck rule are allowed.

A single literal play condition can be preserved in the profile for explicit state validation.

## Snapshot coverage

On the bundled paper-Expanded card pool and effective-legality baseline, the compiler emits:

- **28 print profiles**;
- **8 unique names**.

The name counts are:

| Name | Prints |
| --- | ---: |
| Ultra Ball | 13 |
| Energy Search | 4 |
| Quick Ball | 3 |
| Team Rocket's Petrel | 3 |
| Poké Kid | 2 |
| Evolution Incense | 1 |
| Master Ball | 1 |
| Skyla | 1 |

This is intentionally much smaller than the total Trainer search pool.

## Quick Ball

The three compiled Quick Ball prints are:

- `swsh1-179`;
- `swsh1-216`;
- `swsh8-237`.

Each compiles to:

- action class Item;
- one Basic Pokémon output;
- maximum one unit;
- mandatory one-card discard cost;
- the literal discard play condition retained as metadata.

This removes the manual profile that was previously needed by `trainer_search_hidden_state_bridge`.

## Ultra Ball wording migration

Thirteen Ultra Ball prints are captured across older and newer wording.

All compile to:

- Item;
- one Pokémon output;
- mandatory two-card discard cost.

Some older prints phrase the cost as an effect followed by `If you do`.

Newer prints phrase it as a play/use condition requiring two other cards.

The compiler maps both literal forms to the same local discard-cost field while preserving a play condition only when the source wording contains one.

This is a narrow contextual equivalence within the transaction representation. It does not claim that arbitrary historical wording differences can always be normalized this way.

## Deliberate exclusions

The regression confirms that several nearby families remain outside this compiler.

### Poké Ball

Poké Ball's search is gated by a coin flip.

A deterministic one-output profile would overstate availability, so it is excluded.

### Fighting Gong

Fighting Gong searches for one of two alternative categories.

The current typed selector is conjunctive and does not represent that disjunction, so the card is excluded.

### Arven

Arven has two simultaneous output axes and remains owned by the multi-output compiler.

### Earthen Vessel and Boxed Order

These search for up to multiple cards.

They belong to a multi-unit family rather than this exact-one-target island.

### Restricted selectors

Cards whose target clauses require unsupported predicates such as Rule Box status, HP thresholds, name substrings, or combined categories are also excluded.

## Validation

The reproducer asserts:

- exactly 28 profiles across 8 names;
- exact per-name print counts;
- exact Quick Ball print IDs and one-card discard semantics;
- 13 Ultra Ball profiles with two-card discard semantics;
- four Energy Search profiles;
- three Team Rocket's Petrel Supporter profiles;
- explicit absence of representative coin, disjunctive, multi-output, and multi-unit families.

## Strategic and architectural value

The important result is not the count by itself.

A common revealed search family can now enter the same typed transaction machinery from card data rather than a hand-written connector definition.

That gives downstream work a traceable path:

card text -> conservative profile -> typed target allocation -> exact discard witness -> atomic search transaction -> K1 and signaling bridge.

## Limits

The parser remains literal.

It does not compile:

- random gates;
- alternative target selectors;
- multi-unit search;
- multi-output search;
- target predicates outside the current type lattice;
- destination zones other than hand;
- arbitrary pre-search or post-search effects.

The effective-legality loader follows the repository baseline, including current ban overlays and explicit tournament-exclusion text.

## Next work

The immediate integration is to replace the manual Quick Ball profile in `trainer_search_hidden_state_bridge` with a profile obtained from this compiler.

After that, the next useful semantic islands are probably:

- deterministic multi-unit reveal-to-hand searches;
- alternative/disjunctive one-target selectors;
- selector predicates such as HP limits and name-based families.

Each should be added only with a separate exact regression corpus.
