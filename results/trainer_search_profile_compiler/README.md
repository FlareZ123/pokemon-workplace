# Trainer search profile compiler: turning card text into capacity metadata

## Question

Can a conservative subset of legal Expanded Trainer search text be converted into machine-readable output profiles without collapsing timing, costs, and conditions into a generic reachability edge?

This result compiles the fixed-axis and conditional-additional search cards from `results/multi_output_search_catalog/`.

Implementation: `tools/trainer_search_profile_compiler.py`

Reproducer: `results/trainer_search_profile_compiler/reproduce.py`

## Compiled representation

Each print becomes a `CompiledTrainerSearchProfile` containing:

- card ID and name;
- action class, such as Item or Supporter;
- base search outputs;
- conditional additional outputs;
- mandatory discard of other cards, when literally present;
- optional discard cost that unlocks additional outputs;
- whether the effect discards the player's entire hand;
- a literal play condition when the card text uses `You can play this card only if...`.

Each search output has:

- a literal resource label;
- a maximum unit count, where a fixed distinct axis defaults to one.

The compiler intentionally preserves text-level labels. It does not infer strategic equivalence between labels such as `Pokémon`, `Water Pokémon`, or `Evolution Pokémon`.

## Coverage

The current compiler emits **40 legal Expanded print profiles across 16 unique names**.

The covered names are the union of:

- the 14 fixed-axis Trainer names from the catalog;
- Guzma & Hala;
- Sabrina & Brycen.

This is a deliberately narrow semantic island that can be validated exactly before wider card-text parsing is attempted.

## Representative profiles

### Arven

Action class: Supporter.

Base outputs:

- 1 Item card;
- 1 Pokémon Tool card.

This profile captures two simultaneous search axes inside one Supporter play.

### Secret Box

Action class: Item.

Mandatory state cost:

- discard 3 other cards.

Base outputs:

- 1 Item card;
- 1 Pokémon Tool card;
- 1 Supporter card;
- 1 Stadium card.

This supplies a concrete four-axis profile for the resource-constrained connector planner after the discard gate is satisfied.

The ACE SPEC deck-building constraint remains separate from this local output profile.

### Larry's Skill

Action class: Supporter.

The compiler records that the effect discards the player's entire hand before searching.

Base outputs:

- 1 Pokémon;
- 1 Supporter card;
- 1 Basic Energy card.

A fixed integer discard count would misrepresent this cost. The whole-hand flag keeps the text distinction available for a later state evaluator.

### Rosa

Action class: Supporter.

The compiler retains the literal play condition requiring an appropriate Knock Out during the opponent's previous turn.

Base outputs:

- 1 Pokémon;
- 1 Trainer card;
- 1 basic Energy card.

The profile therefore carries a high output capacity while remaining conditionally unavailable.

### Guzma & Hala

Action class: Supporter.

Base output:

- 1 Stadium card.

Conditional output after discarding 2 other cards:

- 1 Pokémon Tool card;
- 1 Special Energy card.

This card demonstrates why a single permanent connector profile is too coarse. The state can expose a Stadium-only profile or the fuller three-axis profile depending on payability.

### Sabrina & Brycen

Action class: Supporter.

Base output:

- up to 2 basic Energy cards.

Conditional output after discarding 5 other cards:

- up to 3 Pokémon of different types.

The compiler therefore supports multi-unit output on an axis in addition to several distinct axes.

## Parser boundaries

The implementation uses Python's standard regular-expression library for a small set of literal wording patterns.

It recognizes:

- coordinated article-led target lists;
- `up to N` search quantities;
- `any number of` quantities when they occur in the covered rows;
- mandatory `only if you discard N other cards`;
- optional `may discard N other cards` additional-search branches;
- whole-hand discard wording;
- literal Trainer play conditions.

The compiler raises when a covered conditional-additional row lacks a parsed optional discard cost. That makes unexpected wording changes visible instead of silently inventing a profile.

## Relation to connector allocation

This compiler supplies metadata for the deterministic engines in:

- `tools/connector_capacity.py`;
- `tools/resource_constrained_connectors.py`.

A future adapter can map each compiled card to state-valid action profiles.

For example, when Secret Box is in hand and three acceptable discard cards are available, the adapter can emit a four-axis Item action with discard cost 3.

When the cost is unavailable, the action should be absent.

For Guzma & Hala, the adapter can expose the Stadium-only output and conditionally expose the expanded profile if its optional discard cost is paid.

## Why compilation is separate from state evaluation

Card text describes potential outputs and costs.

The current state decides whether those possibilities are legal and strategically realistic.

Keeping these layers separate prevents the parser from needing to know about:

- current Supporter usage;
- lock effects;
- discardability of the actual hand;
- target cards remaining in deck;
- Bench slack;
- matchup-specific preservation;
- competing connector uses.

Those variables belong in the state evaluator and allocator.

## Validation

The reproducer asserts:

- exactly 40 compiled print profiles;
- exactly 16 unique names;
- Arven's two base axes;
- Secret Box's four outputs and mandatory three-card discard;
- Larry's Skill's whole-hand discard flag;
- Rosa's retained play condition;
- Guzma & Hala's Stadium base output, two conditional axes, and optional discard cost 2;
- Sabrina & Brycen's two-unit Energy output, three-unit conditional Pokémon output, and optional discard cost 5.

The source card pool and legality filter are inherited from the reproducible multi-output catalog.

## Limitations

This remains a conservative text compiler.

It does not parse arbitrary Trainer effects or Pokémon attacks and Abilities.

It does not normalize resource labels into a formal type lattice.

It does not resolve optional search counts, deck contents, destination zones, or whether a target satisfies a strategic requirement.

It also does not encode action-window timing beyond the Trainer subtype.

The compiler should grow by validated wording families rather than by accepting ambiguous text heuristically.

## Next useful work

The next step is a state adapter that turns a compiled profile into one or more `ResourceActionProfile` objects.

That adapter should consume:

- current action budgets;
- state-valid discard capacity;
- target availability;
- lock state.

A first concrete integration can compare Computer Search, Secret Box, Arven, and Guzma & Hala in the same multi-resource requirement state while preserving their different costs and action classes.
