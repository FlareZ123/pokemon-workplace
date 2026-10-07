# Regidrago Timeless-GX -> Phantom Dive tactical line

## Question

Can the human-described Regidrago line involving repeated gust, Timeless-GX, and Phantom Dive be represented as an exact executable sequence, and what HP window makes its delayed double Knock Out work?

Yes, under explicit upstream attack-copy prerequisites.

Implementation: `tools/regidrago_timeless_phantom_als.py`  
Regression: `results/regidrago_timeless_phantom_als/reproduce.py`

## Card basis

The bundled effectively Expanded-legal prints used by the regression are:

- Regidrago VSTAR `swsh12-136`: Apex Dragon chooses an attack from a Dragon Pokemon in the discard pile and uses it as Apex Dragon;
- Dialga-GX `sm5-100`: a Dragon Pokemon whose Timeless-GX does 150 damage and grants another turn while skipping the between-turns step;
- Dragapult ex `sv6-130`: a Dragon Pokemon whose Phantom Dive does 200 damage and places six damage counters on the opponent's Bench in any way the user likes;
- Boss's Orders `swsh2-154`: a Supporter that gusts a chosen opposing Benched Pokemon Active.

Existing repository attack-copy work already establishes the separate GX-use and extra-turn scheduling contracts for copied GX bodies. This result composes the position, turn-budget, damage, and KO-threshold layers around that established copy prerequisite.

## Executed line

Start with target B Active and target A Benched.

Turn 1:

1. play Boss's Orders to gust A Active;
2. use Apex Dragon to execute Timeless-GX;
3. A takes 150 damage;
4. Timeless-GX closes the current turn and schedules a fresh extra turn for the same player.

Extra turn:

1. the Supporter quota is fresh again;
2. play Boss's Orders on B, moving B Active and the damaged A back to the Bench;
3. use Apex Dragon to execute Phantom Dive;
4. B takes 200 normal damage;
5. put six Phantom Dive counters on the damaged Benched A;
6. perform the shared end-of-attack KO check.

The regression verifies that the second Boss is available because the extra turn owns a fresh ordinary Supporter budget.

## Exact HP window

For an initially undamaged A:

- after Timeless-GX, A has taken 150;
- A must survive that attack so it can be moved to the Bench on the extra turn;
- six later damage counters add 60.

Therefore A must satisfy:

`150 < HP_A <= 210`

For ordinary 10-HP increments, that is exactly **160 through 210 HP**.

For initially undamaged B, Phantom Dive's main damage gives the simple ceiling:

`HP_B <= 200`

The regression exhaustively checks HP values from 10 through 320 in 10-HP increments. Exactly 120 ordered HP pairs satisfy the two-target final-attack KO condition:

- six possible HP values for A: 160, 170, 180, 190, 200, 210;
- twenty possible HP values for B: 10 through 200.

## Why the second gust matters

The first target has to be on the Bench when Phantom Dive resolves so its six effect counters can finish the earlier Timeless-GX damage. The second Boss's Orders performs two tactical jobs at once:

- exposes a fresh Active target for Phantom Dive's 200 damage;
- moves the 150-damaged first target onto the Bench, making it eligible for Phantom Dive's counter effect.

This is a concrete multi-axis use of gust rather than a generic "target access" bonus.

## Strategic interpretation

The line illustrates why an archetype-specific sequence can be stronger than a bag-of-cards description.

Its feasibility depends jointly on:

- two Dragon attack payloads being available to Apex Dragon;
- an unused GX channel before Timeless-GX;
- the extra-turn boundary refreshing ordinary Supporter bandwidth;
- two legal gust targets across the two turns;
- preservation of damage when the first Active moves to the Bench;
- the first target surviving 150 while remaining within 60 of a later KO;
- the second target being within the 200-damage threshold;
- Phantom Dive's effect-counter placement remaining legal on the Benched target.

Dropping any one of those state variables can turn a graph-reachable line into an illegal or tactically different line.

## Limits

The focused executor assumes these upstream prerequisites have already been established:

- Regidrago can pay Apex Dragon's Energy cost;
- Dialga-GX and Dragapult ex are in the discard pile and selectable;
- the GX attack has not already been used;
- Boss's Orders is accessible on both turns;
- no lock prevents Supporter play or attacks.

The current threshold sweep also assumes no Weakness, Resistance, damage modifiers, healing, HP modifiers, effect immunity, or Prize-replacement effects. Those can be layered through the damage and counter kernels.

A useful extension is to generalize the HP inequalities to prior damage and defensive modifiers, then query real Expanded card states or matchups where the delayed Bench KO changes the Prize map.
