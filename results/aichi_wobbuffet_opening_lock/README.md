# How often can Regidrago start Active Wobbuffet with a natural free pivot?

## Why the opening board matters

The [published 2026 Aichi 10th-place Regidrago deck](../regidrago_aichi_top10_playable/) contains one Wobbuffet with Bide Barricade, four Regidrago V and one Latias ex. If Wobbuffet is selected as the **starting Active**, its Ability is immediately active during the opponent's opening turn (provided no other effect suppresses it). Its lock is asymmetric against the [champion Shadow Rider list](../aichi_wobbuffet_psychic_lock_matchup/): Underworld Door on Psychic VMAX is exempt.

Regidrago can choose its starting Active Pokémon only from Basics in its initial seven-card hand. Additional cards from an opponent's later mulligan can go on the Bench but do not retroactively change that starting-Active choice. The seven-card validity conditioning therefore has a clear and reproducible physical interpretation.

## Exact Basic-valid initial seven-card probabilities

In this exact 60-card deck, **15 cards are Basic Pokémon** (computed from the actual database's Pokémon `subtypes`). Ignoring the opponent's mulligans, after rejecting invalid seven-card hands lacking any Basic:

| Event visible in initial seven (can choose Wobbuffet as starting Active) | Exact conditional chance |
| --- | ---: |
| Wobbuffet is present | **13.220031%** |
| Wobbuffet and at least one Regidrago V present | **4.714352%** |
| Wobbuffet and Latias ex present | **1.344410%** |
| Wobbuffet, Regidrago V and Latias ex all present | **0.416518%** |

The last event is a narrow, entirely natural setup witness: start Wobbuffet Active, put Regidrago V and Latias ex onto the Bench during setup, then on one's legal retreat opportunity use Latias ex's Psychic-exempt **Skyliner** to retreat the Basic Wobbuffet without Energy and promote Regidrago V. The plan can be disrupted by an opposing effect, and only one manual retreat is ordinarily allowed per turn.

The lone Wobbuffet's raw chance of appearing among seven uniformly sampled cards is 7/60. Because Wobbuffet itself is Basic, **every** seven-card sample containing it is accepted. Therefore dividing 7/60 by the probability of **any** Basic in the seven cards gives the exact accepted-opening probability. Extra Regidrago V and Latias events are handled with multivariate inclusion-exclusion on the remaining six cards.

Importantly, these are probabilities for **initial-hand natural combinations only**. The 13.220031% is the maximum share of Basic-valid openings that can *start* with Wobbuffet Active from their initial seven. It is not an upper bound on promoting Wobbuffet through later searches or switches. The 0.416518% conjunction is a specific convenient witness, and Quick Ball, Mysterious Treasure, mobility effects and later draws can create many other routes. Conditional Prize allocation and whether later actions successfully execute are separate problems.

## Reproduction, proof and limitations

[The executable single-file oracle](reproduce.py) reads the published Regidrago manifest and print-subtype database, verifies the relevant copy counts and type/retreat text, computes **exact rational** formulas, and crosschecks four event probabilities in over 100 exhaustively enumerated **smaller labeled physical decks**. The test runs on Windows with Python standard library only.

The test omits opponent mulligan bonus draws, opponent Bench information, Energy and Supporter availability, attacking tempo, any search or draw action during a player's first turn, and the opponent's responses. Consequently, the result is an exact initial-hand census, not a match-win estimate. It is most useful as a calibration point for dynamic board-state policies where the timing of Radiant Eternatus's Bench-entry Ability or the opportunity cost of selecting Wobbuffet Active matters.
