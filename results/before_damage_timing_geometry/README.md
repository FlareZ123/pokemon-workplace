# Before-damage timing geometry in paper Expanded

## Question

Which legal Expanded attacks modify state before damage calculation, and what does that timing imply for copied attacks and defensive resources?

## Rules basis

The Advanced Player's Rulebook resolves attacks in a fixed order.

Step 3 applies text introduced by `Before doing damage`. Step 4 then performs damage calculation. Other effects normally occur afterward.

Pokémon Tool effects are automatically active while the Tool is attached. A Tool removed in step 3 is therefore absent when damage calculation begins in step 4.

This timing distinction matters for damage-reduction Tools, HP-changing Tools, and other Tool effects that would otherwise influence the attack state.

## Card-pool inventory

`tools/before_damage_timing_catalog.py` scans the current legal Expanded card pool for attack text containing `Before doing damage`.

The bundled snapshot contains:

| Quantity | Count |
| --- | ---: |
| Legal print instances | 54 |
| Distinct attack signatures | 34 |
| Dragon signatures | 1 |

The 34 signatures classify as:

| Timing action | Signatures |
| --- | ---: |
| Opponent Tool removal | 25 |
| Own Tool discard for variable damage | 3 |
| Opponent Tool plus Special Energy removal | 1 |
| Opponent Special Energy removal | 1 |
| Self Tool gate | 1 |
| Self Energy attachment before damage | 1 |
| Opponent switch before damage | 1 |
| Coin branch before damage | 1 |

Tool removal dominates this timing family.

## Why pre-damage Tool removal is mechanically distinct

A simulator that resolves Tool removal after damage will use the wrong state for damage calculation.

Eviolite is a direct historical example from the same Expanded pool. Its effect reduces attack damage to an eligible Basic Pokémon while the Tool is attached. If an attack removes that Tool in step 3, Eviolite is gone before damage is calculated.

The same ordering principle applies to any Tool whose active effect changes the step-4 or later state.

This is a general state-transition requirement. The attack body needs an explicit timing phase rather than a flat unordered set of effects.

## Apex Dragon endpoint

The only Dragon Pokémon signature in this `Before doing damage` catalog is Dracovish V's **Slosh 'n' Crash**:

`Before doing damage, discard all Pokémon Tools from your opponent's Active Pokémon. If you discarded a Pokémon Tool in this way, this attack does 120 more damage.`

Its printed damage is 60+.

Apex Dragon can select this attack from a Dragon Pokémon in the user's discard pile. The copied attack therefore preserves the pre-damage Tool-removal timing.

Against an opponent's Active Pokémon with a Tool attached, the attack removes that Tool before damage calculation and satisfies its own Tool-discard condition for the 120-damage bonus. Against a Tool-less Active, the bonus condition is not satisfied.

This is a compact example of discrete tactical value inside the copy pool. The endpoint does damage, changes opponent state before damage, and has output conditional on that same state transition.

## Representation consequence

A copied attack executor should preserve at least these phases:

1. announcement and outer attack legality;
2. attack conditions on the attacker;
3. before-damage effects;
4. damage calculation;
5. effects outside damage;
6. damaged-trigger effects;
7. Knock Out checks.

The selected attack body can create state changes in an earlier phase that alter how later phases evaluate.

For copy systems, the phase belongs to the selected attack body while the actor and current game state belong to the actual attacking Pokémon and player.

## Method

The catalog uses the repository's Expanded-set filter and current print-level ban overlay. Signatures are deduplicated by attack name, printed damage, and normalized attack text.

Classification is a targeted wording parser for the current 34 signatures. The full signature list remains in the tool output so future wording changes can be audited.

## Limitations

This inventory covers explicit `Before doing damage` wording only. Other rules can alter state before or during damage calculation without using that phrase.

The catalog does not compute final damage against every legal Tool. Tool effects can affect HP, damage, Weakness, Resistance, retreat, attack access, or unrelated dimensions, so endpoint value remains matchup and state dependent.

The Dracovish V observation establishes access and timing. It does not by itself justify a deck slot.

## Next useful work

A useful extension is a phased attack-resolution kernel that can apply a selected attack body to a typed state and recalculate damage after each pre-damage mutation.

The existing lock-state and copy-semantics tools provide natural components for that kernel.
