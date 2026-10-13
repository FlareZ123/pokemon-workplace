# Mew VMAX / Genesect V with 2 Wally and 1 Tapu Lele-GX

**Experimental, English paper Expanded playable 60.** Derived from [Yamato Nakano's Aichi 2026 fifth-place list](../mew-genesect/) by replacing both Special Red Cards with one additional Wally and one Tapu Lele-GX. Its tournament evidence belongs exclusively to the original published list.

The [exact two-slot frontier study](../../tests/mew_wally_slot_frontier/) gives this candidate **8.762569342969%** strictly bounded first-turn-going-second Techno Blast access, versus **1.444045204289%** for the unchanged published list. Under an assumed continuously suppressed Wonder Tag, it retains **2.766576228949%** through naturally drawn Wally. These values exclude many real draw/search actions and are **not win probabilities**.

## Full 60-card English-print list

### Pokémon (15)

| Qty | Card | English print |
|---:|---|---|
|4|Mew V|swsh8-113|
|3|Mew VMAX|swsh8-114|
|4|Genesect V|swsh8-185|
|1|Dedenne-GX|sm10-57|
|1|Crobat V|swsh3-104|
|1|Lillie's Clefairy ex|sv9-56|
|1|Tapu Lele-GX|sm2-60|

### Trainers (41)

| Qty | Card | English print |
|---:|---|---|
|2|Guzma|sm3-115|
|2|Karen|xyp-XY177|
|2|Wally|xy6-94|
|1|Marnie|swsh1-169|
|1|Pokémon Ranger|xy11-104|
|4|Quick Ball|swsh1-179|
|4|Ultra Ball|swsh9-150|
|3|Trainers' Mail|xy6-92|
|3|Battle VIP Pass|swsh8-225|
|2|Special Charge|xy11-105|
|2|VS Seeker|xy6-110|
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

| Qty | Card | English print |
|---:|---|---|
|4|Double Colorless Energy|sm1-136|

**Total: 15 Pokémon + 41 Trainers + 4 Energy = 60 cards.** Twelve Basic Pokémon, one ACE SPEC (Secret Box), four DCE. The [machine-readable manifest](deck.json) fixes every representative print ID.


## Opponent-lock access scenarios

The [source-aware conditional lock extension](../../tests/mew_wally_slot_frontier/lock_extension.py) tests the same experimental 60 against already-active restrictions. Its restricted opening Techno Blast access is **4.611126463163%** under opponent Path to the Peak if Sky Field, Field Blower or a payable Lost Vacuum may clear Path; **1.606679962468%** under Item lock; and **1.193927481675%** under combined Item lock plus Path, using naturally seen Sky Field as the remaining counter. Fully independent Wonder Tag suppression leaves 2.766576228949%, or 1.117932655318% if Items are also locked. Source conditional effects and two independent small physical-card oracles were verified by [CI 38331341671](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38331341671). Locked board feasibility, timing and real-game outcomes remain unmeasured.


## Card-specific resilience extensions

Against an already-active Iron Thorns ex (230 HP), Wonder Tag is suppressed. The [checked Muscle Band line](../../tests/mew_wally_slot_frontier/iron_thorns_bridge.py) permits copied Genesect Techno Blast to reach exactly **230 damage**. The candidate's two Wally give **0.454785706377%** restricted going-second first-turn knockout access through naturally held Muscle Band, compared with **0.235122083152%** for original one-Wally Mew, with other setup/search opportunities omitted.

With no Ability/Item lock, [Hisuian Heavy Ball](../../tests/mew_wally_slot_frontier/heavy_ball_prize_bridge.py) in the opening hand can exchange itself for the otherwise Prized singleton Tapu Lele-GX and enable Wonder Tag. This adds a disjoint **0.126438025767 percentage points** to the candidate's restricted opening attack access, reaching **8.889007368736%** when that one Prize-rescue route is included. The underlying card text, exact Prize conditioning and three independent tiny-deck physical oracles passed [CI 38331868821](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38331868821). These mechanical opportunities remain untested against real opponents.

## Joint Prize-retrieval policy

A [joint exhaustive Prize-action model](../../tests/mew_wally_slot_frontier/heavy_ball_joint_policy.py) now permits the single naturally held Hisuian Heavy Ball to retrieve **either Prized Tapu Lele-GX or Prized Genesect V**, whichever can rescue the otherwise failing Wally launch line. The two extra mutually exclusive first-turn access cases contribute **0.126438025767** and **0.138501806794 percentage points** respectively, raising this candidate's limited first-turn attack-access union from **8.762569342969%** to **9.027509175530%**. [CI 38332311041](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38332311041) independently validates physical Prize configurations, original non-Heavy pathways and source-specific card rules. It remains a bound on one route family, not an overall setup or winning probability.

## Play plan and tradeoffs

For a going-second opening with Mew V Active, access Wally directly or use Quick/Ultra Ball to fetch Tapu Lele-GX **into hand**, bench it to trigger Wonder Tag, find Wally, and evolve into Mew VMAX immediately. Attach DCE and copy a Benched Genesect V's Techno Blast via Cross Fusion Strike for 210 before modifiers. Battle VIP Pass can provide Genesect but cannot trigger Wonder Tag by directly Benching Tapu.

The second Wally improves resilience under Wonder Tag suppression and reduces Prize-singleton pressure. Removing **both Special Red Cards** sacrifices late-game hand disruption. Tapu Lele is a two-Prize non-Fusion Strike Bench occupant; opposing Path, Item/Ability/Supporter locks and damage prevention can severely reduce the line's value. Techno Blast also blocks the attacking Mew from attacking next turn unless that effect is cleared. Real multi-turn match tests are needed before favoring this experimental 60 over the proven tournament list.

Validation: [exact physical-opening code and dated print legality proof](../../tests/mew_wally_slot_frontier/reproduce.py); this repository's headless engine is not yet a reliable measure of its competitive win rate.
