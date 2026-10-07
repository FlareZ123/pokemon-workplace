# GX-use budget scope across copied attacks

## Question

When an attack copies a GX attack, where should a simulator charge the once-per-game GX-use resource?

The resource belongs to the player's declared attack resolution. A copied GX body can spend an unused GX channel, while a channel already spent before the attack began blocks GX use. Nested GX bodies inside the same declared resolution must not be charged as separate GX attacks.

Implementation: `tools/attack_copy_kernel.py`  
Regression: `results/attack_copy_gx_budget_scope/reproduce.py`

## Evidence

The Advanced Player's Rulebook C-18 says that `use it as this attack` executes the selected attack's effects and damage while the copying attack remains the declared attack identity in the Foul Play example.

A January 5, 2017 TPCi Rules Team ruling, preserved in the Sun & Moon FAQ and reproduced by PokéBeach, explicitly answers the key resource case for Clefairy's Metronome: Metronome may copy a GX attack, doing so uses the player's one GX attack for the game, and an already-used GX channel prevents choosing the GX attack.

The current legal Zoroark-GX card text supplies the nested boundary case. Trickster-GX is itself a GX attack and says to choose one of the opponent's Pokémon's attacks and use it as Trickster-GX. Its selector does not exclude GX attacks.

## Kernel correction

The earlier copy kernel charged the GX channel every time it entered a body marked `is_gx`. That representation incorrectly treats an outer GX copy attack and the GX body it selects as two separate GX uses.

The kernel now snapshots whether the acting player had already used a GX attack before the declared attack resolution begins.

For every GX body reached during that resolution:

- if the GX channel was already spent before the resolution, execution is rejected;
- otherwise the player's GX-used state is set;
- later GX bodies within the same nested resolution observe the same pre-resolution eligibility and do not create a second charge.

## Regressions

The result checks four cases:

1. **Foul Play -> Timeless-GX, unused channel:** the copied GX body resolves and the player becomes GX-spent.
2. **Foul Play -> Timeless-GX, already-spent channel:** the copied GX body is rejected.
3. **Trickster-GX -> Timeless-GX, unused channel:** the outer GX copy attack and selected GX body resolve under one GX-use budget.
4. **Trickster-GX after an earlier GX use:** the declared GX attack is rejected before it can create a fresh GX use.

The third case is the representation boundary that exposed the previous bug.

## State-model implication

GX usage is a player-global resource with a before-resolution eligibility condition. It should not be modeled as a consumable token charged independently by every copied attack body on the execution stack.

This parallels the existing distinction between declared attack identity and copied body identity: nested execution can contain several attack definitions while still representing one declared attack resolution and one turn-ending attack action.

## Limitations

This result does not model pre-attack failure such as Confusion, attack-declaration legality, or every historical GX ruling. Those belong before or around the copy-resolution kernel.

The Trickster-GX nested case is a rules-model inference from C-18 semantics, the once-per-game GX rule, the TPCi Metronome ruling, and Trickster-GX's unrestricted selector. It is preserved explicitly so future work can challenge the representation if stronger primary-source guidance is found.
