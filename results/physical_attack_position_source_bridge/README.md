# Physical copied-attack position-source bridge

## Question

Can a copied attack's exact printed Active/Bench movement resolve on the
stack-bearing physical board at the correct attack-effect timing while
preserving card-instance identity, target geometry, and later damage reactions?

## Model

`tools/physical_attack_position_source_bridge.py` consumes an already
resolved copied-attack body plus one exact attack profile from
`tools/position_effect_profile_compiler.py`.

The existing position profile now preserves `attack_index`, so the physical
bridge can require the exact body event
`body:<print-id>:attack:<index>` rather than matching only by attack name.

The bridge handles the three rulebook movement families already recognized by
the profile compiler: self-switch, opponent-forced switch, and targeted gust.
Coin-gated and optional branches require explicit inputs. Effect-immunity
overlays remain upstream and are checked against the rulebook-defined target
object. Physical switching clears the outgoing Active's Special Conditions and
temporary attack effects while preserving damage, stack identity, and
attachments.

## Card-grounded regressions

The single-file regression uses three legal source attacks copied through Team
Rocket's Persian ex's Haughty Order.

### Tapu Fini-GX Aqua Ring

Aqua Ring deals 20 damage and may switch the attacker with a Benched Pokemon.
The regression places a Burned copying attacker opposite a Roselia with a live
Poison Point reaction.

If the player declines the pivot, Poison Point can later add Poisoned to the
still-Active original attacker. If the player takes the Aqua Ring pivot, the
original attacker moves to the Bench during the attack-effect step, its Burned
condition clears, and its attached Energy remains. The later damage-triggered
Poison Point reaction still identifies the original attacker by physical ID,
yet cannot apply a Special Condition to that now-Benched Pokemon.

### Bayleef Push Down

Push Down deals 50 damage, then switches out the opponent's Active Pokemon with
the opponent choosing the replacement.

The regression gives the opposing Active exactly 50 HP. Damage first makes it
a pending Knock Out candidate. Push Down then moves that zero-HP Pokemon to the
Bench before the end-of-attack Knock Out check. The later simultaneous-KO
batch removes it from the Bench without requiring another promotion because
the attack effect already installed the replacement Active.

If attack-effect immunity blocks the old Active, the switch does not occur.
The zero-HP Pokemon remains Active and the later KO batch requires a
replacement promotion.

### Clefairy Follow Me

Follow Me is targeted gust. Effect immunity on the selected Benched target
blocks the movement, while immunity on the old Active does not. This preserves
the C-04/C-05 target-geometry distinction on the physical board.

## Architectural result

For this modeled subset, copied-attack position timing can preserve:

`damage -> source attack movement/effect -> damaged-by-attack reactions -> KO`

The attacker identity used by later reactions remains the physical Pokemon that
performed the attack even when a self-switch moves it to the Bench.

## Scope and limitations

This bridge intentionally accepts only complete attack bodies already compiled
by the conservative position-effect profile layer. Compound movement attacks
remain owned by `compound_position_effects`. Attack declaration legality,
Energy payment, stochastic coin generation, and derivation of live
effect-immunity state remain upstream responsibilities.

Damage is materialized by the copied-attack physical replay. This module owns
the later position-effect transaction and its physical state update.

## Reproduction

Run `python results/physical_attack_position_source_bridge/reproduce.py`.

CI workflow: `validate-physical-attack-position-source.yml`.
