# Expanded printed attack-damage notation catalog

## Question

How much of the effectively legal paper-Expanded English snapshot uses a small, mechanically auditable printed damage notation?

All 19,992 attack rows in the current snapshot fall into five surface forms:

| Printed form | Count |
| --- | ---: |
| blank | 3,816 |
| fixed integer | 12,312 |
| integer plus sign | 2,513 |
| integer minus sign | 46 |
| integer multiplication sign | 1,305 |

Implementation: `tools/attack_damage_notation_catalog.py`  
Regression: `results/attack_damage_notation_catalog/reproduce.py`

## Method

The catalog:

1. selects sets whose bundled Expanded legality is Legal;
2. applies the repository's effective-legality classifier at card level;
3. reads every attack's printed `damage` field;
4. accepts only five exact forms: blank, digits, digits+`, digits-`, or digits×.

The parser raises on any unknown notation. The regression therefore acts as a coverage tripwire when the card snapshot changes.

## Why this matters

The ordered damage kernel needs a reliable step-1 representation before more card text can be compiled into executable damage.

This scan establishes that the printed damage field itself has a very small grammar in the current corpus. The hard part is the attack text that determines the modifier or multiplier count, not the surface symbol beside the attack.

The rare minus family is especially important because the Advanced Player's Rulebook gives it an irreversible zero-damage boundary. If a minus attack reaches zero at step 1, a later attacker-side damage boost does not revive it.

The first effectively legal minus witness in catalog order is Throh `bw10-51` / Shoulder Throw, printed as `80-`.

## Compiler boundary

A safe future compiler can separate two tasks:

- parse the printed field exactly into a base value and notation kind;
- compile the associated text predicate or count expression into the runtime modifier.

The first task now has full observed coverage. The second task remains semantic and should be expanded conservatively rather than inferred from the symbol alone.

## Limitations

Coverage is for the current bundled English paper-Expanded snapshot after the repository's effective-legality layer. Regional-only cards outside that snapshot need separate validation.

Blank damage includes attacks whose value is purely effect-driven or whose damage semantics may be encoded entirely in text. A blank field must not automatically be interpreted as zero damage without reading the attack text.

Likewise, the presence of a plus, minus, or multiplication symbol identifies the arithmetic family but does not supply the condition, count source, coin result, or other runtime state needed to resolve the modifier.
