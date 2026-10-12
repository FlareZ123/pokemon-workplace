# Mew VMAX / Genesect V | Aichi 2026 5th place

**Evidence:** Yamato Nakano, Aichi Open League fifth place, 2026-05-10. Fusion Strike draw engine with four Double Colorless Energy.

**Status:** Published 60-card paper Expanded tournament reference. Representative English print IDs are sourced from the [fully print-checked project baseline](../../competitive_deck_baselines/README.md), and may not be the actual Japanese printing. The source validator is [mew_genesect_reproduce.py](../../competitive_deck_baselines/mew_genesect_reproduce.py). Construction checked against the project's October 12, 2026 Expanded English snapshot; regional status and later changes remain to be independently checked.

### Pokémon (14)

| Qty | Card | Print |
|---:|---|---|
|4|Mew V (Fusion Strike)|swsh8-113|
|3|Mew VMAX|swsh8-114|
|4|Genesect V|swsh8-185|
|1|Dedenne-GX|sm10-57|
|1|Crobat V|swsh3-104|
|1|Lillie's Clefairy ex|sv9-56|

### Trainers (42)

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
|2|Special Red Card|me4-82|
|1|Enhanced Hammer|sv6-148|
|1|Field Blower|sm2-125|
|1|Lost Vacuum|swsh11-162|
|1|Escape Rope|swsh5-125|
|1|Hisuian Heavy Ball|swsh10-146|
|1|Secret Box (ACE SPEC)|sv6-163|
|2|Muscle Band|xy1-121|
|2|Float Stone|xy8-137|
|1|Forest Seal Stone|swsh12-156|
|2|Sky Field|xy6-89|
|2|Path to the Peak|swsh6-148|

### Energy (4)

| Qty | Card | Print |
|---:|---|---|
|4|Double Colorless Energy|sm1-136|

**Count verified:** 60 cards.

The published three-VIP list's restricted first-turn Mew plus two Genesect material access is 43.036319% under an assumed D=6 safe-discard pool and a joint paid-Ball / Trainers' Mail sequence. No match win rate is measured.

**Unresolved:** All decks still require legal and capable opponent policies, actual complete-game simulation or match observations, a representative field, and matchup-aware resource preservation before being ranked by expected win percentage.

## First-turn Wally attack route (Agent 40 exact study)

Going second, a Mew V starting Active can evolve immediately through the included Wally, then attack through DCE using Cross Fusion Strike to copy Benched Genesect V's 210-damage Techno Blast. The [exact restricted physical opener study](../../tests/mew_wally_first_attack/) proves **0.907693871722% unconditional** natural-hand/Battle VIP Pass launch access, or **1.167333527391% conditional on a valid initial seven**. These figures exclude Genesect draw Abilities, paid Ball searches and other realistic setup routes, so they must not be read as the full launch frequency or match win rate. Wally is a going-second-only first-turn Supporter line.

The companion [existing paid-Ball execution study](../../tests/mew_wally_first_attack/#existing-paid-ball-routes-mechanical-feasibility-versus-strategic-cost) also counts four Quick Ball and four Ultra Ball copies in the unchanged fifth-place list. With the first natural draw and six random Prizes, the exact mutually exclusive direct/VIP/Quick/Ultra first-turn Wally launch routes sum to **1.444045204289% unconditional**. Discard payment is mechanically feasible for the Ball routes, but the model does not assert the discarded cards are strategically expendable. Genesect draw Abilities remain excluded, so this is a constrained endpoint and cannot rank deck strength.

**Experimental alternate 60:** [Tapu Lele-GX / Wally access variant](../mew-genesect-tapu-wally-counterfactual/) trades one Special Red Card for a Wonder Tag Supporter-search line. Its [exact restricted study](../../tests/mew_wally_tapu_variant/) increases source-aware first-turn going-second 210-damage attack access from 1.444045204289% to 7.326281829134%. This is an untested matchup tradeoff and does not replace the fifth-place tournament reference.
