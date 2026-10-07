# Regidrago Timeless-GX -> Phantom Dive state-dependent KO windows

## Question

How do prior damage, resolved attack-damage modifiers, and attack-effect immunity change the delayed double-KO window in the Regidrago tactical line?

The baseline result established a 160 through 210 HP window for the first target and a 200 HP ceiling for the second target. Those numbers are one instance of a more general state equation.

Implementation: `tools/regidrago_timeless_phantom_als.py`

Regression: `results/regidrago_timeless_phantom_state_windows/reproduce.py`

## General threshold

Let:

- `D_A` be prior damage on the first target;
- `T` be final resolved Timeless-GX damage after damage calculation;
- `K` be damage-counter value later placed on the Benched first target by Phantom Dive;
- `D_B` be prior damage on the second target;
- `P` be final resolved Phantom Dive damage to the second Active target.

For the first target to survive Timeless-GX and then be Knocked Out by Phantom Dive's Bench counters:

`D_A + T < HP_A <= D_A + T + K`.

For the second target to be Knocked Out by Phantom Dive's Active damage:

`HP_B <= D_B + P`.

For the printed attacks in the modeled line, `K = 60`.

The first-target interval therefore always has width 60 damage when all six Phantom Dive counters are placed. Prior damage and resolved Timeless damage translate the interval along the HP axis.

## Baseline

With no prior damage or modifiers:

- `T = 150`;
- `P = 200`;
- `K = 60`.

So:

`150 < HP_A <= 210`

and:

`HP_B <= 200`.

At ordinary 10-HP card increments, the first-target window is 160 through 210 HP.

## Prior damage shifts both thresholds

Give the first target 40 prior damage and the second target 30 prior damage.

Then:

`190 < HP_A <= 250`

and:

`HP_B <= 230`.

At 10-HP increments, the first-target window is 200 through 250 HP.

The delayed Bench-KO tactic can therefore reach substantially larger targets if they enter the sequence already damaged.

## Timeless damage reduction shifts the first-target window downward

Model a resolved defender effect that reduces Timeless-GX by 30 damage.

The damage kernel resolves Timeless-GX to 120.

With no prior damage:

`120 < HP_A <= 180`.

At 10-HP increments, the first-target window becomes 130 through 180 HP.

The later Phantom Dive counter placement is an attack effect that places damage counters. It does not pass through the attack-damage calculation that produced the 120 value.

This creates a useful asymmetry: reducing the first attack's damage can help the target survive Timeless-GX while the later six counters still retain their full KO contribution.

## Phantom Dive damage reduction changes only the Active ceiling

Model a 40-damage reduction on Phantom Dive's damage to the second Active target.

Its final Active damage becomes 160, so with no prior damage:

`HP_B <= 160`.

The six Bench counters on the first target remain a separate effect transition and are unchanged by this Active-target damage reduction.

## Attack-effect immunity is a separate gate

The regression also executes the baseline 180-HP first target and 200-HP second target while marking the first target immune to effects of attacks for Phantom Dive's counter placement.

Timeless-GX still leaves 150 damage on the first target.

Phantom Dive still Knocks Out the 200-HP Active target.

The six requested Bench counters place zero counters on the immune first target, so the first target remains in play at 150 damage.

Numeric HP-window eligibility is therefore insufficient when the effect-placement channel is blocked.

## Validation

The executor now accepts optional `DamageContext` values for Timeless-GX and Phantom Dive, plus a flag representing attack-effect immunity for the first target's later counter placement.

The reusable `derive_timeless_phantom_hp_window()` function resolves the two damage contexts through the canonical damage kernel and returns the resulting threshold values.

The regression exhaustively compares the derived inequalities with the full two-turn executor for every 10-HP pair from 10 through 360 across four state families:

1. baseline;
2. 40 prior damage on A and 30 on B;
3. Timeless-GX reduced by 30;
4. the same prior damage with Timeless-GX reduced by 30 and Phantom Dive reduced by 40.

Every valid starting HP pair matches the closed-form threshold test.

## Strategic implication

The tactic's target map is state-dependent.

A deck or game-state evaluator should not label a Pokémon as simply "in range" or "out of range" from printed HP alone. Relevant state includes:

- prior damage;
- final damage after Weakness, Resistance, and active modifiers;
- effect-counter immunity;
- whether the first target survives the first attack;
- whether switching preserves its accumulated damage.

This also separates two attack channels that can respond differently to defensive effects:

- normal attack damage;
- damage counters placed by an attack effect.

## Limits

The regression supplies already-resolved `DamageContext` inputs rather than deriving every modifier from live card objects.

The first target's effect immunity is supplied explicitly. A full matchup model would compile that state from board Abilities, Tools, attack effects, and lock interactions.

The model still assumes all upstream Apex Dragon, Energy, GX-use, gust, and Supporter-access prerequisites described in the original ALS result.

## Next work

A practical next step is to compile live defensive board effects into the two damage contexts and the effect-immunity flag, then enumerate real Expanded targets whose current board state falls into the delayed-KO window.

That would turn the inequality into a matchup query instead of a hand-supplied tactical test.
