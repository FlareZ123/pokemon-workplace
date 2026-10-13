# Mew VMAX / Genesect V / Tapu Lele-GX, 2026 Aichi counterfactual

**Status: experimental English-paper-Expanded-legal deck, never published as the Aichi fifth-place list.** Take Yamato Nakano's [original Aichi fifth-place 60](../mew-genesect/) and exchange **one of two Special Red Card** (`me4-82`) for **one Tapu Lele-GX** (`sm2-60`). Everything else remains exactly as in the tournament reference. Representative English print IDs are listed below. [Exact source-aware Wally turn-one access experiment](../../tests/mew_wally_tapu_variant/) passed [CI run 38301605855](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38301605855) for card legality and physical toy-oracle regressions.

## Full playable 60-card list

### Pokémon (15)

| Qty | Card | Print |
|---:|---|---|
|4|Mew V|swsh8-113|
|3|Mew VMAX|swsh8-114|
|4|Genesect V|swsh8-185|
|1|Dedenne-GX|sm10-57|
|1|Crobat V|swsh3-104|
|1|Lillie's Clefairy ex|sv9-56|
|1|Tapu Lele-GX|sm2-60|

### Trainers (41)

| Qty | Card | Print |
|---:|---|---|
|2|Guzma|sm3-115|
|2|Karen|xyp-XY177|
|1|Wally|xy6-94|
|1|Marnie|swsh1-169|
|1|Pokémon Ranger|xy11-104|
|4|Quick Ball|swsh1-179|
|4|Ultra Ball|swsh9-150|
|3|Trainers' Mail|xy6-92|
|3|Battle VIP Pass|swsh8-225|
|2|Special Charge|xy11-105|
|2|VS Seeker|xy6-110|
|1|Special Red Card|me4-82|
|1|Enhanced Hammer|sv6-148|
|1|Field Blower|sm2-125|
|1|Lost Vacuum|swsh11-162|
|1|Escape Rope|swsh5-125|
|1|Hisuian Heavy Ball|swsh10-146|
|1|Secret Box|sv6-163|
|2|Muscle Band|xy1-121|
|2|Float Stone|xy8-137|
|1|Forest Seal Stone|swsh12-156|
|2|Sky Field|xy6-89|
|2|Path to the Peak|swsh6-148|

### Energy (4)

| Qty | Card | Print |
|---:|---|---|
|4|Double Colorless Energy|sm1-136|


**Total:** 15 Pokémon + 41 Trainers + 4 Energy = **60 cards**. Twelve opening-eligible Basic Pokémon. One ACE SPEC, Secret Box, unchanged. Wally and Tapu Lele-GX each appear once.

## Strategic thesis and constraints

Going second with Mew V already Active and DCE held/drawn, use the added Tapu Lele-GX's **Wonder Tag** (from hand onto Bench) to find the singleton Wally, then Wally to immediately evolve to Mew VMAX. Benched Genesect V's 210-damage Techno Blast can then be used through Cross Fusion Strike. The original list already has four Quick Ball and four Ultra Ball to find Lele into hand, plus three Battle VIP Pass to Bench Genesect; VIP **does not trigger Wonder Tag**.

The strict initial-seven + one natural-draw + six random Prize-access model, also requiring available deck targets, improves from **1.444045204289%** for the published list to **7.326281829134%** for this variant. This is a subset of mechanically reachable lines, omitting Genesect's Ability draws and many other potential paths. See the detailed [assumptions, exact fractions and independent labeled-card oracle](../../tests/mew_wally_tapu_variant/).

**What the swap loses:** a Special Red Card disruption copy, a Bench space occupied by a non-Fusion Strike two-Prize Pokémon, possible Genesect draw-engine synergy, and resilience under Path to the Peak or other Ability locks. Its tournament reference is only the original fifth-place list. No match win-rate improvement has been demonstrated. This candidate should face full-game, lock-aware and opponent-dependent testing before being recommended above the published 60.

## Under an already-active opponent Path to the Peak

The [joint first-turn counter/payment regression](../../tests/mew_wally_path_joint/) checks the same full 60-card candidate under an opponent's active Path, with six hidden Prizes and one natural first draw. Since Path suppresses Tapu Lele-GX's Wonder Tag, the restricted early 210-damage access falls from **7.326281829134%** (Path absent) to **3.217190331194%**, even allowing naturally held Sky Field, Field Blower, or a payable Lost Vacuum as removal answers. Using only naturally held Sky Field as the answer gives **2.420967242312%**. Two independent fully labeled physical toy oracles and [Windows CI 38302406035](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38302406035) passed. These are conditional line-access probabilities; they deliberately exclude Trainers' Mail counter searches and other natural draw engines. Active Ability suppression independent of the Stadium remains a separate threat.

## Conditional lock matrix and next-turn attack restriction

The [complete conditional lock study](../../tests/mew_wally_lock_matrix/) distinguishes Vileplume-like Item lock, independent Ability suppression, and Active Stoutland Supporter lock. In the same one-turn natural-draw / six-hidden-Prize execution model, **Item lock reduces this deck's Wally attack access to 1.055943416886%**, and simultaneous Item lock plus Path to the Peak reduces it to **0.653777573117%**. Persistent Wonder Tag suppression eliminates the Tapu search contribution even without Path. Active Supporter lock leaves **no Wally-based attack route** under the model. [Windows CI 38302764960 passed](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38302764960).

Techno Blast also applies a **next-turn inability to attack** to Mew VMAX when copied via Cross Fusion Strike, unless that effect is removed, for example by moving Mew to the Bench. Mew VMAX's free Retreat Cost does not alone provide a second promotion on the same turn. These opponent-lock and future-attack costs are reasons to test complete match outcomes before crediting the 210-damage first-turn access as a win-rate improvement.

## Reproducible exact physical print and engine materialization

The [machine-readable 60-card manifest](deck.json) preserves each representative English print ID and quantity. The [source-level Python adjudicator](../../tests/mew_wally_tapu_variant/reproduce.py) verifies that manifest against the original published Aichi 60 plus the one announced Tapu Lele-GX / Special Red Card swap. A separate [pinned Twinleaf loader](../../../simulation/twinleaf/mew-tapu-wally-deck.cjs) takes the existing verified published Mew engine list, retrieves the exact **Tapu Lele-GX `sm2-60`** fullName from the independently verified Regidrago source, and replaces one Special Red Card. Its [single-file engine mapping test](../../../simulation/twinleaf/test-mew-tapu-wally-deck.cjs) verifies unchanged source lists and all 60 candidate copies. [Manual CI 38303895385 passed](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38303895385) against the pinned Twinleaf revision `3348ebdc898f175a2ed8f999133cd13d1afd01f5`.

This step verifies engine **card identity and loadability**. The native bot's hidden-topdeck information leakage and questionable first-turn decision policies remain unresolved, so this mapping is infrastructure for subsequent controlled tests rather than a match-performance result.
