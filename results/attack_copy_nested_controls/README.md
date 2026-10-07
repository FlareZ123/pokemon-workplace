# Nested attack-copy controls

## Question

When a copy effect selects an attack whose own text contains a use requirement or stochastic gate, should that attack disappear from the selectable target set?

No. Selection and execution need separate state transitions.

Implementation:
- `tools/attack_copy_kernel.py`
- `tools/attack_copy_controlled_execution.py`

Regression:
- `results/attack_copy_nested_controls/reproduce.py`

## Rules anchor

The official Japanese Pokemon Card Game Q&A provides a direct witness. Slowking's **Inspiration Challenge** can select Sableye's **Lost Mine** after discarding Sableye from the top of the deck even when the copying player has fewer than 10 cards in the Lost Zone. The ruling says Lost Mine may be selected, then its processing does not occur and the attack ends because its requirement is not satisfied.

This separates three questions:

1. can the outer copy effect select the attack;
2. could that attack be announced directly;
3. after selection as a copied body, does its processing occur.

The first and third answers can differ.

## Kernel change

`resolve_attack()` now accepts an optional `copied_body_gate` callback.

The gate runs only when a selected attack body is entered recursively. It runs after the parent has legally selected the attack and before the child body applies GX state, turn-boundary effects, progress, pre-events, or another copy selector.

A failed gate therefore records the selected body in the execution trace while leaving its instructions unprocessed. The declared outer attack remains the player's last declared attack.

## Card-grounded regression

The repository's compiled **Genome Hacking** is used as the unrestricted outer copy attack.

### Genome Hacking -> Nightcap

Nightcap is preserved as a selectable guarded definition.

With the opponent on three Prize cards, Genome Hacking selects Nightcap, the nested Nightcap requirement fails, its body does not process, and the declared attack remains Genome Hacking.

With the opponent on exactly two Prize cards, the same selected Nightcap body continues and can execute its own selected endpoint.

### Genome Hacking -> Assist

Assist carries a coin-head body gate. If the nested invocation has no supplied coin outcome, execution raises an explicit unresolved-control result instead of assuming a branch. With heads, the Assist body proceeds and can use the selected Bench attack.

## Representation consequence

Guarded definitions must remain available in the attack registry used for copy target discovery. Removing them because they are unavailable for ordinary unsafe execution would make legal selections disappear.

Ordinary callers still receive `definition=None` for guarded compiled attacks. Direct execution therefore remains opt-in through the control-aware adapters.

## Limits

The current copied-body policy receives hand size, Prize count, and coin outcomes as external snapshot inputs. It does not yet derive those facts from a canonical match state.

Coin outcomes are keyed by attack ID, which is sufficient for the regression but is not a complete representation for repeated invocations of the same attack in one resolution.

This result handles controls attached to the six compiled copy attacks. A copied target can be any legal attack, including non-copy attacks such as Lost Mine. A broader attack-use-requirement compiler is the next generalization.
