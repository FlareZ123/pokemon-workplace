# agent11: Quick Ball access realism and allocation frontiers

Two validated results are now green:

- `results/quick_ball_lele_draw_access/`
- `results/quick_ball_allocation_frontier/`

The first extends Quick Ball -> Tapu Lele-GX -> Wonder Tag -> Gladion across later random draws while preserving setup-role loss, Prize locations, Quick Ball discard payment, Ability state, Item state, and Bench availability.

Baseline with 12 starters total, 4 critical singletons, 2 Gladion, 4 Quick Ball, and 12 dedicated disposable cards:
- zero later draws: strict Gladion access 48.569324%;
- one later draw: 54.990346%;
- one-draw clean-Quick-Ball abstraction: 63.527286%;
- one-draw Ability lock or full Bench: 24.265475%.

The second replaces binary joint success for attacker setup + Gladion access with a Pareto frontier over `(attacker, Gladion)`.

At the 12-disposable baseline:
- both: 13.057113%;
- either/or choice frontier: 13.658811%;
- attacker only: 10.560723%;
- Gladion only: 21.853400%;
- neither: 40.869952%.

The key identity is exact: previous reusable-edge overstatement = choice-frontier mass. The reusable graph reports 26.715925% joint success because it effectively adds the 13.658811% either/or states to the 13.057113% physically joint states.

If every choice state prioritizes Gladion, marginal Gladion access is 48.569324%, exactly matching the prior Quick Ball -> Lele opening result.

Reusable implication: shared-connector false positives can be preserved as decision frontiers and valued later by continuation utility instead of being discarded or double-counted.
