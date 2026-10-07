# Copied attacks and partial resolution of effect-side Energy discards

## Question

When an attack is executed through `use it as this attack`, can a resource instruction written inside the copied attack body fail while the copied attack's independent output still happens? How broad is that phenomenon in the current paper Expanded card pool?

## Rules basis

The Advanced Player's Rulebook gives two rules that combine here.

Section C-18 says a copied attack performs the selected attack's effects and damage, normally without requiring the selected attack's printed Energy cost. Its explicit Foul Play / Crimson Blaster example goes further: if the copier has no Fire Energy to discard, the Fire-Energy discard instruction is ignored and Crimson Blaster still deals its fixed 180 damage to a Benched Pokémon.

Section II-A states the general partial-resolution rule: an attack, Ability, or Trainer can still be used when part of its instructions cannot be applied; the applicable parts are followed and the impossible parts are ignored unless wording such as `Do X. If you do, do Y` makes one part conditional on another.

This creates a second copy-cost dimension beyond the selected attack's printed attack cost. A copied attack may contain an **effect-side resource instruction** that is also state-dependent when rebound onto the copier.

## Computational inventory

`tools/copied_attack_partial_resolution.py` conservatively scans legal attack text that begins with:

`Discard all ... Energy from this Pokémon`

It then separates signatures whose output explicitly scales with cards discarded from signatures with independent printed damage or later effect text.

For the current bundled snapshot plus the repository's ban overlay:

| Quantity | Count |
| --- | ---: |
| Matching legal print records | 145 |
| Distinct attack signatures | 70 |
| Output depends on number/type discarded | 12 |
| Independent-output signatures | 58 |
| Independent-output signatures discarding a specific Energy type | 11 |

The 58 independent-output signatures break down by the Energy they try to discard:

| Discard scope | Signatures |
| --- | ---: |
| All Energy | 47 |
| Lightning Energy | 6 |
| Fire Energy | 4 |
| Psychic Energy | 1 |

The specific-type group is the clearest copy interaction. A copier can legally pay its own outer attack using other Energy types, then execute a copied attack whose first instruction tries to discard a type it does not have. Under the rulebook's Crimson Blaster example, that empty discard does not erase the independent output.

## Important examples

**Armarouge, Crimson Blaster.** The attack begins by discarding all Fire Energy from the attacker and then deals 180 damage to a Benched Pokémon. The Advanced Player's Rulebook explicitly says Zoroark using Foul Play can copy Crimson Blaster with no Fire Energy attached, ignore the impossible discard, and still deal the damage. This is the canonical proof case.

**Galvantula ex, Fulgurite.** The attack has 180 printed damage, then says to discard all Energy from the attacker and applies Item lock for the opponent's next turn. In a copy model, the discard instruction binds to the copier. The output is not written as depending on how many cards were discarded.

**Umbreon ex, Onyx.** The text says to discard all Energy from the attacker and take a Prize card. This is a discrete effect rather than damage, showing why copy resolution cannot be modeled as a damage-only substitution.

**Photon Geyser** is a useful contrast. Its bonus damage is explicitly calculated for each Psychic Energy discarded in this way. If the copier has none to discard, the discard count is zero and the variable bonus does not materialize. The scan places this in the 12 discard-count-dependent signatures, outside the independent-output family.

## Strategic and modeling consequence

A copy engine needs two separate resource checks:

1. **outer attack cost**, paid to announce the copy attack unless another rule changes it;
2. **instructions inside the selected attack body**, resolved against the actual copier and current game state.

Those inner instructions are not automatically prerequisites. Whether they gate later output depends on the selected attack's wording and the general partial-resolution rules.

This matters for AMR-style evaluation. The practical cost of copying an attack is not necessarily the source card's printed cost plus every resource instruction visible in the copied text. Some instructions are losses if the copier has the relevant resource, some are empty no-ops when it does not, and some directly determine the copied output.

A simulator should therefore annotate copied attack bodies with at least:

- required announcement cost of the outer attack;
- resource-changing instructions in the copied body;
- whether later output depends on successful payment or on the quantity discarded;
- the copier's actual attached-resource state at resolution;
- output that remains independently resolvable after an impossible instruction.

## Method and boundaries

The parser intentionally uses a narrow wording family validated by the rulebook's Crimson Blaster example. It does not claim that every apparent attack-text cost elsewhere behaves identically.

Signatures are deduplicated by `(attack name, damage field, normalized attack text)`. A signature is marked discard-count-dependent when its text refers to cards or Energy `discarded in this way`. Otherwise it must have printed attack damage or text remaining after the initial discard instruction to enter the independent-output count.

This is a structural inventory. It does not claim every endpoint is realistically reachable by every copy attack, nor that discarding all Energy is strategically free. For generic `all Energy` instructions, a copier that paid an Energy-based outer cost will usually have Energy to discard. The strongest zero-discard cases arise when the copied instruction asks for a specific Energy type absent from the copier, or when some separate effect makes the outer attack costless.

## Next useful work

A natural extension is to build an attack-body dependency parser that distinguishes unconditional sequential instructions, `if you do` gates, quantity-dependent outputs, optional payments, and before-damage instructions. That would generalize this result beyond the narrow `Discard all ... Energy` family.
