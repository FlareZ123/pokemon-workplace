# Harto Miki Raichu/Electrode: two Battle Compressors load the maximum Energy package

## Question

The Prize-state ALS result shows that five attached cards can provide 14 Lightning Energy after Extra Energy Bomb when the comeback condition is active.

Can Harto's four Battle Compressor copies physically load that exact five-card package from a clean deck into the discard pile using two Item plays?

Yes.

Implementation: `tools/battle_compressor_transaction.py`  
Regression: `results/raichu_battle_compressor_loading/reproduce.py`

## Card text and transaction semantics

Battle Compressor Team Flare Gear says:

`Search your deck for up to 3 cards and discard them. Shuffle your deck afterward.`

The new count-state transaction preserves:

- the Item-play channel;
- the physical Battle Compressor leaving hand for a temporary resolving-Trainer zone;
- an exact 1-to-3-card deck selection;
- selected cards moving deck -> discard;
- Battle Compressor moving resolving zone -> discard;
- per-card-class conservation.

The count-state layer does not represent shuffled deck order. That remains a separate topology concern.

## Exact loading witness

Start with:

- two Battle Compressor in hand;
- 4 Reversal Energy in deck;
- 4 Counter Energy in deck;
- 3 Unit Energy LightningPsychicMetal in deck.

First Compressor:

`Battle Compressor -> 3 Reversal Energy to discard`

Second Compressor:

`Battle Compressor -> 1 Reversal + 1 Counter Energy to discard`

The second Item deliberately selects only two cards, which is legal because Battle Compressor says `up to 3`.

Final Energy package in discard:

- 4 Reversal Energy;
- 1 Counter Energy.

That is exactly the five-card package that maximizes the post-self-KO Electro Rain ceiling.

## Connection to the Prize-state switch

At a representative tied 3-3 Prize state:

1. the two Compressors load the five Energy cards;
2. Extra Energy Bomb attaches those five cards to Alolan Raichu;
3. Electrode-GX is Knocked Out;
4. the opponent takes two Prizes and moves from 3 remaining to 1;
5. Reversal and Counter Energy become active;
6. the attached package provides `4 * 3 + 1 * 2 = 14` Lightning Energy units;
7. Electro Rain can convert those units into fourteen 30-damage placements.

Conditional ceiling:

**420 damage from the five cards loaded by the two Compressor plays.**

## Why two Compressors matter

From a clean discard pile, one Battle Compressor can move at most three physical cards.

Extra Energy Bomb's maximum package needs five physical Energy cards.

A one-Compressor-only line therefore cannot load the entire package from zero pre-existing discarded Energy.

Two Compressor plays have six cards of nominal deck-to-discard capacity, and the `up to 3` wording lets the second play stop at two rather than spend an unnecessary sixth target.

This is an example of multi-copy connector capacity rather than one connector being treated as an unlimited edge.

## Competing uses remain real

The witness chooses all five targeted cards for the Electro Rain package.

Battle Compressor has other high-value outputs in this deck. Giratina is an obvious example because Distortion Door can use the discard pile.

The result therefore proves reachability of the five-Energy loading line. It does not claim that spending both Compressor plays entirely on Energy is always optimal.

A stronger planner should compare:

- loading the maximum Energy package;
- using one output on Giratina;
- loading fewer Energy because some are already discarded;
- reserving a Compressor for another future line.

## Mechanical failure boundaries

The regression additionally verifies:

- Item lock rejects Battle Compressor;
- a zero-card selection is rejected at the Item-transaction layer because it would create no represented card-text effect;
- every represented card-class total remains conserved across both Compressor plays.

## Relation to earlier results

This result closes one enabling edge left open by `raichu_electro_rain_als/`.

The two findings now form a concrete line:

`2 Battle Compressor -> 4 Reversal + 1 Counter in discard -> Extra Energy Bomb -> self-KO Prize switch -> 14 Lightning units -> 420 Electro Rain damage`

The remaining hard questions are access and opportunity cost: whether the deck can assemble the two Compressor plays, both Stage 1 Pokémon, and the singleton attacker while preserving enough time and Bench space.

## Limits

This is a clean-deck witness.

It assumes all five targeted Special Energy cards are still in deck when Battle Compressor resolves. Real games can place them in the opening hand, Prize cards, or discard through other costs.

It also assumes a later valid Extra Energy Bomb target and a nonterminal Prize state.

The physical shuffle following each Battle Compressor is not represented because this result uses only exchangeable deck counts after the search.

## Next useful work

The next step is to add the evolution timing:

- establish Pikachu or Ditto Prism Star for Alolan Raichu;
- establish Voltorb for Electrode-GX;
- survive the turn-in-play restriction;
- evolve both Stage 1 lines before Extra Energy Bomb and Electro Rain.

That would convert the Energy-loading witness into a board-ready ALS witness.
