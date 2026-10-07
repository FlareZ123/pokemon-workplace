# Historical Trainer name-reuse divergences

## Question

Which unresolved historical Trainer cards can be proven non-equivalent to a legal Expanded same-name card through a small, explicit game-state witness?

## Result

Eight same-name families yield direct functional divergences across 16 historical prints. Each proof uses a concrete state difference that can be checked from card text and current rules.

| Name | Historical prints | Axis | Concrete divergence |
| --- | ---: | --- | --- |
| Master Ball | 5 | material transition | Historical text only inspects seven cards; current Master Ball searches the deck for a Pokémon |
| Pokémon Breeder | 3 | event semantics | Historical text evolves a Basic into a Stage 2; current text draws two cards and heals |
| Pokémon Center | 3 | target domain | Historical text heals all of your damaged Pokémon; current Stadium heals one Benched Pokémon |
| Max Revive | 1 | material transition | Historical text puts a Basic from discard onto the Bench; current text puts a Pokémon from discard on top of the deck |
| Revive | 1 | material transition | Historical text revives a Basic with damage counters; current text revives it without that damage |
| Devolution Spray | 1 | material transition | Historical text discards removed Evolution cards; current text returns the highest Stage to hand |
| Power Plant | 1 | event semantics | Historical Stadium exchanges Basic Energy; current Stadium removes Abilities from Pokémon-GX and Pokémon-EX |
| Magnetic Storm | 1 | target domain | Historical text changes Resistance only for Psychic and Fighting attackers; current text removes Resistance from every Pokémon in play |

These witnesses are sufficient to establish state-model non-equivalence. The result promotes all 16 source print IDs into the resolver's `known_non_equivalent` evidence set.

## Method

`tools/trainer_name_reuse_divergence.py` stores eight explicit cases. Each case identifies historical source prints, one legal Expanded same-name target, a divergence axis, card-text invariants, and a concrete witness state.

The collector validates that:

1. every source and target still has the expected name;
2. the target belongs to the Expanded set universe and is effectively legal;
3. the card-text fragments supporting the witness remain present.

The tool does not infer divergence from edit distance or general text similarity.

## Witness details

### Master Ball

Put the only desired Pokémon below the top seven cards. The historical Master Ball cannot take it. Current Master Ball searches the deck and can take it. The two effects therefore have different reachable hand transitions.

### Pokémon Breeder

Use a state with a matching Basic in play and Stage 2 in hand. Historical Pokémon Breeder can create an evolved Pokémon. Current Pokémon Breeder performs draw and healing.

### Pokémon Center

Use a state where only the Active Pokémon is damaged. Historical Pokémon Center can remove that damage. Current Pokémon Center's Stadium effect selects a Benched Pokémon.

### Max Revive

Use an open Bench, a Basic Pokémon in the discard pile, and two Energy cards in hand. Historical Max Revive puts the Basic onto the Bench after its cost. Current Max Revive places a Pokémon from the discard pile on top of the deck.

### Revive

Revive the same Basic Pokémon. The historical card places damage counters equal to half its HP. The current card puts the Basic onto the Bench without that damage.

### Devolution Spray

Devolve an evolved Pokémon. The historical card discards the removed Evolution card or cards. The current card puts the highest Stage Evolution card into the hand.

### Power Plant

Use a state with a relevant Pokémon-GX Ability and no useful Energy exchange. Current Power Plant suppresses the Ability. Historical Power Plant provides a Basic Energy exchange action.

### Magnetic Storm

Use a non-Psychic, non-Fighting attacker whose damage would be reduced by Resistance. Current Magnetic Storm removes Resistance. Historical Magnetic Storm only bypasses Resistance for Psychic and Fighting attackers.

## Evidence classes

**Card-text fact.** The source and target fragments are taken from the bundled card database and checked by the regression.

**Current legality fact.** Each comparison target is a directly legal Expanded print under the repository legality baseline.

**State-model proof.** Every family has an explicit reachable state where the historical and current same-name cards permit different transitions or effects.

**Methodological judgment.** A concrete distinguishing state is enough to classify state-model non-equivalence. Tournament policy remains a separate evidence question unless official guidance directly addresses a pair.

## Reproduction

Run `python -m results.trainer_name_reuse_divergence.reproduce`.

The regression validates all 16 source prints and cross-checks that the reprint resolver classifies each as `known_non_equivalent`.

## Limitations

This is a curated semantic island. It covers only eight families whose divergence can be expressed with a short direct witness. Other unresolved same-name Trainer cards still need separate analysis.

## Next work

Audit the remaining Trainer review families for exact optionality, information, destination, and target-scope differences. PokéNav and Pokégear 3.0 are promising because their historical and current texts differ in whether taking a found card is optional.
