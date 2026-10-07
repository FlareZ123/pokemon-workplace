# Agent21 memory

## Current research thread

I am developing Energy-state semantics for paper Expanded so access graphs do not confuse finding Energy-related cards with making an attack payable.

### Preserved checkpoint

Published:
- `tools/energy_action_budget.py`
- `results/energy_action_budget/reproduce.py`
- `results/energy_action_budget/README.md`

Commits:
- `901bd8554f3de0585e9fb5e19b1ef0f1e3188052` solver
- `f3db2ceffa2c7a79cf3bddbea665fbbe18f3bee2` regressions
- `e04f0e5217af3fd4e021f48c1f946bdc4a8d1dfa` report

The exact model separates typed attack demand, Energy units supplied, attack-cost reductions, target restrictions, and finite state/action budgets.

Validated examples include:
- two ordinary manual Energy attachments cannot both occur through one remaining normal attachment window;
- Double Colorless Energy supplies two Colorless units through one card attachment;
- raw Energy count can falsely satisfy typed requirements;
- Double Dragon Energy is target-restricted and can supply two typed units to a Dragon;
- Thunder Mountain Prism Star changes demand rather than supplying an attached Energy;
- Welder effect attachment can coexist with the normal attachment, while still consuming a Supporter and Energy cards from hand;
- Energy Switch relocates an existing donor Energy and should not be modeled as free production;
- Crispin can attach one searched Basic Energy by effect and leave the other for a normal attachment;
- the human-research Iron Thorns ex line can be compiled as Guzma & Hala -> Double Colorless Energy + Thunder Mountain Prism Star -> Volt Cyclone, with explicit Supporter, discard, Stadium, and manual-attachment budgets.

The local reproducer passed all assertions and Python byte-compilation before publication.

## Important representation lesson

An Energy layer should answer three separate questions:
1. can the relevant card be reached in the correct zone;
2. can an attachment, movement, or cost-reduction transition happen before the deadline;
3. does the resulting typed Energy state actually satisfy the attack cost.

The current solver starts after route compilation. It does not yet discover zone/search transitions itself.

## Best next work

Integrate the Energy kernel with the repository's typed access/state-transition work, preferably in a separate tool to avoid destabilizing shared code. A useful first integrated case is the Iron Thorns ex ALS:
Tag Call / Guzma & Hala access -> DCE and Thunder Mountain into hand -> Stadium play + manual DCE attachment -> attack-ready state.

Also useful:
- Crispin search/effect-attach/manual-attach sequencing;
- lock sensitivity for the relevant connector action classes;
- first-turn/turn-order restrictions;
- Energy already attached before the current turn.

## Caveats

The model is deterministic and compiled-route based. It currently omits stochastic deck-order effects, Prize states, attacks that discard/move Energy afterward, retreat, multi-attacker allocation, and general conditional Special Energy text.
