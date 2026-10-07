# Physical attached-Energy card state

## Question

Can one state representation support attack-cost payment and post-effect Energy discards without losing physical Energy-card identity?

This result provides a small reusable adapter that does both.

Implementation: `tools/attached_energy_cards.py`  
Regression: `results/attached_energy_cards/reproduce.py`

## Representation

`AttachedEnergyCard` stores one physical Energy card with:

- a unique physical key;
- card name;
- current number of Energy units provided;
- current Energy symbols those units can satisfy;
- the card's Basic Energy name when it is a Basic Energy card.

The object deliberately separates physical identity from current provider behavior.

This matters because several established repository results now interact:

- one Special Energy card can provide multiple Energy units;
- every-type Energy can satisfy several typed requirements;
- an effect can change what type a Basic Energy provides without changing its Basic Energy name;
- a generic `discard N Energy` requirement can count units from one multi-unit card;
- a `Basic <Type> Energy` requirement selects physical cards by Basic Energy name.

## Regression 1: Regidrago with DDE + Basic Fire

The controlled state contains:

- Double Dragon Energy, two wildcard Energy units;
- Basic Fire Energy, one Fire unit.

Those two physical cards pay Regidrago VSTAR's represented `GGR` demand.

From exactly the same attached-card state:

- generic `discard 2 Energy` can be satisfied by discarding the one DDE card;
- `discard a Basic Fire Energy` selects the Basic Fire card instead;
- `discard a Basic Psychic Energy` selects nothing, even though DDE can currently satisfy Psychic requirements.

After the generic two-Energy discard, one physical Basic Fire remains. After the Basic-Fire discard, DDE remains.

This is a concrete example where the post-effect board cannot be reconstructed from a flattened unit multiset.

## Regression 2: converted Basic Grass Energy

The regression represents the rulebook's Energy Burn plus Wild Growth interaction as one physical card:

- name: Basic Grass Energy;
- Basic Energy name: Grass;
- current provider behavior: two Fire units.

That single card:

- pays a represented two-Fire attack cost;
- matches a Basic Grass Energy selector;
- does not match a Basic Fire Energy selector.

Provider type and selector identity therefore cannot share one field.

## Regression 3: DCE plus Lightning cost reduction

One Double Colorless Energy is represented as one physical card providing two Colorless units.

With a one-Lightning cost reduction, it pays an `LCC` demand. A later generic two-Energy discard removes one physical DCE card and therefore removes both units.

This is the exact physical-card boundary currently absent from the higher-level unified state's `attached_units=("C", "C")` summary.

## Operations

The adapter currently exposes:

- `attack_ready()`, which flattens provider units only for the existing exact payment solver;
- `minimum_generic_discard_outcomes()`, which solves Energy-unit requirements while returning remaining physical-card states;
- `minimum_basic_named_discard_outcomes()`, which solves Basic Energy name/card-count requirements;
- `discard_all_basic_named()`, which removes every matching Basic Energy card by identity.

This establishes a composition rule:

> flatten attached Energy cards into units only at the attack-payment boundary; retain the physical card objects in canonical game state.

## Strategic consequence

Physical card identity determines the future state after an Energy-consuming effect.

Two lines that spend the same number of Energy units can leave very different resources:

- one DDE discarded can remove two flexible units in a single physical-card loss;
- two Basic Energy cards discarded can remove the same two units while losing two attachment objects;
- a Basic-name requirement can force a specific physical Basic Energy card even when another Special Energy currently provides the requested type.

Those differences can change subsequent attacks, recovery, attachment bandwidth, and DCI-style resource valuation.

## Relationship to unified-state work

`tools/unified_state_kernel.py` currently stores attached Energy as a tuple of symbols on the Active Pokémon. That representation is sufficient for its present payment regression and insufficient for discard, movement, card-name selectors, or preserving Energy through future board-object transitions.

The attached-card object is designed as a narrow candidate boundary for that kernel. It does not modify the shared unified state in this result, which keeps the new representation independently testable and avoids coupling it to one planner before the object semantics are stable.

## Evidence classification

- Generic multi-unit discard behavior is rules-derived from the Ignition Energy ruling.
- Basic Energy name selection is rules-derived from E-39.
- The type/name split under Energy Burn plus Wild Growth is directly stated by the Advanced Player's Rulebook.
- DDE and DCE provider profiles are based on their bundled card text.
- The remaining-state regressions are deterministic computational consequences of those represented semantics.

## Limitations

The current object assumes all units provided by one card share the same symbol capability set. That is adequate for the represented DDE, DCE, and converted Basic Energy states but may need generalization if a future provider has heterogeneous per-unit semantics.

The object receives an already-evaluated provider profile. It does not yet activate or deactivate conditional Special Energy text from board state.

The discard helpers optimize for minimum physical-card loss among subsets that satisfy the maximum possible requirement. Strategic policy may prefer a different legal subset.

Energy movement, discard replacement destinations, recovery, attachment to multiple different Pokémon, and turn progression remain outside this adapter.

## Next useful work

Integrate physical attached-Energy objects into the unified board-object state while retaining the existing exact payment solver as a derived view. The first regression should attach DCE, prove `LCC` readiness with Thunder Mountain, apply a generic two-Energy discard, and verify that both payment units disappear because the single DCE physical card leaves the board.
