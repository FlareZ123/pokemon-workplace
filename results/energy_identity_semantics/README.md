# Energy identity versus provided Energy semantics

## Question

Can an Energy card's physical identity be safely collapsed into the Energy types and units it currently provides?

No.

The Advanced Player's Rulebook explicitly distinguishes the **card named Basic <Type> Energy** from the type of Energy that card currently provides. Effects can change what type an attached Energy provides without changing the card's name. Special Energy can likewise provide a type without becoming a Basic Energy card of that type.

This result turns that distinction into an auditable state representation and inventories how broadly named Basic Energy references occur in the current legal Expanded snapshot.

## Rules basis

Section E-39 explains that wording such as `Basic Grass Energy` requires a card **named** Basic Grass Energy.

The same section gives the decisive interaction:

- Charizard's **Energy Burn** makes all Energy attached to Charizard Fire Energy instead of their usual type.
- Meganium's **Wild Growth** applies to cards named Basic Grass Energy and makes each of them provide two Energy.
- A Basic Grass Energy attached to that Charizard therefore remains a Basic Grass Energy card while providing **two Fire Energy**.
- The rulebook separately states that such a converted Basic Water Energy does not become Basic Fire Energy for Charizard's **Burn Brightly**.

The general Energy rules also separate Basic Energy from Special Energy. Double Dragon Energy can provide every Energy type while attached to a Dragon Pokémon, but it remains a Special Energy card.

These are distinct state variables:

1. physical card identity and name;
2. Basic versus Special Energy category;
3. current Energy types provided;
4. current number of Energy units provided;
5. conditions governing those provided types and units.

## Card-pool inventory

`tools/energy_identity_semantics.py` scans the current legal paper-Expanded snapshot for card text containing a named `Basic <Type> Energy` reference.

It finds:

| Quantity | Count |
| --- | ---: |
| Print-text instances with a named Basic Energy reference | 344 |
| Distinct normalized texts | 152 |
| Attack instances | 156 |
| Ability instances | 144 |
| Rule-text instances | 44 |

References by Basic Energy name are:

| Basic Energy name | Print-text instances |
| --- | ---: |
| Darkness | 18 |
| Fighting | 53 |
| Fire | 78 |
| Grass | 49 |
| Lightning | 68 |
| Metal | 18 |
| Psychic | 40 |
| Water | 43 |

No legal reference to `Basic Fairy Energy` appears in this snapshot under the scanner's exact wording.

This inventory is intentionally text-based. Reprints contribute separate print-text instances while identical normalized text contributes once to the distinct-text count.

## Type-override effects

The scanner also finds attached-Energy type override wording of the form `All Energy attached ... are <Type> Energy instead of their usual type`.

There are **4 legal print instances** representing **3 distinct card/effect signatures**:

- Hydreigon, **Dark Aura**, appearing in two legal prints, converts Energy attached to itself to Darkness;
- Charizard, **Energy Burn**, converts Energy attached to itself to Fire;
- Typhlosion, **Blazing Energy**, temporarily converts Energy attached to the player's Pokémon to Fire.

These effects demonstrate why a simulator cannot use a single `energy_type` field as both the card's selector identity and its current payment capability.

## Named-Basic multiplicity effects

Six legal print instances, representing five distinct signatures, both refer to a named Basic Energy and modify how much Energy it provides:

- Gardevoir, **Psychic Mirage**, two legal prints;
- Meganium, **Wild Growth**;
- Charizard, **Burn Brightly**;
- Venusaur, **Jungle Totem**;
- Galarian Weezing, **Energy Factory**.

These effects select physical Basic Energy cards by name/category and then alter unit provision. They make the identity/type/unit split relevant even without Special Energy.

## Executable semantic regressions

The tool defines a minimal `AttachedEnergyState` with:

- `card_name`;
- `is_basic`;
- `units`;
- `provided_types`.

Two controlled regressions demonstrate the separation.

### Basic Grass under Energy Burn plus Wild Growth

The represented attached card is:

- card name: Basic Grass Energy;
- category: Basic;
- units: 2;
- current provided type: Fire.

The model therefore returns:

- matches `Basic Grass Energy`: yes;
- matches `Basic Fire Energy`: no;
- can satisfy a Fire attack-cost symbol: yes;
- can satisfy a Grass attack-cost symbol: no;
- current provided units: 2.

This is the state described by the rulebook's Meganium/Charizard example.

### Double Dragon Energy

The represented DDE is:

- card name: Double Dragon Energy;
- category: Special;
- units: 2;
- current provided types: every type.

It can satisfy a Psychic attack-cost symbol while failing a selector for `Basic Psychic Energy`.

This is the same distinction that corrected the Apex Dragon / Photon Geyser burden result in `results/apex_dragon_special_energy_burden/`.

## Modeling consequence

A robust Energy object should not infer card identity from current provider behavior.

A useful minimum representation is:

```text
physical card identity
  -> Basic/Special category
  -> printed card name
  -> current provider profile
       - number of units
       - types each unit can satisfy
       - activation conditions
```

Selectors such as `Basic Grass Energy` operate on the identity/name layer. Attack-cost payment operates on the current provider profile. Effects that say `discard 2 Energy` operate on supplied units while ultimately discarding physical cards. Effects that say `discard all basic Psychic Energy` require the identity layer as well.

This also means a semantic compiler should preserve qualifying words such as `Basic` rather than normalizing them away as descriptive noise.

## Relationship to existing results

This result extends several existing Energy findings:

- `energy_action_budget/` separates Energy units from attachment-action bandwidth.
- `multi_unit_energy_semantics/` separates physical Energy cards from unit count.
- `apex_dragon_special_energy_burden/` now separates Basic/Special card category from current Energy type.
- `typed_energy_access/` proves typed attack readiness, but its current `attached_units` summary still loses physical Energy-card identity and therefore is not sufficient for effect-side discard transitions.

Together these results suggest that Energy state should be represented as attached card objects rather than only as a multiset of Energy symbols.

## Evidence classification

- The identity/type distinction is rules-derived from E-39 and the Energy-card rules.
- The Charizard/Meganium semantic regression directly implements the rulebook's stated interaction.
- The Double Dragon regression combines its bundled card text with the rules distinction between Basic and Special Energy.
- The 344-reference, type-override, and multiplicity inventories are computational results from the bundled legal snapshot under the repository's current ban overlay.

## Limitations

The scanner recognizes exact English `Basic <Type> Energy` wording and a narrow family of explicit type-override text. It is not a complete semantic parser for every historical Energy interaction.

The `AttachedEnergyState` is deliberately minimal. It does not yet encode replacement effects, Energy-specific discard destinations, target legality, duration, source Ability state, or multiple simultaneous type-changing effects.

The card-pool counts describe this bundled snapshot and legality overlay. They are not universal historical counts for every Expanded card database revision.

## Next useful work

The strongest next step is to replace bare `attached_units` tuples in higher-level state kernels with physical attached-Energy objects carrying identity and provider profiles. That would let one state engine answer both attack-payment questions and post-attack discard/movement questions without recompiling incompatible summaries.
