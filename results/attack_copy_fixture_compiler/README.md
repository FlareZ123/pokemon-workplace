# Attack-copy fixture compiler

## Question

Can the static Expanded copy catalog be translated into executable kernel configuration without maintaining a separate hand-authored selector for every attack?

The current 30-signature snapshot now compiles into typed fixture specs.

Implementation: `tools/attack_copy_fixture_compiler.py`  
Regression: `results/attack_copy_fixture_compiler/reproduce.py`

## Coverage

The compiler maps all **30** distinct copy signatures across all **15** source classes recognized by the catalog.

The source map covers opponent Active, opponent in-play, opponent last attack, opponent hand, revealed top-10 cards, own Bench, filtered Bench families, own Dragon discard, modeled top-deck source, previous Evolutions, and opponent-controlled selection.

The resulting selector configuration also carries source filters, optional selection, selected-attack Energy gates, source-discard timing, Rule Box exclusion for Seek Inspiration, named-family predicates, subtype predicates, and choice authority.

Outer fixture metadata currently compiles the concrete pre/post events needed by Haughty Order, Hypnotic Reign, and Seek Inspiration.

## Representative compiled fixtures

**Copy Anything** becomes an opponent-in-play selector with a selected-attack Energy gate.

**Hypnotic Reign** becomes an optional opponent-hand selector with a non-GX filter and selected-source discard.

**Seek Inspiration** becomes an own-top-card selector whose source is discarded before Rule Box eligibility is checked.

**Haughty Order** becomes an optional revealed-card selector with reveal and shuffle outer events.

**Mimed Games** assigns the attack choice to the opponent. **Night Joker** uses the N's Pokémon name-family predicate. The two distinct **Recall** signatures compile to actor previous-Evolution history. **Trickster-GX** is marked as a GX outer attack.

## Why this matters

The catalog, execution-phase classifier, and executable kernel now share one translation layer.

A simulator can start from the legal card snapshot, compile a copy signature into typed execution metadata, and avoid manually reproducing the same source restrictions in bespoke code.

This also creates a validation boundary: future copy wording that introduces an unrecognized source class or phase can fail explicitly instead of silently mapping to generic behavior.

## Limitations

The fixture compiler produces selector and outer-event metadata. It does not compile arbitrary copied attack effects, damage formulas, attack-cost modifiers, or complete hidden-information procedures.

The Haughty Order reveal event still assumes the surrounding simulator materializes the revealed Pokémon objects. Previous-Evolution attacks are represented through actor history until the board-stack layer supplies them directly.
