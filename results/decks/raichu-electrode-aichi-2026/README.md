# Raichu / Electrode Combo: Aichi 2026 fourth place

**Tournament evidence:** Shu Hosoda finished fourth among 926 players at the May 10, 2026 [CL Aichi Open League](https://limitlesstcg.com/tournaments/566/decklists) with this exact 60-card name-and-count list. The individual [published 60](https://www.limitlesstcg.com/decks/list/26812) is the primary source. These are representative English gameplay prints with separately checked Expanded eligibility, and may differ from the Japanese tournament's actual physical printings. **Status: tournament reference; no independently established field-wide match-win rate.**

## Complete 60-card list

### Pokémon (18)

| Qty | Printed card | English print ID |
| ---: | --- | --- |
| 2 | Voltorb | `xy6-21` |
| 3 | Electrode-GX | `sm7-48` |
| 1 | Pikachu | `swsh11-52` |
| 2 | Alolan Raichu | `sm11-57` |
| 2 | Dedenne-GX | `sm10-57` |
| 2 | Crobat V | `swsh3-104` |
| 1 | Squawkabilly ex | `sv2-169` |
| 1 | Tapu Lele-GX | `sm2-60` |
| 1 | Eldegoss V | `swsh2-19` |
| 1 | Gengar & Mimikyu-GX | `sm9-53` |
| 1 | Klefki | `sv1-96` |
| 1 | Ditto ◇ | `sm8-154` |

### Trainers (30)

| Qty | Printed card | English print ID |
| ---: | --- | --- |
| 1 | Gladion | `sm4-95` |
| 1 | Carmine | `sv6-145` |
| 1 | Pokémon Ranger | `xy11-104` |
| 1 | Lillie's Determination | `me1-119` |
| 4 | Quick Ball | `swsh1-179` |
| 4 | Battle Compressor | `xy4-92` |
| 4 | Rescue Stretcher | `sm2-130` |
| 3 | Escape Rope | `swsh5-125` |
| 2 | Hisuian Heavy Ball | `swsh10-146` |
| 1 | Ultra Ball | `swsh9-150` |
| 1 | Battle VIP Pass | `swsh8-225` |
| 1 | Secret Box | `sv6-163` |
| 1 | Telescopic Sight | `swsh4-160` |
| 1 | U-Turn Board | `sm11-211` |
| 1 | Forest Seal Stone | `swsh12-156` |
| 3 | Sky Field | `xy6-89` |

### Energy (12)

| Qty | Printed card | English print ID |
| ---: | --- | --- |
| 4 | Reversal Energy | `sv2-192` |
| 4 | Counter Energy | `sm4-100` |
| 4 | Unit Energy LPM | `sm5-138` |

**Total: 18 Pokémon + 30 Trainers + 12 Energy = 60 cards.** There are 13 ordinary Basic Pokémon, one ACE SPEC (Secret Box), and one Prism Star (Ditto ◇).

## Strategic role

- **Electrode-GX Extra Energy Bomb:** the deck discards Energy and then moves Energy from discard into play, deliberately Knocking Out Electrode-GX and changing the Prize differential. The target Alolan Raichu is a Stage 1 single-Prize attacker eligible to receive this acceleration.
- **Alolan Raichu Electro Rain:** each Lightning Energy discarded from Alolan Raichu lets the attack target one opposing Pokémon for 30 damage, including repeated hits on the same target, while ignoring Weakness and Resistance. The Special Energy mix matters: Unit Energy LPM can supply Lightning while attached, and the conditions of Reversal Energy / Counter Energy require exact verification in the current board state.
- **Prize and evolution resilience:** two Alolan Raichu, one Pikachu and Ditto ◇ provide two Basic evolution paths; four Rescue Stretcher and two Hisuian Heavy Ball provide zone-dependent recovery. Extra Energy Bomb's self-Knock-Out changes timing of which Special Energy effects are active.
- **Control and draw concessions:** Klefki's Active Mischievous Lock can disable the deck's own Basic support Abilities while stopping the opponent's Basic Abilities. Four Battle Compressor, four Quick Ball, one Ultra Ball, singleton Secret Box and two Heavy Ball have sharply different discard, Prize and search prerequisites.

## Critical Energy and Prize timing

In this list, the order of prize-taking and attack declaration changes Electro Rain's effective damage. Electrode-GX's Extra Energy Bomb attaches **five physical Energy cards from the discard pile** and then Knocks Out Electrode-GX, granting the opponent **two Prize cards**. The Reversal and Counter Energy conditions are evaluated on the resulting Prize state. The attacker must be an ordinary evolved, non-Rule-Box Alolan Raichu.

| Prizes remaining before Electrode's self-KO (ours / theirs) | Afterwards (ours / theirs) | Conditional Lightning units available from five attached cards | Unmodified Electro Rain |
| --- | --- | --- | ---: |
| 6 / 6 | 6 / 4, now behind | 4 Reversal × 3 + 1 Counter × 2 = **14** | **420 distributed damage** |
| 4 / 6 | 4 / 4, tied | At most 4 Unit LPM × 1 = **4** | **120 distributed damage** |
| 2 / 6 | 2 / 4, ahead | At most 4 Unit LPM × 1 = **4** | **120 distributed damage** |
| 6 / 2 | 6 / 0, opponent immediately wins | No attack possible | — |

This is a **conditional five-card ceiling**, assuming the correct five Energy cards are in the discard pile, one Alolan Raichu receives them, its attack can be used, and no further modifiers apply. Reversal Energy provides three Lightning units **only if behind in Prizes and attached to a no-Rule-Box Evolution**; Counter Energy provides two Lightning units only if behind and attached to a non-GX/non-EX Pokémon. Unit Energy LPM provides one Lightning unit at all Prize counts. Electro Rain measures each **Energy**, unlike attacks that explicitly count discarded Energy *cards*. The attached cards themselves are always discarded as whole cards. Additional Tools, damage prevention, or timing constraints can change actual results. The [source-text regression](../../tests/raichu_2026_print_validation/prize_energy_modes.py) verifies all three printed Energy conditions and the immediate self-KO consequences against the bundled card archive.

A tactical consequence: an Electrode Bomb can activate triple/double Energy when the starting Prize count is tied, but it may fail to do so when the Raichu player was **ahead** before the Bomb. If the opponent has two or fewer Prizes left, voluntarily knocking out Electrode-GX hands them the game before an attack can occur. A practical optimizer must evaluate the transition itself.

## Why this list belongs on the competitive shortlist

It is an additional fourth-place 2026 Aichi archetype missing from the initial five-deck print-verified shortlist. Its deliberately self-Knock-Out-driven tempo and spreading attack create different win conditions from the main VMAX, Item-lock and Regidrago decks. Its published placement is meaningful tournament evidence, with no modeled matchup table, best-of-three rate or validated match simulator coverage currently established.

**Important comparison warning:** Agent 2's [2024 Harto Raichu target-payment study](../../tests/raichu_target_payment_frontier/) uses a structurally different 2024 list: one Alolan Raichu, two Gladion, three Ultra Ball, singleton Computer Search, eleven Special Energy, and a Giratina. This 2026 list instead has **two Alolan Raichu, one Gladion, one Ultra Ball, Secret Box and twelve Special Energy**, among other changes. Do not transfer the 30.578700% strict-model access estimate to this deck.

Reproducible source/count/print audit: [manifest](manifest.json), [standalone validator](../../tests/raichu_2026_print_validation/reproduce.py), [manual Windows workflow](../../../.github/workflows/validate-agent2-raichu-2026-print.yml). Regional card legality, live match strategy and complete-game win percentages need independent evaluation.
