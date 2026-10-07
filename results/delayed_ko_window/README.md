# Analytic delayed-KO windows

## Question

For a line that damages a target, moves it to the Bench, then later finishes it with effect-placed damage counters, what pre-hit HP range makes the delayed KO possible?

If the first hit deals D damage and the later effect places C 10-damage counters, a target that starts that sequence with remaining HP R must satisfy:

D < R <= D + 10C

The strict lower bound makes the target survive the first attack. The upper bound makes the later counter effect finish it.

Implementation: tools/delayed_ko_window.py
Regression: results/delayed_ko_window/reproduce.py

## Timeless-GX / Phantom Dive instance

For Timeless-GX's 150 damage followed by six Phantom Dive counters, the exact remaining-HP window is 160 through 210 with ordinary 10-HP granularity.

Existing damage simply changes the target's remaining HP before the first hit. For example, a 260-HP Pokemon with five existing damage counters has 210 remaining and lies inside the same window.

## Current Expanded corpus coverage

The deterministic scan uses the repository's effective-legality policy and current English paper-Expanded snapshot.

It contains 12,504 effectively legal Pokemon prints with parseable HP. Among them, the pristine 160-210 HP window contains 1,653 prints, 544 unique names, and 858 distinct gameplay fingerprints.

Print counts by HP:

| HP | Prints |
| --- | ---: |
| 160 | 258 |
| 170 | 327 |
| 180 | 350 |
| 190 | 176 |
| 200 | 201 |
| 210 | 341 |

At print level, 428 records use the ordinary one-Prize rule and 1,225 have text indicating two Prizes when Knocked Out. After deduplicating alternate-art/reprint gameplay fingerprints, the split is 338 one-Prize versus 520 two-Prize fingerprints.

No pristine target in this HP window has a parsed three-Prize rule in the current snapshot.

## Strategic interpretation

The reusable abstraction is the remaining-HP window. It lets a planner evaluate the delayed-KO condition directly from current state instead of hard-coding particular printed HP values.

Card-pool frequency is only an availability observation. Matchup value still depends on which Pokemon are actually played, whether they begin the line damaged, whether they can be gusted, whether effects are prevented, and how many Prizes matter in the current game.

## Limits

The corpus view uses printed HP and printed Prize-rule text. Live HP modifiers, Prize modification, damage prevention, healing, Weakness/Resistance, and other effects can change tactical outcomes.

The formula also assumes the first target survives in play between the two stages and that accumulated damage remains on it through the position change. Those conditions are separately modeled by the board/position layer.

Future matchup analysis can feed actual damaged board states into this window rather than treating every target as pristine.
