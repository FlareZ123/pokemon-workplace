# Harto Miki Raichu/Electrode: Extra Energy Bomb as a Prize-state Energy switch

## Question

The Harto Miki Raichu/Electrode list contains a specific five-card interaction surface:

- Electrode-GX uses **Extra Energy Bomb** to attach five Energy cards from the discard pile, then Knocks itself Out;
- Alolan Raichu uses **Electro Rain** to discard any amount of Lightning Energy and deal 30 damage for each Energy discarded;
- the list's Reversal Energy and Counter Energy provide multiple units of every Energy type only while the player is behind on Prizes.

Can Electrode-GX's own two-Prize Knock Out turn those conditional Special Energy cards on before Electro Rain, and how large is the resulting ceiling?

Yes.

Implementation: `tools/raichu_electro_rain_als.py`  
Regression: `results/raichu_electro_rain_als/reproduce.py`

## Card-grounded package

The bundled list and card records give:

- **4 Reversal Energy**: on an Evolution Pokémon without a Rule Box, while its player has more Prize cards remaining than the opponent, each card provides every type and **3 Energy at a time**;
- **4 Counter Energy**: on a non-GX/non-EX Pokémon, under the same Prize-deficit test, each card provides every type and **2 Energy at a time**;
- **3 Unit Energy LightningPsychicMetal**: each provides Lightning, Psychic, or Metal, **1 Energy at a time**;
- Alolan Raichu is a Stage 1 without a Rule Box, so it satisfies the target restrictions of both comeback Energy effects;
- Extra Energy Bomb attaches **5 Energy cards** from discard to non-GX/non-EX Pokémon, then Knocks Out Electrode-GX;
- Electrode-GX awards **2 Prize cards** when Knocked Out;
- Electro Rain costs one Lightning and says to discard any amount of Lightning Energy, then deal 30 damage once for each Energy discarded.

The Advanced Player's Rulebook explicitly separates Energy cards from Energy units. Its Ignition Energy example states that one physical card providing three Energy can count as three Energy being discarded. The every-type Energy rule likewise makes a currently active Reversal or Counter Energy provide Lightning rather than allowing its controller to ignore that type.

## Prize timing

Let:

- `S` be the Raichu player's Prize cards remaining;
- `O` be the opponent's Prize cards remaining before Extra Energy Bomb.

If the game continues, the self-KO changes the opponent's count to:

`O' = O - 2`

Reversal Energy and Counter Energy are active afterward exactly when:

`S > O'`

or:

`S > O - 2`.

This creates an important state switch.

### Tied before the self-KO

At 3 Prizes each:

- before: `3 > 3` is false;
- Extra Energy Bomb Knocks Out Electrode-GX;
- opponent takes two Prizes and goes to 1;
- after: `3 > 1` is true.

The five attached Special Energy cards immediately use their comeback provider profiles before the attack window.

### One Prize ahead before the self-KO

At 2 Prizes remaining versus the opponent's 3:

- before: `2 > 3` is false;
- after the self-KO: opponent has 1;
- `2 > 1` is true.

The combo can therefore deliberately donate two Prizes and turn the comeback Energy effects on even from one Prize ahead.

### Two Prizes ahead before the self-KO

At 1 Prize remaining versus the opponent's 3:

- after the self-KO, both players have 1 Prize remaining;
- `1 > 1` is false.

The comeback effects remain off.

The exact activation boundary is therefore broader than "already losing."

## Five-card Energy ceiling

When the comeback condition is active, the best five physical Energy cards from the Harto package are:

- 4 Reversal Energy = 12 Lightning Energy units;
- 1 Counter Energy = 2 Lightning Energy units.

Total:

**14 Lightning Energy units from 5 physical cards.**

If Electro Rain discards all five of those cards, the attack has fourteen 30-damage placements:

**420 total damage**, assignable in 30-damage increments, including repeated selection of the same opposing Pokémon.

This is a direct consequence of the Energy-card versus Energy-unit distinction. Treating one Energy card as one Energy would incorrectly cap the same five-card attachment at 150.

## Inactive ceiling

When the comeback condition remains off:

- Reversal Energy provides only Colorless;
- Counter Energy provides only Colorless;
- only the three Unit Energy LightningPsychicMetal copies provide Lightning.

With five physical Energy cards attached, the best available Lightning total is therefore 3 units:

**90 Electro Rain damage.**

The Prize-state switch changes the conditional ceiling from 90 to 420 in this controlled full-energy-pool state.

## Terminal boundary

Electrode-GX's self-KO awards the opponent two Prizes before the player can proceed to an attack.

If the opponent begins the line with one or two Prize cards remaining, that Prize award takes their final Prize and the game ends.

The modeled Electro Rain continuation is therefore unavailable regardless of how much Energy was attached.

This prevents an optimizer from treating Extra Energy Bomb purely as acceleration when it is actually a losing action at that Prize boundary.

## Complete 1-to-6 Prize matrix

Across the 36 integer pairs `(own Prizes remaining, opponent Prizes remaining)`:

- 12 pairs are terminal because the opponent begins with at most two Prizes;
- 24 pairs continue;
- 14 of those continuing pairs have the comeback Energy condition active after the self-KO;
- in 8 of those 14, Extra Energy Bomb itself changes the condition from off to on;
- 10 continuing pairs leave the condition inactive.

The eight exact off-to-on pairs are:

`(2,3), (3,3), (3,4), (4,4), (4,5), (5,5), (5,6), (6,6)`

where each pair is `(own remaining, opponent remaining)`.

These are the tied or one-Prize-ahead states in which donating two Prizes crosses the comeback threshold without ending the game.

## Strategic interpretation

Extra Energy Bomb has three coupled roles in this archetype:

1. it moves five physical Energy cards from discard onto Alolan Raichu;
2. its self-KO changes the Prize count;
3. that Prize change can change the provider profile of the Energy cards it just attached.

The line is therefore state-transforming in a stronger sense than ordinary Energy acceleration.

A simulator that snapshots Reversal/Counter provider values before resolving the self-KO will miss the 90-to-420 transition. A simulator that applies the two-Prize award after the attack will also get the line wrong.

This is a concrete Archetype-Line-Specific interaction in which event order changes the meaning of already-attached resources.

## Evidence classification

Rules-derived:

- one physical multi-unit Energy card can represent several discarded Energy units;
- the Prize award occurs in the Knock Out process before play continues;
- taking the final Prize ends the game;
- conditional Special Energy provider text is evaluated from the current state.

Card-text facts:

- Reversal Energy's three-unit every-type profile and target condition;
- Counter Energy's two-unit every-type profile and target condition;
- Unit Energy LPM's one-unit Lightning profile;
- Extra Energy Bomb's five-card attachment and self-KO;
- Electro Rain's per-Energy 30-damage effect.

Computational result:

- the 36-state Prize matrix;
- the eight self-KO activation pairs;
- the five-card maxima of 14 active Lightning units and 3 inactive Lightning units.

## Limits

This is a conditional ceiling model.

It assumes the relevant five Energy cards are already in the discard pile and available to Extra Energy Bomb. It does not yet calculate Battle Compressor sequencing, natural Energy access, Prize losses of the Energy cards, or the probability of assembling Electrode-GX plus Alolan Raichu.

It also assumes Alolan Raichu remains in play after Electrode-GX is Knocked Out, so the self-KO does not simultaneously cause a no-Pokémon loss.

The 420 value is total available 30-damage placement, not a match win-rate estimate. Opposing effects can prevent or modify damage, and real targets impose discrete knockout requirements.

## Next useful work

The strongest continuation is to model how often the deck can put five high-value Special Energy cards into the discard pile before Extra Energy Bomb.

Battle Compressor is the obvious enabling connector. That analysis should preserve its competing uses, including Giratina and other payloads, and should distinguish the number of physical Energy cards loaded from the number of Energy units those cards later provide.
