# Multi-unit Energy cards and discard semantics

## Question

How often can one attached Energy card represent more than one Energy unit in paper Expanded, and how often can that distinction affect attack effects that discard Energy from the attacker?

## Rules basis

The Advanced Player's Rulebook explicitly separates Energy cards from the amount of Energy they provide.

In section C-01, Ignition Energy is the direct example. When it is attached to an Evolution Pokémon, one Ignition Energy card provides three Colorless Energy. The rulebook says that discarding that one card can count as discarding three Energy for an effect or action that requires three Energy. It also says the same card can be discarded when only one Energy is required.

Section D-08 adds type semantics for cards that provide every type of Energy. Such a card cannot be treated as if it temporarily lacks a relevant type. The Crimson Blaster example says an every-type Energy must be discarded by an instruction to discard all Fire Energy.

These rules mean a simulator needs at least two resource layers:

- physical Energy cards;
- Energy units and types currently provided by those cards.

## Current Expanded inventory

`tools/multi_unit_energy_semantics.py` scans the legal card pool for Special Energy text that can provide more than one Energy unit at a time.

The current bundled snapshot contains:

| Quantity | Count |
| --- | ---: |
| Legal multi-unit Energy print instances | 30 |
| Distinct Energy names | 13 |
| Distinct name / text / maximum-unit signatures | 14 |

The 13 names are:

- Counter Energy;
- Double Aqua Energy;
- Double Colorless Energy;
- Double Dragon Energy;
- Double Magma Energy;
- Double Turbo Energy;
- Ignition Energy;
- Neo Upper Energy;
- Rapid Strike Energy;
- Reversal Energy;
- Super Boost Energy Prism Star;
- Team Rocket's Energy;
- Triple Acceleration Energy;
- Twin Energy.

Some providers are conditional. Reversal Energy reaches three units only under its Prize and target conditions, Counter Energy reaches two under its own conditions, and Super Boost Energy Prism Star can reach four in the appropriate Stage 2 state. The inventory records the maximum unit count stated by the card text and does not assume its condition is always active.

## Attack-side exposure

The same tool scans legal attacks for generic self-discard text of these forms:

`Discard N Energy attached to/from this Pokémon`

`Discard all Energy attached to/from this Pokémon`

It finds:

| Required Energy | Distinct attack signatures |
| --- | ---: |
| 1 | 130 |
| 2 | 92 |
| 3 | 25 |
| all | 75 |
| **total** | **322** |

There are 117 fixed-count signatures requiring two or three Energy.

Those 117 signatures are the clearest place where a one-card-equals-one-Energy simplification can overstate physical card loss. A single legal multi-unit Energy card may satisfy more than one required Energy unit when its active text provides enough units.

The Ignition Energy ruling proves the phenomenon directly for a three-Energy discard.

## Why this matters for simulation

A state representation such as:

`attached_energy_count = 3`

is insufficient when discard effects, Energy movement, attachment-card recovery, Lost Zone replacement, or type-specific effects matter.

A stronger representation treats each attached Energy card as an object with state-dependent properties, including:

- physical card identity;
- current Energy-unit count;
- current Energy types;
- attachment legality conditions;
- replacement behavior when discarded;
- effects tied to that card remaining attached.

For a generic discard instruction, the player chooses Energy cards to discard. The Energy amount contributed by each chosen card determines whether the requirement has been met. This means the number of discarded cards can be lower than the number of discarded Energy units.

The reverse distinction matters too. Losing one physical Double Dragon Energy removes two provided Energy units. A card-count metric alone would understate the attacker's post-effect loss.

## Connection to Apex Dragon

This is directly relevant to `results/apex_dragon_discard_burden/`.

That result used only Basic Energy cards so every card provided one unit of one type. Double Dragon Energy is legal in the same format and, while attached to a Dragon Pokémon, provides every type of Energy and two Energy units at a time.

A future Apex Dragon burden model therefore needs Energy-card objects rather than a simple multiset of Basic Energy types. Generic discard-two instructions, typed discard instructions, and discard-all-type instructions can all behave differently once Double Dragon Energy is attached.

## Method

The Energy inventory recognizes three text families:

- `provides only N Energy at a time`;
- `provides N in any combination`;
- repeated type symbols represented in the database as strings such as `ColorlessColorless Energy`.

The attack inventory recognizes only generic self-discard text and deduplicates signatures by attack name, damage field, and normalized attack text.

The tool uses the repository's Expanded-set filter and current print-level ban overlay.

## Limitations

The maximum-unit catalog is an inventory, not a full condition evaluator. It records a card's largest textually available unit count even when that value requires a particular Pokémon, Prize state, board state, or other condition.

The attack scan excludes typed Energy discards, Energy discarded from other Pokémon, Energy moved elsewhere, optional discard wording, and effects created by Trainers or Abilities.

The parser also does not yet solve which physical Energy cards a rational player should choose when several subsets can satisfy the same requirement.

## Next useful work

The strongest extension is a subset solver over attached Energy-card objects. Given a requirement such as generic two Energy, two Darkness Energy, or one Water plus one Lightning Energy, it should enumerate legal discard subsets and preserve the player's choice among them.

That solver can then compare Basic-only and Double Dragon Energy states for Apex Dragon endpoints.
