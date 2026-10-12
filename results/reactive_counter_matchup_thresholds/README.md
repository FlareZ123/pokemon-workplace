# Mega Scrafty retaliation against four real Aichi attacker prints

## Printed HP and Prize breakpoints

The prior [reactive counter ceiling](../reactive_counter_stack_frontier/) reaches 29 damage counters at a high setup cost. Here, four named primary attackers from the [2026 Aichi tournament reference collection](../competitive_deck_baselines/) receive those counters in a conditional post-damage snapshot. Exact print IDs, HP, and Prize rules are checked against the supplied Expanded card pool, as are all five retaliation sources and lock-source rules.

| Aichi attacker | Printed HP | Prizes on KO | Prior damage required for KO from 290 counter-damage | From the 170-counter lean stack |
| --- | ---: | ---: | ---: | ---: |
| Champion Shadow Rider Calyrex VMAX `swsh6-75` | 320 | 3 | **30** | 150 |
| Fifth-place Mew VMAX `swsh8-114` | 310 | 3 | **20** | 140 |
| Tenth-place Regidrago VSTAR `swsh12-136` | 280 | 2 | **0** | 110 |
| Eighth-place Mega Absol ex `me1-86` | 280 | 3 | **0** | 110 |

These numbers are arithmetic breakpoints conditional on a successful, unprevented damaging attack into the Scrafty board, all reaction sources surviving through the response window, and no relevant modifiers to the printed HP. The model does not estimate how likely the opponent is to attack into such a board.

Under **Path to the Peak**, the full stack drops to 24 counters. Even the two printed 280 HP attackers then require **40 pre-existing damage** for a reactive Knock Out. Under **Garbotoxin**, it drops to 20 counters, requiring **80 existing damage**. Effects that prevent damage-counter placement would change all these conclusions.

## Prize exchange and an effect-only bypass

Mega Scrafty ex is a **three-Prize Pokémon**. If an opposing Regidrago VSTAR and Mega Scrafty are both Knocked Out, the player claiming Regidrago takes two Prizes while the opponent claiming Mega Scrafty takes three, a **one-Prize disadvantage**, subject to terminal Prize conditions. Against a Mega Absol ex, both sides would take three Prizes. If only one Pokémon is Knocked Out, the trade differs.

Mega Absol ex also has **Terminal Period**, a printed attack with zero damage that directly Knocks Out an opposing Active Pokémon if it has **exactly six damage counters**. This attack can resolve a Knock Out without ever damaging the defender. All five modeled Scrafty/Spiritomb/Spiky/Deluxe reactions require a Pokémon to be *damaged by an attack*, so Terminal Period's effect-only route does not activate them. Its other attack, **Claw of Darkness**, deals 200 printed damage and can satisfy that prerequisite. Attack choice and damage-state conditioning matter more than comparing printed HP alone.

Regidrago VSTAR's Apex Dragon and Mew VMAX's Cross Fusion Strike copy other attacks; whether a particular selected attack deals qualifying damage has to be resolved separately. Shadow Rider's Max Geist has printed damage but still needs Energy and an unprevented final damage outcome to trigger a reaction.

## Conclusion and boundaries

The extreme 29-counter source inventory can only one-shot two of these four full-HP primary attacker prints. Shadow Rider VMAX and Mew VMAX survive even the maximum unless already damaged. The lean 170-counter alternative does not one-shot any of these four from full HP. This further weakens the case for calling a raw counter-stack ceiling a competitive deck strength measure.

The report provides **rules-derived conditional tactical breakpoints** with exact card and print checks. It supplies neither full opponent policy nor match frequency nor a tournament recommendation.

## Reproduction

Run `python results/reactive_counter_matchup_thresholds/reproduce.py`. The exhaustive arithmetic oracle checks each ten-HP breakpoint up to 400 HP across 0–30 retaliation counters. Exact printed attack names, damage types and Prize rules are asserted. Windows workflow: `.github/workflows/validate-reactive-counter-matchup-thresholds.yml`.
