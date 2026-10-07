# Selected-attack Energy gates are body gates, not target illegality

## Question

How should a copy resolver model attacks such as Ditto's **Copy Anything**, whose text selects another attack and then says the copying Pokémon must have the necessary Energy to use it?

The Energy clause gates execution of the selected body. Failing that gate does not retroactively make the selected target illegal, and the declared attack still counts as used.

Implementation: `tools/attack_copy_kernel.py`  
Regression: `results/attack_copy_selected_energy_gate/reproduce.py`

## Rules basis

Advanced Player's Rulebook C-18 establishes the general rule that a copying Pokémon can execute the chosen attack's effects and damage without having the Energy required by the chosen attack, unless the copying text says otherwise.

The same section gives **Copy Anything** as the explicit exception: the attack first chooses an opponent's attack and says that if the copying Pokémon lacks the necessary Energy, the attack does nothing.

The rulebook's terminology section separately states that an attack that "does nothing" still counts as having been used and the turn ends.

## Execution consequence

A resolver should distinguish three events:

1. the declared copy attack is legal and is used;
2. a selected attack target is identified;
3. a selected-target-dependent Energy gate decides whether that body's effects and damage execute.

Collapsing step 3 into target filtering changes the semantics. It turns a valid used attack that does nothing into an illegal selection.

## Kernel representation

`CopySelector.require_selected_energy` now requests a selected-body Energy check.

The copying Pokémon carries modeled attached Energy units. The selected attack carries its modeled Energy cost. The kernel uses the repository's typed Energy feasibility engine to evaluate whether those units satisfy the selected cost.

If the check fails:

- the selected attack remains recorded in the trace;
- `selected_body_executed` is false;
- the selected body is not appended to the executed body chain;
- the declared attack identity is still stored as the player's last attack.

## Regressions

A synthetic endpoint costs Fire + Colorless + Colorless.

- Copy Anything with only two matching Energy units selects the endpoint, executes no endpoint body, and still hands the turn to the opponent through the canonical turn scheduler.
- With three matching units, the selected body executes.
- Generic C-18 copying through **Foul Play** executes the same endpoint with no matching Energy at all, confirming that the Energy gate is edge-local to the copy attack that states it.

## Architectural implication

Copy constraints can apply at different semantic phases.

A source restriction determines which target may be selected. A selected-attack Energy clause can instead determine whether an already selected body's effects run. Static composition graphs should preserve that distinction if they are later used to predict executable lines.

## Limitations

The small Energy check models attached typed Energy units against the selected attack's represented cost. It does not yet compile dynamic attack-cost modifiers, Special Energy cards whose provided units change with state, effects that say to ignore costs, or historical wording nuances.

Those are existing concerns of the repository's typed Energy and board-state layers and can be integrated later without changing the body-gate distinction established here.
