# Apex Dragon effect-side discard burden

## Question

When Regidrago VSTAR uses Apex Dragon, how much Energy can a copied Dragon attack force Regidrago to discard through the copied attack body itself?

This result isolates one concrete state: Regidrago has exactly three Basic Energy cards attached, two Grass and one Fire. That state satisfies Apex Dragon's printed Grass, Grass, Fire attack cost without relying on Special Energy or attack-cost modifiers.

## Rules basis

The Advanced Player's Rulebook says that `use it as this attack` executes the chosen attack's effects and damage without normally requiring the chosen attack's own printed Energy cost.

The same rulebook allows partial resolution when part of an attack cannot be applied. Its Foul Play and Crimson Blaster example explicitly says that a copied Fire-Energy discard can fail while the independent attack output still happens.

These rules make the copied attack's effect-side Energy discard a separate burden from Apex Dragon's announcement cost.

## Result

`tools/apex_dragon_discard_burden.py` scans legal Dragon Pokémon attacks whose normalized text starts with a self-Energy discard instruction.

For the current snapshot:

| Quantity | Count |
| --- | ---: |
| Matching legal print instances | 71 |
| Distinct attack signatures | 38 |
| Deterministic discard signatures parsed | 35 |
| Choice or variable discard signatures | 3 |

Under the exact Basic-Energy state `Grass, Grass, Fire`, the 35 deterministic signatures divide as follows:

| Forced Energy cards discarded | Signatures |
| --- | ---: |
| 0 | 5 |
| 1 | 11 |
| 2 | 7 |
| 3 | 12 |

Four of the five zero-discard signatures have output independent of a `discarded in this way` quantity:

- Hydreigon, **Dragonblast**, 140 damage, with `Discard 2 Darkness Energy attached to this Pokémon.`
- Zygarde, **Core Enforcer**, 150 damage, with a Darkness plus Fairy discard instruction.
- Kingdra, **Dragon Blast**, 150 damage, with a Water plus Lightning discard instruction. Two distinct text signatures in the bundled card pool express this attack.

In the modeled Regidrago state, none of those requested Energy types is attached. The discard instruction therefore contributes zero forced discarded cards. The printed damage is independent of the missing discard.

Ultra Necrozma-GX's **Photon Geyser** is the fifth zero-discard signature. Its Psychic discard is also zero in this state, but the bonus damage explicitly depends on cards discarded in this way. It therefore remains a useful contrast rather than an independent-output example.

## High-burden endpoints

Twelve deterministic signatures discard all three cards in the modeled state. Examples include:

- Black Kyurem-EX, **Black Ballista**, 200 damage and discard 3 Energy;
- Garchomp V, **Sonic Strike**, 220 damage to one opposing Pokémon and discard 3 Energy;
- Hydreigon BREAK, **Calamity Blast**, 150 Active damage plus 50 to two Benched Pokémon and discard 3 Energy;
- Kyurem, **Trifrost**, 110 damage to three opposing Pokémon and discard all Energy;
- Mega Latias ex, **Illusory Impulse**, 300 damage and discard all Energy.

These endpoints can be tactically strong while creating a large post-attack resource loss.

## Strategic consequence

A source card's printed Energy symbols do not describe the full resource burden when Apex Dragon copies that attack.

Two separate questions matter:

1. What does Regidrago need to announce Apex Dragon?
2. What does the chosen attack body later instruct the actual Regidrago to discard?

Typed discard instructions can collapse when the relevant type is absent. Generic discard instructions remain expensive because the attached Grass and Fire cards are valid targets.

This makes copied endpoint selection state-sensitive. A 150-damage attack with a source-side Water plus Lightning discard can preserve the entire modeled Regidrago attachment, while a similar generic three-Energy discard can empty it.

## Method

The model keeps only legal Expanded Dragon Pokémon under the repository's current ban overlay. It matches attacks whose first normalized sentence begins with `Discard` and refers to `this Pokémon`.

The parser supports:

- discard all Energy;
- discard a fixed number of generic Energy cards;
- discard a fixed number of one named Energy type;
- discard one card of each of two named Energy types.

Three choice or variable signatures are preserved outside the deterministic burden distribution. These include Dragon Burst's Fire-or-Lightning choice and Savage Wing's player-chosen Fire discard count.

The scenario evaluator uses Basic Energy cards only. Each card has exactly one type, so typed-discard counting is unambiguous.

## Limitations

The `Grass, Grass, Fire` state is a deliberately controlled scenario. It is not a claim about every Regidrago list or every live game.

Special Energy can change the result because one attached card may provide different types or multiple Energy units. Additional attachments also change generic discard burden and can change typed burden.

The scan covers first-sentence self-discard instructions. It does not include later conditional discards, optional discards that appear after other clauses, self-discard instructions using different wording, or costs created by external effects.

The output is a structural resource analysis. It does not rank the endpoint attacks by matchup value, damage efficiency, Prize mapping, or the opportunity cost of the Dragon card occupying a deck slot.

## Next useful work

A useful extension is a typed Energy-card state evaluator that models Special Energy identities as cards rather than just Energy units. That would allow Apex Dragon endpoint burden to be evaluated under Double Dragon Energy, Rainbow-style providers, and mixed Basic/Special attachment states.
