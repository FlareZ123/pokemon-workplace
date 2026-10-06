# Multi-output Trainer search catalog: concrete connector capacities in paper Expanded

## Question

How common are legal Expanded Trainer effects whose single play can obtain more than one card or more than one resource category from the deck?

This catalog supplies concrete card-pool evidence for the connector-capacity models in `results/connector_capacity_semantics/` and `results/connector_profile_access/`.

Implementation: `tools/multi_output_search_catalog.py`

Reproducer: `results/multi_output_search_catalog/reproduce.py`

## Scope and method

The scan uses the bundled English card database for sets in the repository's paper Expanded scope and applies the existing print-level ban overlay from `tools/build_expanded_legality_baseline.py`.

It examines Trainer cards whose text contains `search your deck for`.

The classifier is deliberately conservative and text-structural. It records four overlapping classes:

| Class | Meaning |
| --- | --- |
| `fixed_axes` | one search clause explicitly names several coordinated target categories |
| `numeric_multi` | the wording explicitly allows two or more searched cards |
| `unbounded_multi` | the wording explicitly says `any number of` |
| `conditional_additional` | the same play may perform an additional search after a condition or optional cost |

These classes describe search-output shape. They do not by themselves establish that every target is useful, legal, or simultaneously available in a particular game state.

## Snapshot counts

The conservative scan finds **202 legal Expanded Trainer print records across 90 unique card names** in the union of the four classes.

| Classification | Print records | Unique card names |
| --- | ---: | ---: |
| Fixed distinct axes | 37 | 14 |
| Numeric multi-card search | 161 | 73 |
| Conditional additional search | 3 | 2 |
| Unbounded multi-card search | 2 | 2 |

The categories overlap. The union counts therefore cannot be recovered by summing the rows.

## Fixed-axis search cards

The 14 unique names captured by the fixed-axis rule are:

| Card | Literal search shape captured by the catalog |
| --- | --- |
| Arven | an Item card and a Pokémon Tool card |
| Colress's Tenacity | a Stadium card and an Energy card |
| Dawn | a Basic Pokémon, a Stage 1 Pokémon, and a Stage 2 Pokémon |
| Hilda | an Evolution Pokémon and an Energy card |
| Irida | a Water Pokémon and an Item card |
| Korrina | a Fighting Pokémon and an Item card |
| Larry's Skill | a Pokémon, a Supporter, and a Basic Energy |
| Piers | an Energy card and a Darkness Pokémon |
| Rosa | a Pokémon, a Trainer, and a basic Energy card |
| Secret Box | an Item, a Pokémon Tool, a Supporter, and a Stadium |
| Steven | a Supporter and a basic Energy card |
| Team Aqua's Great Ball | a Team Aqua Basic Pokémon and a basic Energy card |
| Team Magma's Great Ball | a Team Magma Basic Pokémon and a basic Energy card |
| Volkner | an Item card and a Lightning Energy card |

These effects are important for connector modeling because a single play can create several different resource channels together.

A graph that expands each card into independent target edges loses the shared-action structure. A capacity profile can preserve it.

For example, the cataloged Secret Box wording supports four Trainer-category outputs in one use after its own play conditions are satisfied. That differs structurally from an any-card search that chooses only one target.

## Conditional additional-search cards

The literal scan captures two names:

- `Guzma & Hala`;
- `Sabrina & Brycen`.

These are useful examples of **state-dependent output profiles**.

For Guzma & Hala, the base search obtains a Stadium. Its optional discard condition can unlock additional Tool and Special Energy outputs. A state compiler should therefore expose different profiles depending on whether the optional cost is realistically payable.

This is preferable to assigning the card one permanent capacity value.

## Unbounded multi-search cards

The scan captures:

- `Energy Search Pro`;
- `Precious Trolley`.

Their wording contains `any number of`, so a fixed small integer capacity is an inadequate abstraction.

A useful state representation should instead constrain output by the targets remaining in the deck, available board space where relevant, and the exact effect text.

## Numeric multi-card search

The largest class contains 73 unique names.

This class includes effects that can retrieve several cards from the same broad category as well as effects whose selected cards may differ within that category.

That distinction matters.

Searching two Pokémon does not automatically create two independent strategic axes. It provides two units of Pokémon-search capacity. Whether those units satisfy separate requirements depends on the current line.

The connector profile should therefore be derived from both card text and the current target-requirement vector.

## Why this matters for associativity models

The repository's capacity experiments show that edge breadth and realized output capacity are separate properties.

The catalog demonstrates that higher-capacity search is common enough in Expanded to deserve explicit representation.

Two opposite graph errors are possible.

A graph can overvalue a capacity-one any-card search by spending the same physical use on several targets.

It can also undervalue a genuine multi-output effect by treating one card play as if it could satisfy only one target edge.

A typed capacity profile handles both cases.

## Relationship to action costs and timing

This catalog intentionally does not decide whether a card is currently playable.

A complete state-derived profile needs separate checks for:

- Supporter action availability;
- discard or hand costs;
- Item, Supporter, or other lock effects;
- target cards remaining in the searchable zone;
- Bench capacity for effects that place Pokémon into play;
- other card-specific conditions.

For example, a multi-output Supporter may have excellent capacity while being unusable after the current Supporter play has already been spent.

Similarly, Secret Box can expose a rich output profile only when its discard cost and other play requirements are satisfied.

## Validation

The reproducer asserts the complete snapshot summary:

- 202 print records in the union;
- 90 unique names in the union;
- 37 fixed-axis prints across 14 names;
- 161 numeric-multi prints across 73 names;
- 3 conditional-additional prints across 2 names;
- 2 unbounded prints across 2 names.

It also asserts the exact 14 fixed-axis names, the two conditional-additional names, the two unbounded names, the captured Secret Box four-axis clause, and the classification of Guzma & Hala.

The catalog is deterministic for the bundled database and legality overlay.

## Limitations

This is a literal text classifier rather than a complete card-text parser.

It may miss semantically equivalent effects with unusual wording.

The `fixed_axes` heuristic deliberately excludes coordinated alternatives using `or`, because those represent choice rather than simultaneous output.

The `numeric_multi` class says that several cards can be searched. It does not infer whether the selected cards occupy distinct strategic roles.

The catalog currently covers Trainer search effects only. Pokémon attacks and Abilities can also have multi-output capacity.

Some search effects have conditional branches, optional costs, placement destinations, or action timing that require a richer state model.

## Next useful work

The next useful step is a profile compiler for the conservative fixed-axis and conditional-additional cases.

For each card, the compiler can emit abstract output channels plus state predicates. Those predicates can then be evaluated by the typed access engine before the profile is handed to the resource-constrained allocator.

That would convert card-pool text into state-valid finite-capacity search actions while keeping mechanical legality, cost realism, and connector allocation as separate layers.
