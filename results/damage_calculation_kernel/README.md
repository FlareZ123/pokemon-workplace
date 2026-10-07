# Ordered attack-damage calculation kernel

## Question

Can attack damage be represented as an auditable ordered transition instead of one scalar arithmetic expression?

Yes, for the Advanced Player's Rulebook damage-calculation family modeled here. The new kernel preserves the six rulebook steps and the early-stop conditions that make some superficially equivalent arithmetic expressions wrong.

Implementation: `tools/damage_calculation_kernel.py`  
Regression: `results/damage_calculation_kernel/reproduce.py`

## Rule basis

The bundled Advanced Player's Rulebook defines attack resolution with damage calculation before effects outside damage and before the final Knock Out check. Inside damage calculation it gives this order:

1. resolve the attack's printed damage, including `+`, `-`, or `x` attack-text arithmetic;
2. apply effects on the Pokemon doing the damage;
3. apply Weakness;
4. apply Resistance;
5. apply effects on the Pokemon taking the damage;
6. apply final damage, including prevention.

The manual also supplies non-commutative stop rules. If a `x` or `-` attack becomes zero or negative in step 1, damage calculation ends there. If an attacker-side effect, Resistance, or a defender-side effect later reduces damage to zero or below, calculation likewise stops at the specified step. A later positive modifier cannot revive damage after one of those boundaries.

## Representation

`AttackDamage` separates four step-1 forms:

- fixed printed damage;
- `+` damage;
- `-` damage;
- `x` damage.

`DamageContext` then carries independent state for attacker-side modifiers, current Weakness, current Resistance, defender-side modifiers, final damage prevention, attack text that ignores Weakness/Resistance, and attack text that ignores effects on the defending Pokemon.

`DamageResult` records each reached intermediate value plus any early-stop step. This makes the calculation trace inspectable by a future attack executor or planner.

## Critical distinction: ignoring defender effects is not restoring Weakness

The rulebook's B-07 wording says an attack whose damage is not affected by effects on the opponent's Active Pokemon ignores step-5 defender modifiers and damage-prevention effects. The same section explicitly notes that Weakness/Resistance wordings are not themselves "effects on a Pokemon."

The bundled Keldeo ex / Sonic Edge example goes further: if another effect has already made the target have no Weakness, Sonic Edge does not bring that Weakness back.

The kernel therefore treats the target's current Weakness/Resistance state as an input to steps 3 and 4. `ignore_defender_effects=True` skips step 5 and final prevention only. It does not reconstruct suppressed Weakness or Resistance.

This prevents a representation error where every defensive state modifier is stored in one bag and then indiscriminately ignored.

## Regression witnesses

The deterministic regression checks:

- a full ordered chain: 100 base, +30 attacker effect, x2 Weakness, -30 Resistance, -30 defender effect = 200;
- a step-1 `-` attack that reaches zero and cannot be revived by a later +30 attacker effect;
- a step-1 `x` attack with multiplier zero and the same no-revival property;
- Resistance reducing damage to zero before a later positive defender modifier could apply;
- Benched-style damage that skips Weakness and Resistance;
- ordinary final damage prevention after step-5 reduction;
- Sonic-Edge-style ignoring of defender modifiers and prevention;
- Weakness still applying when it currently exists under that wording;
- an upstream effect that has removed Weakness remaining respected.

## Strategic relevance

Damage arithmetic is a prerequisite for exact tactical-line evaluation. The order matters for KO thresholds, multi-KO lines, damage-prevention matchups, Weakness exploitation, defensive Tools/Stadiums, and copied attacks. A graph that labels an edge "does 100 damage" without this state can misclassify whether a line actually takes a Prize.

This kernel is intentionally mechanical. It supplies a reusable damage value to the existing Knock Out and Prize infrastructure rather than trying to merge those phases prematurely.

## Limits

This first slice does not yet parse arbitrary card text into `DamageContext`. It also leaves several concerns outside the kernel:

- pre-damage attack effects;
- effects outside damage, including placing damage counters;
- damage-triggered effects after damage;
- Weakness/Resistance type matching itself;
- variable attack-text predicates beyond the already-resolved step-1 modifier;
- Knock Out and Prize resolution.

Those are separate transitions in the rulebook order. The next useful bridge is to compose this damage result with a small HP/damage-counter state so that attack damage and effect-placed counters can feed the existing Knock Out phase without losing their distinct semantics.
